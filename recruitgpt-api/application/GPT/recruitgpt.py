# import streamlit as st
from application.GPT.utils import Utils
import os
import json
# from tiktoken import Tokenizer
import openai
# from openai import api_v1
import time
import pandas as pd
from pandas import json_normalize
import tempfile
from flask import Flask, request, jsonify
import boto3
import uuid
import io
from database import UserSession
from database import db
from datetime import datetime
import constants 


# def gpt_token_counts(text):
#     tokenizer = Tokenizer(api_v1.MODEL_CLASSES["gpt-3.5-turbo-16k"].vocab())
#     num_tokens = len(list(tokenizer.tokenize(text)))
#     # st.write('Num of Tokens: ', num_tokens)

aws_access_key = constants.aws_access_key
aws_secret_key = constants.aws_secret_key
bucket_name = constants.bucket_name
bucket_region = constants.bucket_region
s3_client = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
result_link=''
    
class Gpt:

    def parse_resume(resumetext):
        try:
            # Ensure resume text does not exceed 4000 tokens
            # resumetext = truncate_text_by_words(resumetext, 4000)
            resumetext = Utils.truncate_text_by_words(resumetext, 4000)
            system = """
            You are an excellent NLP engineer and data scientist and your task is to analyse and parse candidate resumes into meaningful structured JSON format.
            You will be provided with candidate resume text.

            The system instruction is:
            
            Step-1: 
            Analyse and parse the following information from the candidate's resume, do not just extract the data, rephrase it meaningfully:
            name, gmail, phone number, social media links, skillset and expertise, certifications, Explanation of projects, 
            Explanation of position of responsibilities, years of experience, Previous work experience description, educational qualification, 
            extracurriculars,awards and achievements, previous job title.
            If value of a key is missing in the resume then value should be null. 
            If not a resume then all the key's value should be null

            Step-2:
            Return the meaningful parsed data in a sturctured JSON format with key and corresponding value format as follows-
            'name': string,
            'gmail': string,
            'phone number' : string,
            'social media links': list of string,
            'skillset and expertise': list of string,
            'certifications': list of string,
            'Explanation of projects': list of string under 200 tokens,
            'Explanation of position of responsibilities': list of string under 200 tokens,
            'years of experience': float,
            'Previous work experience description': list of string under 200 tokens,
            'educational qualification': list of string,
            'extracurriculars': list of string,
            'awards and achievements': list of string,
            'previous job title': list of string
            If not a resume then all the key's value should be null.

            Step-3:
            Only return the parsed JSON format resume, nothing else.
            """
            prompt = f"""
            Only return the structured parsed json format of the resume of candidate.
            Information about the candidate's resume is given inside text delimited by triple backticks.

            Candidate's Resume :```{resumetext}```
            """
            
            messages =  [
            {'role':'system', 'content':system},
            {'role':'user', 'content': prompt}]

            input_string = system + prompt
            # st.write('Input tokens for resume parsing: ')
            # gpt_token_counts(input_string)

            start_time = time.time()
            parsed_resume = Utils.get_choice_text_from_prompt(messages)
            end_time = time.time()
            parsing_time = end_time - start_time
            print(f"Time taken to parse : {parsing_time} seconds")
            # st.write('Time taken for resume parsing : ', parsing_time)
            
            return parsed_resume
        except Exception as e:
            print(f"Error parsing resume: {e}")
            # st.error(f"Error parsing resume: {e}")
            return ""

    def score_resume(parsed_resume,job_description):
        try:
            # Ensure resume text does not exceed 4000 tokens
            # parsed_resume = truncate_text_by_words(resumetext, 4000)

            system = """
            You are an expert talent recruiter with a keen eye for detail. Your primary task is to meticulously evaluate and 
            score candidates' resumes against a specific job description. You also need to provide a detailed explanation and 
            reasoning behind that scoring. The score should range between 0-100, reflecting the candidate's suitability for the role. 
            You will be provided with a job description and structured JSON candidate resume.

            Follow these steps for evaluation:

            Step-1: Ascertain the authenticity of the resume. Ensure it's a genuine resume and not random or irrelevant content.

            Step-2: *Score Assignment*- 
            If the document isn't a genuine resume, assign a score of 0.
            If it is, proceed to evaluate the candidate's JSON-structured resume 
            against the given job description by considering the following criteria:
            1. Relevant Experience: Does the candidate have experience pertinent to the role or industry?
            2. Duration of Experiences: Assess the longevity of their relevant roles.
            3. Previous Job Titles: Do their past titles align with the role's requirements?
            4. Specific Responsibilities and Impact: Identify instances where the candidate made a significant difference.
            5. Achievements: Highlight accomplishments that demonstrate the candidate's capabilities.
            6. Education: Evaluate the relevance of the candidate's educational background.
            7. Educational Quality: Consider the prestige of the institutions they attended.
            8. Certifications: Identify any specialized training or certifications.
            9. Technical Skills: Gauge their proficiency in tools and methodologies crucial for the role.
            10. Projects: Highlight projects that resonate with the job's requirements.

            Step 3: Assign a detailed score between 0-100. This score should reflect the candidate's overall suitability for the role, 
            considering all the criteria mentioned. Ensure the score is a floating-point number with up to two decimal places for accuracy. 
            If the document isn't a genuine resume, the score should remain 0. If the resume perfectly matches with the job description 
            requirements without any deviation at all and if the candidate has experiences and skills which exceeds the job description 
            requirements then it should be scored 100.
            

            Step-4: *Score Explanation*- 
            Along with the score, provide a comprehensive explanation for the score. This explanation should:
            1. Detail how the candidate meets or falls short of each criterion.
            2. Highlight standout qualities or areas of concern.
            3. Explore how the candidate's overall profile aligns with the job description.
            4. Use specific examples from the resume to justify the score.

            Step-5: As mentioned earlier, only return a final score and the comprehensive scoring explanation in a JSON format. 
            The keys should be 'Score' and 'Score Explanation'. The format of the json output - 
            'Score': float
            'Score Explanation' : string
            """

            prompt = f"""
                Only return score out of 100 and score explanation of the resume of candidate against the given job description.
                Information about the candidate's resume in JSON format and job description are given inside text delimited by triple backticks.

                Candidate's Resume in structured JSON format :```{parsed_resume}```

                Job Description for the Target Role: ```{job_description}```
            """
            messages =  [
            {'role':'system', 'content':system},
            {'role':'user', 'content': prompt}]

            input_string = system + prompt
            # st.write('Input tokens for resume scoring and evaluation: ')
            # gpt_token_counts(input_string)

            start_time = time.time()
            resume_detail = Utils.get_choice_text_from_prompt(messages)
            end_time = time.time()
            parsing_time = end_time - start_time
            print(f"Time taken to parse : {parsing_time} seconds")
            # st.write('Time taken for resume scoring and evaluation: ', parsing_time)

            return resume_detail
        except Exception as e:
            print(f"Error analyzing resume: {e}")
            return ""


    # Folder path 
    def analyze_all_resumes(folder_path, job_description):
        resumes = Utils.get_all_resumes(folder_path)
        data = []
        
        for filename, resume_text in zip(os.listdir(folder_path), resumes):
            print(filename)
            parsed_resume = Gpt.parse_resume(resume_text)
            print('resume parsed!')
            score = Gpt.score_resume(parsed_resume, job_description)
            print('resume scored!')
            data.append([filename, json.loads(parsed_resume), json.loads(score)])
            print(filename, json.loads(score), json.loads(parsed_resume))
            print('-----------------------------------------------------------------')
        
        # Initial dataframe
        df = pd.DataFrame(data, columns=["File_Name", "Parsed_Resume", "Score"])
        
        # Normalize Parsed_Resume and Score columns
        df_parsed = json_normalize(df['Parsed_Resume'])
        df_score = json_normalize(df['Score'])
        
        # Drop the original Parsed_Resume and Score columns
        df.drop(columns=['Parsed_Resume', 'Score'], inplace=True)
        df = pd.concat([df, df_parsed, df_score], axis=1)
        return df


    def streamlit_analyse(file_paths, job_description, email, username, resume_link):
        
        
        # DataFrame to store dynamic results
        dynamic_df = pd.DataFrame(columns=["File_Name", "Score", "Score Explanation"])

        data = []

        for file_path in file_paths:
            filename = os.path.basename(file_path)

            # Read and convert files with error handling
            try:
                resume_text = Utils.convert_files_to_text(file_path)		
            except Exception as e:
                return jsonify({"error": f"Failed to convert {filename}: {str(e)}"})

            # Parse resumes with error handling
            try:
                parsed_resume = Gpt.parse_resume(resume_text)
            except Exception as e:
                return jsonify({"error": f"Failed to parse resume from {filename}: {str(e)}"})

            # Score resumes with error handling
            try:
                score = Gpt.score_resume(parsed_resume, job_description)
            except Exception as e:
                return jsonify({"error": f"Failed to score resume from {filename}: {str(e)}"})
            
            # Handle potential JSON errors
            try:
                score_json = json.loads(score)
                values = list(score_json.values())
            except json.JSONDecodeError:
                return jsonify({"error": f"Error decoding JSON for {filename}."})
            
            # Append new data to the dynamic dataframe
            new_row = pd.DataFrame({
                "File_Name": [filename], 
                "Score": [values[0]],
                "Score Explanation": [values[-1]]
            })
            dynamic_df = pd.concat([dynamic_df, new_row], ignore_index=True)
            print(dynamic_df)
        
        df=dynamic_df
        csv = df.to_csv(index=False)
        csv_bytes = io.StringIO(csv).read().encode('utf-8')
        csv_file=io.BytesIO(csv_bytes)
        unique_id = str(uuid.uuid4())
        try:
            csvName = f'result_{unique_id}.csv'
            s3_client.upload_fileobj(csv_file, bucket_name, csvName)
            encoded_csv_name = csvName.replace(' ', '+')
            result_link = f"https://s3.console.aws.amazon.com/s3/object/{bucket_name}?region={bucket_region}&prefix={encoded_csv_name}"
            print(f'File {csvName} uploaded to {bucket_name}/{csvName}')
            print(f"Result File uploaded successfully! S3 URL: <a href='{result_link}'>{result_link}</a>")
        except Exception as e:
            print(f"Error: {e}")

        user = UserSession(email=email, username=username, login_time=datetime.now(), resume_file_link=resume_link, result_file_link=result_link)
        db.session.add(user)
        db.session.commit()
        # Convert the final dataframe to JSON and return it
        result_json = dynamic_df.to_json(orient="records")
        return jsonify({"data": json.loads(result_json)})
        # return dynamic_df


    # Add a feedback text box at the end
    # feedback = st.text_area("Provide Feedback:", height=100)
