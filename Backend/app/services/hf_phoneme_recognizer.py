from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from app.config import settings
from app.services.speech import load_audio_from_bytes

logger = logging.getLogger("speaksmart.hf_phoneme_recognizer")
logger.setLevel(logging.INFO)


_LEGACY_MOJIBAKE_KANA = [
    "あ", "い", "う", "え", "お",
    "か", "き", "く", "け", "こ",
    "さ", "し", "す", "せ", "そ",
    "た", "ち", "つ", "て", "と",
    "な", "に", "ぬ", "ね", "の",
    "は", "ひ", "ふ", "へ", "ほ",
    "ま", "み", "む", "め", "も",
    "や", "ゆ", "よ",
    "ら", "り", "る", "れ", "ろ",
    "わ", "を", "ん",
    "が", "ぎ", "ぐ", "げ", "ご",
    "ざ", "じ", "ず", "ぜ", "ぞ",
    "だ", "ぢ", "づ", "で", "ど",
    "ば", "び", "ぶ", "べ", "ぼ",
    "ぱ", "ぴ", "ぷ", "ぺ", "ぽ",
    "ぁ", "ぃ", "ぅ", "ぇ", "ぉ",
    "っ", "ゃ", "ゅ", "ょ", "ゎ",
    "ー",
]

DEFAULT_KANA = [
    "\u3042", "\u3044", "\u3046", "\u3048", "\u304a",
    "\u304b", "\u304d", "\u304f", "\u3051", "\u3053",
    "\u3055", "\u3057", "\u3059", "\u305b", "\u305d",
    "\u305f", "\u3061", "\u3064", "\u3066", "\u3068",
    "\u306a", "\u306b", "\u306c", "\u306d", "\u306e",
    "\u306f", "\u3072", "\u3075", "\u3078", "\u307b",
    "\u307e", "\u307f", "\u3080", "\u3081", "\u3082",
    "\u3084", "\u3086", "\u3088",
    "\u3089", "\u308a", "\u308b", "\u308c", "\u308d",
    "\u308f", "\u3092", "\u3093",
    "\u304c", "\u304e", "\u3050", "\u3052", "\u3054",
    "\u3056", "\u3058", "\u305a", "\u305c", "\u305e",
    "\u3060", "\u3062", "\u3065", "\u3067", "\u3069",
    "\u3070", "\u3073", "\u3076", "\u3079", "\u307c",
    "\u3071", "\u3074", "\u3077", "\u307a", "\u307d",
    "\u3041", "\u3043", "\u3045", "\u3047", "\u3049",
    "\u3063", "\u3083", "\u3085", "\u3087", "\u308e",
    "\u30fc",
]


DEFAULT_PHONEMES = [
    "a", "i", "u", "e", "o", "I", "U",
    "k", "ky", "g", "gy",
    "s", "sh", "z", "j",
    "t", "ts", "ch", "d",
    "n", "ny", "h", "hy", "f",
    "b", "by", "p", "py",
    "m", "my", "y", "r", "ry", "w",
    "N", "q", "Q", "cl",
]


@dataclass(frozen=True)
class HFPhonemeRecognition:
    recognized_kana: str
    recognized_phonemes: list[str]
    raw_phonemes: list[str]
    confidence: float
    token_confidences: list[dict[str, Any]]
    model_id: str
    device: str
    elapsed_ms: float
    ctc_enabled: bool = True
    fallback_used: bool = False
    warning: str | None = None

    def to_metadata(self) -> dict[str, Any]:
        return {
            "provider": "hybrid_hf_ctc",
            "ctc_model_id": self.model_id,
            "ctc_enabled": self.ctc_enabled,
            "fallback_used": self.fallback_used,
            "device": self.device,
            "recognized_kana": self.recognized_kana,
            "recognized_phonemes": self.recognized_phonemes,
            "raw_phonemes": self.raw_phonemes,
            "confidence": round(self.confidence, 4),
            "elapsed_ms": round(self.elapsed_ms, 1),
            "warning": self.warning,
        }


_model_bundle: dict[str, Any] | None = None


