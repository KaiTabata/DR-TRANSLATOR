import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, session
from werkzeug.utils import secure_filename #ファイル名保護用
from datetime import timedelta #settion管理で時間情報を用いるため

'''Docx'''
import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from docx.oxml.xmlchemy import OxmlElement
from docx import Document
from retry import retry
from googletrans import Translator
import array
import os
import sys
import time
import requests
import json

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['docx', 'pdf', 'doc', 'gdoc'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'user'
app.permanent_session_lifetime = timedelta(minutes=5) # -> 5分 #(days=5) -> 5日保存

#拡張子が有効かどうか確認する関数
def allowed_file(filename):
    # .があるかどうかのチェックと、拡張子の確認
    # OKなら１、だめなら0
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template("index.html")



@app.route('/upload', methods=['GET', 'POST'])

#アップロードされたファイルのURLにリダイレクトする関数
def upload_file():
    if request.method == 'POST':
        print("POST requested!!")

        file = request.files.get('filename')

        # post リクエストがファイル部分を持つかどうかをチェック
        if 'filename' not in request.files:
            print('No file part')
            return redirect(request.url)

        # ユーザーがファイルを選択しない場合、ファイル名のない空のファイルを送信
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            securename = secure_filename(file.filename)
            print(securename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], securename))
            return redirect(url_for('translate_file', name=securename))
    return render_template("upload.html")


@app.route('/uploads/translated_<name>')
def translate_file(name):
    translator = Translator(service_urls=['translate.googleapis.com'])
    dest_lang = "ja"
    doc = docx.Document("./uploads/"+name)
    pg= len(doc.paragraphs) #文書内の段落数を取得
    print("処理が始まりました")

    array=[]
    for i in range(1, pg): #ループ：最初の段落であるタイトルを除いてドキュメントの各段落に実行　あとでtwdmかます
        try:
            para=doc.paragraphs[i]
        except IndexError as e:
          print(e)
          break #トライキャッチ：インデックスエラーの捕捉。パラグラフが翻訳されていればコメントが追加。もし段落が空であればその段落をスキップ

        bfori_text=para.text
        bfori_text=bfori_text.replace("\r","")
        ori_text=bfori_text.replace("\x07","")
        if str(ori_text)=="":
            z=1
            print("パラグラフ　"+str(i)+"　はテキストが存在しないのでパスしました。")
        else:
            z=0
            translation = translator.translate(ori_text, dest=dest_lang)
            array.extend([ori_text, translation.text])
            time.sleep(0.0005)
            print("Google Translate :: "+ori_text)
        if z==0:
            try:
                run = para.add_run(' ')
                run.add_comment(translation.text,author='DR_translator',initials= 'KT')
            except:
                print("何らかの理由により、パラグラフ　"+str(i)+"　はコメントを追加することができませんでした。")

    core_properties = doc.core_properties
    lastpara = doc.add_paragraph(" ")
    lastrun = lastpara.add_run(' ')
    lastrun.add_comment("Document_Revision: "+str(core_properties.revision)+"\n"+"このファイルはDR_translatorによって自動翻訳されています。訳文のコメントを削除したい場合は、校閲→コメント→ドキュメント内のすべてのコメントを削除を押下してください。",author='DR_translator',initials= 'KT')
    downloadfile = "translated_"+name
    doc.save(os.path.join(app.config['UPLOAD_FOLDER'], downloadfile))
    return send_from_directory(app.config["UPLOAD_FOLDER"], downloadfile)

if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost')
