# VidMind AI 🎬

An AI-powered video intelligence tool that transforms YouTube videos and local media files into structured knowledge briefs — instantly.

## What it does
Paste a YouTube URL or local file path, hit Analyse, and get:
- 📋 **Summary** — concise AI-generated overview of the content
- ✅ **Action Items** — extracted tasks and next steps
- 🔑 **Key Decisions** — important conclusions from the video
- ❓ **Open Questions** — unresolved topics worth following up
- 🗒 **Full Transcript** — complete speech-to-text output
- 💬 **RAG Chat** — ask anything about the video using retrieval-augmented generation

## Tech Stack
- **Frontend** — Streamlit with custom CSS (dark theme, DM Mono + Syne fonts)
- **Transcription** — Whisper / speech-to-text pipeline
- **Summarization & Extraction** — LLM-powered (GPT-4o / Claude / Gemini)
- **RAG Engine** — LangChain + vector store for in-context Q&A
- **Audio Processing** — yt-dlp for YouTube, FFmpeg for local files

## Features
- YouTube URL and local MP4/MP3 support
- Multi-language transcription (English, Hinglish, Hindi, and more)
- Configurable model, chunk size, and insight depth via sidebar
- Clean dark UI with color-coded insight cards

## Setup
```bash
git clone https://github.com/yourusername/vidmind-ai
cd vidmind-ai
pip install -r requirements.txt
cp .env.example .env   # add your API keys
streamlit run app.py
```