def recognize_pronunciation_audio(audio_bytes: bytes) -> HFPhonemeRecognition:
    bundle = get_model_bundle()
    torch = bundle["torch"]
    model = bundle["model"]
    feature_extractor = bundle["feature_extractor"]
    device = bundle["device"]

    waveform, sample_rate = load_audio_from_bytes(audio_bytes, sr=16000)
    if waveform.size == 0:
        return HFPhonemeRecognition(
            recognized_kana="",
            recognized_phonemes=[],
            raw_phonemes=[],
            confidence=0.0,
            token_confidences=[],
            model_id=settings.PHONEME_CTC_MODEL_ID,
            device=str(device),
            elapsed_ms=0.0,
            warning="empty waveform",
        )

    audio_array = np.asarray(waveform, dtype=np.float32)
    inputs = feature_extractor(
        audio_array,
        sampling_rate=sample_rate,
        return_tensors="pt",
        return_attention_mask=True,
    )
    input_values = inputs.input_values.to(device)
    attention_mask = inputs.attention_mask.to(device)

    started = time.perf_counter()
    with torch.no_grad():
        outputs = model(input_values, attention_mask=attention_mask)
    elapsed_ms = (time.perf_counter() - started) * 1000.0

    kana_tokens, _kana_confidences, recognized_kana = _decode_ctc_logits(
        outputs["kana_logits"],
        bundle["kana_itos"],
        normalize=False,
    )
    raw_phonemes, token_confidences, _phoneme_text = _decode_ctc_logits(
        outputs["phoneme_logits"],
        bundle["phoneme_itos"],
        normalize=True,
    )
    confidence_values = [float(item["confidence"]) for item in token_confidences]
    confidence = float(np.mean(confidence_values)) if confidence_values else 0.0

    logger.info(
        "hf phoneme recognition model=%s device=%s elapsed_ms=%.1f kana=%s phonemes=%s confidence=%.4f",
        settings.PHONEME_CTC_MODEL_ID,
        device,
        elapsed_ms,
        recognized_kana,
        " ".join(raw_phonemes),
        confidence,
    )

    return HFPhonemeRecognition(
        recognized_kana=recognized_kana or "".join(kana_tokens),
        recognized_phonemes=[_normalize_phoneme_token(item) for item in raw_phonemes],
        raw_phonemes=raw_phonemes,
        confidence=confidence,
        token_confidences=token_confidences,
        model_id=settings.PHONEME_CTC_MODEL_ID,
        device=str(device),
        elapsed_ms=elapsed_ms,
    )


