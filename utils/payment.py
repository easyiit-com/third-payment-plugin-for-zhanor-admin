import json
import time
import uuid
import logging
from flask import request
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradeAppPayModel import AlipayTradeAppPayModel
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.request.AlipayTradeAppPayRequest import AlipayTradeAppPayRequest
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from wechatpayv3 import WeChatPay, WeChatPayType
from app.utils.logger import logger

class Payment:
    def __init__(self):
        self.config = self._load_payment_config()
        self._alipay_client = None
        self._wechatpay = None

    def _load_payment_config(self):
        with open('app/plugins/third_payment/payment_config.json', 'r') as f:
            return json.load(f)

    @property
    def alipay_client(self):
        if self._alipay_client is None:
            alipay_client_config = AlipayClientConfig()
            alipay_client_config.server_url = 'https://openapi.alipay.com/gateway.do'
            alipay_client_config.app_id = self.config['alipay']['app_id']
            alipay_client_config.app_private_key = self.config['alipay']['private_key']
            alipay_client_config.alipay_public_key = self.config['alipay']['ali_public_key']
            self._alipay_client = DefaultAlipayClient(alipay_client_config=alipay_client_config)
        return self._alipay_client

    @property
    def wechatpay(self):
        if self._wechatpay is None:
            with open(self.config['wechat']['cert_key']) as f:
                private_key = f.read()

            self._wechatpay = WeChatPay(
                wechatpay_type=WeChatPayType.NATIVE,
                mchid=self.config['wechat']['mch_id'],
                private_key=private_key,
                cert_serial_no=self.config['wechat']['cert_serial_no'],
                appid=self.config['wechat']['appid'],
                apiv3_key=self.config['wechat']['api_v3_key'],
                notify_url=self.config['wechat']['notify_url'],
                cert_dir=None,
                logger=logging.getLogger("wechatpay"),
                partner_mode=False,
                proxy=None,
                timeout=(10, 30)
            )
        return self._wechatpay

    def process_payment(self, order_id, order_identifier, amount, payment_type, pay_method, wechatpay_type=WeChatPayType.NATIVE):
        """
        处理支付请求。

        Args:
            order_id (str): 订单号。
            order_identifier (str): 订单描述或标题。
            amount (float): 支付金额。
            payment_type (str): 支付平台（'alipay' 或 'wechat_pay'）。
            pay_method (str): 支付方式（'web' 或 'app'）。
            wechatpay_type (WeChatPayType, optional): 微信支付类型，默认是 NATIVE。

        Returns:
            dict: 支付响应数据。
        """
        if payment_type == 'alipay':
            return self._alipay_payment(order_id, order_identifier, amount, pay_method)
        elif payment_type == 'wechat_pay':
            return self._wechat_payment(order_id, order_identifier, amount, pay_method, wechatpay_type)
        else:
            raise ValueError("Invalid payment type. Choose 'alipay' or 'wechat_pay'.")

    def _alipay_payment(self, order_id, order_identifier, amount, pay_method):
        if pay_method == 'web':
            model = AlipayTradePagePayModel()
            model.out_trade_no = order_id
            model.total_amount = str(amount)
            model.subject = order_identifier
            model.product_code = "FAST_INSTANT_TRADE_PAY"
            # model.qr_pay_mode = 1
            request = AlipayTradePagePayRequest(biz_model=model)
            request.notify_url = self.config['alipay']['notify_url']
            response = self.alipay_client.page_execute(request, http_method="GET")
            return {"payment_code": response}
        elif pay_method == 'app':
            model = AlipayTradeAppPayModel()
            model.timeout_express = "90m"
            model.total_amount = str(amount)
            model.subject = order_identifier
            model.out_trade_no = order_id
            request = AlipayTradeAppPayRequest(biz_model=model)
            request.notify_url = self.config['alipay']['notify_url']
            response = self.alipay_client.sdk_execute(request)
            return {"payment_code": response}
        else:
            raise ValueError("Invalid pay method. Choose 'web' or 'app'.")

    def _wechat_payment(self, order_id, order_identifier, amount, pay_method, wechatpay_type):
        description = order_identifier
        out_trade_no = order_id
        amount_data = {'total': int(float(amount) * 100)}
        
        if pay_method == 'web':
            code, message = self.wechatpay.pay(
                description=description,
                out_trade_no=out_trade_no,
                amount=amount_data,
                pay_type=wechatpay_type,
                scene_info={'payer_client_ip': request.remote_addr}
            )
            logger.info(f"微信支付返回====>message:{message}")
            result = json.loads(message)
            if code in range(200, 300):
                return {"code_url": result.get('code_url')}
            else:
                return {'code': -1, 'result': {'reason': result.get('code')}}
        elif pay_method == 'app':
            code, message = self.wechatpay.pay(
                description=description,
                out_trade_no=out_trade_no,
                amount=amount_data,
                pay_type=WeChatPayType.APP
            )
            result = json.loads(message)
            if code in range(200, 300):
                prepay_id = result.get('prepay_id')
                timestamp = str(int(time.time()))
                nonce_str = uuid.uuid4().hex
                sign = self.wechatpay.sign(data=[
                    self.config['wechat']['appid'], timestamp, nonce_str, prepay_id
                ])
                return {
                    'code': 0,
                    'result': {
                        'appid': self.config['wechat']['appid'],
                        'partnerid': self.config['wechat']['mch_id'],
                        'prepayid': prepay_id,
                        'package': 'Sign=WXPay',
                        'nonceStr': nonce_str,
                        'timestamp': timestamp,
                        'sign': sign
                    }
                }
            else:
                return {'code': -1, 'result': {'reason': result.get('code')}}
        else:
            raise ValueError("Invalid pay method. Choose 'web' or 'app'.")

    @staticmethod
    def wechatpay_callback(wechatpay_instance):
        return wechatpay_instance.callback(request.headers, request.data)
