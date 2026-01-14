import librosa
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.ndimage import uniform_filter1d


class LongMusicGenerator:
    """
    A class for creating seamless audio loops using advanced techniques:
    - Optimal loop point detection via self-similarity
    - Spectral-domain crossfading
    - Zero-crossing alignment
    - Optional micro-variations to prevent listener fatigue
    """

    def __init__(self, crossfade_sec: float = 3.0, variation: bool = True):
        """
        Initialize the LongMusicGenerator.

        Args:
            crossfade_sec: Duration of crossfade in seconds (default: 3.0)
            variation: Whether to add subtle variations to prevent monotony (default: True)
        """
        self.crossfade_sec = crossfade_sec
        self.variation = variation
        self.hop_length = 512
        self.n_fft = 2048

    def find_optimal_loop_points(self, y: np.ndarray, sr: int,
                                  min_loop_length: float = 10,
                                  max_loop_length: float = None) -> tuple:
        """
        Find the best loop points using self-similarity matrix.

        Args:
            y: Audio time series
            sr: Sample rate
            min_loop_length: Minimum loop length in seconds (default: 10)
            max_loop_length: Maximum loop length in seconds (default: audio length - 1)

        Returns:
            Tuple of (start_sample, end_sample, similarity_score)
        """
        if max_loop_length is None:
            max_loop_length = len(y) / sr - 1

        # Compute chromagram for harmonic similarity
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

        # Compute MFCCs for timbral similarity
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

        # Combine features
        features = np.vstack([chroma, mfccs])

        # Normalize
        features = librosa.util.normalize(features, axis=1)

        # Compute self-similarity matrix
        sim_matrix = np.dot(features.T, features)

        # Convert frame indices to time
        frame_to_sample = lambda f: f * self.hop_length

        min_frames = int(min_loop_length * sr / self.hop_length)
        max_frames = int(max_loop_length * sr / self.hop_length)

        best_score = -np.inf
        best_start, best_end = 0, len(y)

        # Search for best loop points (end should match start)
        n_frames = sim_matrix.shape[0]

        for end_frame in range(min_frames, min(max_frames, n_frames)):
            # Look at similarity between frame 0 and end_frame
            # Also consider a window around these points
            window = 5
            start_region = slice(0, window)
            end_region = slice(max(0, end_frame - window), end_frame)

            score = np.mean(sim_matrix[start_region, end_region])

            if score > best_score:
                best_score = score
                best_start = 0
                best_end = frame_to_sample(end_frame)

        return best_start, min(best_end, len(y)), best_score

    def spectral_crossfade(self, y1: np.ndarray, y2: np.ndarray,
                           sr: int, crossfade_duration: float = 3.0) -> np.ndarray:
        """
        Perform crossfade in the spectral domain for smoother transitions.
        This preserves phase coherence better than time-domain crossfading.

        Args:
            y1: First audio segment (ending)
            y2: Second audio segment (starting)
            sr: Sample rate
            crossfade_duration: Duration of crossfade in seconds

        Returns:
            Crossfaded audio segment
        """
        n_crossfade = int(crossfade_duration * sr)
        hop_length = self.n_fft // 4

        # Get the crossfade regions
        end_region = y1[-n_crossfade:]
        start_region = y2[:n_crossfade]

        # Compute STFTs
        stft1 = librosa.stft(end_region, n_fft=self.n_fft, hop_length=hop_length)
        stft2 = librosa.stft(start_region, n_fft=self.n_fft, hop_length=hop_length)

        # Create smooth crossfade curve in spectral domain
        n_frames = stft1.shape[1]
        fade = np.linspace(0, 1, n_frames)[np.newaxis, :]

        # Blend magnitudes and phases separately for better results
        mag1, phase1 = np.abs(stft1), np.angle(stft1)
        mag2, phase2 = np.abs(stft2), np.angle(stft2)

        # Smooth magnitude interpolation
        blended_mag = mag1 * (1 - fade) + mag2 * fade

        # Phase interpolation (using circular mean)
        # This is tricky - we'll use weighted combination
        blended_phase = np.angle(
            (1 - fade) * np.exp(1j * phase1) + fade * np.exp(1j * phase2)
        )

        # Reconstruct
        blended_stft = blended_mag * np.exp(1j * blended_phase)
        crossfaded = librosa.istft(blended_stft, hop_length=hop_length, length=n_crossfade)

        return crossfaded

    def find_zero_crossing_near(self, y: np.ndarray, target_idx: int,
                                 search_range: int = 1000) -> int:
        """
        Find the nearest zero crossing to target index.

        Args:
            y: Audio time series
            target_idx: Target sample index
            search_range: Number of samples to search around target

        Returns:
            Sample index of nearest zero crossing
        """
        start = max(0, target_idx - search_range)
        end = min(len(y), target_idx + search_range)

        region = y[start:end]
        zero_crossings = np.where(np.diff(np.signbit(region)))[0]

        if len(zero_crossings) == 0:
            return target_idx

        nearest = zero_crossings[np.argmin(np.abs(zero_crossings - search_range))]
        return start + nearest

    def generate(self, input_file: str, output_file: str,
                 target_duration_mins: float = 60, verbose: bool = True) -> tuple:
        """
        Create a seamless loop from an input audio file.

        Args:
            input_file: Path to input audio file
            output_file: Path to save the output audio file
            target_duration_mins: Target duration in minutes (default: 60)
            verbose: Whether to print progress messages (default: True)

        Returns:
            Tuple of (audio_array, sample_rate)
        """
        if verbose:
            print("Loading audio...")
        y, sr = librosa.load(input_file, sr=None)

        if verbose:
            print("Finding optimal loop points...")
        loop_start, loop_end, similarity_score = self.find_optimal_loop_points(y, sr)
        if verbose:
            print(f"  Best loop: {loop_start/sr:.2f}s to {loop_end/sr:.2f}s (similarity: {similarity_score:.3f})")

        # Align to zero crossings for click-free cuts
        loop_start = self.find_zero_crossing_near(y, loop_start)
        loop_end = self.find_zero_crossing_near(y, loop_end)

        # Extract loop segment
        loop_segment = y[loop_start:loop_end].copy()
        loop_duration = len(loop_segment) / sr
        if verbose:
            print(f"  Loop duration: {loop_duration:.2f}s")

        # Calculate how many loops we need
        target_samples = int(target_duration_mins * 60 * sr)
        crossfade_samples = int(self.crossfade_sec * sr)

        # Build the result
        if verbose:
            print("Building seamless loop...")
        result = loop_segment.copy()
        loop_count = 1

        while len(result) < target_samples:
            # Get the segment to append
            segment_to_add = loop_segment.copy()

            # Optional: Add subtle variations to prevent monotony
            if self.variation and loop_count % 4 == 0:
                # Subtle pitch variation (±0.5%)
                variation_factor = 1 + np.random.uniform(-0.005, 0.005)
                segment_to_add = librosa.effects.time_stretch(segment_to_add, rate=variation_factor)

            # Perform spectral crossfade
            crossfaded = self.spectral_crossfade(
                result, segment_to_add, sr, self.crossfade_sec
            )

            # Combine: keep result up to crossfade, add crossfaded region, add rest of segment
            result = np.concatenate([
                result[:-crossfade_samples],
                crossfaded,
                segment_to_add[crossfade_samples:]
            ])

            loop_count += 1
            if verbose and loop_count % 10 == 0:
                print(f"  Progress: {len(result) / sr / 60:.1f} minutes ({loop_count} loops)")

        # Trim to target
        result = result[:target_samples]

        # Normalize to prevent clipping
        result = result / np.max(np.abs(result)) * 0.95

        if verbose:
            print(f"Saving to {output_file}...")
        sf.write(output_file, result, sr)
        if verbose:
            print(f"Done! Created {target_duration_mins} minute seamless loop.")

        return result, sr


if __name__ == "__main__":
    # Example usage
    generator = LongMusicGenerator(crossfade_sec=3.0, variation=True)
    generator.generate(
        "/home/g/gnikesh/projects/lofi-gen/sleep.wav",
        "seamless_audio.wav",
        target_duration_mins=5
    )
    print('Done...')