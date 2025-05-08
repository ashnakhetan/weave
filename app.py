from flask import Flask, request, render_template, send_from_directory, session, url_for, redirect
import os
import papermill as pm
from werkzeug.utils import secure_filename
import demo_yc_uganda

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER") or 'uploads'
RESULT_FOLDER = os.getenv("RESULT_FOLDER") or 'results'
INDEX_FILE = os.getenv("INDEX_FILE") or 'index.html'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app = Flask(__name__)
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

@app.route('/')
def step_1():
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
    return render_template('step3.html',
                           task=session.get('task_description'),
                           doc=session.get('data_documentation'),
                           sections=session.get('data_sections', {}))


@app.route('/upload', methods=['POST'])
def final_submit():
    saved_files = {
        'task_description': session.get('task_description'),
        'data_documentation': session.get('data_documentation'),
        'data_sections': session.get('data_sections')
    }
    demo_yc_uganda.run(saved_files, RESULT_FOLDER)
    return {'status': 'success', 'file': 'result.csv'}


@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(RESULT_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)