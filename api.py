import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import splitter

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'flac', 'ape', 'mp3', 'wav'}
ALLOWED_CUE = {'cue'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_audio(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_cue(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_CUE

def mod_cue_target_file(cue_sheet):
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], cue_sheet)): # Si el cue está en el servidor
        cue_en_lista = []
        with open(os.path.join(app.config['UPLOAD_FOLDER'], cue_sheet),'r') as mod_cue:
            cue_en_lista = [ line for line in mod_cue ]
        print("--------------------------------------")
        for i in range(len(cue_en_lista)):
            if cue_en_lista[i].split(' ')[0] == "FILE":
                el_split = cue_en_lista[i].split('\"')
                el_split[1] = secure_filename(el_split[1])
                cue_en_lista[i] = '\"'.join(el_split)
        with open(os.path.join(app.config['UPLOAD_FOLDER'], cue_sheet),'w') as mod_cue:
            mod_cue.writelines(cue_en_lista)
        print("CUE ajustado")      
        print("--------------------------------------")

@app.route('/', methods=['GET'])
def wellcome():
    return redirect(url_for('wellcome_cue'))

@app.route('/cue', methods=['GET'])
def wellcome_cue():
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/audio', methods=['GET'])
def wellcome_audio():
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

#@app.route('/', methods=['GET', 'POST'])
#TODO: para el hash seguramente haya que hacerlo del archivo completo :(
@app.route('/cue', methods=['POST'])
def upload_cue():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_cue(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            mod_cue_target_file(filename)
            return redirect(url_for('wellcome_audio', name=filename))

@app.route('/audio', methods=['POST'])
def upload_audio():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        cue = request.args['name']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_audio(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('info_cue', name=cue))

@app.route('/download/<name>', methods=['GET'])
def download_file(name):
    comprimido = splitter.split_it_like_solomon(os.path.join(app.config['UPLOAD_FOLDER'], name))
    return send_from_directory(app.config['UPLOAD_FOLDER'], comprimido.split('/')[2])

#TODO: seleccionar el archivo cue.
@app.route('/info/<name>', methods=['GET'])
def info_cue(name):
    respuesta = splitter.album_info(os.path.join(app.config['UPLOAD_FOLDER'], name))
    respuesta['cue_file'] = name
    return respuesta