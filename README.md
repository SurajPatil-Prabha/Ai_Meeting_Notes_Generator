# NoTeX — AI Meeting Intelligence Platform

> **Record. Transcribe. Understand. Remember.**

NoTeX is a modern, futuristic **AI-powered meeting intelligence platform** designed to help users record meetings, convert conversations into structured notes, identify important decisions and action items, and interact with their meeting through an intelligent AI Meeting Copilot.

The application provides a complete workflow from **live meeting recording → transcription → AI analysis → searchable notes → meeting reminders → AI-powered questions**.

---

## ✨ Features

### 🎙️ Live Meeting Recording

Record meetings directly from your browser using the device microphone.

Features include:

* Start / pause / resume recording
* Live recording timer
* Stop recording
* Automatic audio processing
* Speech-to-text transcription
* Meeting analysis after transcription

---

### 📝 AI Meeting Notes

NoTeX analyzes meeting transcripts and generates structured information such as:

* Meeting summary
* Key points
* Important topics
* Decisions
* Action items
* Tasks
* Deadlines
* Participants
* Speaker statistics
* Important keywords

This makes long meeting conversations easier to understand and review.

---

### 🤖 Meeting Copilot

The **Meeting Copilot** allows users to ask questions about their meeting.

Example questions:

```text
What were the main decisions?

Who has the most action items?

What tasks were assigned to John?

What are the important deadlines?

Give me a short summary of this meeting.

What problems were discussed?

What should we follow up on?
```

The Copilot uses the current meeting transcript and analysis as context.

NoTeX can work with its built-in analysis engine, and it can optionally connect to a local **Ollama LLM** for more advanced conversational intelligence.

---

### 📅 Meeting Calendar & Reminders

NoTeX includes a meeting scheduling system.

Users can:

* Add a meeting title
* Select date
* Select start time
* Set meeting duration
* Set reminder time
* Create a calendar event
* Download an `.ics` calendar file

The generated calendar event can be imported into:

* Google Calendar
* Microsoft Outlook
* Apple Calendar
* Other calendar applications supporting `.ics`

---

### 📂 Meeting History

Previously processed meetings can be stored and reviewed.

Users can access:

* Previous meetings
* Meeting summaries
* Transcripts
* Action items
* Decisions
* Meeting analytics

---

### 🔎 Transcript Search

Search through meeting transcripts to quickly find:

* Topics
* People
* Decisions
* Tasks
* Keywords
* Specific conversations

---

### 📊 Meeting Analytics

NoTeX provides useful meeting statistics including:

* Number of speakers
* Speaker participation
* Transcript length
* Meeting duration
* Important keywords
* Action-item statistics

---

### 📄 Export

Meeting information can be exported into different formats.

Supported formats include:

* PDF
* DOCX
* Markdown
* TXT

---

## 🖥️ User Interface

NoTeX uses a modern futuristic dashboard design with:

* Dark interface
* Glassmorphism-inspired components
* Responsive layout
* Interactive cards
* AI-focused visual elements
* Sidebar navigation
* Meeting analytics dashboard
* Copilot chat interface
* Calendar interface

The frontend is designed to feel like a modern AI SaaS application.

---

# 🏗️ Project Architecture

NoTeX uses a **frontend + backend architecture**.

```text
                  ┌─────────────────────────┐
                  │       NoTeX Frontend    │
                  │                         │
                  │ HTML + CSS + JavaScript │
                  └────────────┬────────────┘
                               │
                               │ REST API
                               ▼
                  ┌─────────────────────────┐
                  │      FastAPI Backend    │
                  │                         │
                  │ Python                  │
                  └────────────┬────────────┘
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
       Transcription      NLP Analysis      Meeting Data
          Engine             Engine            & History
             │                 │
             ▼                 ▼
          Whisper        AI/Rule-based
                          Processing
                               │
                               ▼
                       Meeting Copilot
                               │
                               ▼
                         Optional LLM
                           (Ollama)
```

---

# 🛠️ Technologies Used

## Frontend

### HTML5

Used to create the structure and layout of the web application.

### CSS3

Used for:

* Responsive design
* Dark theme
* Animations
* Glassmorphism effects
* Layout
* UI components

### JavaScript

Used for:

* Frontend interactions
* API communication
* Live recording
* Audio processing
* Copilot chat
* Calendar functionality
* Dynamic dashboard updates

### Browser MediaRecorder API

Used for recording live meetings directly from the user's microphone.

---

# ⚙️ Backend

## Python

Python is the primary backend programming language.

It handles:

* Transcription
* NLP processing
* Meeting analysis
* API endpoints
* File processing
* Export generation
* Meeting history
* Copilot functionality

---

## FastAPI

FastAPI is used as the backend web framework.

It provides REST APIs for:

```text
Frontend
   ↓
FastAPI
   ↓
Python AI/NLP modules
```

FastAPI also serves the frontend application.

---

# 🧠 AI & Machine Learning

## OpenAI Whisper

Whisper is used for speech-to-text transcription.

It converts:

```text
Meeting Audio
      ↓
   Whisper
      ↓
Meeting Transcript
```

This allows NoTeX to process recorded meetings.

---

## NLP Processing

The project contains Natural Language Processing components for extracting useful information from transcripts.

The analysis can identify:

* Important sentences
* Topics
* Action items
* Decisions
* Keywords
* Participants
* Meeting statistics

---

## Ollama — Optional

NoTeX can optionally use **Ollama** to provide a local Large Language Model for the Meeting Copilot.

This allows the Copilot to provide more natural conversational answers.

Architecture:

```text
Meeting Transcript
        ↓
   NoTeX Backend
        ↓
      Ollama
        ↓
    Local LLM
        ↓
 Meeting Copilot
```

