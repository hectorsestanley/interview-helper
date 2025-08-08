# Interview Assistant

A Flask web application that helps with interview preparation by using AI to generate answers based on your CV and recorded questions.

## Features

- 📄 CV Upload: Upload your CV in PDF, DOC, DOCX, or TXT format
- 🎙️ Audio Processing: Upload audio files of interview questions
- 🤖 AI-Powered Answers: Get personalized interview answers using Google's Gemini AI
- 🚀 Vercel Deployment Ready

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your:
- `GEMINI_API_KEY`: Get from Google AI Studio
- `SECRET_KEY`: A random secret key for Flask sessions

3. Run locally:
```bash
python app.py
```

## Deployment to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

3. Set environment variables in Vercel dashboard:
   - `GEMINI_API_KEY`
   - `SECRET_KEY`

## How to Use

1. **Upload CV**: Upload your resume/CV first
2. **Record Question**: Upload an audio file of an interview question
3. **Get Answer**: The AI will analyze the question and provide a tailored answer based on your CV

## Supported File Formats

- **CV**: PDF, DOC, DOCX, TXT
- **Audio**: WAV, MP3, M4A, and other common audio formats

## API Endpoints

- `GET /`: Main interface
- `POST /upload_cv`: Upload CV file
- `POST /process_audio`: Process audio and get AI response