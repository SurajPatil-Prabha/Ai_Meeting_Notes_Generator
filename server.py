"""NoTeX FastAPI backend — no Streamlit required."""
from __future__ import annotations
import io, os, tempfile, json
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from docx import Document as DocxReader

from utils.summarizer import summarize, top_keywords
from utils.extractor import extract_action_items, extract_decisions, extract_speaker_breakdown
from utils.exporter import export_to_docx, export_to_pdf, export_to_markdown
from utils.transcriber import transcribe_media, ffmpeg_available, is_video, is_audio, TranscriptionError
from utils.analytics import meeting_stats, speaker_sentiment, sentiment_score, talk_time_distribution, tag_action_items
from utils.history import save_meeting, list_meetings, load_meeting, delete_meeting

ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "frontend"
app = FastAPI(title="NoTeX Meeting Intelligence API", version="4.0.0")

class AnalyzeRequest(BaseModel):
    transcript: str
    title: str = "Meeting Notes"
    summary_sentences: int = 5
    keywords: int = 10

class HistoryLoadRequest(BaseModel):
    filename: str

class CopilotRequest(BaseModel):
    message: str
    transcript: str = ""
    result: dict | None = None


def analyze(transcript: str, title: str, summary_sentences: int, keywords: int) -> dict:
    transcript = (transcript or "").strip()
    if not transcript:
        raise HTTPException(400, "Transcript cannot be empty.")
    summary_sentences = max(1, min(int(summary_sentences), 30))
    keywords = max(1, min(int(keywords), 50))
    action_items_raw = extract_action_items(transcript)
    speaker_notes = extract_speaker_breakdown(transcript)
    return {
        "title": title.strip() or "Meeting Notes",
        "summary": summarize(transcript, num_sentences=summary_sentences),
        "action_items": action_items_raw,
        "action_items_tagged": tag_action_items(action_items_raw),
        "decisions": extract_decisions(transcript),
        "keywords": top_keywords(transcript, num_keywords=keywords),
        "speaker_notes": speaker_notes,
        "stats": meeting_stats(transcript),
        "overall_sentiment": sentiment_score(transcript),
        "per_speaker_sentiment": speaker_sentiment(speaker_notes),
        "talk_time": talk_time_distribution(speaker_notes),
    }

@app.get("/api/health")
def health():
    return {"ok": True, "app_name": "NoTeX", "streamlit_required": False, "ffmpeg_available": ffmpeg_available(), "copilot_local_model": os.getenv("OLLAMA_MODEL", "") or None}

@app.post("/api/analyze")
def api_analyze(payload: AnalyzeRequest):
    result = analyze(payload.transcript, payload.title, payload.summary_sentences, payload.keywords)
    return {"result": result, "transcript": payload.transcript}

@app.post("/api/read-file")
async def read_file(file: UploadFile = File(...)):
    name = (file.filename or "").lower(); raw = await file.read()
    try:
        if name.endswith(".txt"):
            text = raw.decode("utf-8", errors="replace")
        elif name.endswith(".docx"):
            doc = DocxReader(io.BytesIO(raw)); text = "\n".join(p.text for p in doc.paragraphs)
        else:
            raise HTTPException(400, "Only .txt and .docx transcript files are supported.")
    except HTTPException: raise
    except Exception as exc: raise HTTPException(400, f"Could not read file: {exc}")
    return {"filename": file.filename, "text": text}

@app.post("/api/transcribe")
async def api_transcribe(file: UploadFile = File(...), model_size: str = Form("base"), language: str = Form("")):
    filename = file.filename or "recording"
    if not (is_audio(filename) or is_video(filename)):
        raise HTTPException(400, "Unsupported audio/video file type.")
    if is_video(filename) and not ffmpeg_available():
        raise HTTPException(400, "FFmpeg is required for video transcription but was not found on PATH.")
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp:
            tmp.write(await file.read()); tmp_path = tmp.name
        text = transcribe_media(tmp_path, filename, model_size=model_size if model_size in {"tiny","base","small","medium"} else "base", language=language.strip() or None)
        return {"filename": filename, "text": text}
    except TranscriptionError as exc: raise HTTPException(400, str(exc))
    except Exception as exc: raise HTTPException(500, f"Transcription failed: {exc}")
    finally:
        if tmp_path:
            try: os.remove(tmp_path)
            except OSError: pass

