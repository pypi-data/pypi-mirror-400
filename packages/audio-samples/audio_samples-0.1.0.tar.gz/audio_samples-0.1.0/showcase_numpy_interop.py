#!/usr/bin/env python3
"""
AudioSamples Numpy Interoperability Showcase

This file demonstrates the comprehensive numpy array integration capabilities
of the AudioSamples Python library, showcasing the enhanced ergonomics for
traditional Python audio workflows.

Features Demonstrated:
- Element-wise arithmetic operations with numpy arrays
- In-place operations for performance-critical code
- Multi-channel audio processing with numpy arrays
- Traditional soundfile.read() workflow migration
- Complex audio processing chains using numpy operations
- Type safety and error handling
- Performance comparisons and benchmarks
"""

import numpy as np
import audio_samples as aus
import time
from typing import Tuple, List
import matplotlib.pyplot as plt


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_subsection(title: str) -> None:
    """Print a formatted subsection header."""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")


def demonstrate_basic_operations():
    """Demonstrate basic arithmetic operations between AudioSamples and numpy arrays."""
    print_section("BASIC NUMPY ARRAY OPERATIONS")

    # Create a test audio signal
    audio = aus.generation.sine_wave(440.0, 0.5, sample_rate=44100)
    print(f"Created AudioSamples: {audio.channels} channel(s), {len(audio)} samples, {audio.sample_rate} Hz")

    # Create numpy arrays for operations
    gain_array = np.ones(len(audio)) * 0.5
    fade_in = np.linspace(0, 1, len(audio))
    fade_out = np.linspace(1, 0, len(audio))

    print_subsection("Element-wise Operations")

    # Addition
    print("✓ AudioSamples + numpy array (DC offset)")
    dc_offset = np.full(len(audio), 0.1)
    offset_audio = audio + dc_offset
    print(f"  Original mean: {np.mean(audio.to_numpy()):.6f}")
    print(f"  With offset:   {np.mean(offset_audio.to_numpy()):.6f}")

    # Multiplication (gain)
    print("\n✓ AudioSamples * numpy array (variable gain)")
    gained_audio = audio * gain_array
    print(f"  Original peak: {np.max(np.abs(audio.to_numpy())):.6f}")
    print(f"  Gained peak:   {np.max(np.abs(gained_audio.to_numpy())):.6f}")

    # Subtraction
    print("\n✓ AudioSamples - numpy array (DC removal)")
    dc_removed = offset_audio - dc_offset
    print(f"  After DC removal: {np.mean(dc_removed.to_numpy()):.6f}")

    # Division
    print("\n✓ AudioSamples / numpy array (normalization)")
    normalization_factor = np.full(len(audio), 2.0)
    normalized = gained_audio / normalization_factor
    print(f"  Normalized peak: {np.max(np.abs(normalized.to_numpy())):.6f}")

    print_subsection("Complex Processing Chains")

    # Demonstrate chaining operations
    print("Chaining multiple numpy operations:")
    print("  1. Apply fade-in envelope")
    print("  2. Apply variable gain")
    print("  3. Apply fade-out envelope")

    processed = audio * fade_in * gain_array * fade_out
    print(f"  Final peak amplitude: {np.max(np.abs(processed.to_numpy())):.6f}")
    print(f"  Result type: {type(processed)}")

    return audio, processed


def demonstrate_inplace_operations():
    """Demonstrate in-place operations for memory-efficient processing."""
    print_section("IN-PLACE OPERATIONS (MEMORY EFFICIENT)")

    # Create test audio
    audio = aus.generation.sine_wave(220.0, 0.3, sample_rate=44100)
    original_id = id(audio)

    print(f"Original AudioSamples ID: {original_id}")
    print(f"Original peak: {np.max(np.abs(audio.to_numpy())):.6f}")

    print_subsection("In-place Arithmetic with Numpy Arrays")

    # In-place addition
    dc_bias = np.full(len(audio), 0.05)
    audio += dc_bias
    print(f"✓ After += numpy array: peak = {np.max(np.abs(audio.to_numpy())):.6f}")

    # In-place multiplication
    gain = np.full(len(audio), 0.8)
    audio *= gain
    print(f"✓ After *= numpy array: peak = {np.max(np.abs(audio.to_numpy())):.6f}")

    # In-place subtraction
    audio -= dc_bias
    print(f"✓ After -= numpy array: peak = {np.max(np.abs(audio.to_numpy())):.6f}")

    # In-place division
    boost = np.full(len(audio), 0.8)  # Effectively multiply by 1/0.8 = 1.25
    audio /= boost
    print(f"✓ After /= numpy array: peak = {np.max(np.abs(audio.to_numpy())):.6f}")

    print(f"\nFinal AudioSamples ID: {id(audio)} (same object: {id(audio) == original_id})")


