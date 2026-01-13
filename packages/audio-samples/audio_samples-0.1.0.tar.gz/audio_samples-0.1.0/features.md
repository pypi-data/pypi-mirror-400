# AudioSamples Showcase

## 1. AUDIO GENERATION

### Waveform Generation

```python
#  signal generators with precise frequency control
sine = aus.generation.sine_wave(440.0, duration, sample_rate)
cosine = aus.generation.cosine_wave(880.0, duration, sample_rate)
sawtooth = aus.generation.sawtooth_wave(220.0, duration, sample_rate)
square = aus.generation.square_wave(110.0, duration, sample_rate)
triangle = aus.generation.triangle_wave(660.0, duration, sample_rate)
chirp = aus.generation.chirp(100.0, 2000.0, duration, sample_rate)
```

Sine wave: 44100Hz, 1.000s
Cosine wave: 44100Hz, 1.000s
Sawtooth wave: 44100Hz, 1.000s
Square wave: 44100Hz, 1.000s
Triangle wave: 44100Hz, 1.000s
Frequency chirp: 44100Hz, 1.000s

###  Noise Generation

```python
#  noise generators for audio testing
white = aus.generation.white_noise(duration, sample_rate)
pink = aus.generation.pink_noise(duration, sample_rate)
brown = aus.generation.brown_noise(duration, sample_rate)
impulse = aus.generation.impulse(100, sample_rate)  # 100ms impulse
silence = aus.generation.silence(duration, sample_rate)
```

White noise: RMS=0.5754
Pink noise: RMS=0.1925
Brown noise: RMS=0.3573
Impulse response: 4410000 samples
Silence: RMS=0.000000

## 2. AUDIO ANALYSIS

### Audio Statistics

```python
# Create complex test signal using AudioSamples operations
test_signal = sine + cosine * 0.3 + white * 0.05

# Built-in audio statistics - no external libraries needed
mean_amp = test_signal.mean()
rms_level = test_signal.rms()
variance = test_signal.variance()
std_dev = test_signal.std_dev()
zero_crossings = test_signal.zero_crossings()
crossing_rate = test_signal.zero_crossing_rate()
```

Mean amplitude: -0.000130
RMS level: 0.738531
Variance: 0.545428
Standard deviation: 0.738531
Zero crossings: 882
Zero crossing rate: 882.0000

### Spectral Analysis

```python
#  spectral analysis built-in
centroid = test_signal.spectral_centroid()
rolloff = test_signal.spectral_rolloff(0.85)  # 85th percentile
```

Spectral centroid: 492.24 Hz
Spectral rolloff (85%): 440.00 Hz

### Correlation Analysis

```python
# Advanced correlation analysis
autocorr = test_signal.autocorrelation(1000)  # 1000 samples max lag
cross_corr = sine.cross_correlation(cosine, 500)
```

Autocorrelation computed: 1001 samples
Peak autocorrelation at lag 0: 0.5454
Cross-correlation computed: 501 samples

## 3. BUILT-IN AUDIO TRANSFORMATIONS

## Audio Processing and Cleanup

```python
# Built-in audio processing operations
effect_audio = aus.generation.sine_wave(440.0, 0.5, sample_rate)

# Scaling and normalization
effect_audio.scale(0.5)  # 50% gain
# or
effect_audio *= 0.5

effect_audio.normalize(-1.0, 1.0, 'minmax')  # Min-max normalization

# Audio cleanup
effect_audio.remove_dc_offset()
effect_audio.clip(-0.8, 0.8)  # Soft clipping

# Reverse operations
reversed_audio = effect_audio.reverse()
effect_audio.reverse_in_place()
```

Original RMS: 0.7071
After scaling (0.5x): 0.3536
After normalization: 0.7071

## 4. MULTI-CHANNEL OPERATIONS

### Advanced Channel Processing

```python
# Multi-channel operations using AudioSamples methods
# Create stereo using AudioSamples.stack() - the proper way!
left_channel = sine
right_channel = cosine * 0.7
stereo = aus.AudioSamples.stack([left_channel, right_channel])

# channel operations
stereo.pan(0.3)  # Pan 30% to the right
stereo.balance(0.2)  # 20% balance adjustment

# Channel extraction and manipulation
left_extracted = stereo.extract_channel(0)
right_extracted = stereo.extract_channel(1)
stereo.swap_channels(0, 1)

# Channel conversion
mono_converted = stereo.to_mono('average')
stereo_from_mono = sine.to_stereo('duplicate')
```

