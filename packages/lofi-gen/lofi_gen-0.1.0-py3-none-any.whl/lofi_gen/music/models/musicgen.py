from .base import BaseMusicGenModel
from typing import Dict, Any, Optional, Tuple
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import torch
import numpy as np
import scipy.io.wavfile as wavfile


class MusicGenModel(BaseMusicGenModel):
    """MusicGen model wrapper for text-to-music generation.

    Example usage:
        from lofi_gen.music.models.musicgen import MusicGenModel

        model = MusicGenModel(model_size="large")
        audio, sample_rate = model.generate_music(
            prompt="lofi hip hop beat with soft piano",
            duration_seconds=30
        )
        model.save_audio(audio, sample_rate, "output.wav")
    """

    def __init__(self,
                 model_size: str = "large",
                 device: Optional[str] = None,
                 **kwargs):
        """Initialize the MusicGen model.

        Args:
            model_size: Model variant - "small", "medium", or "large"
                       (small is faster, large has better quality)
            device: Device to run on ("cuda" or "cpu"). If None, auto-detects.
            **kwargs: Additional configuration options.
        """
        model_name = f"facebook/musicgen-{model_size}"
        super().__init__(model_name=model_name, config=kwargs)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self._processor = None
        self.load_model()

    def load_model(self):
        """Load the MusicGen model and processor."""
        if self._model is None:
            self._processor = AutoProcessor.from_pretrained(self.model_name)
            self._model = MusicgenForConditionalGeneration.from_pretrained(self.model_name)
            self._model = self._model.to(self.device)

    def generate_music(
        self,
        prompt: str,
        duration_seconds: int = 30,
        guidance_scale: float = 3.0,
        temperature: float = 1.0,
        top_k: int = 250,
        top_p: float = 0.0,
        **kwargs
    ) -> Tuple[np.ndarray, int]:
        """Generate music based on the given prompt.

        Args:
            prompt: Text description for music generation.
            duration_seconds: Length of generated audio in seconds.
            guidance_scale: How closely to follow the prompt (higher = more adherent).
            temperature: Randomness in generation (higher = more varied).
            top_k: Number of top tokens to consider.
            top_p: Nucleus sampling threshold (0 to disable).

        Returns:
            Tuple of (audio_array, sample_rate)
        """
        inputs = self._processor(
            text=[prompt],
            padding=True,
            return_tensors="pt",
        ).to(self.device)

        # MusicGen generates at ~50 tokens per second of audio
        max_new_tokens = int(duration_seconds * 50)

        with torch.no_grad():
            audio_values = self._model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                guidance_scale=guidance_scale,
                temperature=temperature,
                do_sample=True,
                top_k=top_k,
                top_p=top_p if top_p > 0 else None,
            )

        sample_rate = self._model.config.audio_encoder.sampling_rate
        audio_array = audio_values[0, 0].cpu().numpy()

        return audio_array, sample_rate

    def save_audio(
        self,
        audio_array: np.ndarray,
        sample_rate: int,
        output_path: str,
        normalize: bool = True
    ) -> str:
        """Save generated audio to a WAV file.

        Args:
            audio_array: Audio data as numpy array.
            sample_rate: Audio sample rate.
            output_path: Path to save the WAV file.
            normalize: Whether to normalize audio to prevent clipping.

        Returns:
            The output path where the file was saved.
        """
        if normalize:
            audio_array = audio_array / np.max(np.abs(audio_array))

        # Convert to 16-bit PCM
        audio_int16 = (audio_array * 32767).astype(np.int16)

        wavfile.write(output_path, sample_rate, audio_int16)
        return output_path
