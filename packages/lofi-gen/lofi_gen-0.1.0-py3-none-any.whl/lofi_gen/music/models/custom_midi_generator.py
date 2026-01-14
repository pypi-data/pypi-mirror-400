#!/usr/bin/env python3
"""
Lofi Music Generator with Nepali/South Asian Scale Support
Generates MIDI, renders to audio, and applies lofi effects
"""

import random
import subprocess
import os
from midiutil import MIDIFile
from pydub import AudioSegment
from pydub.generators import WhiteNoise
import numpy as np
from scipy.io import wavfile
from scipy import signal
import tempfile


# ============================================
# SCALES AND MUSIC THEORY
# ============================================

# Nepali and South Asian inspired scales (MIDI note offsets from root)
SCALES = {
    # Pentatonic scales common in Nepali folk
    'nepali_folk': [0, 2, 4, 7, 9],  # Major pentatonic
    'nepali_minor': [0, 3, 5, 7, 10],  # Minor pentatonic
    
    # Raag-inspired scales
    'bhairav': [0, 1, 4, 5, 7, 8, 11],  # Morning raga
    'yaman': [0, 2, 4, 6, 7, 9, 11],  # Evening raga (Kalyan)
    'khamaj': [0, 2, 4, 5, 7, 9, 10],  # Light classical
    'bhairavi': [0, 1, 3, 5, 7, 8, 10],  # Devotional
    'des': [0, 2, 4, 5, 7, 9, 10],  # Folk-friendly
    
    # Lofi-friendly scales
    'lofi_major': [0, 2, 4, 7, 9],
    'lofi_minor': [0, 3, 5, 7, 10],
    'lofi_dorian': [0, 2, 3, 5, 7, 9, 10],
    'lofi_mixolydian': [0, 2, 4, 5, 7, 9, 10],
}

# Chord progressions (as scale degree offsets)
CHORD_PROGRESSIONS = {
    'lofi_classic': [(0, 'maj7'), (3, 'min7'), (5, 'maj7'), (4, 'min7')],  # I - IV - vi - V
    'jazzy': [(0, 'maj9'), (5, 'min7'), (3, 'dom7'), (4, 'min7')],
    'nepali_folk': [(0, 'maj'), (4, 'min'), (5, 'maj'), (0, 'maj')],
    'melancholic': [(0, 'min7'), (5, 'min7'), (3, 'maj7'), (4, 'dom7')],
    'chill': [(0, 'maj7'), (4, 'min7'), (3, 'min7'), (5, 'maj7')],
}

# Chord voicings (intervals from root)
CHORD_VOICINGS = {
    'maj': [0, 4, 7],
    'min': [0, 3, 7],
    'maj7': [0, 4, 7, 11],
    'min7': [0, 3, 7, 10],
    'dom7': [0, 4, 7, 10],
    'maj9': [0, 4, 7, 11, 14],
    'min9': [0, 3, 7, 10, 14],
    'sus4': [0, 5, 7],
    'add9': [0, 4, 7, 14],
}