## 5. AUDIO EDITING

### Non-destructive Audio Operations

```python
# Audio editing operations
trimmed = test_signal.trim(0.2, 0.8)  # Keep 0.2s to 0.8s
trim_silence = test_signal.trim_silence(-40.0)  # -40dB threshold

# Audio manipulation
repeated = sine.repeat(3)
padded = sine.pad(0.5, 0.5, 0.0)  # 0.5s padding each side

# AudioSamples concatenation
concatenated = aus.AudioSamples.concatenate([sine, square, triangle])
segments = concatenated.split(0.5)  # 0.5s segments
```

Trimmed to 0.600s
Silence-trimmed to 1.000s
Repeated 3x: 3.000s total
Zero-padded: 2.000s total
Concatenated 3 signals: 3.000s total
Split into 6 segments of ~0.5s each

### Fade Operations

```python
#  fade curves
fade_audio = aus.generation.sine_wave(440.0, 0.2, sample_rate)
fade_audio.fade_in(0.05, 'exponential')  # 50ms exponential
fade_audio.fade_out(0.05, 'logarithmic')  # 50ms logarithmic
```

Applied exponential fade in (50ms)
Applied logarithmic fade out (50ms)

## 6. RESAMPLING

### High-Quality Sample Rate Conversion

```python
#  resampling algorithms
resample_signal = aus.generation.sine_wave(440.0, 0.5, sample_rate)

# High-quality resampling to different rates
upsampled = resample_signal.resample(88200, 'high')  # 2x upsampling
downsampled = resample_signal.resample(22050, 'high')  # 2x downsampling

# Ratio-based resampling
ratio_resampled = resample_signal.resample_by_ratio(1.5, 'high')
```

Upsampled to 88200Hz (48892 samples)
Downsampled to 22050Hz (12223 samples)
Resampled by ratio 1.5x to 66150Hz

## 7. MULTI-FORMAT TYPE SYSTEM

### Audio Formats

AudioSamples supports multiple sample formats:
i16: 16-bit integer samples
i24: 24-bit integer samples
i32: 32-bit integer samples
f32: 32-bit floating-point samples
f64: 64-bit floating-point samples
Type-safe conversions prevent data corruption

## 8. METADATA & INTROSPECTION

### Rich Audio Metadata
audio.info()
Sample rate: 44100 Hz
Channels: 2
Total samples: 88200
Samples per channel: 44100
Duration: 1.000s (1000.0ms)
Shape: [2, 44100]
Is mono: False
Is multi-channel: True
Is empty: False
Dimensions: 2
✓  audio metadata always preserved

============================================================
 9.  FILTERING
============================================================

----------------------------------------
 Built-in Digital Filters
----------------------------------------
```python
#  digital filters built-in
filter_signal = aus.generation.sine_wave(440.0, 0.5, sample_rate)

# Simple filter operations
filter_signal.low_pass_filter(1000.0)
filter_signal.high_pass_filter(100.0)
filter_signal.band_pass_filter(200.0, 2000.0)
```
✓ Applied low-pass filter (1kHz)
✓ Applied high-pass filter (100Hz)
✓ Applied band-pass filter (200Hz-2kHz)

============================================================
 10. AUDIOSAMPLE METHODS VS NUMPY INTEROPERABILITY
============================================================

----------------------------------------
 When to Use AudioSamples Methods vs NumPy
----------------------------------------
```python
# ✅ GOOD: Use AudioSamples methods for audio-specific operations
# Multi-channel operations
stereo = aus.AudioSamples.stack([left, right])  # Proper way
concatenated = aus.AudioSamples.concatenate([audio1, audio2])  # Proper way

# Audio processing
audio.fade_in(0.1, 'linear')  # Built-in audio fades
audio.normalize(-1.0, 1.0, 'peak')  # Audio normalization
resampled = audio.resample(48000, 'high')  #  resampling

# ❌ AVOID: Don't use numpy for operations AudioSamples handles better
# stereo_bad = np.vstack([left.to_numpy(), right.to_numpy()])  # Bad!
# concatenated_bad = np.concatenate([a1.to_numpy(), a2.to_numpy()])  # Bad!
```
✅ Use AudioSamples methods for:
  • Multi-channel operations (stack, concatenate)
  • Audio-specific processing (fades, normalization)
  •  operations (resampling, filtering)
  • Metadata preservation