Ollama is optional.

The application can run without it using the built-in meeting analysis engine.

---

# 📅 Calendar Technology

NoTeX generates standard `.ics` calendar files.

This allows meeting reminders to work with calendar applications that support the iCalendar format.

---

# 📄 Document Processing

The project uses Python libraries for processing and exporting meeting documents.

Depending on the feature, the project can work with:

* TXT
* DOCX
* PDF
* Markdown

---

# 🧪 Testing

The project includes automated tests for important backend functionality.

Run the tests using:

```bash
pytest
```

A successful test run should show all tests passing.

---

# 💻 Requirements

Recommended:

```text
Python 3.10+
```

You will also need:

* A modern web browser
* Microphone access for live recording
* Internet connection if using online dependencies/models
* FFmpeg for certain audio/video transcription workflows

---

# 🚀 Installation

## 1. Clone or download the project

Download the NoTeX project and open the project directory.

```bash
cd NoTeX
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

---

# 📦 3. Install Dependencies

Run:

```bash
pip install -r requirements.txt
```

This installs the Python packages required by the backend and AI processing system.

---

# ▶️ 4. Start NoTeX

Run:

```bash
uvicorn server:app --reload
```

You should see something similar to:

```text
Uvicorn running on http://127.0.0.1:8000
```

Open your browser and visit:

```text
http://127.0.0.1:8000
```

---

# 🎙️ Using Live Meeting Recording

1. Open NoTeX.
2. Navigate to the recording section.
3. Allow microphone permission.
4. Click **Start Recording**.
5. Conduct your meeting.
6. Click **Stop Recording**.
7. NoTeX processes the recording.
8. Whisper generates the transcript.
9. The transcript is analyzed.
10. Meeting notes and insights are displayed.

---

# 🤖 Setting Up the Advanced Meeting Copilot

The Copilot works without an external LLM.

For more advanced AI conversations, install Ollama.

After installing Ollama, download a supported model.

Example:

```bash
ollama pull llama3.2
```

Then configure the model used by NoTeX.

Example:

```text
OLLAMA_MODEL=llama3.2
```

Start the backend again:

```bash
uvicorn server:app --reload
```

The Meeting Copilot can then use the local model to generate more natural answers based on the meeting context.

---

# 🔐 Privacy

NoTeX is designed with local processing in mind.

Meeting recordings and transcripts can be processed locally on the user's computer.

When using Ollama, the language model can also run locally instead of sending meeting content to a third-party cloud AI service.

Always review the configuration of any external service before using it with sensitive meeting information.

---

# 📁 Project Structure

A simplified structure of the project is:

```text
NoTeX/
│
├── server.py
├── requirements.txt
├── README.md
│
├── app_streamlit.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── nlp/
│   ├── analyzer.py
│   └── ...
│
├── transcription/
│   └── ...
│
├── analytics/
│   └── ...
│
├── history/
│   └── ...
│
├── exporters/
│   └── ...
│
└── tests/
    └── ...
```

The exact structure may vary depending on the project version.

---

# 🌐 API

The frontend communicates with the FastAPI backend through REST endpoints.

The backend provides functionality for:

```text
Health Check
        ↓
Meeting Upload
        ↓
Transcription
        ↓
Meeting Analysis
        ↓
Copilot
        ↓
Meeting History
        ↓
Calendar
        ↓
Export
```

FastAPI also provides automatic API documentation.

After starting the server, open:

```text
http://127.0.0.1:8000/docs
```

This displays the interactive API documentation.

---

# 🚫 Is Streamlit Required?

**No.**

The current NoTeX application does **not require Streamlit**.

The primary architecture is:

```text
HTML
CSS
JavaScript
   ↓
FastAPI
   ↓
Python AI Backend
```

Streamlit is retained only as an alternative/legacy interface.

The main NoTeX application should be started using:

```bash
uvicorn server:app --reload
```

You do **not** need to run:

```bash
streamlit run app_streamlit.py
```

---

# 🎯 Project Objective

The main objective of NoTeX is to reduce the amount of manual work required after meetings.

Instead of:

```text
Meeting
   ↓
Manually write notes
   ↓
Find decisions
   ↓
Find tasks
   ↓
Remember deadlines
   ↓
Create reminder
```

NoTeX provides:

```text
Meeting
   ↓
Record
   ↓
Transcribe
   ↓
AI Analysis
   ↓
Structured Notes
   ↓
Action Items
   ↓
Decisions
   ↓
Meeting Copilot
   ↓
Calendar Reminder
```

---

# 🔮 Future Improvements

Possible future versions could include:

* Real-time transcription while the meeting is happening
* Real-time AI Meeting Copilot
* Automatic speaker identification
* Google Calendar integration
* Microsoft Outlook integration
* Zoom integration
* Google Meet integration
* Microsoft Teams integration
* Automatic email follow-ups
* Automatic task creation
* Personalized AI meeting summaries
* Voice interaction with the Copilot
* Multi-language transcription
* Multi-language summaries
* Cloud synchronization
* User authentication
* Team workspaces
* Meeting sentiment analysis
* Automatic follow-up email generation

---

# 👨‍💻 Development

Start the development server with:

```bash
uvicorn server:app --reload
```

The `--reload` option automatically restarts the server when backend files are modified.

---

# 🧪 Run Tests

```bash
pytest
```

For more detailed output:

```bash
pytest -v
```

---

# 📌 Quick Start

For a quick setup on Windows:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

---

# 🏆 NoTeX

### AI Meeting Intelligence Platform

**Record → Transcribe → Analyze → Ask → Remember**

Built using:

**HTML5 · CSS3 · JavaScript · Python · FastAPI · Whisper · NLP · Ollama · REST API**
