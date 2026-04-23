from __future__ import annotations

import os
from pathlib import Path

import whisper


def main() -> None:
    model_name = os.getenv("OPENAI_WHISPER_MODEL", "small")
    cache_dir = Path(os.getenv("OPENAI_WHISPER_CACHE_DIR", ".cache/openai-whisper"))
    if not cache_dir.is_absolute():
        cache_dir = Path.cwd() / cache_dir
    cache_dir.mkdir(parents=True, exist_ok=True)

    print(f"Prefetching official Whisper model '{model_name}' into {cache_dir}...")
    whisper.load_model(model_name, download_root=str(cache_dir))
    print("Whisper model is ready.")


if __name__ == "__main__":
    main()
