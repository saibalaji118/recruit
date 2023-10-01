
from flask import jsonify, request, redirect, Blueprint
import json
import requests
import jwt
from database import UserSession
from database import db
import re
from application.GPT.utils import Utils
import os
import tempfile
from application.GPT.recruitgpt import Gpt
import pandas as pd
import boto3
import uuid
import io
import constants 

# Replace these with your own values
aws_access_key = constants.aws_access_key
aws_secret_key = constants.aws_secret_key
bucket_name = constants.bucket_name
bucket_region = constants.bucket_region
s3_client = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

email = None
username = None
resume_link = None


api_bp = Blueprint(
    'api', __name__,
    url_prefix='/'
    )

@api_bp.route('/', methods=['GET'])
def index():
    return "Welcome to RecruitGPT AWS Server!"

@api_bp.route('/upload', methods=['POST'])
def upload_files():
    # Get the list of uploaded files
    uploaded_files = request.files.getlist('file')

    # Get the description from the request
    description = request.form.get('description')


    # Create a directory to save the uploaded files (you can customize the path)
    # upload_dir = 'uploads'
    # os.makedirs(upload_dir, exist_ok=True)
    temp_dir = tempfile.TemporaryDirectory()

    file_paths = []
    global resume_link
    global email
    global username

    for file in uploaded_files:
        if file.filename != '':
            # Save the uploaded file to the server
            with open(os.path.join(temp_dir.name, file.filename), "wb") as f:
                    f.write(file.read())
            file_paths.append(os.path.join(temp_dir.name, file.filename))

            # You can perform additional processing on each file here
            try:
                unique_id = str(uuid.uuid4())
                fileName = f'{file.filename}_{unique_id}'
                s3_client.upload_fileobj(file, bucket_name, fileName)
                encoded_file_name = fileName.replace(' ', '+')
                resume_link = f"https://s3.console.aws.amazon.com/s3/object/{bucket_name}?region={bucket_region}&prefix={encoded_file_name}"
                print(f"File '{fileName}' uploaded to '{bucket_name}/{fileName}'")
                print(f"File uploaded successfully! S3 URL: <a href='{resume_link}'>{resume_link}</a>")
            except Exception as e:
                print(f"Error: {e}")

    return Gpt.streamlit_analyse(file_paths, description, email, username, resume_link)

    # return jsonify({"message": "Files uploaded and processed successfully"})



@api_bp.route('/login', methods=['POST', 'GET'])
def login():

    code = request.args.get('code')

    if not code:
        return jsonify({'error': 'Invalid request'}), 400
    
    token_endpoint = 'https://oauth2.googleapis.com/token'

    client_id = constants.client_id
    client_secret = constants.client_secret

    ############# Change ##################
    redirect_uri = 'http://127.0.0.1:5000/login'

    # Exchange authorization code for ID token
    data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    response = requests.post(token_endpoint, data=data)
    token_data = json.loads(response.text)


    if 'id_token' in token_data:

        id_token_str = token_data['id_token']

        # Decode the ID token
        decoded_token = jwt.decode(id_token_str, options={"verify_signature": False})

        global email
        global username

        # Access the account details
        email = decoded_token['email']
        username = decoded_token['name']

        if UserSession.query.filter_by(username=username).first() is not None:
            return redirect(f"http://localhost:3000/?q={username}")
            

        elif UserSession.query.filter_by(email=email).first() is not None:
            user = UserSession.query.filter_by(email=email).first()
            return redirect(f"http://localhost:3000/?q={user.username}")
        

        else:
            # user = UserSession(email=email, username=username)
            # db.session.add(user)
            # db.session.commit()


            return redirect(f"http://localhost:3000/?q={username}")


        # return redirect(f"http://localhost:3000/?q={name}")


        # if User.query.filter_by(username=name).first() is not None:
        #     return redirect(f"https://www.recruitgpt.info?q={name}")
            

        # elif User.query.filter_by(email=email).first() is not None:
        #     user = User.query.filter_by(email=email).first()
        #     return redirect(f"https://www.recruitgpt.info?q={user.username}")
        

        # else:
        #     user = User(email=email, username=name, password='123456')
        #     db.session.add(user)
        #     db.session.commit()


        #     return redirect(f"https://www.recruitgpt.info?q={user.username}")

    else:
        return jsonify({'error': 'An error occured please try with other method.'}), 200
