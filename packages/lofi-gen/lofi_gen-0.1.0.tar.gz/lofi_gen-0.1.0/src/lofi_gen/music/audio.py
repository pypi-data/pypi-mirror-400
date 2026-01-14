import os
import scipy

class AudioProcessor:
    def __init__(self, sampling_rate=32000):
        self.sampling_rate = sampling_rate

    def set_output_dir(self, output_dir):
        self.output_dir = output_dir

    def write_to_file(self, audio_data, filename):
        save_path = os.path.join(self.output_dir, filename)
        os.makedirs(self.output_dir, exist_ok=True)
        scipy.io.wavfile.write(save_path, rate=audio_data['sampling_rate'], data=audio_data["audio"])
        