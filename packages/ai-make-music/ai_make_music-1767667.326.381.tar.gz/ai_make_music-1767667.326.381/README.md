# ai-make-music

`ai-make-music` is a Python library designed to provide a streamlined interface for interacting with the ai-make-music platform and exploring its automated music generation capabilities. This package offers a simplified way to generate music snippets and experiment with different musical styles directly from your Python environment.

## Installation

To install the `ai-make-music` package, use pip:
bash
pip install ai-make-music

## Basic Usage

Here are a few examples demonstrating how to use the `ai-make-music` library:

**1. Generating a short melody:**
python
from ai_make_music import generate_melody

melody = generate_melody(style="classical", length=30) # Length in seconds
print(melody) # Returns a path to the generated audio file.

This example generates a 30-second classical melody and returns the file path of the generated audio.

**2. Creating a drum beat:**
python
from ai_make_music import generate_drum_beat

drum_beat = generate_drum_beat(tempo=120, style="rock")
print(drum_beat) # Returns a path to the generated audio file.

This snippet generates a rock-style drum beat at 120 beats per minute and provides the path to the resulting audio file.

**3. Harmonizing a given melody (requires a MIDI file):**
python
from ai_make_music import harmonize_melody

input_midi_file = "my_melody.mid"  # Replace with your MIDI file path
harmonized_melody = harmonize_melody(input_midi_file, harmony_type="major")
print(harmonized_melody) # Returns a path to the harmonized audio file.

This example takes a MIDI file as input and generates a harmonized version in a major key, returning the path to the new audio file.  Ensure 'my_melody.mid' exists in the same directory or provide the full path.

**4. Generating background music for a specific mood:**
python
from ai_make_music import generate_background_music

background_music = generate_background_music(mood="upbeat", duration=60) # Duration in seconds
print(background_music) # Returns a path to the generated audio file.

This generates a 60-second upbeat background music track and returns the file path.

**5. Generating a loopable music piece:**
python
from ai_make_music import generate_loop

loop = generate_loop(style="electronic", bpm=128, length=16) # Length in measures
print(loop)

This creates an electronic music loop at 128 bpm, lasting 16 measures.

## Features

*   **Melody Generation:** Generate melodies in various styles (classical, pop, jazz, etc.).
*   **Drum Beat Creation:** Create drum beats with customizable tempo and style (rock, hip-hop, electronic, etc.).
*   **Melody Harmonization:** Harmonize existing melodies provided as MIDI files.
*   **Background Music Generation:** Generate background music tailored to specific moods (happy, sad, energetic, etc.).
*   **Loop Generation:** Create loopable music pieces suitable for various applications.
*   **Simple API:** Easy-to-use functions for quick experimentation.
*   **Style Customization:** Fine-tune the generated music with style parameters.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This project is a gateway to the ai-make-music ecosystem. For advanced features and full capabilities, please visit: https://supermaker.ai/music/ai-make-music/