def demonstrate_multichannel_processing():
    """Demonstrate multi-channel audio processing with numpy arrays."""
    print_section("MULTI-CHANNEL AUDIO PROCESSING")

    # Create stereo audio manually
    left_channel = aus.generation.sine_wave(440.0, 1.0, sample_rate=44100)
    right_channel = aus.generation.sine_wave(660.0, 1.0, sample_rate=44100)  # Perfect fifth

    # Combine into stereo
    left_data = left_channel.to_numpy()
    right_data = right_channel.to_numpy()
    stereo_data = np.vstack([left_data, right_data])
    stereo_audio = aus.AudioSamples.new_multi(stereo_data, sample_rate=44100)

    print(f"Created stereo audio: {stereo_audio.channels} channels, {stereo_audio.samples_per_channel()} samples")

    print_subsection("Channel-specific Processing")

    # Create different processing for each channel
    num_samples = stereo_audio.samples_per_channel()

    # Left channel: fade in
    # Right channel: fade out
    fade_in = np.linspace(0, 1, num_samples)
    fade_out = np.linspace(1, 0, num_samples)

    # Create 2D processing array
    channel_processing = np.vstack([fade_in, fade_out])

    processed_stereo = stereo_audio * channel_processing

    print(f"✓ Applied fade-in to left, fade-out to right")
    print(f"  Left channel final amplitude: {processed_stereo.to_numpy()[0, -1]:.6f}")
    print(f"  Right channel final amplitude: {processed_stereo.to_numpy()[1, -1]:.6f}")

    print_subsection("Stereo Effects with Numpy")

    # Stereo width effect
    width_factor = 1.5
    mid = (left_data + right_data) / 2
    side = (left_data - right_data) / 2

    # Apply width
    wide_side = side * width_factor
    wide_left = mid + wide_side
    wide_right = mid - wide_side

    wide_stereo_data = np.vstack([wide_left, wide_right])
    wide_stereo = aus.AudioSamples.new_multi(wide_stereo_data, sample_rate=44100)

    # Apply to our audio using numpy operations
    stereo_matrix = np.array([[0.5, 0.5], [1.5, -1.5]]) @ stereo_data
    processed_wide = aus.AudioSamples.new_multi(stereo_matrix, sample_rate=44100)

    print(f"✓ Applied stereo width effect")
    print(f"  Stereo correlation: {np.corrcoef(processed_wide.to_numpy())[0,1]:.6f}")

    return stereo_audio, processed_stereo