def get_model_bundle() -> dict[str, Any]:
    global _model_bundle
    if _model_bundle is not None:
        return _model_bundle

    import torch
    import torch.nn as nn
    from huggingface_hub import hf_hub_download
    from transformers import Wav2Vec2Config, Wav2Vec2FeatureExtractor, Wav2Vec2Model

    cache_dir = get_hf_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    device = resolve_ctc_device(torch)
    checkpoint_path = hf_hub_download(
        repo_id=settings.PHONEME_CTC_MODEL_ID,
        filename=settings.PHONEME_CTC_CHECKPOINT_FILENAME,
        cache_dir=str(cache_dir),
    )
    checkpoint = _load_checkpoint(torch, checkpoint_path)
    checkpoint_config = checkpoint.get("config") if isinstance(checkpoint.get("config"), dict) else {}
    pretrained = str(
        checkpoint.get("pretrained")
        or checkpoint.get("base_model")
        or checkpoint_config.get("pretrained")
        or checkpoint_config.get("pretrained_model")
        or settings.PHONEME_CTC_BASE_MODEL_ID
    )
    inter_ctc_layer = checkpoint.get("inter_ctc_layer") or checkpoint_config.get("inter_ctc_layer")

    state_dict = checkpoint.get("model_state_dict", checkpoint)
    kana_vocab_size = _head_vocab_size(state_dict, "kana_head.weight")
    phoneme_vocab_size = _head_vocab_size(state_dict, "phoneme_head.weight")

    kana_stoi, kana_itos = _vocab_from_checkpoint(
        checkpoint.get("kana_vocab"),
        DEFAULT_KANA,
        target_size=kana_vocab_size,
    )
    phoneme_stoi, phoneme_itos = _vocab_from_checkpoint(
        checkpoint.get("phoneme_vocab"),
        DEFAULT_PHONEMES,
        target_size=phoneme_vocab_size,
    )

    config = Wav2Vec2Config.from_pretrained(pretrained, cache_dir=str(cache_dir))
    config.mask_time_prob = 0.0
    if inter_ctc_layer is None:
        inter_ctc_layer = int(config.num_hidden_layers // 2)

    encoder = Wav2Vec2Model.from_pretrained(
        pretrained,
        config=config,
        cache_dir=str(cache_dir),
    )
    model = _create_dual_ctc_model(
        nn=nn,
        encoder=encoder,
        kana_vocab_size=len(kana_stoi),
        phoneme_vocab_size=len(phoneme_stoi),
        hidden_size=int(config.hidden_size),
        inter_ctc_layer=int(inter_ctc_layer),
    )
    model.load_state_dict(state_dict, strict=False)
    model.float()
    model.to(device)
    model.eval()

    feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(
        pretrained,
        cache_dir=str(cache_dir),
    )

    _model_bundle = {
        "torch": torch,
        "model": model,
        "feature_extractor": feature_extractor,
        "device": device,
        "kana_itos": kana_itos,
        "phoneme_itos": phoneme_itos,
        "checkpoint_path": checkpoint_path,
    }
    logger.info(
        "hf phoneme model loaded model=%s base=%s device=%s cache_dir=%s",
        settings.PHONEME_CTC_MODEL_ID,
        pretrained,
        device,
        cache_dir,
    )
    return _model_bundle


def get_hf_cache_dir() -> Path:
    cache_dir = Path(settings.PHONEME_CTC_CACHE_DIR)
    if cache_dir.is_absolute():
        return cache_dir
    return Path(__file__).resolve().parents[2] / cache_dir


def resolve_ctc_device(torch_module: Any) -> str:
    configured = settings.PHONEME_CTC_DEVICE.strip().lower()
    if configured != "auto":
        return configured
    if torch_module.cuda.is_available():
        return "cuda"
    if hasattr(torch_module.backends, "mps") and torch_module.backends.mps.is_available():
        return "mps"
    return "cpu"


def reset_model_cache() -> None:
    global _model_bundle
    _model_bundle = None


def _create_dual_ctc_model(
    *,
    nn: Any,
    encoder: Any,
    kana_vocab_size: int,
    phoneme_vocab_size: int,
    hidden_size: int,
    inter_ctc_layer: int,
) -> Any:
    class DualCTCModel(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.encoder = encoder
            self.inter_ctc_layer = inter_ctc_layer
            self.kana_head = nn.Linear(hidden_size, kana_vocab_size)
            self.phoneme_head = nn.Linear(hidden_size, phoneme_vocab_size)

        def forward(self, input_values: Any, attention_mask: Any | None = None) -> dict[str, Any]:
            outputs = self.encoder(
                input_values,
                attention_mask=attention_mask,
                output_hidden_states=True,
            )
            return {
                "kana_logits": self.kana_head(outputs.last_hidden_state),
                "phoneme_logits": self.phoneme_head(outputs.hidden_states[self.inter_ctc_layer]),
            }

    return DualCTCModel()


def _load_checkpoint(torch_module: Any, checkpoint_path: str) -> dict[str, Any]:
    try:
        checkpoint = torch_module.load(
            checkpoint_path,
            map_location="cpu",
            weights_only=True,
        )
    except TypeError:
        checkpoint = torch_module.load(checkpoint_path, map_location="cpu")

    if not isinstance(checkpoint, dict):
        raise RuntimeError("HF phoneme checkpoint did not contain a state dict")
    return checkpoint


def _vocab_from_checkpoint(
    raw_vocab: Any,
    fallback_tokens: list[str],
    *,
    target_size: int | None = None,
) -> tuple[dict[str, int], dict[int, str]]:
    if isinstance(raw_vocab, dict):
        if all(isinstance(key, str) for key in raw_vocab):
            stoi = {str(key): int(value) for key, value in raw_vocab.items()}
        else:
            stoi = {str(value): int(key) for key, value in raw_vocab.items()}
    elif isinstance(raw_vocab, list):
        stoi = {str(token): index for index, token in enumerate(raw_vocab)}
    else:
        stoi = {"": 0}
        for index, token in enumerate(fallback_tokens, start=1):
            stoi[token] = index

    if "" not in stoi:
        shifted = {token: index + 1 for token, index in stoi.items()}
        shifted[""] = 0
        stoi = shifted

    if target_size is not None:
        if len(stoi) > target_size:
            stoi = {token: index for token, index in stoi.items() if index < target_size}
        while len(stoi) < target_size:
            index = len(stoi)
            stoi[f"__extra_{index}"] = index

    itos = {index: token for token, index in stoi.items()}
    return stoi, itos


def _head_vocab_size(state_dict: dict[str, Any], key: str) -> int | None:
    weight = state_dict.get(key)
    if weight is None or not hasattr(weight, "shape"):
        return None
    return int(weight.shape[0])


def _decode_ctc_logits(
    logits: Any,
    itos: dict[int, str],
    *,
    normalize: bool,
) -> tuple[list[str], list[dict[str, Any]], str]:
    probs = logits.squeeze(0).softmax(dim=-1)
    confidences, indices = probs.max(dim=-1)
    tokens: list[str] = []
    token_confidences: list[dict[str, Any]] = []
    previous_index: int | None = None

    for frame_index, token_index in enumerate(indices.tolist()):
        token_index = int(token_index)
        if token_index == 0:
            previous_index = token_index
            continue
        if previous_index == token_index:
            continue

        token = itos.get(token_index, "")
        if token and not token.startswith("__extra_"):
            normalized_token = _normalize_phoneme_token(token) if normalize else token
            tokens.append(token)
            token_confidences.append(
                {
                    "position": len(tokens) - 1,
                    "frame_index": frame_index,
                    "token": normalized_token,
                    "raw_token": token,
                    "confidence": float(confidences[frame_index].item()),
                }
            )
        previous_index = token_index

    return tokens, token_confidences, "".join(tokens)


def _normalize_phoneme_token(token: str) -> str:
    normalized = str(token).strip()
    mapping = {
        "q": "Q",
        "cl": "Q",
        "N": "N",
        "I": "i",
        "U": "u",
    }
    return mapping.get(normalized, normalized)
