"""
Standalone test of core logic (no streamlit needed to run this).
Run: python3 test_core.py
"""

import sys
from utils.summarizer import summarize, top_keywords
from utils.extractor import extract_action_items, extract_decisions, extract_speaker_breakdown
from utils.exporter import export_to_docx, export_to_pdf

SAMPLE_TRANSCRIPT = """
John: Good morning everyone, let's start the meeting. Today we need to discuss the Q3 budget and the new marketing campaign.
Sarah: Sure. I think we should increase the marketing budget by 15 percent to support the new product launch.
John: That sounds reasonable. We agreed last week that the launch date is October 15th.
Mike: I will send the updated budget sheet to everyone by Friday.
Sarah: Great. Also, we decided that Mike will take care of coordinating with the design team.
John: One more thing, we need to finalize the vendor contract before the end of this month.
Mike: I have to follow up with legal on that contract, I'll do it tomorrow.
Sarah: Sounds good. We approved the final campaign creative in yesterday's review.
John: Perfect. Let's wrap up. Action item for me: I will schedule the next review meeting for next week.
Mike: Sounds like a plan. Thanks everyone.
"""

NO_SPEAKER_TRANSCRIPT = """
The team discussed the quarterly roadmap in detail. Several risks were raised regarding the timeline.
It was decided that the release would be delayed by two weeks to accommodate testing.
The QA lead needs to prepare a full regression test plan by next Monday.
Everyone agreed that communication with stakeholders should improve going forward.
The budget for the new hires was approved during the call.
"""


def run_test(name, transcript):
    print(f"\n{'='*60}\nTEST: {name}\n{'='*60}")

    summary = summarize(transcript, num_sentences=4)
    print(f"\n[Summary] ({len(summary)} sentences)")
    for s in summary:
        print(f"  - {s}")
    assert len(summary) > 0, "Summary should not be empty"

    action_items = extract_action_items(transcript)
    print(f"\n[Action Items] ({len(action_items)})")
    for a in action_items:
        print(f"  - {a}")
    assert len(action_items) > 0, "Should detect at least one action item"

    decisions = extract_decisions(transcript)
    print(f"\n[Decisions] ({len(decisions)})")
    for d in decisions:
        print(f"  - {d}")
    assert len(decisions) > 0, "Should detect at least one decision"

    keywords = top_keywords(transcript, num_keywords=8)
    print(f"\n[Keywords] {keywords}")
    assert len(keywords) > 0, "Should extract keywords"

    speakers = extract_speaker_breakdown(transcript)
    print(f"\n[Speakers] {list(speakers.keys())}")

    # Test exports
    docx_bytes = export_to_docx(
        title=f"Test - {name}", summary=summary, action_items=action_items,
        decisions=decisions, keywords=keywords, speaker_notes=speakers
    )
    assert len(docx_bytes) > 1000, "DOCX export should produce a real file"
    print(f"\n[Export] DOCX size: {len(docx_bytes)} bytes OK")

    pdf_bytes = export_to_pdf(
        title=f"Test - {name}", summary=summary, action_items=action_items,
        decisions=decisions, keywords=keywords, speaker_notes=speakers
    )
    assert len(pdf_bytes) > 500, "PDF export should produce a real file"
    assert pdf_bytes[:4] == b"%PDF", "Should be a valid PDF file"
    print(f"[Export] PDF size: {len(pdf_bytes)} bytes OK, valid PDF header confirmed")

    print(f"\n✅ ALL CHECKS PASSED for '{name}'")
    return docx_bytes, pdf_bytes


def test_edge_cases():
    print(f"\n{'='*60}\nTEST: Edge cases\n{'='*60}")

    # Empty text
    assert summarize("") == []
    assert extract_action_items("") == []
    assert extract_decisions("") == []
    assert top_keywords("") == []
    assert extract_speaker_breakdown("") == {}
    print("  - Empty text handled correctly")

    # Very short text (fewer sentences than requested summary length)
    short = "We agreed to proceed. John will send the report."
    s = summarize(short, num_sentences=10)
    assert len(s) <= 2
    print("  - Short text handled correctly")

    # Text with no action items / decisions
    plain = "The weather was nice today. We had coffee and chatted about the weekend."
    assert extract_action_items(plain) == []
    assert extract_decisions(plain) == []
    print("  - No-signal text handled correctly (empty results, no crash)")

    # Export with all-empty sections should still produce valid files, not crash
    docx_bytes = export_to_docx(title="Empty Test", summary=[], action_items=[], decisions=[], keywords=[], speaker_notes={})
    pdf_bytes = export_to_pdf(title="Empty Test", summary=[], action_items=[], decisions=[], keywords=[], speaker_notes={})
    assert len(docx_bytes) > 500
    assert pdf_bytes[:4] == b"%PDF"
    print("  - Export with empty sections handled correctly")

    print("\n✅ ALL EDGE CASE CHECKS PASSED")


if __name__ == "__main__":
    try:
        run_test("With speaker labels", SAMPLE_TRANSCRIPT)
        run_test("Without speaker labels", NO_SPEAKER_TRANSCRIPT)
        test_edge_cases()
        print(f"\n{'='*60}\n🎉 ALL TESTS PASSED SUCCESSFULLY\n{'='*60}")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        raise
