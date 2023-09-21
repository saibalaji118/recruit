from pdfminer.high_level import extract_text
import os
import docx
import openai
import constants

openai.api_key = constants.OPENAI_API_KEY

class Utils:
    def get_all_resumes(folder_path):
        resumes = []
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                text = Utils.convert_files_to_text(file_path)
                resumes.append(text)
        return resumes

    def convert_files_to_text(file_path):
        try:
            if file_path.endswith('.pdf'):
                text = Utils.convert_pdf_to_text2(file_path)
            elif file_path.endswith('.docx'):
                text = Utils.convert_docx_to_text(file_path)
            elif file_path.endswith('.txt'):
                text = Utils.convert_txt_to_text(file_path)
            else:
                return "Not a Resume"
            return text
        except Exception as e:
            print(f"Error converting file {file_path} to text: {e}")
            return ""
    def convert_pdf_to_text2(file_path):
        try:
            text = extract_text(file_path)
            return text
        except Exception as e:
            print(f"Error extracting text from PDF {file_path}: {e}")
            return ""

    def convert_docx_to_text(file_path):
        try:
            doc = docx.Document(file_path)
            text = ''
            for paragraph in doc.paragraphs:
                text += paragraph.text + '\\n'
            return text
        except Exception as e:
            print(f"Error extracting text from DOCX {file_path}: {e}")
            return ""
    def convert_txt_to_text(file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return content
        except Exception as e:
            return f"An error occurred: {e}"

    def get_choice_text_from_prompt(messages):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=messages,
                temperature=0,
                max_tokens=4000
            )
            choice_text = response.choices[0]["message"]["content"]
            return choice_text
        except Exception as e:
            print("Error in get_choice_text_from_prompt:", str(e))
            return ""
        
    def truncate_text_by_words(text, max_words=4000):
        """
        Truncates the text to a specified number of words.
        """
        words = text.split()
        if len(words) <= max_words:
            return text
        return " ".join(words[:max_words])