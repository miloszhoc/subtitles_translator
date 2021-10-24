import os
from config import app, db, jsonify, request, API_KEY, ALLOWED_EXTENSIONS, azure_storage, AZURE_CONTAINER_NAME
import models
from flask import render_template, url_for, redirect, send_file
from werkzeug.utils import secure_filename
from translate.languages import show_all_languages_translation
from translate.translate import Translator
import requests
from io import BytesIO
import datetime

# for uploaded files
UPLOAD_FOLDER = r'files/'

# for translated files
TRANSLATED_FOLDER = r'files/translated/'

# for uploaded files
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# determine extension
def extensions(f_name):
    ext = f_name.split('.')[-1]
    return True if ext in ALLOWED_EXTENSIONS else False


# add language code to file name and set new path for translated files
def name_for_translated(lang, path=None, f_name=None):
    if f_name is not None:
        f_name = f_name.split('.')
        f_name.insert(-1, lang)
        return '.'.join(f_name)
    else:
        path = path.split('.')
        path.insert(-1, lang)
        path = '.'.join(path).split('/')
        path.insert(-1, 'translated')
        return '/'.join(path)


def add_timestamp(file_name):
    file_name = file_name.split('.')
    file_name.insert(-1, str(datetime.datetime.now().timestamp()))
    return '.'.join(file_name)


# download translated file
@app.route('/download', methods=['POST'])
def download():
    if request.method == 'POST':
        f_id = request.form['f_id']
        schema = models.FileSchema()
        file = models.File.query.get(f_id)
        data = schema.dump(file)
        translated = data['translated_file']

        # download a file from memory
        content = azure_storage.block_blob_service.get_blob_to_bytes(container_name=AZURE_CONTAINER_NAME,
                                                                     blob_name='translated/' + translated, ).content
        s = BytesIO(content)
        return send_file(s, as_attachment=True, attachment_filename=translated)

    return redirect(url_for('upload'))


@app.route('/files', methods=['GET'])
def get_files():
    schema = models.FileSchema(many=True)
    files = models.File.query.order_by(models.File.id.desc())
    data = schema.dump(files)
    return jsonify(data)


# add file to database
def add_file(original, translated):
    success = False
    error = ''
    data = []
    try:
        new_file = models.File(original, translated)
        db.session.add(new_file)
        db.session.commit()
        db.session.refresh(new_file)
        data = {'id': new_file.id,
                'original_file': original,
                'translated': translated}
        success = True
    except Exception as e:
        error = str(e)
    finally:
        return {'success': success,
                'data': data,
                'error': error}


def translate_subtitles(file, lang):
    original_filename = secure_filename(file.filename)  # source file name
    original_filename = add_timestamp(original_filename)
    path_to_original_file = os.path.join(UPLOAD_FOLDER + original_filename)  # path to source file

    file.save(os.path.join(UPLOAD_FOLDER, original_filename))  # save source file locally (temporarily)

    # save file to azure blob storage
    azure_storage.block_blob_service.create_blob_from_path(container_name=AZURE_CONTAINER_NAME,
                                                           blob_name='original/' + file.filename,
                                                           file_path=path_to_original_file)

    # set new name and path for translated file
    translated_file_name = name_for_translated(lang=lang, f_name=original_filename)
    translated_file_path = os.path.join(TRANSLATED_FOLDER, translated_file_name)

    # translate subtitles
    tr = Translator(API_KEY, path_to_original_file)
    tr.translate_all(lang, translated_file_path)

    # upload translated file to azure
    azure_storage.block_blob_service.create_blob_from_path(container_name=AZURE_CONTAINER_NAME,
                                                           blob_name='translated/' + translated_file_name,
                                                           file_path=translated_file_path)
    # remove temporary files
    os.remove(path_to_original_file)
    os.remove(translated_file_path)

    add_file(original_filename, translated_file_name)


@app.route('/', methods=['GET', 'POST'])
def upload():
    BASE_URL = request.url_root
    data = {'languages': show_all_languages_translation(),
            'error': '',
            'translated': '',
            'db_content': []}

    file_list = requests.get('{}files'.format(BASE_URL)).json()

    data['db_content'] = file_list

    if request.method == 'POST':
        file = request.files['file']
        lang = request.form['dest_lang']
        if (file.filename == '' and lang != '') or (file.filename != '' and lang == ''):
            data['error'] = 'Please choose file and language.'

        if file and extensions(file.filename):
            translate = translate_subtitles(file, lang)

            data['translated'] = translate

            # redirect to '/' route in order to reload database content
            return redirect(url_for('upload'))
    return render_template("upload.html", data=data)


if __name__ == '__main__':
    app.run()
