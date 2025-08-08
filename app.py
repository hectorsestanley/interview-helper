from flask import Flask, request, render_template, jsonify, session
import os
import google.generativeai as genai
import speech_recognition as sr
from werkzeug.utils import secure_filename
import tempfile
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_cv', methods=['POST'])
def upload_cv():
    if 'cv' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['cv']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        cv_text = extract_text_from_file(filepath)
        session['cv_content'] = cv_text
        
        return jsonify({'message': 'CV uploaded successfully', 'filename': filename})
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file uploaded'}), 400
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': 'No audio file selected'}), 400
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
        audio_file.save(tmp_file.name)
        
        r = sr.Recognizer()
        with sr.AudioFile(tmp_file.name) as source:
            audio = r.record(source)
        
        try:
            question = r.recognize_google(audio)
            
            cv_content = session.get('cv_content', '')
            
            prompt = f"""
            You are an AI interview assistant. Based on the following CV content and the interview question, 
            provide a concise, relevant answer that showcases the candidate's experience and skills.
            
            CV Content: {cv_content}
            
            Interview Question: {question}
            
            Please provide a professional answer that:
            1. Directly addresses the question
            2. Uses specific examples from the CV when relevant
            3. Is concise and interview-appropriate
            4. Demonstrates the candidate's strengths
            """
            
            response = model.generate_content(prompt)
            answer = response.text
            
            os.unlink(tmp_file.name)
            
            return jsonify({
                'question': question,
                'answer': answer
            })
            
        except sr.UnknownValueError:
            return jsonify({'error': 'Could not understand audio'}), 400
        except sr.RequestError as e:
            return jsonify({'error': f'Speech recognition error: {str(e)}'}), 500
        except Exception as e:
            return jsonify({'error': f'Error processing request: {str(e)}'}), 500

def extract_text_from_file(filepath):
    file_extension = filepath.split('.')[-1].lower()
    
    if file_extension == 'txt':
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    elif file_extension == 'pdf':
        try:
            import PyPDF2
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except ImportError:
            return "PDF processing not available. Please install PyPDF2."
    elif file_extension in ['doc', 'docx']:
        try:
            from docx import Document
            doc = Document(filepath)
            text = ''
            for paragraph in doc.paragraphs:
                text += paragraph.text + '\n'
            return text
        except ImportError:
            return "Word document processing not available. Please install python-docx."
    
    return "Could not extract text from file."

if __name__ == '__main__':
    app.run(debug=True)