def demonstrate_traditional_workflow():
    """Demonstrate traditional Python audio workflow integration."""
    print_section("TRADITIONAL WORKFLOW INTEGRATION")

    print("Simulating traditional soundfile.read() workflow...")

    # Simulate what you'd get from soundfile.read()
    sample_rate = 48000
    duration = 2.0
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)

    # Complex signal: fundamental + harmonics + noise
    fundamental = 0.7 * np.sin(2 * np.pi * 262 * t)  # C4
    harmonic2 = 0.3 * np.sin(2 * np.pi * 524 * t)    # C5
    harmonic3 = 0.15 * np.sin(2 * np.pi * 786 * t)   # G5
    noise = 0.02 * np.random.randn(num_samples)

    # Traditional format: mono signal as 1D array
    traditional_data = fundamental + harmonic2 + harmonic3 + noise

    print(f"✓ Simulated soundfile.read(): shape={traditional_data.shape}, dtype={traditional_data.dtype}")

    print_subsection("Migration to AudioSamples")

    # Convert to AudioSamples (zero-copy when possible)
    audio = aus.AudioSamples.new_mono(traditional_data.astype(np.float64), sample_rate)
    print(f"✓ Converted to AudioSamples: {audio.channels} ch, {audio.sample_rate} Hz")

    print_subsection("Traditional Audio Processing with Numpy")

    # 1. Apply window function (traditional numpy operation)
    window = np.hanning(len(traditional_data))
    windowed_audio = audio * window
    print("✓ Applied Hanning window")

    # 2. High-pass filter effect using numpy diff
    highpass_kernel = np.array([1, -1]) / 2
    # Simulate convolution effect with numpy operations
    original_data = audio.to_numpy()
    diff_signal = np.diff(original_data, prepend=0) * 0.5

    # Mix original with filtered signal
    filtered_data = original_data + diff_signal
    filtered_audio = aus.AudioSamples.new_mono(filtered_data, sample_rate)
    print("✓ Applied simple high-pass effect")

    # 3. Dynamic range compression (traditional approach)
    audio_data = filtered_audio.to_numpy()
    threshold = 0.5
    ratio = 4.0

    # Compression curve using numpy
    magnitude = np.abs(audio_data)
    compressed_magnitude = np.where(
        magnitude > threshold,
        threshold + (magnitude - threshold) / ratio,
        magnitude
    )

    # Apply compression with original phase
    compression_factor = np.divide(
        compressed_magnitude,
        magnitude,
        out=np.ones_like(magnitude),
        where=(magnitude != 0)
    )

    compressed_audio = audio * compression_factor
    print(f"✓ Applied compression (threshold={threshold}, ratio={ratio})")

    # 4. Normalize to target level
    target_level = 0.8
    current_peak = np.max(np.abs(compressed_audio.to_numpy()))
    normalization_gain = np.full(len(compressed_audio), target_level / current_peak)

    final_audio = compressed_audio * normalization_gain
    print(f"✓ Normalized to {target_level} peak level")

    print_subsection("Processing Chain Summary")
    original_peak = np.max(np.abs(audio.to_numpy()))
    final_peak = np.max(np.abs(final_audio.to_numpy()))
    original_rms = np.sqrt(np.mean(audio.to_numpy() ** 2))
    final_rms = np.sqrt(np.mean(final_audio.to_numpy() ** 2))

    print(f"Original - Peak: {original_peak:.6f}, RMS: {original_rms:.6f}")
    print(f"Final    - Peak: {final_peak:.6f}, RMS: {final_rms:.6f}")
    print(f"Dynamic range change: {20 * np.log10(final_rms / original_rms):.2f} dB")

    return audio, final_audio


def demonstrate_advanced_effects():
    """Demonstrate advanced audio effects using numpy integration."""
    print_section("ADVANCED EFFECTS WITH NUMPY INTEGRATION")

    # Create a test signal
    audio = aus.generation.sine_wave(440.0, 1.0, sample_rate=44100)

    print_subsection("Tremolo Effect")

    # Tremolo: amplitude modulation
    tremolo_rate = 5  # Hz
    tremolo_depth = 0.5
    t = np.linspace(0, 1.0, len(audio))
    tremolo_lfo = 1 - tremolo_depth * (1 + np.sin(2 * np.pi * tremolo_rate * t)) / 2

    tremolo_audio = audio * tremolo_lfo
    print(f"✓ Applied tremolo: {tremolo_rate} Hz, {tremolo_depth*100}% depth")

    print_subsection("Chorus Effect (Simplified)")

    # Simple chorus: mix original with delayed and modulated versions
    delay_samples = int(0.02 * 44100)  # 20ms delay

    # Create delayed version (simplified - just numpy roll)
    delayed_data = np.roll(audio.to_numpy(), delay_samples)
    delayed_data[:delay_samples] = 0  # Clear the wrapped portion

    # Slight pitch modulation using interpolation
    lfo_rate = 0.5  # Hz
    lfo_depth = 0.001  # Very slight
    lfo = lfo_depth * np.sin(2 * np.pi * lfo_rate * t)

    # Create modulated delay (simplified approach)
    modulated_delay = aus.AudioSamples.new_mono(delayed_data, 44100)

    # Mix: 70% original, 30% delayed (using numpy arrays to avoid mixed backing issue)
    original_data = audio.to_numpy()
    delayed_data = modulated_delay.to_numpy()

    chorus_data = original_data * 0.7 + delayed_data * 0.3
    chorus_audio = aus.AudioSamples.new_mono(chorus_data, 44100)

    print(f"✓ Applied chorus effect with {delay_samples/44100*1000:.1f}ms delay")

    print_subsection("Distortion/Saturation")

    # Soft clipping distortion
    drive = 3.0
    driven_signal = audio.to_numpy() * drive

    # Tanh saturation
    saturated = np.tanh(driven_signal) / np.tanh(drive)
    distorted_audio = aus.AudioSamples.new_mono(saturated, 44100)

    print(f"✓ Applied tanh saturation with {drive}x drive")

    print_subsection("Frequency-dependent Processing")

    # Simple spectral tilt using numpy operations
    # High frequencies get boosted, low frequencies get attenuated

    # Create frequency-dependent gain curve
    freq_response = np.linspace(0.5, 2.0, len(audio))  # Low to high gain

    # Apply spectral tilt (simplified - not actual frequency domain)
    # This is just a demonstration of the concept
    tilted_audio = audio * freq_response

    print("✓ Applied spectral tilt (conceptual)")

    return {
        'tremolo': tremolo_audio,
        'chorus': chorus_audio,
        'distortion': distorted_audio,
        'tilt': tilted_audio
    }


