# scripts/seed_phrases.py
import asyncio
import os
import sys

from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import texttospeech
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select

from app.config import settings
from app.db.base import Base
from app.db.models.module import Module
from app.db.models.phrase import Phrase
from app.services.r2_storage import upload_audio
from scripts.phrase_data import MODULES, PHRASES



# ── Google TTS client ──────────────────────────────────────────────────────────
tts_client = texttospeech.TextToSpeechClient()

VOICE = texttospeech.VoiceSelectionParams(
    language_code="ja-JP",
    name="ja-JP-Wavenet-B",
)

AUDIO_CONFIG = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
    sample_rate_hertz=16000,
    speaking_rate=0.85,
    pitch=0.0,
)


def generate_tts(japanese_text: str) -> bytes:
    """Calls Google TTS and returns WAV bytes."""
    client = texttospeech.TextToSpeechClient()  # initialized here, after .env is loaded
    synthesis_input = texttospeech.SynthesisInput(text=japanese_text)
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=VOICE,
        audio_config=AUDIO_CONFIG,
    )
    return response.audio_content


# ── DB setup ───────────────────────────────────────────────────────────────────
engine = create_async_engine(settings.DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


# ── Seeder ─────────────────────────────────────────────────────────────────────
async def seed():
    async with SessionLocal() as db:

        # 1. Seed modules
        print("Seeding modules...")
        for mod_data in MODULES:
            result = await db.execute(
                select(Module).where(Module.module_id == mod_data["module_id"])
            )
            if not result.scalar_one_or_none():
                db.add(Module(**mod_data))
                print(f"  ✅ Module created: {mod_data['title']}")
            else:
                print(f"  ⏭️  Module exists:  {mod_data['title']}")

        await db.commit()

        # 2. Seed phrases + generate TTS + upload to R2
        print("\nSeeding phrases + generating TTS audio...")
        for phrase_data in PHRASES:
            result = await db.execute(
                select(Phrase).where(Phrase.phrase_id == phrase_data["phrase_id"])
            )
            existing = result.scalar_one_or_none()

            if existing and existing.reference_audio_url:
                print(f"  ⏭️  Skipping (exists): {phrase_data['romaji']}")
                continue

            # Generate TTS audio
            print(f"  🎙️  Generating TTS: {phrase_data['japanese_text']}")
            audio_bytes = generate_tts(phrase_data["japanese_text"])

            # Upload to R2
            object_key = f"reference-audio/{phrase_data['module_id']}/{phrase_data['phrase_id']}.wav"
            audio_url = upload_audio(audio_bytes, object_key)
            print(f"  ☁️  Uploaded to R2: {object_key}")

            # Save or update phrase in DB
            if existing:
                existing.reference_audio_url = audio_url
            else:
                db.add(Phrase(
                    **phrase_data,
                    reference_audio_url=audio_url,
                ))

            await db.commit()
            print(f"  ✅ Done: {phrase_data['romaji']}")

        print("\n✅ Seeding complete — all modules and phrases are ready.")


if __name__ == "__main__":
    asyncio.run(seed())