import io

import librosa
import numpy as np


def load_audio_from_bytes(audio_bytes, sr: int = 16000) -> tuple[np.ndarray, int]:
    """
    Loads raw audio bytes into a numpy array.
    Works entirely in memory - no temp files written to disk.

    Returns:
        y  - audio time series as float32 numpy array
        sr - sample rate (always resampled to 16000 Hz)
    """
    buffer = io.BytesIO(audio_bytes)
    y, sr = librosa.load(buffer, sr=sr, mono=True)
    return y, sr


def prepare_waveform(y: np.ndarray) -> np.ndarray:
    """
    Trim leading/trailing silence and normalize amplitude so scoring focuses on
    the spoken portion instead of dead air or recording gain.
    """
    trimmed, _ = librosa.effects.trim(y, top_db=30)
    processed = trimmed if trimmed.size > 0 else y

    peak = float(np.max(np.abs(processed))) if processed.size > 0 else 0.0
    if peak > 0:
        processed = processed / peak

    return processed


def extract_mfcc(y: np.ndarray, sr: int = 16000, n_mfcc: int = 13) -> np.ndarray:
    """
    Extracts MFCC features from an audio signal.

    Returns:
        mfcc - shape (n_mfcc, T) where T is number of time frames
    """
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    # Normalize each coefficient to zero mean - improves DTW comparison
    mfcc = mfcc - np.mean(mfcc, axis=1, keepdims=True)
    return mfcc


def get_audio_duration(y: np.ndarray, sr: int = 16000) -> float:
    """
    Returns the duration of the audio in seconds.
    """
    return librosa.get_duration(y=y, sr=sr)


def extract_features(audio_bytes: bytes) -> dict:
    """
    Full feature extraction pipeline for a single audio file.

    Returns a dict with:
        mfcc      - normalized MFCC matrix (13 x T)
        duration  - audio length in seconds
        rms       - root mean square energy (used for silence detection)
    """
    y, sr = load_audio_from_bytes(audio_bytes)
    processed = prepare_waveform(y)

    mfcc = extract_mfcc(processed, sr)
    duration = get_audio_duration(processed, sr)
    rms = float(np.sqrt(np.mean(processed**2)))

    return {
        "mfcc": mfcc,
        "duration": duration,
        "rms": rms,
    }


def validate_audio(audio_bytes: bytes, max_size_mb: int = 10) -> None:
    """
    Validates audio before scoring.
    Raises ValueError with a descriptive message on failure.
    """
    size_mb = len(audio_bytes) / (1024 * 1024)
    if size_mb > max_size_mb:
        raise ValueError(
            f"Audio file is too large ({size_mb:.2f} MB). Max allowed is {max_size_mb} MB."
        )

    if len(audio_bytes) < 1000:
        raise ValueError("Audio file is too short or empty.")

    try:
        y, sr = load_audio_from_bytes(audio_bytes)
    except Exception:
        raise ValueError("Could not decode audio file - ensure it's a valid Wav or WebM file.")

    processed = prepare_waveform(y)

    duration = get_audio_duration(processed, sr)
    if duration < 0.3:
        raise ValueError(f"Audio too short: {duration:.2f}s (minimum 0.3s).")

    rms = float(np.sqrt(np.mean(processed**2)))
    if rms < 0.001:
        raise ValueError("Audio appears to be silent - please check your microphone")