def demonstrate_performance_comparison():
    """Compare performance between different processing approaches."""
    print_section("PERFORMANCE COMPARISON")

    # Create larger audio for meaningful benchmarks
    large_audio = aus.generation.sine_wave(440.0, 10.0, sample_rate=44100)  # 10 seconds
    large_numpy = large_audio.to_numpy().copy()

    print(f"Benchmark audio: {len(large_audio)} samples ({len(large_audio)/44100:.1f} seconds)")

    print_subsection("Gain Application Benchmark")

    gain = 0.75

    # Method 1: Pure numpy
    start_time = time.perf_counter()
    numpy_result = large_numpy * gain
    numpy_time = time.perf_counter() - start_time

    # Method 2: AudioSamples with scalar
    start_time = time.perf_counter()
    scalar_result = large_audio * gain
    scalar_time = time.perf_counter() - start_time

    # Method 3: AudioSamples with numpy array
    gain_array = np.full(len(large_audio), gain)
    start_time = time.perf_counter()
    array_result = large_audio * gain_array
    array_time = time.perf_counter() - start_time

    print(f"Pure numpy:           {numpy_time*1000:.2f} ms")
    print(f"AudioSamples scalar:  {scalar_time*1000:.2f} ms")
    print(f"AudioSamples + array: {array_time*1000:.2f} ms")

    print_subsection("Complex Processing Chain Benchmark")

    # Create processing arrays
    fade_in = np.linspace(0, 1, len(large_audio))
    fade_out = np.linspace(1, 0, len(large_audio))
    gain_curve = 0.5 + 0.5 * np.sin(np.linspace(0, 4*np.pi, len(large_audio)))

    # Method 1: Pure numpy
    start_time = time.perf_counter()
    numpy_chain = large_numpy * fade_in * fade_out * gain_curve
    numpy_chain_time = time.perf_counter() - start_time

    # Method 2: AudioSamples chained operations
    start_time = time.perf_counter()
    audio_chain = large_audio * fade_in * fade_out * gain_curve
    audio_chain_time = time.perf_counter() - start_time

    print(f"Pure numpy chain:     {numpy_chain_time*1000:.2f} ms")
    print(f"AudioSamples chain:   {audio_chain_time*1000:.2f} ms")
    print(f"Overhead ratio:       {audio_chain_time/numpy_chain_time:.2f}x")

    # Verify results are equivalent
    result_diff = np.max(np.abs(audio_chain.to_numpy() - numpy_chain))
    print(f"Max difference:       {result_diff:.2e}")

    return {
        'numpy_time': numpy_time,
        'scalar_time': scalar_time,
        'array_time': array_time,
        'overhead': array_time / numpy_time
    }


