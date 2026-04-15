# scripts/test_scoring.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.services.r2_storage import download_audio
from app.services.scoring import score_attempt


def test_scoring():
    print("Testing scoring pipeline...")

    # Download the first reference audio from R2
    object_key = "reference-audio/module_greetings/ph_greet_001.wav"
    print(f"Downloading reference audio: {object_key}")
    reference_audio = download_audio(object_key)
    print(f"✅ Downloaded {len(reference_audio)} bytes")

    # Score the reference against itself — should return a very high score
    print("\nScoring reference audio against itself (expect ~90–100%)...")
    result = score_attempt(reference_audio, reference_audio)

    print(f"\n  accuracy_score:    {result['accuracy_score']}%")
    print(f"  mora_timing_score: {result['mora_timing_score']}%")
    print(f"  consonant_score:   {result['consonant_score']}%")
    print(f"  vowel_score:       {result['vowel_score']}%")
    print(f"  feedback:          {result['feedback_text']}")
    print(f"\n  phoneme_error_map: {result['phoneme_error_map']}")

    assert result["accuracy_score"] >= 85, "Self-comparison score too low — check DTW weights"
    print("\n✅ Scoring pipeline is working correctly.")


if __name__ == "__main__":
    test_scoring()