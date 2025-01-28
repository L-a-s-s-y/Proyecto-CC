import logging.handlers
import os
from flask import Flask, request, redirect, url_for, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from ffcuesplitter.cuesplitter import InvalidFileError
from ffcuesplitter.cuesplitter import FFCueSplitterError
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
import splitter

#flask --app api run --host='0.0.0.0'

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'flac', 'ape', 'mp3', 'wav'}
ALLOWED_CUE = {'cue'}

app = Flask(__name__)
#CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

el_logger = logging.getLogger()

#el_logger_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%m-%Y | %H:%:%S")

consoleHandler = logging.StreamHandler()
#consoleHandler.setFormatter(el_logger_formatter)
el_logger.addHandler(consoleHandler)

fileHandler = logging.handlers.RotatingFileHandler("logs.log", backupCount=100, maxBytes=1048576, encoding='utf-8')
#fileHandler.setFormatter(el_logger_formatter)
el_logger.addHandler(fileHandler)

#@app.after_request
#def after_request(response):
#    response.headers.add('Access-Control-Allow-Origin', '*')  # Permite todas las solicitudes de origen
#    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')  # Cabeceras permitidas
#    response.headers.add('Access-Control-Allow-Methods', 'GET,POST')  # Métodos permitidos
#    return response
#
#@app.before_request
#def log_request_info():
#    el_logger.debug(f"Request Headers: {request.headers}")
#    el_logger.debug(f"Request Body: {request.get_data()}")

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




#@app.route('/', methods=['GET', 'POST'])
#TODO: para el hash seguramente haya que hacerlo del archivo completo :(
@app.route('/cue', methods=['POST'])
def upload_cue():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            #flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            #flash('No selected file')
            return redirect(request.url)
        if file and allowed_cue(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            mod_cue_target_file(filename)
            response = {}
            
            response['filename'] = filename
            return response
            #return redirect(url_for('wellcome_audio', name=filename))
        else:
            error = {}
            error['error'] = "not a .cue file"
            return error

@app.route('/audio', methods=['POST'])
def upload_audio():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            #flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        #cue = request.args['name'] #para tomar el nombre del cue origen
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            #flash('No selected file')
            return redirect(request.url)
        if file and allowed_audio(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            response = {}
            response['filename'] = filename
            return response
            #return redirect(url_for('info_cue', name=cue))
        else:
            error = {}
            error['error'] = "not a valid audio file"
            return error

@app.route('/download/<name>', methods=['GET'])
def download_file(name):
    try:
        comprimido = splitter.split_it_like_solomon(os.path.join(app.config['UPLOAD_FOLDER'], name))
        respuesta = send_from_directory(app.config['UPLOAD_FOLDER'], comprimido.split('/')[2])
        #respuesta.headers['Access-Control-Allow-Origin'] = '*'
        respuesta.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return respuesta
        #return send_from_directory(app.config['UPLOAD_FOLDER'], comprimido.split('/')[2], as_attachment=True)
    except InvalidFileError:
        error = {}
        error['error'] = "InvalidFileError: "+name+" no existe en el directorio."
        return error
    except FFCueSplitterError:
        error = {}
        error['error'] = "FFCueSplitterError: el archivo de audio no existe o no se puede abrir."
        return error

@app.route('/info/<name>', methods=['GET'])
def info_cue(name):
    try:
        respuesta = splitter.album_info(os.path.join(app.config['UPLOAD_FOLDER'], name))
        respuesta['cue_file'] = name
        return respuesta
    except InvalidFileError:
        error = {}
        error['error'] = "InvalidFileError: "+name+" no existe en el directorio."
        return error
    except FFCueSplitterError:
        error = {}
        error['error'] = "FFCueSplitterError: el archivo de audio no existe o no se puede abrir."
        return error
    
#@app.route('/cue', methods=['GET'])
#def wellcome_cue():
#    return '''
#    <!doctype html>
#    <title>Upload new File</title>
#    <h1>Upload new File</h1>
#    <form method=post enctype=multipart/form-data>
#      <input type=file name=file>
#      <input type=submit value=Upload>
#    </form>
#    '''
#
#@app.route('/audio', methods=['GET'])
#def wellcome_audio():
#    return '''
#    <!doctype html>
#    <title>Upload new File</title>
#    <h1>Upload new File</h1>
#    <form method=post enctype=multipart/form-data>
#      <input type=file name=file>
#      <input type=submit value=Upload>
#    </form>
#    '''
#@app.route('/', methods=['GET'])
#def wellcome():
#    return redirect(url_for('wellcome_cue'))