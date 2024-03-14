import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from models.applicant import Applicant, ApplicantDB


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = ApplicantDB(uri=os.environ.get("MONGODB_CONNECTION_STRING"),
                 db_name=os.environ.get("DB_NAME"))


def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    """Save an uploaded file to the UPLOAD_FOLDER."""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')  # Get from config or use default
        # Ensure the upload directory exists
        os.makedirs(upload_folder, exist_ok=True)  # Creates the directory if it doesn't exist
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        return file_path
    return None


##############
# APPLICANTS #
##############

@app.route('/applicant', methods=['POST'])
def add_applicant():
    # Ensure content type is multipart/form-data
    if 'application/json' in request.content_type:
        return jsonify({'error': 'Content type must be multipart/form-data'}), 415

    # Retrieve text fields from form data
    data = request.form.to_dict()

    # Convert specific fields if necessary (e.g., 'languages' and 'tools' from comma-separated string to list)
    if 'languages' in data:
        data['languages'] = data['languages'].split(',')
    if 'tools' in data:
        data['tools'] = data['tools'].split(',')
    
    # Files
    cv_file = request.files.get('cv_file')
    img_file = request.files.get('img_file')
    
    # Save files if they are present
    cv_path = save_file(cv_file) if cv_file else None
    img_path = save_file(img_file) if img_file else None

    # Add file paths to data dict
    data['cv_path'] = cv_path
    data['img_path'] = img_path
    
    try:
        # Assuming you have a modified Applicant constructor or method to handle file paths
        applicant = Applicant(**data)
        applicant_id = db.add_applicant(applicant)
        return jsonify({'message': 'Inserted Applicant with ID: {}'.format(applicant_id)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/applicant/<applicant_id>', methods=['GET'])
def get_applicant(applicant_id):
    try:
        applicant = db.get_applicant(applicant_id)
        if applicant:
            return jsonify(applicant.to_dict()), 200
        else:
            return jsonify({'error': 'Applicant not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/applicants/search', methods=['GET'])
def search_applicants():
    query_field = request.args.get('query_field')
    query_value = request.args.get('query_value')

    if not query_field or not query_value:
        return jsonify({'error': 'Missing query field or value'}), 400

    try:
        if query_field in ['languages', 'tools']:
            query = {query_field: {"$in": [query_value]}}
        else:
            query = {query_field: query_value}

        applicants = db.search_applicants(query)
        return jsonify([applicant.to_dict() for applicant in applicants]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
