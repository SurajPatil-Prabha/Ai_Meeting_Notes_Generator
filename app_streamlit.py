"""
AI Meeting Notes Generator — CYBERDECK edition
------------------------------------------------
100% local, no API key required. Uses TF-IDF based extractive
summarization + rule-based extraction for action items and decisions.
Audio/video transcripts are produced locally with faster-whisper.

Run with:
    streamlit run app.py
"""

import html
import io
import os
import tempfile
from datetime import datetime

import streamlit as st
from docx import Document as DocxReader

from utils.summarizer import summarize, top_keywords
from utils.extractor import extract_action_items, extract_decisions, extract_speaker_breakdown
from utils.exporter import export_to_docx, export_to_pdf, export_to_markdown
from utils.transcriber import (
    transcribe_media,
    ffmpeg_available,
    is_video,
    is_audio,
    TranscriptionError,
)
from utils.analytics import (
    meeting_stats,
    speaker_sentiment,
    sentiment_score,
    talk_time_distribution,
    tag_action_items,
)
from utils.history import save_meeting, list_meetings, load_meeting, delete_meeting
from utils.theme import inject_theme, header_html, section_html, chip_html, highlight

WHISPER_MODEL_SIZES = ["tiny", "base", "small", "medium"]

st.set_page_config(page_title="AI Meeting Notes // Cyberdeck", page_icon="🧠", layout="wide")
inject_theme(st)


def read_uploaded_file(uploaded_file) -> str:
    """Read text from an uploaded .txt or .docx file."""
    name = uploaded_file.name.lower()
    if name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")
    elif name.endswith(".docx"):
        doc = DocxReader(io.BytesIO(uploaded_file.read()))
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        st.error("Unsupported file type. Please upload a .txt or .docx file.")
        return ""


