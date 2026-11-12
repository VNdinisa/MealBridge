"""Speech-to-text abstraction for MealBridge (Google Cloud + NVIDIA + Sidecar)."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path


class Transcriber(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str | Path) -> str:
        """Transcribe an audio file to text."""
        pass


class SidecarTranscriber(Transcriber):
    """Deterministic offline transcriber that reads a .txt file next to the audio file.
    
    Guarantees 100% reproducible tests, offline capability, and instant demo execution.
    """

    def transcribe(self, audio_path: str | Path) -> str:
        p = Path(audio_path)
        sidecar_path = p.with_suffix(".txt")

        if not sidecar_path.exists():
            # If the path passed is already a .txt file, read it directly
            if p.suffix == ".txt" and p.exists():
                return p.read_text(encoding="utf-8").strip()
            raise FileNotFoundError(
                f"Sidecar transcript not found for audio '{audio_path}'. Expected '{sidecar_path}'."
            )

        return sidecar_path.read_text(encoding="utf-8").strip()


class NvidiaNimTranscriber(Transcriber):
    """Transcribes audio using NVIDIA NIM (e.g., Whisper-large-v3 / Parakeet on api.nvidia.com)."""

    def __init__(self, api_key: str | None = None, base_url: str = "https://integrate.api.nvidia.com/v1"):
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        self.base_url = base_url

    def transcribe(self, audio_path: str | Path) -> str:
        if not self.api_key:
            raise ValueError("NVIDIA_API_KEY is not set. Use SidecarTranscriber for offline tests.")

        # In production, uses OpenAI-compatible audio client against NVIDIA NIM endpoint
        from openai import OpenAI
        client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        with open(audio_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="nvidia/whisper-large-v3",
                file=f,
            )
        return transcript.text
