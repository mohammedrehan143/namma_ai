import io
import struct
import math
import httpx
from typing import Union
from backend.core.config import settings
from backend.core.logging import logger

def generate_minimal_wav(duration_seconds: float = 0.5, sample_rate: int = 16000, frequency: float = 440.0) -> bytes:
    """Generates a valid 16-bit mono PCM WAV in memory for fallback/mock testing."""
    num_samples = int(duration_seconds * sample_rate)
    data = bytearray()
    for i in range(num_samples):
        # Generate a gentle audible sine tone or silence
        value = int(32767.0 * 0.15 * math.sin(2.0 * math.pi * frequency * (i / sample_rate)))
        data.extend(struct.pack('<h', value))
    
    data_size = len(data)
    total_size = 36 + data_size
    
    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        total_size,
        b'WAVE',
        b'fmt ',
        16,              # Subchunk1Size for PCM
        1,               # AudioFormat (1 = PCM)
        1,               # NumChannels (1 = Mono)
        sample_rate,     # SampleRate
        sample_rate * 2, # ByteRate (SampleRate * NumChannels * BitsPerSample/8)
        2,               # BlockAlign (NumChannels * BitsPerSample/8)
        16,              # BitsPerSample
        b'data',
        data_size
    )
    return header + data

class AudioService:
    """Handles communication with Faster-Whisper (STT) and Piper (TTS)."""

    def __init__(self):
        self.stt_url = settings.STT_SERVICE_URL
        self.tts_url = settings.TTS_SERVICE_URL
        self.stt_provider = settings.STT_PROVIDER.lower()
        self.tts_provider = settings.TTS_PROVIDER.lower()

    async def transcribe(self, audio_bytes: bytes, filename: str = "caller_turn.wav") -> str:
        """Converts caller speech audio into text using Faster-Whisper STT."""
        if not audio_bytes or len(audio_bytes) < 44:
            return ""

        # If running in mock/offline mode or test environment
        if self.stt_provider == "mock":
            # If the audio contains embedded text markers from tests, parse them
            try:
                raw_text = audio_bytes.decode('utf-8', errors='ignore')
                if "TEXT:" in raw_text:
                    return raw_text.split("TEXT:")[1].strip()
            except Exception:
                pass
            return "There is a deep dangerous pothole near BMSIT main gate."

        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                files = {"file": (filename, audio_bytes, "audio/wav")}
                data = {
                    "model": "Systran/faster-whisper-base.en",
                    "language": "en"
                }
                response = await client.post(self.stt_url, files=files, data=data)
                if response.status_code == 200:
                    result = response.json()
                    transcript = result.get("text", "").strip()
                    logger.info(f"Faster-Whisper STT output: '{transcript}'")
                    return transcript
                else:
                    logger.warning(f"Whisper STT returned HTTP {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"Faster-Whisper STT connection failed: {e}. Falling back to default utterance.")

        return ""

    async def synthesize(self, text: str) -> bytes:
        """Converts response text into 16kHz mono WAV audio using Piper TTS."""
        if not text:
            return generate_minimal_wav(0.2)

        # If live Piper TTS is enabled
        if self.tts_provider == "piper":
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    # Piper HTTP API accepts GET or POST
                    response = await client.get(self.tts_url, params={"text": text})
                    if response.status_code == 200 and len(response.content) > 44:
                        return response.content
                    else:
                        logger.warning(f"Piper TTS returned HTTP {response.status_code}")
            except Exception as e:
                logger.warning(f"Piper TTS connection failed: {e}. Falling back to minimal audio stream.")

        # Deterministic valid PCM WAV for offline / test runs
        return generate_minimal_wav(duration_seconds=0.5, sample_rate=16000, frequency=350.0)

audio_service = AudioService()
