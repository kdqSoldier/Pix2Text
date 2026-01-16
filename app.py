'''
@Description: 
@Author: QiLan Gao
@Date: 2025-06-06 12:10:17
@LastEditTime: 2025-06-06 17:34:44
@LastEditors: QiLan Gao
'''
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from formula_worker import FormulaWorker

app = Flask(__name__)
UPLOAD_FOLDER = os.path.abspath("uploads")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 初始化 FormulaWorker
worker = FormulaWorker()

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(full_path):
        print(f"[❌ 文件不存在] {full_path}")
    else:
        print(f"[✅ 访问图片] {full_path}")
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recognize', methods=['POST'])
def recognize():
    print("[DEBUG] 收到 POST /recognize")
    file = request.files.get('file')
    if not file:
        return jsonify({'error': '未检测到图像'}), 400

    filename = datetime.now().strftime("%Y%m%d%H%M%S_") + secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # 调用 FormulaWorker 的 recognize 方法
        result = worker.recognize(filepath)
        return jsonify({'image': filename, 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
