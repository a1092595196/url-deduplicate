from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
import os
from werkzeug.utils import secure_filename
import chardet

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                return jsonify(error="未选择文件"), 400
            file = request.files['file']
            
            if file.filename == '':
                return jsonify(error="文件名为空"), 400
            
            if not allowed_file(file.filename):
                return jsonify(error="仅支持 TXT 文件"), 400
            
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            encoding = detect_encoding(input_path)
            
            output_filename = f"deduplicated_{filename}"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            seen_urls = set()
            try:
                with open(input_path, 'r', encoding=encoding, errors='replace') as infile, \
                     open(output_path, 'w', encoding='utf-8') as outfile:
                    for line in infile:
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split(maxsplit=1)
                        url_part = parts[0]
                        comment_part = parts[1] if len(parts) > 1 else ""
                        
                        if url_part not in seen_urls:
                            seen_urls.add(url_part)
                            outfile.write(f"{url_part} {comment_part}\n")
            except Exception as e:
                return jsonify(error=f"文件处理失败: {str(e)}"), 500
            
            os.remove(input_path)
            
            return redirect(url_for('download', filename=output_filename))
        
        except Exception as e:
            return jsonify(error=f"服务器内部错误: {str(e)}"), 500
    
    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    try:
        return send_file(
            os.path.join(app.config['UPLOAD_FOLDER'], filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify(error=f"文件下载失败: {str(e)}"), 404

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
