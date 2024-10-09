import json
import os
from flask import Blueprint, request, render_template
from app.core.base_response import Response
from app.utils.logger import logger
from app.core.admin.login.utils import admin_required

# 创建蓝图
bp = Blueprint("third_payment_config", __name__, url_prefix="/admin/third/payment", template_folder="templates", static_folder='static')

@bp.route("/config", methods=["POST", "GET"])
@admin_required
def config():
    current_dir = os.getcwd()  # 获取当前工作目录
    json_file = os.path.join(current_dir, "app", "plugins", "third_payment", "payment_config.json")  # JSON配置文件路径
    if request.method == "POST":
        try:
            # 解析 JSON 数据
            json_data = request.get_json()  # 获取 JSON 数据
            if not json_data:
                return Response.error(msg="无效的输入数据")  # 返回错误信息

            # 转换为嵌套结构
            config_data = {}
            for key, value in json_data.items():
                # 解析出 row 名称和字段
                parts = key.split('[')
                if len(parts) > 1:
                    main_key = parts[1][:-1]  # 取出主要键名
                    sub_key = parts[2][:-1] if len(parts) > 2 else None  # 取出子键名
                    if main_key not in config_data:
                        config_data[main_key] = {}
                    if sub_key:
                        config_data[main_key][sub_key] = value
            
            # 写入 JSON 文件
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False)  # 确保写入非ASCII字符

        except Exception as e:
            return Response.error(msg=f"发生错误: {e}")  # 返回错误信息
        
        return Response.success(msg="保存成功。")  # 返回成功信息

    # 读取并渲染配置文件
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            configs = json.load(f)  # 加载配置文件内容
    except FileNotFoundError:
        configs = {}  # 如果文件不存在，初始化为空字典

    return render_template("config.jinja2", payment_config=configs)  # 渲染模板

@bp.route("/upload", methods=["POST"])
@admin_required
def upload():
    current_dir = os.getcwd()  # 获取当前工作目录
    upload_directory = os.path.join(current_dir, "app", "plugins", "third_payment", "certs")  # 上传目录
    allowed_extensions = ['.pem']  # 允许的文件扩展名

    # 获取上传的文件和文件名
    upload_file = request.files.get('file')
    save_filename = request.form.get('filename')

    if not upload_file or not save_filename:
        return Response.error(msg='文件和文件名是必需的。')  # 检查文件和文件名是否存在

    filename = upload_file.filename
    ext = os.path.splitext(filename)[1].lower()  # 获取文件扩展名并转为小写

    if ext not in allowed_extensions:
        return Response.error(msg='不允许的文件类型。')  # 检查文件类型

    # 构建保存的文件路径
    file_path = os.path.join(upload_directory, f'{save_filename}{ext}')

    # 确保目标目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # 创建目录

    # 保存文件
    with open(file_path, 'wb') as output_file:
        output_file.write(upload_file.read())  # 写入文件内容

    return Response.success(msg="上传成功。", data=file_path)  # 返回成功信息和文件路径