def demonstrate_error_handling():
    """Demonstrate error handling and type safety."""
    print_section("ERROR HANDLING & TYPE SAFETY")

    audio = aus.generation.sine_wave(440.0, 0.5, sample_rate=44100)

    print_subsection("Shape Compatibility")

    # Compatible array
    compatible = np.ones(len(audio)) * 0.5
    try:
        result = audio * compatible
        print(f"✓ Compatible shape {compatible.shape}: SUCCESS")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Incompatible array
    incompatible = np.ones(len(audio) + 100)
    try:
        result = audio * incompatible
        print(f"✓ Incompatible shape {incompatible.shape}: UNEXPECTED SUCCESS")
    except Exception as e:
        print(f"✓ Incompatible shape {incompatible.shape}: Correctly rejected - {type(e).__name__}")

    print_subsection("Division by Zero Protection")

    # Safe division
    safe_divisor = np.ones(len(audio)) * 2.0
    try:
        result = audio / safe_divisor
        print(f"✓ Safe division: SUCCESS")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    # Division by zero
    zero_divisor = np.zeros(len(audio))
    try:
        result = audio / zero_divisor
        print(f"✗ Division by zero: UNEXPECTED SUCCESS")
    except Exception as e:
        print(f"✓ Division by zero: Correctly rejected - {type(e).__name__}")

    print_subsection("Type Compatibility")

    # Test different numpy dtypes
    dtypes_to_test = [np.int16, np.int32, np.float32, np.float64]

    for dtype in dtypes_to_test:
        test_array = np.ones(len(audio), dtype=dtype) * 0.5
        try:
            result = audio * test_array
            print(f"✓ {dtype.__name__:8}: SUCCESS")
        except Exception as e:
            print(f"✗ {dtype.__name__:8}: {type(e).__name__}")

    # Invalid types
    try:
        result = audio + "invalid"
        print("✗ String operand: UNEXPECTED SUCCESS")
    except Exception as e:
        print(f"✓ String operand: Correctly rejected - {type(e).__name__}")

    try:
        result = audio + [1, 2, 3]
        print("✗ List operand: UNEXPECTED SUCCESS")
    except Exception as e:
        print(f"✓ List operand: Correctly rejected - {type(e).__name__}")


def demonstrate_real_world_example():
    """Demonstrate a complete real-world audio processing example."""
    print_section("REAL-WORLD EXAMPLE: PODCAST POST-PROCESSING")

    print("Simulating podcast audio post-processing pipeline...")

    # Simulate "loaded" podcast audio (voice with some noise)
    sample_rate = 44100
    duration = 5.0
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Voice-like signal: lower frequency content
    voice_fundamental = np.sin(2 * np.pi * 200 * t)  # 200 Hz fundamental
    voice_formant1 = 0.6 * np.sin(2 * np.pi * 800 * t)  # First formant
    voice_formant2 = 0.3 * np.sin(2 * np.pi * 1500 * t)  # Second formant

    # Add some amplitude variation (speech dynamics)
    speech_envelope = 0.7 + 0.3 * np.sin(2 * np.pi * 3 * t) * np.sin(2 * np.pi * 0.5 * t)

    # Background noise
    noise = 0.05 * np.random.randn(len(t))

    # Room tone / hum
    hum = 0.03 * np.sin(2 * np.pi * 60 * t)  # 60 Hz hum

    # Combine signal
    raw_audio_data = (voice_fundamental + voice_formant1 + voice_formant2) * speech_envelope + noise + hum

    # Convert to AudioSamples
    raw_audio = aus.AudioSamples.new_mono(raw_audio_data, sample_rate)

    print(f"✓ Created simulated podcast audio: {duration}s at {sample_rate} Hz")
    print(f"  Raw audio peak: {np.max(np.abs(raw_audio.to_numpy())):.3f}")

    print_subsection("Step 1: Noise Gate")

    # Simple noise gate using numpy
    gate_threshold = 0.1
    gate_ratio = 10.0

    audio_magnitude = np.abs(raw_audio.to_numpy())
    gate_gain = np.where(
        audio_magnitude > gate_threshold,
        1.0,
        1.0 / gate_ratio
    )

    gated_audio = raw_audio * gate_gain
    noise_reduction_db = 20 * np.log10(1.0 / gate_ratio)
    print(f"✓ Applied noise gate: {noise_reduction_db:.1f} dB noise reduction")

    print_subsection("Step 2: High-pass Filter (Rumble Removal)")

    # Simple high-pass effect using numpy diff
    highpass_strength = 0.3
    gated_data = gated_audio.to_numpy()
    diff_signal = np.diff(gated_data, prepend=0)

    # Mix original with highpassed signal
    filtered_data = gated_data * (1 - highpass_strength) + diff_signal * highpass_strength
    filtered_audio = aus.AudioSamples.new_mono(filtered_data, sample_rate)
    print(f"✓ Applied high-pass filter for rumble removal")

    print_subsection("Step 3: Compression")

    # Multi-band compression simulation (simplified to single band)
    threshold = 0.3
    ratio = 3.0
    attack_time = 0.003  # 3ms
    release_time = 0.1   # 100ms

    # Simple peak detection and gain reduction
    audio_data = filtered_audio.to_numpy()
    peak_magnitude = np.abs(audio_data)

    # Compression curve
    compressed_magnitude = np.where(
        peak_magnitude > threshold,
        threshold + (peak_magnitude - threshold) / ratio,
        peak_magnitude
    )

    # Apply compression
    compression_gain = np.divide(
        compressed_magnitude,
        peak_magnitude,
        out=np.ones_like(peak_magnitude),
        where=(peak_magnitude != 0)
    )

    compressed_audio = filtered_audio * compression_gain
    print(f"✓ Applied compression: {ratio}:1 ratio, {threshold} threshold")

    print_subsection("Step 4: EQ (Presence Boost)")

    # Simulate presence boost around 2-5 kHz (voice clarity)
    # Using a simple gain curve
    eq_boost = 1.2
    eq_curve = 1.0 + 0.2 * np.sin(np.linspace(0, 2*np.pi, len(compressed_audio)))  # Simplified EQ curve

    eq_audio = compressed_audio * eq_curve
    print(f"✓ Applied presence EQ boost")

    print_subsection("Step 5: Limiting and Normalization")

    # Soft limiting
    limit_threshold = 0.85
    audio_data = eq_audio.to_numpy()
    limited_data = np.tanh(audio_data / limit_threshold) * limit_threshold
    limited_audio = aus.AudioSamples.new_mono(limited_data, sample_rate)

    # Normalize to target level
    target_lufs = 0.7  # Simplified target level
    current_rms = np.sqrt(np.mean(limited_audio.to_numpy() ** 2))
    normalization_gain = np.full(len(limited_audio), target_lufs / current_rms)

    final_audio = limited_audio * normalization_gain

    print(f"✓ Applied limiting and normalization")
    print(f"  Target level: {target_lufs}")
    print(f"  Normalization gain: {20*np.log10(target_lufs/current_rms):.1f} dB")

    print_subsection("Processing Summary")

    # Calculate processing metrics
    original_peak = np.max(np.abs(raw_audio.to_numpy()))
    final_peak = np.max(np.abs(final_audio.to_numpy()))
    original_rms = np.sqrt(np.mean(raw_audio.to_numpy() ** 2))
    final_rms = np.sqrt(np.mean(final_audio.to_numpy() ** 2))

    print(f"Original audio:")
    print(f"  Peak: {original_peak:.3f} ({20*np.log10(original_peak):.1f} dBFS)")
    print(f"  RMS:  {original_rms:.3f} ({20*np.log10(original_rms):.1f} dBFS)")

    print(f"Processed audio:")
    print(f"  Peak: {final_peak:.3f} ({20*np.log10(final_peak):.1f} dBFS)")
    print(f"  RMS:  {final_rms:.3f} ({20*np.log10(final_rms):.1f} dBFS)")

    print(f"Changes:")
    print(f"  RMS change: {20*np.log10(final_rms/original_rms):.1f} dB")
    print(f"  Dynamic range: {20*np.log10(final_peak/final_rms) - 20*np.log10(original_peak/original_rms):.1f} dB")

    return raw_audio, final_audio