----------------------------------------
 Appropriate NumPy Integration
----------------------------------------
```python
# ✅ GOOD: Use numpy for mathematical operations on audio data
numpy_audio = aus.generation.sine_wave(440.0, 0.5, sample_rate)

# Mathematical transformations
gain_curve = np.linspace(0.1, 1.0, len(numpy_audio))
gained_audio = numpy_audio * gain_curve  # Custom gain curves

# Signal processing with custom algorithms
window = np.hanning(len(numpy_audio))
windowed_audio = numpy_audio * window

# In-place operations for memory efficiency
numpy_audio *= 0.5  # Scalar operations

# Custom mathematical operations
distortion = np.tanh(numpy_audio.to_numpy() * 3.0)  # Custom distortion
distorted_audio = aus.AudioSamples.new_mono(distortion, sample_rate)
```
✅ Use NumPy for:
  • Mathematical transformations (gain curves, windows)
  • Custom signal processing algorithms
  • Element-wise operations with arrays
  • Mathematical functions (tanh, sin, etc.)
✓ Applied custom gain curve: RMS 0.707 → 0.430
✓ Applied Hanning window: RMS 0.707 → 0.433
✓ Applied tanh distortion: RMS 0.707 → 0.802
✓ Seamless interop: AudioSamples ⟷ NumPy as needed

============================================================
 11.  AUDIO I/O
============================================================

----------------------------------------
 Format-Aware Audio I/O
----------------------------------------
AudioSamples provides  I/O capabilities:
✓ aus.io.read() - Auto-detect format and sample rate
✓ aus.io.read_with_info() - Get detailed file metadata
✓ aus.io.read_as_f32() - Force specific sample format
✓ aus.io.save() - Maintain original format
✓ aus.io.save_as_type() - Convert format on save
✓ Support for: WAV, FLAC, MP3, OGG, M4A, and more
✓  metadata preservation

============================================================
 SUMMARY: AudioSamples Advantages
============================================================

AudioSamples offers  audio processing capabilities that
extend far beyond basic numpy operations:

  🎯 Built-in  audio algorithms and generators
  ⚡ High-performance Rust backend with Python ergonomics
  🔧 Comprehensive audio statistics and analysis functions
  🎛️ Advanced channel operations (panning, balance, extraction)
  🎵  waveform and noise generators
  📊 Spectral analysis tools (centroid, rolloff, correlation)
  🎪 Intelligent audio editing (silence trimming, segmentation)
  🔄 High-quality resampling with multiple algorithms
  💾 Multi-format type system (i16/i24/i32/f32/f64)
  📁  audio I/O with metadata preservation
  🛡️ Type safety with compile-time guarantees
  🧮 Seamless numpy interoperability for traditional workflows
  ⚙️ Zero-copy operations where possible for performance
  🎚️  fade curves and audio transformations
  🔊 Built-in filtering and audio processing
  📈 Rich metadata and introspection capabilities

🚀 Result: AudioSamples is a complete  audio processing
   library that combines the performance of Rust with Python's
   ergonomics, providing capabilities that would require multiple
   specialized libraries in traditional Python audio workflows!

💡 Key Differentiators vs Pure NumPy:
• Audio-specific algorithms built-in (no external dependencies)
• Automatic sample rate and channel tracking
• Type-safe format conversions
•  audio editing operations
• High-quality resampling algorithms
• Built-in spectral analysis functions
• Zero-configuration audio I/O
• Memory-efficient operations with multiple backing types

🎯 Best Practices:
✅ Use AudioSamples.stack() for multi-channel creation
✅ Use AudioSamples.concatenate() for joining audio
✅ Use AudioSamples methods for audio-specific operations
✅ Use NumPy for mathematical transformations only
✅ Preserve metadata with AudioSamples operations
❌ Avoid numpy for operations AudioSamples handles natively