# Drum patterns (16th note grid, 1 = hit, 0 = rest)
DRUM_PATTERNS = {
    'lofi_basic': {
        'kick':  [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        'snare': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        'hihat': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    },
    'lofi_swing': {
        'kick':  [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        'snare': [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
        'hihat': [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
    },
    'madal_inspired': {  # Inspired by Nepali madal drum
        'kick':  [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0],
        'snare': [0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],
        'hihat': [1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1],
    },
    'minimal': {
        'kick':  [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        'snare': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        'hihat': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
    },
}


# ============================================
# MELODY GENERATION
# ============================================

class MelodyGenerator:
    def __init__(self, scale_name='nepali_folk', root_note=60, octave_range=2):
        self.scale = SCALES.get(scale_name, SCALES['nepali_folk'])
        self.root = root_note
        self.octave_range = octave_range
        self.notes = self._build_note_pool()
        self.current_note = random.choice(self.notes)
        
    def _build_note_pool(self):
        """Build available notes across octaves"""
        notes = []
        for octave in range(self.octave_range):
            for interval in self.scale:
                notes.append(self.root + interval + (octave * 12))
        return notes
    
    def generate_phrase(self, length=8, rhythm_density=0.7):
        """Generate a melodic phrase with rhythm"""
        phrase = []
        
        for i in range(length):
            # Decide if this beat has a note
            if random.random() < rhythm_density:
                # Prefer stepwise motion
                if random.random() < 0.7:
                    # Move to adjacent scale note
                    current_idx = self.notes.index(self.current_note) if self.current_note in self.notes else 0
                    step = random.choice([-1, 1])
                    new_idx = max(0, min(len(self.notes) - 1, current_idx + step))
                    self.current_note = self.notes[new_idx]
                else:
                    # Jump to random note (weighted towards closer notes)
                    self.current_note = random.choice(self.notes)
                
                # Vary note duration
                duration = random.choice([0.5, 1, 1.5, 2])
                velocity = random.randint(60, 90)
                phrase.append((self.current_note, duration, velocity))
            else:
                # Rest
                phrase.append((None, 1, 0))
        
        return phrase


# ============================================
# MIDI GENERATION
# ============================================

class LofiMidiGenerator:
    def __init__(self, bpm=75, scale='nepali_folk', root='C', progression='lofi_classic'):
        self.bpm = bpm
        self.scale_name = scale
        self.root_note = self._note_to_midi(root, 4)  # Root in octave 4
        self.progression_name = progression
        
        # MIDI setup
        self.midi = MIDIFile(4)  # 4 tracks: melody, chords, bass, drums
        self.midi.addTempo(0, 0, bpm)
        
        # Track names
        self.tracks = {
            'melody': 0,
            'chords': 1,
            'bass': 2,
            'drums': 3,
        }
        
        # GM instruments
        self.instruments = {
            'melody': 4,   # Electric Piano 1
            'chords': 0,   # Acoustic Grand Piano
            'bass': 33,    # Electric Bass (finger)
            'drums': 0,    # Standard drum kit (channel 9)
        }
        
        # Set instruments
        for track_name, track_num in self.tracks.items():
            if track_name != 'drums':
                self.midi.addProgramChange(track_num, track_num, 0, self.instruments[track_name])
    
    def _note_to_midi(self, note_name, octave):
        """Convert note name to MIDI number"""
        notes = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
        base = notes.get(note_name.upper(), 0)
        return base + (octave + 1) * 12
    
    def add_melody(self, bars=8):
        """Add melody track"""
        track = self.tracks['melody']
        channel = 0
        
        melody_gen = MelodyGenerator(
            scale_name=self.scale_name,
            root_note=self.root_note + 12,  # One octave up
            octave_range=2
        )
        
        time = 0
        for bar in range(bars):
            phrase = melody_gen.generate_phrase(length=8, rhythm_density=0.6)
            for note, duration, velocity in phrase:
                if note is not None:
                    # Add slight humanization
                    actual_time = time + random.uniform(-0.02, 0.02)
                    actual_velocity = velocity + random.randint(-5, 5)
                    self.midi.addNote(track, channel, note, max(0, actual_time),
                                     duration, max(40, min(100, actual_velocity)))
                time += duration  # Use actual note duration
    
    def add_chords(self, bars=8):
        """Add chord progression"""
        track = self.tracks['chords']
        channel = 1
        
        progression = CHORD_PROGRESSIONS.get(self.progression_name, CHORD_PROGRESSIONS['lofi_classic'])
        
        time = 0
        for bar in range(bars):
            chord_idx = bar % len(progression)
            degree, chord_type = progression[chord_idx]
            
            # Get chord root from scale
            scale = SCALES.get(self.scale_name, SCALES['nepali_folk'])
            chord_root = self.root_note + scale[degree % len(scale)]
            
            # Build chord
            voicing = CHORD_VOICINGS.get(chord_type, CHORD_VOICINGS['maj7'])
            
            # Add chord notes with slight arpeggio feel
            for i, interval in enumerate(voicing):
                note = chord_root + interval - 12  # One octave down
                # Slight stagger for arpeggio effect
                note_time = time + (i * 0.02)
                velocity = random.randint(50, 70)
                self.midi.addNote(track, channel, note, note_time, 3.8, velocity)
            
            time += 4  # One bar (4 beats)
    
    def add_bass(self, bars=8):
        """Add bass line"""
        track = self.tracks['bass']
        channel = 2
        
        progression = CHORD_PROGRESSIONS.get(self.progression_name, CHORD_PROGRESSIONS['lofi_classic'])
        
        time = 0
        for bar in range(bars):
            chord_idx = bar % len(progression)
            degree, _ = progression[chord_idx]
            
            # Get bass note from scale
            scale = SCALES.get(self.scale_name, SCALES['nepali_folk'])
            bass_note = self.root_note + scale[degree % len(scale)] - 24  # Two octaves down
            
            # Simple bass pattern
            pattern = [
                (0, 1.5, 80),     # Beat 1
                (2, 0.5, 60),     # Beat 3 (pickup)
                (2.5, 1, 70),     # Beat 3.5
            ]
            
            for beat_offset, duration, velocity in pattern:
                vel = velocity + random.randint(-10, 10)
                self.midi.addNote(track, channel, bass_note, time + beat_offset, duration, vel)
            
            time += 4
    
    def add_drums(self, bars=8, pattern_name='lofi_basic'):
        """Add drum track"""
        track = self.tracks['drums']
        channel = 9  # GM drum channel
        
        pattern = DRUM_PATTERNS.get(pattern_name, DRUM_PATTERNS['lofi_basic'])
        
        # GM drum map
        drum_notes = {
            'kick': 36,
            'snare': 38,
            'hihat': 42,
            'hihat_open': 46,
            'rim': 37,
        }
        
        time = 0
        sixteenth = 0.25  # Duration of 16th note
        
        for bar in range(bars):
            for step in range(16):
                for drum, hits in pattern.items():
                    if hits[step]:
                        note = drum_notes.get(drum, 36)
                        velocity = random.randint(70, 100) if drum == 'kick' else random.randint(60, 90)
                        # Add swing feel
                        swing = 0.02 if step % 2 == 1 else 0
                        self.midi.addNote(track, channel, note, time + swing, sixteenth, velocity)
                time += sixteenth
    
    def generate(self, bars=8, drum_pattern='lofi_basic'):
        """Generate complete track"""
        self.add_chords(bars)
        self.add_bass(bars)
        self.add_melody(bars)
        self.add_drums(bars, drum_pattern)
        return self.midi
    
    def save(self, filename):
        """Save MIDI file"""
        with open(filename, 'wb') as f:
            self.midi.writeFile(f)


# ============================================
# AUDIO RENDERING AND LOFI EFFECTS
# ============================================

class LofiEffects:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
    
    def apply_lowpass(self, audio_data, cutoff=4000):
        """Apply low-pass filter for warmth"""
        nyquist = self.sample_rate / 2
        normalized_cutoff = cutoff / nyquist
        b, a = signal.butter(4, normalized_cutoff, btype='low')
        return signal.filtfilt(b, a, audio_data)
    
    def apply_highpass(self, audio_data, cutoff=80):
        """Apply high-pass filter to remove rumble"""
        nyquist = self.sample_rate / 2
        normalized_cutoff = cutoff / nyquist
        b, a = signal.butter(2, normalized_cutoff, btype='high')
        return signal.filtfilt(b, a, audio_data)
    
    def add_vinyl_crackle(self, audio_data, intensity=0.02):
        """Add vinyl crackle noise"""
        noise = np.random.randn(len(audio_data)) * intensity
        # Make it more crackly with sparse pops
        crackle_mask = np.random.random(len(audio_data)) > 0.9998
        pops = np.random.randn(len(audio_data)) * 0.1 * crackle_mask
        return audio_data + noise + pops
    
    def apply_tape_saturation(self, audio_data, drive=0.3):
        """Simulate tape saturation/warmth"""
        # Soft clipping
        return np.tanh(audio_data * (1 + drive)) / (1 + drive * 0.5)
    
    def add_bit_crush(self, audio_data, bits=12):
        """Reduce bit depth for lo-fi character"""
        max_val = 2 ** (bits - 1)
        return np.round(audio_data * max_val) / max_val
    
    def apply_all(self, audio_data, 
                  lowpass_cutoff=5000,
                  vinyl_intensity=0.015,
                  saturation_drive=0.2,
                  bit_depth=14):
        """Apply all lofi effects"""
        # Normalize
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val
        
        # Apply effects chain
        audio_data = self.apply_highpass(audio_data, 60)
        audio_data = self.apply_tape_saturation(audio_data, saturation_drive)
        audio_data = self.apply_lowpass(audio_data, lowpass_cutoff)
        audio_data = self.add_bit_crush(audio_data, bit_depth)
        audio_data = self.add_vinyl_crackle(audio_data, vinyl_intensity)
        
        # Final normalization
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val * 0.9
        
        return audio_data


def render_midi_to_audio(midi_path, output_path, soundfont=None):
    """Render MIDI to WAV using FluidSynth"""
    # Find soundfont if not specified
    if soundfont is None:
        possible_paths = [
            os.path.expanduser('~/soundfonts/MuseScore_General.sf2'),
            os.path.expanduser('~/soundfonts/FluidR3_GM.sf2'),
            '/usr/share/sounds/sf2/FluidR3_GM.sf2',
            '/usr/share/soundfonts/default.sf2',
            '/usr/share/soundfonts/FluidR3_GM.sf2',
        ]
        for path in possible_paths:
            if os.path.exists(path):
                soundfont = path
                break

        if soundfont is None:
            print("ERROR: No soundfont found!")
            print("Please download a soundfont to ~/soundfonts/")
            print("Example: wget https://ftp.osuosl.org/pub/musescore/soundfont/MuseScore_General/MuseScore_General.sf2 -P ~/soundfonts/")
            return False

    # Check if soundfont exists
    if not os.path.exists(soundfont):
        print(f"ERROR: Soundfont not found at {soundfont}")
        return False

    cmd = [
        'fluidsynth',
        '-ni',  # No interactive mode
        '-g', '0.5',  # Gain (reduced to prevent clipping)
        '-r', '44100',  # Sample rate
        '-F', output_path,  # Output file
        soundfont,
        midi_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FluidSynth error: {result.stderr}")
        return False
    return True


def apply_lofi_effects_to_file(input_path, output_path):
    """Apply lofi effects to an audio file"""
    # Read audio
    sample_rate, audio_data = wavfile.read(input_path)

    # Convert to float32 normalized to [-1, 1]
    if audio_data.dtype == np.int16:
        audio_data = audio_data.astype(np.float32) / 32768.0
    elif audio_data.dtype == np.int32:
        audio_data = audio_data.astype(np.float32) / 2147483648.0
    elif audio_data.dtype == np.uint8:
        audio_data = (audio_data.astype(np.float32) - 128) / 128.0
    elif audio_data.dtype in [np.float32, np.float64]:
        audio_data = audio_data.astype(np.float32)
    else:
        print(f"Warning: Unexpected audio dtype {audio_data.dtype}, attempting conversion")
        audio_data = audio_data.astype(np.float32)
        # Normalize to [-1, 1] range
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val

    # Handle stereo
    if len(audio_data.shape) == 2:
        left = audio_data[:, 0]
        right = audio_data[:, 1]

        effects = LofiEffects(sample_rate)
        left = effects.apply_all(left)
        right = effects.apply_all(right)

        audio_data = np.column_stack((left, right))
    else:
        effects = LofiEffects(sample_rate)
        audio_data = effects.apply_all(audio_data)

    # Convert back to int16
    audio_data = np.clip(audio_data, -1.0, 1.0)  # Ensure no overflow
    audio_data = (audio_data * 32767).astype(np.int16)

    # Save
    wavfile.write(output_path, sample_rate, audio_data)


# ============================================
# MAIN GENERATION FUNCTION
# ============================================

def generate_lofi_track(
    output_name='lofi_track',
    bpm=75,
    scale='nepali_folk',
    root='C',
    progression='lofi_classic',
    drum_pattern='lofi_basic',
    bars=16,
    apply_effects=True,
    output_dir='.'
):
    """
    Generate a complete lofi track
    
    Parameters:
    -----------
    output_name : str
        Base name for output files
    bpm : int
        Tempo in beats per minute (60-90 typical for lofi)
    scale : str
        Scale to use. Options: 'nepali_folk', 'nepali_minor', 'bhairav', 
        'yaman', 'khamaj', 'bhairavi', 'des', 'lofi_major', 'lofi_minor',
        'lofi_dorian', 'lofi_mixolydian'
    root : str
        Root note (C, D, E, F, G, A, B)
    progression : str
        Chord progression. Options: 'lofi_classic', 'jazzy', 'nepali_folk',
        'melancholic', 'chill'
    drum_pattern : str
        Drum pattern. Options: 'lofi_basic', 'lofi_swing', 'madal_inspired', 'minimal'
    bars : int
        Number of bars to generate
    apply_effects : bool
        Whether to apply lofi effects
    output_dir : str
        Directory for output files
    
    Returns:
    --------
    str : Path to the generated audio file
    """
    
    os.makedirs(output_dir, exist_ok=True)
    
    midi_path = os.path.join(output_dir, f'{output_name}.mid')
    raw_audio_path = os.path.join(output_dir, f'{output_name}_raw.wav')
    final_audio_path = os.path.join(output_dir, f'{output_name}.wav')
    
    print(f"Generating lofi track...")
    print(f"  Scale: {scale}")
    print(f"  Root: {root}")
    print(f"  BPM: {bpm}")
    print(f"  Progression: {progression}")
    print(f"  Drum pattern: {drum_pattern}")
    print(f"  Bars: {bars}")
    
    # Generate MIDI
    print("\n1. Generating MIDI...")
    generator = LofiMidiGenerator(
        bpm=bpm,
        scale=scale,
        root=root,
        progression=progression
    )
    generator.generate(bars=bars, drum_pattern=drum_pattern)
    generator.save(midi_path)
    print(f"   MIDI saved to: {midi_path}")
    
    # Render to audio
    print("\n2. Rendering audio...")
    if not render_midi_to_audio(midi_path, raw_audio_path):
        print("   ERROR: Failed to render audio")
        return None
    print(f"   Raw audio saved to: {raw_audio_path}")
    
    # Apply effects
    if apply_effects:
        print("\n3. Applying lofi effects...")
        apply_lofi_effects_to_file(raw_audio_path, final_audio_path)
        print(f"   Final audio saved to: {final_audio_path}")
        # Clean up raw file
        os.remove(raw_audio_path)
    else:
        os.rename(raw_audio_path, final_audio_path)
    
    # Calculate duration
    try:
        audio = AudioSegment.from_wav(final_audio_path)
        duration = len(audio) / 1000  # Convert to seconds
        print(f"\n✓ Track generated successfully!")
        print(f"  Duration: {duration:.1f} seconds")
        print(f"  Output: {final_audio_path}")
    except:
        pass
    
    return final_audio_path


# ============================================
# CLI
# ============================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate lofi music with Nepali/South Asian scales')
    parser.add_argument('--output', '-o', default='lofi_track', help='Output filename (without extension)')
    parser.add_argument('--bpm', type=int, default=75, help='Tempo (default: 75)')
    parser.add_argument('--scale', default='nepali_folk', 
                       choices=list(SCALES.keys()),
                       help='Scale to use')
    parser.add_argument('--root', default='C', 
                       choices=['C', 'D', 'E', 'F', 'G', 'A', 'B'],
                       help='Root note')
    parser.add_argument('--progression', default='lofi_classic',
                       choices=list(CHORD_PROGRESSIONS.keys()),
                       help='Chord progression')
    parser.add_argument('--drums', default='lofi_basic',
                       choices=list(DRUM_PATTERNS.keys()),
                       help='Drum pattern')
    parser.add_argument('--bars', type=int, default=16, help='Number of bars (default: 16)')
    parser.add_argument('--no-effects', action='store_true', help='Skip lofi effects')
    parser.add_argument('--output-dir', default='.', help='Output directory')
    
    args = parser.parse_args()
    
    generate_lofi_track(
        output_name=args.output,
        bpm=args.bpm,
        scale=args.scale,
        root=args.root,
        progression=args.progression,
        drum_pattern=args.drums,
        bars=args.bars,
        apply_effects=not args.no_effects,
        output_dir=args.output_dir
    )
