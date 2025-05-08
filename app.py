from flask import Flask, request, render_template, send_from_directory, session, url_for, redirect
import os
import papermill as pm
from werkzeug.utils import secure_filename
import pipeline
from utils.app_utils import find_file_by_stem

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER") or 'uploads'
RESULT_FOLDER = os.getenv("RESULT_FOLDER") or 'results'
STATIC_FOLDER = os.getenv("STATIC_FOLDER") or 'static'
INDEX_FILE = os.getenv("INDEX_FILE") or 'index.html'
RESULT_FILE = os.getenv('RESULT_FILE') or 'generated_dataset.csv'
SAMPLE_DATA_FOLDER = os.getenv('SAMPLE_DATA_FOLDER') or 'sample_data'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)
os.makedirs(SAMPLE_DATA_FOLDER, exist_ok=True)

app = Flask(__name__)
HOST = os.getenv('HOST') or '0.0.0.0'
PORT = int(os.getenv('PORT') or 10000)
app.secret_key = os.getenv('SECRET_KEY') or 'forager'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

def save_file_as(name):
    file = request.files.get(name)
    if file and file.filename:
        path = os.path.join(UPLOAD_FOLDER, f'{name}{os.path.splitext(file.filename)[1]}')
        file.save(path)
        return path
    return None

@app.route('/')  # Root shows welcome
def welcome():
    return render_template('welcome.html')

@app.route('/step1')
def step1():
    return render_template('step1.html')

@app.route('/step1', methods=['POST'])
def handle_step1():
    """Save the task description and data documentation with those names."""
    task_path = save_file_as('task_description')
    doc_path = save_file_as('data_documentation')
    # session dict stored between multiple requests
    session['task_description'] = task_path
    session['data_documentation'] = doc_path
    return redirect(url_for('step2'))

@app.route('/data-sections')
def step2():
    return render_template('step2.html')

@app.route('/step2', methods=['POST'])
def handle_step2():
    use_original_filenames = request.form.get("use_original_filenames") == "true"
    session['use_original_filenames'] = use_original_filenames

    data_sections = {}
    section_idx = 0

    while True:
        # get section name
        name_key = f"data_name_{section_idx}"
        if name_key not in request.form: # we are done with all sections
            break
        section_name = request.form[name_key] # SECTION NAME
        # create the section folder
        folder_path = os.path.join(UPLOAD_FOLDER, section_name)
        os.makedirs(folder_path, exist_ok=True)

        section = {'folder_path': folder_path, 'metadata': None, 'data': []}

        # metadata
        metadata_file = request.files.get(f"data_metadata_{section_idx}")
        if metadata_file and metadata_file.filename:
            file_name = f"{section_name}_metadata{os.path.splitext(metadata_file.filename)[1]}"
            metadata_path = os.path.join(folder_path, file_name)
            metadata_file.save(metadata_path)
            section['metadata'] = metadata_path

        # data files
        data_files = request.files.getlist(f"data_data_{section_idx}")
        for i, data_file in enumerate(data_files):
            if data_file and data_file.filename:
                # use original filename or <section_name>_<i>
                if use_original_filenames:
                    file_name = secure_filename(data_file.filename)
                else:
                    file_name = f"{section_name}_{i}{os.path.splitext(data_file.filename)[1]}"
                data_path = os.path.join(folder_path, file_name)
                data_file.save(data_path)
                section['data'].append(data_path)

        data_sections[section_name] = section
        section_idx += 1

    session['data_sections'] = data_sections
    return redirect(url_for('step3'))


@app.route('/review')
def step3():
    print("Uploaded files:", os.listdir(app.config['UPLOAD_FOLDER']), flush=True)

    raw_sections = session.get('data_sections', {})
    section_list = list(raw_sections.values())
    return render_template('step3.html',
                           task=session.get('task_description'),
                           doc=session.get('data_documentation'),
                           sections=section_list)