@app.post("/api/copilot")
def copilot(payload: CopilotRequest):
    """Use a local Ollama model when configured; otherwise provide a deterministic meeting-aware fallback."""
    message = payload.message.strip()
    if not message: raise HTTPException(400, "Ask the copilot a question first.")
    transcript = payload.transcript.strip()
    result = payload.result or {}
    model = os.getenv("OLLAMA_MODEL", "").strip()
    if model:
        prompt = f"""You are NoTeX Meeting Copilot. Be concise, accurate and helpful. Only use facts present in the meeting context. If something is unknown, say so.\n\nMEETING NOTES:\n{json.dumps(result, ensure_ascii=False)[:18000]}\n\nTRANSCRIPT:\n{transcript[:30000]}\n\nUSER QUESTION:\n{message}"""
        try:
            body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
            req = Request(os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate"), data=body, headers={"Content-Type":"application/json"})
            with urlopen(req, timeout=90) as r:
                data = json.loads(r.read().decode())
            answer = str(data.get("response", "")).strip()
            if answer: return {"answer": answer, "mode": "local-llm"}
        except Exception:
            pass
    answer = fallback_copilot(message, transcript, result)
    return {"answer": answer, "mode": "meeting-engine"}

def fallback_copilot(message: str, transcript: str, result: dict) -> str:
    q = message.lower()
    if not transcript and not result: return "I’m ready. Add a transcript or record a meeting first, then ask me about decisions, risks, owners, action items or follow-ups."
    if any(x in q for x in ["action", "todo", "task", "follow up"]):
        items = result.get("action_items_tagged") or result.get("action_items") or extract_action_items(transcript)
        if not items: return "I couldn’t identify a clear action item from the meeting context."
        return "Here are the clearest action items:\n" + "\n".join(f"• {x.get('text', x)}" if isinstance(x, dict) else f"• {x}" for x in items[:10])
    if any(x in q for x in ["decision", "decided", "agreed", "approved"]):
        items = result.get("decisions") or extract_decisions(transcript)
        return "Key decisions:\n" + "\n".join(f"• {x}" for x in items[:10]) if items else "No explicit decisions were detected."
    if any(x in q for x in ["summary", "summarize", "what happened", "overview"]):
        items = result.get("summary") or summarize(transcript, 5)
        return "Meeting summary:\n" + "\n".join(f"• {x}" for x in items[:7])
    if any(x in q for x in ["risk", "problem", "issue", "concern"]):
        return "I can flag risks from the transcript, but this local fallback does not infer hidden risks. Look for phrases about blockers, delays, dependencies, budget, unresolved issues or missing owners. A local Ollama model gives NoTeX deeper reasoning."
    keywords = result.get("keywords") or top_keywords(transcript, 8)
    return f"Based on the meeting context, the main topics are: {', '.join(keywords[:8]) or 'not enough signal'}. I can also help with decisions, action items, summaries and risks."

@app.get("/api/history")
def history(): return {"meetings": list_meetings()}
@app.post("/api/history")
def history_save(payload: dict):
    if not payload.get("title"): payload["title"] = "Meeting Notes"
    if not payload.get("transcript"): raise HTTPException(400, "Transcript is required.")
    return {"filename": save_meeting(payload)}
@app.post("/api/history/load")
def history_load(payload: HistoryLoadRequest):
    try: return load_meeting(payload.filename)
    except (OSError, FileNotFoundError, ValueError): raise HTTPException(404, "Meeting history entry not found.")
@app.delete("/api/history/{filename}")
def history_delete(filename: str):
    if Path(filename).name != filename or not filename.endswith(".json"): raise HTTPException(400, "Invalid history filename.")
    delete_meeting(filename); return {"ok": True}

@app.post("/api/export")
def export_notes(payload: dict):
    result = payload.get("result") or {}; fmt = payload.get("format", "pdf").lower()
    kwargs = {"title":result.get("title","Meeting Notes"),"summary":result.get("summary",[]),"action_items":result.get("action_items",[]),"decisions":result.get("decisions",[]),"keywords":result.get("keywords",[]),"speaker_notes":result.get("speaker_notes",{})}
    safe_title = re_safe_filename(kwargs["title"])
    if fmt == "docx": data, media, ext = export_to_docx(**kwargs), "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "docx"
    elif fmt == "md": data, media, ext = export_to_markdown(**kwargs), "text/markdown", "md"
    elif fmt == "pdf": data, media, ext = export_to_pdf(**kwargs), "application/pdf", "pdf"
    else: raise HTTPException(400, "Unsupported export format.")
    return Response(data, media_type=media, headers={"Content-Disposition":f'attachment; filename="{safe_title}.{ext}"'})

def re_safe_filename(title: str) -> str:
    import re
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", (title or "meeting").strip())[:100] or "meeting"

app.mount("/", StaticFiles(directory=str(FRONTEND), html=True), name="frontend")
