import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import whisper

from app.config import settings
from app.services.speech import load_audio_from_bytes

logger = logging.getLogger("speaksmart.asr")
logger.setLevel(logging.INFO)


@dataclass(frozen=True)
class ASRTranscript:
    text: str
    language: str | None
    avg_logprob: float | None
    no_speech_prob: float | None
    compression_ratio: float | None


_whisper_model = None


def initialize_asr() -> None:
    if settings.ASR_PROVIDER != "openai_whisper":
        raise RuntimeError(f"Unsupported ASR provider: {settings.ASR_PROVIDER}")

    get_whisper_model()


def get_whisper_model():
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model

    cache_dir = get_whisper_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "loading whisper model provider=%s model=%s device=%s cache_dir=%s",
        settings.ASR_PROVIDER,
        settings.OPENAI_WHISPER_MODEL,
        settings.OPENAI_WHISPER_DEVICE,
        cache_dir,
    )
    _whisper_model = whisper.load_model(
        settings.OPENAI_WHISPER_MODEL,
        device=settings.OPENAI_WHISPER_DEVICE,
        download_root=str(cache_dir),
    )
    logger.info(
        "whisper model loaded model=%s device=%s",
        settings.OPENAI_WHISPER_MODEL,
        settings.OPENAI_WHISPER_DEVICE,
    )
    return _whisper_model


def transcribe_audio_bytes(audio_bytes: bytes) -> ASRTranscript:
    model = get_whisper_model()
    waveform, _sample_rate = load_audio_from_bytes(audio_bytes, sr=16000)

    if waveform.size == 0:
        return ASRTranscript(
            text="",
            language=None,
            avg_logprob=None,
            no_speech_prob=1.0,
            compression_ratio=None,
        )

    waveform = np.asarray(waveform, dtype=np.float32)
    padded = whisper.pad_or_trim(waveform)
    mel = whisper.log_mel_spectrogram(padded, n_mels=model.dims.n_mels).to(model.device)

    language = settings.OPENAI_WHISPER_LANGUAGE
    try:
        _, language_probs = whisper.detect_language(mel)
        detected_language = max(language_probs, key=language_probs.get)
    except Exception:
        detected_language = None

    options = whisper.DecodingOptions(
        language=language,
        task="transcribe",
        without_timestamps=True,
        fp16=settings.OPENAI_WHISPER_DEVICE.startswith("cuda"),
    )
    result = whisper.decode(model, mel, options)

    transcript = ASRTranscript(
        text=(result.text or "").strip(),
        language=detected_language,
        avg_logprob=getattr(result, "avg_logprob", None),
        no_speech_prob=getattr(result, "no_speech_prob", None),
        compression_ratio=getattr(result, "compression_ratio", None),
    )
    logger.info(
        "whisper transcript model=%s device=%s detected_language=%s avg_logprob=%s no_speech_prob=%s compression_ratio=%s text=%s",
        settings.OPENAI_WHISPER_MODEL,
        settings.OPENAI_WHISPER_DEVICE,
        transcript.language,
        transcript.avg_logprob,
        transcript.no_speech_prob,
        transcript.compression_ratio,
        _truncate_for_log(transcript.text),
    )
    return transcript


def get_whisper_cache_dir() -> Path:
    cache_dir = Path(settings.OPENAI_WHISPER_CACHE_DIR)
    if cache_dir.is_absolute():
        return cache_dir
    return Path(__file__).resolve().parents[2] / cache_dir


def _truncate_for_log(value: str | None, limit: int = 160) -> str | None:
    if value is None:
        return None
    if len(value) <= limit:
        return value
    return f"{value[:limit]}..."
