# lofi-gen

A Python package for generating Lofi music using AI models like MusicGen.

## Features

- Generate lofi music from text prompts using Meta's MusicGen model
- Create seamless long-form music loops (extend short clips to hours-long sessions)
- Easy-to-use API for music generation
- Spectral crossfading for smooth transitions

## Installation

### From PyPI

```bash
pip install lofi-gen
```

### From Source

```bash
git clone https://github.com/gnikesh/lofi-gen.git
cd lofi-gen
pip install -e .
```

## Quick Start

### Basic Music Generation

```python
from lofi_gen.music.models import MusicGenModel

# Initialize the model
model = MusicGenModel(model_size="large")  # Options: "small", "medium", "large"

# Generate music from a text prompt
audio, sample_rate = model.generate_music(
    prompt="lofi hip hop beat with soft piano, chill vibes",
    duration_seconds=30
)

# Save the generated audio
model.save_audio(audio, sample_rate, "output.wav")
```

### Generate Long-Form Music

```python
from lofi_gen.music.models import MusicGenModel
from lofi_gen.music.pipelines import LongMusicGenerator

# Generate initial clip
model = MusicGenModel()
audio, sample_rate = model.generate_music(
    prompt="relaxing nepali lofi with bansuri flute",
    duration_seconds=60
)
model.save_audio(audio, sample_rate, "base_clip.wav")

# Extend it to a long seamless loop
extender = LongMusicGenerator(crossfade_sec=3.0, variation=True)
extender.generate(
    input_file="base_clip.wav",
    output_file="extended_lofi.wav",
    target_duration_mins=60  # Create a 60-minute loop
)
```


## Requirements

- Python >= 3.8
- PyTorch >= 2.0.0
- transformers >= 4.30.0
- librosa >= 0.10.0
- scipy, numpy, soundfile

See [requirements.txt](requirements.txt) for full dependencies.

## Model Sizes

MusicGen comes in three sizes:

- **small**: Fastest, lower quality (~300MB)
- **medium**: Balanced speed and quality (~1.5GB)
- **large**: Best quality, slower (~3.3GB)

Choose based on your hardware and quality requirements.

## Advanced Usage

### Custom Generation Parameters

```python
audio, sample_rate = model.generate_music(
    prompt="lofi hip hop beat",
    duration_seconds=30,
    guidance_scale=3.0,      # How closely to follow the prompt (1.0-15.0)
    temperature=1.0,         # Randomness (0.1-2.0)
    top_k=250,              # Sampling diversity
    top_p=0.0               # Nucleus sampling (0 to disable)
)
```

### Seamless Loop Configuration

```python
extender = LongMusicGenerator(
    crossfade_sec=3.0,    # Crossfade duration
    variation=True        # Add subtle variations to prevent monotony
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Meta AI for the [MusicGen](https://github.com/facebookresearch/audiocraft) model
- Hugging Face for the Transformers library
- The open-source community for various audio processing tools


## Support

For issues, questions, or suggestions:
- Open an issue on [GitHub](https://github.com/gnikesh/lofi-gen/issues)


## Roadmap

- [ ] Add more AI models (AudioLDM, Stable Audio, etc.)
- [ ] Video generation capabilities
- [ ] CLI interface for easy command-line usage
- [ ] Pre-trained models fine-tuned on Nepali music
- [ ] Web interface for music generation