def main():
    """Main showcase function."""
    print("🎵 AudioSamples Numpy Interoperability Showcase 🎵")
    print("=" * 60)
    print("Demonstrating comprehensive numpy array integration for AudioSamples")
    print("Perfect for traditional Python audio workflows and advanced processing")

    try:
        # Run all demonstrations
        demonstrate_basic_operations()
        demonstrate_inplace_operations()
        demonstrate_multichannel_processing()
        demonstrate_traditional_workflow()
        demonstrate_advanced_effects()
        performance_results = demonstrate_performance_comparison()
        demonstrate_error_handling()
        demonstrate_real_world_example()

        # Final summary
        print_section("SHOWCASE COMPLETE")
        print("✅ All demonstrations completed successfully!")
        print("\n🎯 Key Takeaways:")
        print("   • Seamless integration with numpy arrays")
        print("   • Full support for traditional Python audio workflows")
        print("   • Element-wise operations with multi-channel audio")
        print("   • Memory-efficient in-place operations")
        print("   • Comprehensive error handling and type safety")
        print(f"   • Performance overhead: {performance_results['overhead']:.2f}x vs pure numpy")
        print("\n🚀 AudioSamples + Numpy = Powerful Audio Processing!")

    except Exception as e:
        print(f"\n❌ Error during showcase: {e}")
        raise


if __name__ == "__main__":
    main()