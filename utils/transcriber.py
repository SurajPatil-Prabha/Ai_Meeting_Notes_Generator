"""
Local audio/video transcription using faster-whisper (CTranslate2 build of
OpenAI's Whisper model). Everything runs on-device once the model weights
are downloaded the first time — no API key, no per-call network request.

Video files are handled by first stripping the audio track out with ffmpeg
(the system binary, not a Python wrapper), then transcribing that audio
the same way as a direct audio upload.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".wma"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}

# Cache loaded models across calls (keyed by model size) so re-running a
# transcription in the same session doesn't reload weights from disk.
_MODEL_CACHE: dict[str, object] = {}


class TranscriptionError(Exception):
    pass


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def is_video(filename: str) -> bool:
    return Path(filename).suffix.lower() in VIDEO_EXTENSIONS


def is_audio(filename: str) -> bool:
    return Path(filename).suffix.lower() in AUDIO_EXTENSIONS


def extract_audio_from_video(video_path: str) -> str:
    """Use ffmpeg to pull a mono 16kHz WAV track out of a video file.
    Returns the path to the extracted audio (caller is responsible for
    cleanup)."""
    if not ffmpeg_available():
        raise TranscriptionError(
            "ffmpeg is not installed or not on PATH. Install it (e.g. "
            "`sudo apt install ffmpeg`, `brew install ffmpeg`, or the "
            "Windows build from ffmpeg.org) to enable video transcription."
        )

    out_fd, out_path = tempfile.mkstemp(suffix=".wav")
    import os
    os.close(out_fd)

    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn",                # drop video stream
        "-ac", "1",            # mono
        "-ar", "16000",        # 16kHz, whisper's expected sample rate
        "-f", "wav",
        out_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise TranscriptionError(f"ffmpeg failed to extract audio: {result.stderr[-500:]}")
    return out_path


def _load_model(model_size: str = "base"):
    """Lazily import + load a faster-whisper model, caching it in-process.
    Import is deferred so the rest of the app works even if faster-whisper
    isn't installed and the user only ever uses text transcripts."""
    if model_size in _MODEL_CACHE:
        return _MODEL_CACHE[model_size]

    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        raise TranscriptionError(
            "faster-whisper is not installed. Run `pip install faster-whisper` "
            "to enable audio/video transcription (still 100% local, no API key)."
        ) from e

    # CPU + int8 quantization keeps this usable without a GPU. faster-whisper
    # downloads model weights from Hugging Face once and caches them locally
    # (~/.cache/huggingface) — after that first download it needs no network.
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    _MODEL_CACHE[model_size] = model
    return model


def transcribe_audio_file(
    file_path: str,
    model_size: str = "base",
    language: str | None = None,
    progress_callback=None,
) -> str:
    """
    Transcribe an audio file to text using a local Whisper model.
    Returns plain transcript text with rough timestamp markers per segment,
    which downstream speaker/action-item logic can still parse fine since
    they operate on sentence text, not the timestamps.
    """
    model = _load_model(model_size)

    segments, info = model.transcribe(
        file_path,
        language=language,  # None = auto-detect
        vad_filter=True,     # skip silence, keeps output cleaner
        beam_size=5,
    )

    lines = []
    for seg in segments:
        text = seg.text.strip()
        if not text:
            continue
        lines.append(text)
        if progress_callback:
            progress_callback(seg.end, info.duration)

    return " ".join(lines).strip()


def transcribe_media(
    uploaded_path: str,
    filename: str,
    model_size: str = "base",
    language: str | None = None,
    progress_callback=None,
) -> str:
    """
    Entry point for the app: handles both audio and video uploads.
    `uploaded_path` is a path to the file already saved on disk.
    """
    cleanup_path = None
    try:
        if is_video(filename):
            audio_path = extract_audio_from_video(uploaded_path)
            cleanup_path = audio_path
        elif is_audio(filename):
            audio_path = uploaded_path
        else:
            raise TranscriptionError(f"Unsupported media type: {filename}")

        return transcribe_audio_file(
            audio_path,
            model_size=model_size,
            language=language,
            progress_callback=progress_callback,
        )
    finally:
        if cleanup_path:
            import os
            try:
                os.remove(cleanup_path)
            except OSError:
                pass