def main():
    st.markdown(
        header_html(
            "Paste, upload, or transcribe a meeting and get "
            "<b>summary // action items // decisions // sentiment // analytics</b> "
            "— fully offline once installed."
        ),
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("### ⚙ CONFIG.SYS")
        num_summary_sentences = st.slider("Summary length (sentences)", 3, 15, 5)
        num_keywords = st.slider("Number of keywords", 5, 20, 10)
        meeting_title = st.text_input("Meeting title", value=f"Meeting Notes - {datetime.now().strftime('%d %b %Y')}")
        st.markdown("---")
        st.markdown("**🎙 TRANSCRIPTION.CFG** (for audio/video input)")
        whisper_model_size = st.selectbox(
            "Whisper model size",
            WHISPER_MODEL_SIZES,
            index=1,
            help=(
                "Bigger = more accurate but slower on CPU. 'tiny'/'base' are "
                "good for quick drafts; 'small'/'medium' for higher accuracy. "
                "The model downloads once and is cached locally afterward."
            ),
        )
        whisper_language = st.text_input(
            "Language code (optional)",
            value="",
            placeholder="e.g. en, hi, es — leave blank to auto-detect",
        )
        st.markdown("---")
        st.markdown(
            "**Tip:** For speaker-wise notes, format your transcript like:\n\n"
            "```\nJohn: Let's start with the budget.\nSarah: I agree, we need to review it.\n```"
        )
        st.markdown("---")
        st.markdown("### 🗂 MEETING_HISTORY.DB")
        history_entries = list_meetings()
        if history_entries:
            labels = [f"{e['title']} — {e['saved_at'][:16].replace('T',' ')}" for e in history_entries]
            selected_idx = st.selectbox(
                "Past meetings (saved locally as JSON)",
                range(len(labels)),
                format_func=lambda i: labels[i],
                key="history_select",
            )
            hc1, hc2 = st.columns(2)
            with hc1:
                if st.button("↩ Load", use_container_width=True):
                    record = load_meeting(history_entries[selected_idx]["filename"])
                    st.session_state["results"] = record.get("results")
                    st.session_state["transcript_loaded_from_history"] = record.get("transcript", "")
                    st.rerun()
            with hc2:
                if st.button("🗑 Delete", use_container_width=True):
                    delete_meeting(history_entries[selected_idx]["filename"])
                    st.rerun()
        else:
            st.caption("No saved meetings yet — generate notes and hit 'Save to history'.")

    st.markdown(section_html("01", "PROVIDE_TRANSCRIPT.IN"), unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs([
        "📋 Paste text",
        "📁 Upload file (.txt / .docx)",
        "🎙️ Upload audio / video",
    ])

    transcript = ""
    if "av_transcript" not in st.session_state:
        st.session_state["av_transcript"] = ""
    if st.session_state.get("transcript_loaded_from_history"):
        transcript = st.session_state["transcript_loaded_from_history"]

    with tab1:
        pasted = st.text_area("Paste your meeting transcript here", height=250, key="paste_area",
                               value=st.session_state.get("transcript_loaded_from_history", ""))
        if pasted:
            transcript = pasted

    with tab2:
        uploaded_file = st.file_uploader("Upload a .txt or .docx transcript", type=["txt", "docx"])
        if uploaded_file is not None:
            file_text = read_uploaded_file(uploaded_file)
            if file_text:
                transcript = file_text
                st.success(f"Loaded {len(file_text)} characters from {uploaded_file.name}")
                with st.expander("Preview uploaded content"):
                    st.text(file_text[:2000] + ("..." if len(file_text) > 2000 else ""))

    with tab3:
        st.markdown(
            "Upload a recorded meeting and it will be transcribed **entirely "
            "on your machine** with [faster-whisper](https://github.com/SYSTRAN/faster-whisper) "
            "— no API key, no audio ever leaves your computer."
        )
        if not ffmpeg_available():
            st.warning(
                "⚠️ `ffmpeg` was not found on PATH. Audio files will still work, but "
                "video files need ffmpeg installed to extract the audio track first."
            )

        media_file = st.file_uploader(
            "Upload an audio or video file",
            type=["mp3", "wav", "m4a", "aac", "flac", "ogg", "wma", "mp4", "mov", "mkv", "avi", "webm"],
            key="media_uploader",
        )

        if media_file is not None:
            kind = "video" if is_video(media_file.name) else "audio" if is_audio(media_file.name) else None
            if kind is None:
                st.error("Unsupported file type.")
            else:
                st.info(f"Loaded {kind} file: {media_file.name} ({media_file.size / 1_000_000:.1f} MB)")
                if kind == "audio":
                    st.audio(media_file)

                if st.button("🎧 Transcribe this file", use_container_width=True):
                    suffix = os.path.splitext(media_file.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(media_file.getbuffer())
                        tmp_path = tmp.name

                    progress_bar = st.progress(0.0, text="Loading local Whisper model (first run downloads it once)...")

                    def _progress(done, total):
                        if total:
                            frac = min(done / total, 1.0)
                            progress_bar.progress(frac, text=f"Transcribing... {frac * 100:.0f}%")

                    try:
                        with st.spinner("Transcribing locally — this can take a while on CPU for long recordings..."):
                            text = transcribe_media(
                                tmp_path,
                                media_file.name,
                                model_size=whisper_model_size,
                                language=whisper_language.strip() or None,
                                progress_callback=_progress,
                            )
                        progress_bar.progress(1.0, text="Done!")
                        if text:
                            st.session_state["av_transcript"] = text
                            st.success(f"Transcribed {len(text)} characters.")
                        else:
                            st.warning("No speech detected in the file.")
                    except TranscriptionError as e:
                        st.error(str(e))
                    finally:
                        try:
                            os.remove(tmp_path)
                        except OSError:
                            pass

        if st.session_state["av_transcript"]:
            with st.expander("Preview transcribed text", expanded=True):
                edited = st.text_area(
                    "You can edit the transcript before generating notes",
                    value=st.session_state["av_transcript"],
                    height=200,
                    key="av_transcript_edit",
                )
                st.session_state["av_transcript"] = edited
            transcript = st.session_state["av_transcript"]

    gcol1, gcol2 = st.columns([3, 1])
    with gcol1:
        generate = st.button("✨ GENERATE MEETING NOTES", type="primary", use_container_width=True)
    with gcol2:
        if st.button("⟲ RESET SESSION", use_container_width=True):
            for key in ["results", "av_transcript", "transcript_loaded_from_history"]:
                st.session_state.pop(key, None)
            st.rerun()

    if generate:
        if not transcript or not transcript.strip():
            st.warning("Please paste or upload a transcript first.")
            return

        with st.spinner("Analyzing transcript..."):
            summary = summarize(transcript, num_sentences=num_summary_sentences)
            action_items_raw = extract_action_items(transcript)
            action_items = tag_action_items(action_items_raw)
            decisions = extract_decisions(transcript)
            keywords = top_keywords(transcript, num_keywords=num_keywords)
            speaker_notes = extract_speaker_breakdown(transcript)
            stats = meeting_stats(transcript)
            overall_sentiment = sentiment_score(transcript)
            per_speaker_sentiment = speaker_sentiment(speaker_notes)
            talk_time = talk_time_distribution(speaker_notes)

        st.session_state["results"] = {
            "title": meeting_title,
            "summary": summary,
            "action_items": action_items_raw,
            "action_items_tagged": action_items,
            "decisions": decisions,
            "keywords": keywords,
            "speaker_notes": speaker_notes,
            "stats": stats,
            "overall_sentiment": overall_sentiment,
            "per_speaker_sentiment": per_speaker_sentiment,
            "talk_time": talk_time,
        }
        st.session_state["last_transcript"] = transcript

    if "results" in st.session_state and st.session_state["results"]:
        r = st.session_state["results"]
        st.markdown(section_html("02", "GENERATED_NOTES.OUT"), unsafe_allow_html=True)

        # --- Analytics strip ---
        stats = r.get("stats", {})
        overall_sentiment = r.get("overall_sentiment", {"label": "Neutral"})
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("WORDS", stats.get("word_count", "—"))
        m2.metric("EST. DURATION", f"{stats.get('est_duration_min', '—')} min")
        m3.metric("READING TIME", f"{stats.get('est_reading_min', '—')} min")
        m4.metric("OVERALL TONE", overall_sentiment.get("label", "—"))

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="hud-panel"><div class="cyber-label">📄 SUMMARY</div>', unsafe_allow_html=True)
            if r["summary"]:
                for line in r["summary"]:
                    st.markdown(f"- {line}")
            else:
                st.info("No summary could be generated (transcript too short).")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="hud-panel"><div class="cyber-label">✅ ACTION ITEMS</div>', unsafe_allow_html=True)
            tagged = r.get("action_items_tagged") or tag_action_items(r.get("action_items", []))
            if tagged:
                for item in tagged:
                    chip = chip_html(item["priority"], item["priority"])
                    st.markdown(f"- {item['text']} {chip}", unsafe_allow_html=True)
            else:
                st.info("No action items detected.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="hud-panel"><div class="cyber-label">📌 KEY DECISIONS</div>', unsafe_allow_html=True)
            if r["decisions"]:
                for d in r["decisions"]:
                    st.markdown(f"- {d}")
            else:
                st.info("No decisions detected.")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="hud-panel"><div class="cyber-label">🏷 KEYWORDS / TOPICS</div>', unsafe_allow_html=True)
            if r["keywords"]:
                st.write(", ".join(r["keywords"]))
            else:
                st.info("No keywords extracted.")
            st.markdown("</div>", unsafe_allow_html=True)

        # --- Speaker analytics: sentiment + talk time ---
        talk_time = r.get("talk_time") or {}
        per_speaker_sentiment = r.get("per_speaker_sentiment") or {}
        if r["speaker_notes"]:
            st.markdown(section_html("03", "SPEAKER_ANALYTICS.LOG"), unsafe_allow_html=True)

            if talk_time:
                chart_data = {speaker: v["words"] for speaker, v in talk_time.items()}
                st.markdown('<div class="hud-panel"><div class="cyber-label">🎚 TALK-TIME DISTRIBUTION (by word share)</div>', unsafe_allow_html=True)
                st.bar_chart(chart_data)
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("### 🗣️ Speaker-wise Notes")
            for speaker, lines in r["speaker_notes"].items():
                sent = per_speaker_sentiment.get(speaker, {"label": "Neutral"})
                pct = talk_time.get(speaker, {}).get("pct", 0)
                label = f"{speaker}  ·  {pct}% airtime"
                with st.expander(label):
                    st.markdown(chip_html(sent["label"], sent["label"]), unsafe_allow_html=True)
                    for line in lines:
                        st.markdown(f"- {line}")

        # --- Transcript search / highlight ---
        last_transcript = st.session_state.get("last_transcript", "")
        if last_transcript:
            st.markdown(section_html("04", "TRANSCRIPT_SEARCH.QRY"), unsafe_allow_html=True)
            query = st.text_input("Search / highlight a term in the transcript", key="search_query")
            with st.expander("View full transcript", expanded=bool(query)):
                escaped = html.escape(last_transcript)
                content = highlight(escaped, query) if query else escaped
                st.markdown(
                    f'<div class="hud-panel" style="max-height:320px; overflow-y:auto; white-space:pre-wrap; font-size:13px;">{content}</div>',
                    unsafe_allow_html=True,
                )

        st.markdown(section_html("05", "EXPORT.SH"), unsafe_allow_html=True)

        export_kwargs = {
            "title": r["title"], "summary": r["summary"], "action_items": r["action_items"],
            "decisions": r["decisions"], "keywords": r["keywords"], "speaker_notes": r["speaker_notes"],
        }
        docx_bytes = export_to_docx(**export_kwargs)
        pdf_bytes = export_to_pdf(**export_kwargs)
        md_bytes = export_to_markdown(**export_kwargs)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.download_button(
                "⬇ WORD (.docx)", data=docx_bytes,
                file_name=f"{r['title'].replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        with c2:
            st.download_button(
                "⬇ PDF", data=pdf_bytes,
                file_name=f"{r['title'].replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        with c3:
            st.download_button(
                "⬇ MARKDOWN (.md)", data=md_bytes,
                file_name=f"{r['title'].replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with c4:
            if st.button("💾 SAVE TO HISTORY", use_container_width=True):
                save_meeting({
                    "title": r["title"],
                    "transcript": st.session_state.get("last_transcript", ""),
                    "results": r,
                })
                st.success("Saved to local meeting history (see sidebar).")

    st.markdown(
        '<div class="cyber-footer">SYSTEM: 100% LOCAL // NO_API_KEY // NO_CLOUD_UPLOAD // '
        'v2.0-CYBERDECK</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
