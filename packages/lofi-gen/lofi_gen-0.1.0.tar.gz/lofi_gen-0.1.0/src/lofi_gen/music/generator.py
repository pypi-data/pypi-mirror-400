import os
from models import MusicGenModel
from audio import AudioProcessor

class MusicGenerator:
    def __init__(self, model, config):
        self.model = model
        self.config = config

    def generate_music(self, prompt, **kwargs):
        return self.model.generate_music(prompt, **kwargs)


if __name__ == "__main__":
    model = MusicGenModel(model_name="facebook/musicgen-large", device=1)
    generator = MusicGenerator(model=model, config={})
    audio_processor = AudioProcessor()
    audio_processor.set_output_dir("generated_music")

    prompt = (
            "lofi hip hop beat with traditional Nepali instruments, "
            "soft sarangi melody, gentle madal drums, relaxing ambient "
            "atmosphere, himalayan vibes, peaceful meditation music, "
            "warm analog sound, vinyl crackle, slow tempo 70 bpm"
        )
    
    music = generator.generate_music(prompt=prompt, duration=30)
    # Save or process the generated music as needed
    audio_processor.write_to_file(music, "relaxing_lofi_beat.wav")