@app.route('/upload', methods=['POST'])
def submit_part_1():
    saved_files = {
        'task_description': session.get('task_description'),
        'data_documentation': session.get('data_documentation'),
        'data_sections': session.get('data_sections')
    }
    print(f"Saved files: {saved_files}", flush=True)
    result = pipeline.run_part_1_2_module_field_selection(saved_files, RESULT_FOLDER)

    if result.get('success'):
        session['part_1_result'] = result
        return redirect(url_for('view_selected_fields'))
    else:
        session['error_message'] = result.get('message')
        return redirect(url_for('upload_failed'))
    
@app.route('/view-selected-fields')
def view_selected_fields():
    result = session.get('part_1_result')
    return render_template('selected_fields.html', field_summary=result.get('field_summary', []),
        summary_csv=result.get('summary_csv'),
        selected_sections=result.get('selected_sections')
    )

@app.route('/transform-data', methods=['POST'])
def transform_data():
    # first get files, then pass them through
    saved_files = {
        'task_description': session.get('task_description'),
        'data_documentation': session.get('data_documentation'),
        'data_sections': session.get('data_sections'),
        'selected_sections': session.get('part_1_result').get('selected_sections'),
        'summary_csv': session.get('part_1_result').get('summary_csv'),
        'field_summary': session.get('part_1_result').get('field_summary', []),
        'question_map_csv': session.get('part_1_result').get('question_map_csv')
    }
    print("Saved Files @ Transform step:", saved_files)
    result = pipeline.run_part_3_transform_data(saved_files, RESULT_FOLDER)

    if result.get('success'):
        return redirect(url_for('download_ready'))
    else:
        session['error_message'] = result.get('message')
        return redirect(url_for('upload_failed'))

@app.route('/download-ready')
def download_ready():
    return render_template('download.html', filename=RESULT_FILE)

@app.route('/upload-failed')
def upload_failed():
    return render_template('fail.html', message=session.get('error_message'))

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(RESULT_FOLDER, filename, as_attachment=True)

@app.route('/load-sample')
def load_sample_data():
    import shutil

    task_description = find_file_by_stem(UPLOAD_FOLDER, 'task_description')
    data_documentation = find_file_by_stem(UPLOAD_FOLDER, 'data_documentation')

    # Clear & copy task + doc
    shutil.copy(f'{SAMPLE_DATA_FOLDER}/task_description{os.path.splitext(task_description)[1]}', task_description)
    shutil.copy(f'{SAMPLE_DATA_FOLDER}/data_documentation{os.path.splitext(data_documentation)[1]}', data_documentation)

    session['task_description'] = task_description
    session['data_documentation'] = data_documentation
    session['use_original_filenames'] = True  # or False

    data_sections = {}

    sections = [dir_name for dir_name in os.listdir(f'{SAMPLE_DATA_FOLDER}') if not dir_name.startswith('task_description') and not dir_name.startswith('data_documentation')]
    for section_name in sections:
        section_path = os.path.join(SAMPLE_DATA_FOLDER, section_name)
        dest_path = os.path.join(UPLOAD_FOLDER, section_name)
        os.makedirs(dest_path, exist_ok=True)

        section = {'folder_path': dest_path, 'metadata': None, 'data': []}

        for file in os.listdir(section_path):
            src = os.path.join(section_path, file)
            dst = os.path.join(dest_path, file)
            shutil.copy(src, dst)
            if 'metadata' in file:
                section['metadata'] = dst
            else:
                section['data'].append(dst)

        data_sections[section_name] = section

    session['data_sections'] = data_sections

    return redirect(url_for(request.args.get('next') or 'step2'))  # or step3 to skip to end

import zipfile
from io import BytesIO
from flask import send_file

@app.route('/download-sample')
def download_sample():
    sample_folder = 'sample_data'
    buffer = BytesIO()

    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(sample_folder):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, sample_folder)
                zf.write(full_path, arcname=relative_path)

    buffer.seek(0)
    return send_file(buffer, mimetype='application/zip', as_attachment=True, download_name='sample_data.zip')

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)