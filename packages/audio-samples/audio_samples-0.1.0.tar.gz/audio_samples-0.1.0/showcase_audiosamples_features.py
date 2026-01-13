#!/usr/bin/env python3
"""
AudioSamples Advanced Features Showcase

This showcase demonstrates the unique capabilities of AudioSamples that go far beyond
basic numpy array operations, highlighting professional audio processing features,
type safety, metadata preservation, and audio-specific functionality.
"""

import numpy as np
import audio_samples as aus


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_subheader(title: str):
    """Print a formatted subheader."""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")


def main():
    """Comprehensive showcase of AudioSamples advanced features."""
    print("🎵 AudioSamples Advanced Features Showcase")
    print("Professional audio processing capabilities beyond numpy")

    # Create test audio for demonstrations
    sample_rate = 44100
    duration = 1.0

    print_header("1. ADVANCED AUDIO GENERATION")

    # Built-in signal generators with perfect frequency precision
    print_subheader("Professional Waveform Generation")

    print("```python")
    print("# Professional signal generators with precise frequency control")
    print("sine = aus.generation.sine_wave(440.0, duration, sample_rate)")
    print("cosine = aus.generation.cosine_wave(880.0, duration, sample_rate)")
    print("sawtooth = aus.generation.sawtooth_wave(220.0, duration, sample_rate)")
    print("square = aus.generation.square_wave(110.0, duration, sample_rate)")
    print("triangle = aus.generation.triangle_wave(660.0, duration, sample_rate)")
    print("chirp = aus.generation.chirp(100.0, 2000.0, duration, sample_rate)")
    print("```")

    sine = aus.generation.sine_wave(440.0, duration, sample_rate)
    cosine = aus.generation.cosine_wave(880.0, duration, sample_rate)
    sawtooth = aus.generation.sawtooth_wave(220.0, duration, sample_rate)
    square = aus.generation.square_wave(110.0, duration, sample_rate)
    triangle = aus.generation.triangle_wave(660.0, duration, sample_rate)
    chirp = aus.generation.chirp(100.0, 2000.0, duration, sample_rate)

    print(f"✓ Sine wave: {sine.sample_rate}Hz, {sine.duration_seconds:.3f}s")
    print(f"✓ Cosine wave: {cosine.sample_rate}Hz, {cosine.duration_seconds:.3f}s")
    print(f"✓ Sawtooth wave: {sawtooth.sample_rate}Hz, {sawtooth.duration_seconds:.3f}s")
    print(f"✓ Square wave: {square.sample_rate}Hz, {square.duration_seconds:.3f}s")
    print(f"✓ Triangle wave: {triangle.sample_rate}Hz, {triangle.duration_seconds:.3f}s")
    print(f"✓ Frequency chirp: {chirp.sample_rate}Hz, {chirp.duration_seconds:.3f}s")

    # Noise generation with professional algorithms
    print_subheader("Professional Noise Generation")

    print("```python")
    print("# Professional noise generators for audio testing")
    print("white = aus.generation.white_noise(duration, sample_rate)")
    print("pink = aus.generation.pink_noise(duration, sample_rate)")
    print("brown = aus.generation.brown_noise(duration, sample_rate)")
    print("impulse = aus.generation.impulse(100, sample_rate)  # 100ms impulse")
    print("silence = aus.generation.silence(duration, sample_rate)")
    print("```")

    white = aus.generation.white_noise(duration, sample_rate)
    pink = aus.generation.pink_noise(duration, sample_rate)
    brown = aus.generation.brown_noise(duration, sample_rate)
    impulse = aus.generation.impulse(100, sample_rate)  # 100ms impulse
    silence = aus.generation.silence(duration, sample_rate)

    print(f"✓ White noise: RMS={white.rms():.4f}")
    print(f"✓ Pink noise: RMS={pink.rms():.4f}")
    print(f"✓ Brown noise: RMS={brown.rms():.4f}")
    print(f"✓ Impulse response: {impulse.samples_per_channel()} samples")
    print(f"✓ Silence: RMS={silence.rms():.6f}")

    print_header("2. PROFESSIONAL AUDIO ANALYSIS")

    # Create complex test signal
    print_subheader("Built-in Audio Statistics")

    print("```python")
    print("# Create complex test signal using AudioSamples operations")
    print("test_signal = sine + cosine * 0.3 + white * 0.05")
    print("")
    print("# Built-in audio statistics - no external libraries needed")
    print("mean_amp = test_signal.mean()")
    print("rms_level = test_signal.rms()")
    print("variance = test_signal.variance()")
    print("std_dev = test_signal.std_dev()")
    print("zero_crossings = test_signal.zero_crossings()")
    print("crossing_rate = test_signal.zero_crossing_rate()")
    print("```")

    test_signal = sine + cosine * 0.3 + white * 0.05

    print(f"✓ Mean amplitude: {test_signal.mean():.6f}")
    print(f"✓ RMS level: {test_signal.rms():.6f}")
    print(f"✓ Variance: {test_signal.variance():.6f}")
    print(f"✓ Standard deviation: {test_signal.std_dev():.6f}")
    print(f"✓ Zero crossings: {test_signal.zero_crossings()}")
    print(f"✓ Zero crossing rate: {test_signal.zero_crossing_rate():.4f}")

    print_subheader("Advanced Spectral Analysis")

    print("```python")
    print("# Professional spectral analysis built-in")
    print("centroid = test_signal.spectral_centroid()")
    print("rolloff = test_signal.spectral_rolloff(0.85)  # 85th percentile")
    print("```")

    centroid = test_signal.spectral_centroid()
    rolloff = test_signal.spectral_rolloff(0.85)  # 85th percentile
    print(f"✓ Spectral centroid: {centroid:.2f} Hz")
    print(f"✓ Spectral rolloff (85%): {rolloff:.2f} Hz")

    print_subheader("Correlation Analysis")

    print("```python")
    print("# Advanced correlation analysis")
    print("autocorr = test_signal.autocorrelation(1000)  # 1000 samples max lag")
    print("cross_corr = sine.cross_correlation(cosine, 500)")
    print("```")

    autocorr = test_signal.autocorrelation(1000)  # 1000 samples max lag
    if autocorr:
        print(f"✓ Autocorrelation computed: {len(autocorr)} samples")
        print(f"✓ Peak autocorrelation at lag 0: {max(autocorr):.4f}")

    # Cross-correlation between two signals
    cross_corr = sine.cross_correlation(cosine, 500)
    if cross_corr:
        print(f"✓ Cross-correlation computed: {len(cross_corr)} samples")

    print_header("3. BUILT-IN AUDIO TRANSFORMATIONS")

    print_subheader("Audio Processing and Cleanup")

    print("```python")
    print("# Built-in audio processing operations")
    print("effect_audio = aus.generation.sine_wave(440.0, 0.5, sample_rate)")
    print("")
    print("# Scaling and normalization")
    print("effect_audio.scale(0.5)  # 50% gain")
    print("effect_audio.normalize(-1.0, 1.0, 'minmax')  # Min-max normalization")
    print("")
    print("# Audio cleanup")
    print("effect_audio.remove_dc_offset()")
    print("effect_audio.clip(-0.8, 0.8)  # Soft clipping")
    print("")
    print("# Reverse operations")
    print("reversed_audio = effect_audio.reverse()")
    print("effect_audio.reverse_in_place()")
    print("```")

    # Create working copy for effects
    effect_audio = aus.generation.sine_wave(440.0, 0.5, sample_rate)

    # Scaling and normalization
    print(f"Original RMS: {effect_audio.rms():.4f}")
    effect_audio.scale(0.5)  # 50% gain
    print(f"After scaling (0.5x): {effect_audio.rms():.4f}")

    effect_audio.normalize(-1.0, 1.0, "minmax")  # Min-max normalization
    print(f"After normalization: {effect_audio.rms():.4f}")

    # Audio cleanup
    effect_audio.remove_dc_offset()
    print("✓ DC offset removed")

    effect_audio.clip(-0.8, 0.8)  # Soft clipping
    print("✓ Clipped to [-0.8, 0.8] range")

    # Reverse operations
    reversed_audio = effect_audio.reverse()
    print(f"✓ Reversed audio: {reversed_audio.duration_seconds:.3f}s")

    effect_audio.reverse_in_place()
    print("✓ Reversed in-place")

    print_header("4. MULTI-CHANNEL OPERATIONS")

    print_subheader("Advanced Channel Processing")

    print("```python")
    print("# Professional multi-channel operations using AudioSamples methods")
    print("# Create stereo using AudioSamples.stack() - the proper way!")
    print("left_channel = sine")
    print("right_channel = cosine * 0.7")
    print("stereo = aus.AudioSamples.stack([left_channel, right_channel])")
    print("")
    print("# Professional channel operations")
    print("stereo.pan(0.3)  # Pan 30% to the right")
    print("stereo.balance(0.2)  # 20% balance adjustment")
    print("")
    print("# Channel extraction and manipulation")
    print("left_extracted = stereo.extract_channel(0)")
    print("right_extracted = stereo.extract_channel(1)")
    print("stereo.swap_channels(0, 1)")
    print("")
    print("# Channel conversion")
    print("mono_converted = stereo.to_mono('average')")
    print("stereo_from_mono = sine.to_stereo('duplicate')")
    print("```")

    # Create stereo for channel operations using proper AudioSamples method
    left_channel = sine
    right_channel = cosine * 0.7
    stereo = aus.AudioSamples.stack([left_channel, right_channel])

    print(f"✓ Created stereo: {stereo.channels} channels, {stereo.samples_per_channel()} samples/ch")

    # Channel operations
    stereo.pan(0.3)  # Pan 30% to the right
    print("✓ Applied panning (30% right)")

    stereo.balance(0.2)  # 20% balance adjustment
    print("✓ Applied balance adjustment")

    # Extract individual channels
    left_extracted = stereo.extract_channel(0)
    right_extracted = stereo.extract_channel(1)
    print(f"✓ Extracted left channel: {left_extracted.channels} channel")
    print(f"✓ Extracted right channel: {right_extracted.channels} channel")

    # Channel manipulation
    stereo.swap_channels(0, 1)
    print("✓ Swapped stereo channels")

    # Convert to mono
    mono_converted = stereo.to_mono("average")
    print(f"✓ Converted to mono: {mono_converted.channels} channel")

    # Convert mono to stereo
    stereo_from_mono = sine.to_stereo("duplicate")
    print(f"✓ Converted to stereo: {stereo_from_mono.channels} channels")

    print_header("5. PROFESSIONAL AUDIO EDITING")

    print_subheader("Non-destructive Audio Operations")

    print("```python")
    print("# Professional audio editing operations")
    print("trimmed = test_signal.trim(0.2, 0.8)  # Keep 0.2s to 0.8s")
    print("trim_silence = test_signal.trim_silence(-40.0)  # -40dB threshold")
    print("")
    print("# Audio manipulation")
    print("repeated = sine.repeat(3)")
    print("padded = sine.pad(0.5, 0.5, 0.0)  # 0.5s padding each side")
    print("")
    print("# AudioSamples concatenation - the proper way!")
    print("concatenated = aus.AudioSamples.concatenate([sine, square, triangle])")
    print("segments = concatenated.split(0.5)  # 0.5s segments")
    print("```")

    # Precise trimming
    trimmed = test_signal.trim(0.2, 0.8)  # Keep 0.2s to 0.8s
    print(f"✓ Trimmed to {trimmed.duration_seconds:.3f}s")

    # Intelligent silence trimming
    trim_silence = test_signal.trim_silence(-40.0)  # -40dB threshold
    print(f"✓ Silence-trimmed to {trim_silence.duration_seconds:.3f}s")

    # Audio repetition
    repeated = sine.repeat(3)
    print(f"✓ Repeated 3x: {repeated.duration_seconds:.3f}s total")

    # Padding with silence (zero values)
    padded = sine.pad(0.5, 0.5, 0.0)  # 0.5s padding each side with zeros
    print(f"✓ Zero-padded: {padded.duration_seconds:.3f}s total")

    # Advanced concatenation using proper AudioSamples method
    concatenated = aus.AudioSamples.concatenate([sine, square, triangle])
    print(f"✓ Concatenated 3 signals: {concatenated.duration_seconds:.3f}s total")

    # Audio segmentation
    segments = concatenated.split(0.5)  # 0.5s segments
    print(f"✓ Split into {len(segments)} segments of ~0.5s each")

    print_subheader("Professional Fade Operations")

    print("```python")
    print("# Professional fade curves")
    print("fade_audio = aus.generation.sine_wave(440.0, 0.2, sample_rate)")
    print("fade_audio.fade_in(0.05, 'exponential')  # 50ms exponential")
    print("fade_audio.fade_out(0.05, 'logarithmic')  # 50ms logarithmic")
    print("```")

    fade_audio = aus.generation.sine_wave(440.0, 0.2, sample_rate)

    # Advanced fade curves
    fade_audio.fade_in(0.05, "exponential")  # 50ms exponential fade in
    print("✓ Applied exponential fade in (50ms)")

    fade_audio.fade_out(0.05, "logarithmic")  # 50ms logarithmic fade out
    print("✓ Applied logarithmic fade out (50ms)")

    print_header("6. PROFESSIONAL RESAMPLING")

    print_subheader("High-Quality Sample Rate Conversion")

    print("```python")
    print("# Professional resampling algorithms")
    print("resample_signal = aus.generation.sine_wave(440.0, 0.5, sample_rate)")
    print("")
    print("# High-quality resampling to different rates")
    print("upsampled = resample_signal.resample(88200, 'high')  # 2x upsampling")
    print("downsampled = resample_signal.resample(22050, 'high')  # 2x downsampling")
    print("")
    print("# Ratio-based resampling")
    print("ratio_resampled = resample_signal.resample_by_ratio(1.5, 'high')")
    print("```")

    resample_signal = aus.generation.sine_wave(440.0, 0.5, sample_rate)

    # High-quality resampling to different rates
    upsampled = resample_signal.resample(88200, "high")  # 2x upsampling
    print(f"✓ Upsampled to {upsampled.sample_rate}Hz ({upsampled.samples_per_channel()} samples)")

    downsampled = resample_signal.resample(22050, "high")  # 2x downsampling
    print(f"✓ Downsampled to {downsampled.sample_rate}Hz ({downsampled.samples_per_channel()} samples)")

    # Ratio-based resampling
    ratio_resampled = resample_signal.resample_by_ratio(1.5, "high")
    print(f"✓ Resampled by ratio 1.5x to {ratio_resampled.sample_rate}Hz")

    print_header("7. MULTI-FORMAT TYPE SYSTEM")

    print_subheader("Professional Audio Formats")

    print("AudioSamples supports multiple sample formats:")
    print("✓ i16: 16-bit integer samples")
    print("✓ i24: 24-bit integer samples (professional audio)")
    print("✓ i32: 32-bit integer samples")
    print("✓ f32: 32-bit floating-point samples")
    print("✓ f64: 64-bit floating-point samples")
    print("✓ Seamless format conversion preserves audio quality")
    print("✓ Type-safe conversions prevent data corruption")

    print_header("8. METADATA & INTROSPECTION")

    print_subheader("Rich Audio Metadata")

    # Comprehensive audio information
    info_audio = stereo
    print(f"Sample rate: {info_audio.sample_rate} Hz")
    print(f"Channels: {info_audio.channels}")
    print(f"Total samples: {info_audio.total_samples}")
    print(f"Samples per channel: {info_audio.samples_per_channel()}")
    print(f"Duration: {info_audio.duration_seconds:.3f}s ({info_audio.duration_milliseconds:.1f}ms)")
    print(f"Shape: {info_audio.shape}")
    print(f"Is mono: {info_audio.is_mono()}")
    print(f"Is multi-channel: {info_audio.is_multi_channel()}")
    print(f"Is empty: {info_audio.is_empty()}")
    print(f"Dimensions: {info_audio.ndim}")
    print("✓ Professional audio metadata always preserved")

    print_header("9. PROFESSIONAL FILTERING")

    print_subheader("Built-in Digital Filters")

    print("```python")
    print("# Professional digital filters built-in")
    print("filter_signal = aus.generation.sine_wave(440.0, 0.5, sample_rate)")
    print("")
    print("# Simple filter operations")
    print("filter_signal.low_pass_filter(1000.0)")
    print("filter_signal.high_pass_filter(100.0)")
    print("filter_signal.band_pass_filter(200.0, 2000.0)")
    print("```")

    filter_signal = aus.generation.sine_wave(440.0, 0.5, sample_rate)

    # Simple filters
    filter_signal.low_pass_filter(1000.0)
    print("✓ Applied low-pass filter (1kHz)")

    filter_signal.high_pass_filter(100.0)
    print("✓ Applied high-pass filter (100Hz)")

    filter_signal.band_pass_filter(200.0, 2000.0)
    print("✓ Applied band-pass filter (200Hz-2kHz)")

    print_header("10. AUDIOSAMPLE METHODS VS NUMPY INTEROPERABILITY")

    print_subheader("When to Use AudioSamples Methods vs NumPy")

    print("```python")
    print("# ✅ GOOD: Use AudioSamples methods for audio-specific operations")
    print("# Multi-channel operations")
    print("stereo = aus.AudioSamples.stack([left, right])  # Proper way")
    print("concatenated = aus.AudioSamples.concatenate([audio1, audio2])  # Proper way")
    print("")
    print("# Audio processing")
    print("audio.fade_in(0.1, 'linear')  # Built-in audio fades")
    print("audio.normalize(-1.0, 1.0, 'peak')  # Audio normalization")
    print("resampled = audio.resample(48000, 'high')  # Professional resampling")
    print("")
    print("# ❌ AVOID: Don't use numpy for operations AudioSamples handles better")
    print("# stereo_bad = np.vstack([left.to_numpy(), right.to_numpy()])  # Bad!")
    print("# concatenated_bad = np.concatenate([a1.to_numpy(), a2.to_numpy()])  # Bad!")
    print("```")

    print("✅ Use AudioSamples methods for:")
    print("  • Multi-channel operations (stack, concatenate)")
    print("  • Audio-specific processing (fades, normalization)")
    print("  • Professional operations (resampling, filtering)")
    print("  • Metadata preservation")

    print_subheader("Appropriate NumPy Integration")

    print("```python")
    print("# ✅ GOOD: Use numpy for mathematical operations on audio data")
    print("numpy_audio = aus.generation.sine_wave(440.0, 0.5, sample_rate)")
    print("")
    print("# Mathematical transformations")
    print("gain_curve = np.linspace(0.1, 1.0, len(numpy_audio))")
    print("gained_audio = numpy_audio * gain_curve  # Custom gain curves")
    print("")
    print("# Signal processing with custom algorithms")
    print("window = np.hanning(len(numpy_audio))")
    print("windowed_audio = numpy_audio * window")
    print("")
    print("# In-place operations for memory efficiency")
    print("numpy_audio *= 0.5  # Scalar operations")
    print("")
    print("# Custom mathematical operations")
    print("distortion = np.tanh(numpy_audio.to_numpy() * 3.0)  # Custom distortion")
    print("distorted_audio = aus.AudioSamples.new_mono(distortion, sample_rate)")
    print("```")

    print("✅ Use NumPy for:")
    print("  • Mathematical transformations (gain curves, windows)")
    print("  • Custom signal processing algorithms")
    print("  • Element-wise operations with arrays")
    print("  • Mathematical functions (tanh, sin, etc.)")

    # Demonstrate appropriate numpy interoperability
    numpy_audio = aus.generation.sine_wave(440.0, 0.5, sample_rate)
    original_rms = numpy_audio.rms()

    # Appropriate numpy usage - mathematical operations
    gain_curve = np.linspace(0.1, 1.0, len(numpy_audio))
    gained_audio = numpy_audio * gain_curve  # Custom gain envelope
    print(f"✓ Applied custom gain curve: RMS {original_rms:.3f} → {gained_audio.rms():.3f}")

    # Mathematical windowing
    window = np.hanning(len(numpy_audio))
    windowed_audio = numpy_audio * window
    print(f"✓ Applied Hanning window: RMS {original_rms:.3f} → {windowed_audio.rms():.3f}")

    # Custom mathematical transformation
    numpy_data = numpy_audio.to_numpy()
    distorted_data = np.tanh(numpy_data * 2.0)  # Custom distortion
    distorted_audio = aus.AudioSamples.new_mono(distorted_data, sample_rate)
    print(f"✓ Applied tanh distortion: RMS {original_rms:.3f} → {distorted_audio.rms():.3f}")

    print(f"✓ Seamless interop: AudioSamples ⟷ NumPy as needed")

    print_header("11. PROFESSIONAL AUDIO I/O")

    print_subheader("Format-Aware Audio I/O")

    print("AudioSamples provides professional I/O capabilities:")
    print("✓ aus.io.read() - Auto-detect format and sample rate")
    print("✓ aus.io.read_with_info() - Get detailed file metadata")
    print("✓ aus.io.read_as_f32() - Force specific sample format")
    print("✓ aus.io.save() - Maintain original format")
    print("✓ aus.io.save_as_type() - Convert format on save")
    print("✓ Support for: WAV, FLAC, MP3, OGG, M4A, and more")
    print("✓ Professional metadata preservation")

    print_header("SUMMARY: AudioSamples Advantages")

    advantages = [
        "🎯 Built-in professional audio algorithms and generators",
        "⚡ High-performance Rust backend with Python ergonomics",
        "🔧 Comprehensive audio statistics and analysis functions",
        "🎛️ Advanced channel operations (panning, balance, extraction)",
        "🎵 Professional waveform and noise generators",
        "📊 Spectral analysis tools (centroid, rolloff, correlation)",
        "🎪 Intelligent audio editing (silence trimming, segmentation)",
        "🔄 High-quality resampling with multiple algorithms",
        "💾 Multi-format type system (i16/i24/i32/f32/f64)",
        "📁 Professional audio I/O with metadata preservation",
        "🛡️ Type safety with compile-time guarantees",
        "🧮 Seamless numpy interoperability for traditional workflows",
        "⚙️ Zero-copy operations where possible for performance",
        "🎚️ Professional fade curves and audio transformations",
        "🔊 Built-in filtering and audio processing",
        "📈 Rich metadata and introspection capabilities"
    ]

    print("\nAudioSamples offers professional audio processing capabilities that")
    print("extend far beyond basic numpy operations:")
    print()
    for advantage in advantages:
        print(f"  {advantage}")

    print(f"\n🚀 Result: AudioSamples is a complete professional audio processing")
    print(f"   library that combines the performance of Rust with Python's")
    print(f"   ergonomics, providing capabilities that would require multiple")
    print(f"   specialized libraries in traditional Python audio workflows!")

    print("\n💡 Key Differentiators vs Pure NumPy:")
    differentiators = [
        "• Audio-specific algorithms built-in (no external dependencies)",
        "• Automatic sample rate and channel tracking",
        "• Type-safe format conversions",
        "• Professional audio editing operations",
        "• High-quality resampling algorithms",
        "• Built-in spectral analysis functions",
        "• Zero-configuration audio I/O",
        "• Memory-efficient operations with multiple backing types"
    ]

    for diff in differentiators:
        print(diff)

    print("\n🎯 Best Practices:")
    best_practices = [
        "✅ Use AudioSamples.stack() for multi-channel creation",
        "✅ Use AudioSamples.concatenate() for joining audio",
        "✅ Use AudioSamples methods for audio-specific operations",
        "✅ Use NumPy for mathematical transformations only",
        "✅ Preserve metadata with AudioSamples operations",
        "❌ Avoid numpy for operations AudioSamples handles natively"
    ]

    for practice in best_practices:
        print(practice)


if __name__ == "__main__":
    main()