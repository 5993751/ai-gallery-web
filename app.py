# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
from werkzeug.utils import secure_filename

# =============================================
# 1. 初始化后端服务器
# =============================================
app = Flask(__name__)
CORS(app)  # 允许所有前端跨域访问（以后你随便写HTML都能连）

# 配置文件（优化版）
UPLOAD_FOLDER = 'uploads'  # 图片存到这个文件夹（会自动在 L:\daima 下面创建）
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制单张图片最大 16MB（防止服务器卡死）

# 允许的图片格式（不够自己加）
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}

# 启动时自动创建 L:\daima\uploads 文件夹（你完全不用手动管）
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print(f"📁 已自动创建图片目录: {os.path.abspath(UPLOAD_FOLDER)}")


# =============================================
# 2. 辅助函数
# =============================================
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# =============================================
# 3. 核心后端接口（API）
# =============================================

# 【接口1】根路径测试（返回JSON，让前端知道后端活着）
@app.route('/')
def hello():
    return jsonify({
        "code": 200,
        "message": "🎨 画廊后端运行正常！",
        "tips": {
            "获取图片列表": "GET /api/images",
            "上传图片": "POST /upload (字段名: file)",
            "查看图片": "GET /images/文件名"
        },
        "server_time": str(uuid.uuid4())  # 随便加个动态值，表示服务在动
    })


# 【接口2】获取所有图片列表（按上传时间倒序，最新的排最前面）
@app.route('/api/images', methods=['GET'])
def get_images():
    try:
        files = os.listdir(UPLOAD_FOLDER)
        # 只保留允许的图片格式
        image_list = [f for f in files if allowed_file(f)]
        # 按修改时间倒序排列（最新的靠前）
        image_list.sort(
            key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER, x)),
            reverse=True
        )
        return jsonify({
            "code": 200,
            "message": f"获取成功，共 {len(image_list)} 张图片",
            "data": image_list
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"}), 500


# 【接口3】上传图片（核心接口）
@app.route('/upload', methods=['POST'])
def upload_image():
    # 检查前端是否传了文件
    if 'file' not in request.files:
        return jsonify({"code": 400, "message": "错误：缺少文件字段，请使用字段名 'file'"}), 400

    file = request.files['file']

    # 检查是否选了空文件
    if file.filename == '':
        return jsonify({"code": 400, "message": "错误：未选择文件"}), 400

    # 检查文件格式
    if not allowed_file(file.filename):
        return jsonify({
            "code": 400,
            "message": f"不支持此格式，请上传: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400

    try:
        # 获取原始扩展名
        ext = file.filename.rsplit('.', 1)[1].lower()
        # 生成唯一文件名（防止重名覆盖）
        unique_name = str(uuid.uuid4()) + '.' + ext
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)

        # 保存到硬盘（L:\daima\uploads\随机名.后缀）
        file.save(save_path)

        # 打印日志到终端（方便你调试）
        print(f"✅ 上传成功 -> {unique_name} (保存在 {os.path.abspath(save_path)})")

        return jsonify({
            "code": 200,
            "message": "上传成功！",
            "filename": unique_name,
            "url": f"/images/{unique_name}"  # 额外返回访问路径，方便前端直接使用
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"保存失败: {str(e)}"}), 500


# 【接口4】访问图片（浏览器的 <img> 标签直接调用这个地址）
@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# =============================================
# 4. 启动服务（运行就靠它）
# =============================================
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 画廊后端服务器启动中（优化版）...")
    print(f"📂 图片存储绝对路径: {os.path.abspath(UPLOAD_FOLDER)}")
    print("🌐 本地访问地址: http://127.0.0.1:5000")
    print("📡 前端请求根地址: http://127.0.0.1:5000")
    print("📏 单张图片大小限制: 16 MB")
    print("=" * 60)
    # host='0.0.0.0' 让同一台电脑下的局域网设备（比如手机）也能访问
    app.run(debug=True, host='0.0.0.0', port=5000)