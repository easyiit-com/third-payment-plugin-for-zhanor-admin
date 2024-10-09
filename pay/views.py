import json
import os
from flask import Blueprint, request, render_template
from app.core.base_response import Response
from app.utils.logger import logger
from app.core.admin.login.utils import admin_required

# 创建蓝图
bp = Blueprint("third_payment", __name__, url_prefix="/third/payment", template_folder="templates", static_folder='static')

@bp.route("/pay", methods=["POST", "GET"])
def config():
    current_dir = os.getcwd()  # 获取当前工作目录
    json_file = os.path.join(current_dir, "app", "plugins", "third_payment", "payment_config.json")  # JSON配置文件路径
    if request.method == "POST":
        try:
            # 解析 JSON 数据
            json_data = request.get_json()  # 获取 JSON 数据
        except Exception as e:
            return Response.error(msg=f"发生错误: {e}")  # 返回错误信息
        
        return Response.success(msg="保存成功。")  # 返回成功信息

    # 读取并渲染配置文件
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            configs = json.load(f)  # 加载配置文件内容
    except FileNotFoundError:
        configs = {}  # 如果文件不存在，初始化为空字典

    return render_template("pay.jinja2", payment_config=configs)  # 渲染模板
