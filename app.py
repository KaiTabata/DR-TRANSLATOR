import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, session
from werkzeug.utils import secure_filename #ファイル名保護用
from datetime import timedelta #settion管理で時間情報を用いるため

UPLOAD_FOLDER = '/temp/uploads'
ALLOWED_EXTENSIONS = {'docx', 'pdf', 'doc', 'gdoc'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'user'
app.permanent_session_lifetime = timedelta(minutes=5) # -> 5分 #(days=5) -> 5日保存

@app.route('/')
def index():
    return render_template("index.html")


#拡張子が有効かどうか確認する関数
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
#アップロードされたファイルのURLにリダイレクトする関数
def upload_file():
    if request.method == 'POST':
        # post リクエストがファイル部分を持つかどうかをチェック
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # ユーザーがファイルを選択しない場合、ファイル名のない空のファイルを送信
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost')
