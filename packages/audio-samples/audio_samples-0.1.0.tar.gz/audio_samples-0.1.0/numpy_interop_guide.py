#!/usr/bin/env python3
"""
AudioSamples + Numpy: Quick Start Guide

This file provides a concise introduction to using AudioSamples with numpy arrays,
perfect for users migrating from traditional Python audio workflows.
"""

import numpy as np
import audio_samples as aus


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")


def main():
    """Quick start guide for numpy interoperability."""
    print("🎵 AudioSamples + Numpy Quick Start Guide")

    print_header("1. BASIC OPERATIONS")

    # Create audio
    audio = aus.generation.sine_wave(440.0, 1.0, sample_rate=44100)
    print(f"Created audio: {audio.channels} channel, {len(audio)} samples")

    # Create numpy arrays
    gain = np.full(len(audio), 0.5)
    fade_in = np.linspace(0, 1, len(audio))

    # Direct operations
    gained = audio * gain        # Gain control
    faded = audio * fade_in      # Fade in
    scaled = audio * 0.5         # Scalar gain

    print("✓ AudioSamples * numpy array (gain)")
    print("✓ AudioSamples * numpy array (fade)")
    print("✓ AudioSamples * scalar (gain)")

    print_header("2. TRADITIONAL WORKFLOW MIGRATION")

    # Traditional workflow:
    # data, sr = soundfile.read("audio.wav")
    # Simulate this:
    duration = 1.0
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    traditional_data = 0.7 * np.sin(2 * np.pi * 440 * t)

    # Convert to AudioSamples (preserves metadata!)
    audio = aus.AudioSamples.new_mono(traditional_data, sample_rate)

    # Apply traditional numpy processing
    window = np.hanning(len(audio))
    windowed = audio * window

    # Chain operations
    processed = windowed * 0.8  # Gain

    print(f"✓ Migrated traditional workflow")
    print(f"  Original: numpy {traditional_data.shape} -> AudioSamples {audio.channels}ch")

    print_header("3. IN-PLACE OPERATIONS")

    audio_copy = aus.generation.sine_wave(220.0, 0.5, sample_rate=44100)
    gain_curve = np.linspace(0.2, 1.0, len(audio_copy))

    # Memory efficient in-place operations
    audio_copy *= gain_curve     # In-place gain curve
    offset_array = np.full(len(audio_copy), 0.05)
    audio_copy += offset_array   # In-place DC bias

    print("✓ In-place *= with numpy array")
    print("✓ In-place += with numpy array")

    print_header("4. MULTI-CHANNEL PROCESSING")

    # Create stereo audio
    mono = aus.generation.sine_wave(440.0, 0.5, sample_rate=44100)
    mono_data = mono.to_numpy()
    stereo_data = np.vstack([mono_data, mono_data * 0.7])  # Left + quieter right
    stereo = aus.AudioSamples.new_multi(stereo_data, sample_rate=44100)

    # Channel-specific processing
    left_gain = np.ones(stereo.samples_per_channel()) * 1.0
    right_gain = np.ones(stereo.samples_per_channel()) * 0.5
    channel_gains = np.vstack([left_gain, right_gain])

    processed_stereo = stereo * channel_gains

    print(f"✓ Stereo processing: {processed_stereo.channels} channels")

    print_header("MIGRATION CHECKLIST")
    print("For existing numpy-based audio code:")
    print("1. ✓ Replace: data, sr = soundfile.read()")
    print("   With: audio = AudioSamples.new_mono(data, sr)")
    print("2. ✓ Keep all your numpy operations: audio * gain_array")
    print("3. ✓ Use in-place operations for efficiency: audio *= gain_array")
    print("4. ✓ Access numpy data anytime: data = audio.to_numpy()")
    print("5. ✓ Enjoy metadata preservation and type safety!")

    print(f"\n🎯 Result: Your existing numpy audio code works with minimal changes!")
    print(f"🚀 Plus you get: metadata tracking, type safety, and audio-specific methods!")


if __name__ == "__main__":
    main()