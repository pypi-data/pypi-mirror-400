"""
Tests for NumPy and PyTorch interoperability features.

This test module verifies the enhanced integration features:
- NumPy array protocol methods (__array_ufunc__, __array_function__, __array_wrap__)
- DLPack protocol support (__dlpack__, __dlpack_device__, from_dlpack)
- PyTorch tensor convenience methods (to_torch, from_torch)
"""

import pytest
import numpy as np
import audio_samples as aus

# Try to import torch, skip torch tests if not available
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None


class TestNumpyArrayProtocols:
    """Test the enhanced NumPy array protocol support."""

    def test_array_ufunc_basic_operations(self):
        """Test that __array_ufunc__ allows basic numpy operations."""
        # Create test audio
        audio = aus.generation.sine_wave(440.0, 1.0, sample_rate=44100)

        # Test ufunc operations
        result_add = np.add(audio, 0.1)
        result_multiply = np.multiply(audio, 0.5)
        result_subtract = np.subtract(audio, 0.05)

        # Results should be numpy arrays
        assert isinstance(result_add, np.ndarray)
        assert isinstance(result_multiply, np.ndarray)
        assert isinstance(result_subtract, np.ndarray)

        # Check shapes are preserved
        original_array = audio.to_numpy()
        assert result_add.shape == original_array.shape
        assert result_multiply.shape == original_array.shape
        assert result_subtract.shape == original_array.shape

    def test_array_function_statistical_operations(self):
        """Test that __array_function__ enables numpy function calls."""
        # Create test audio
        audio = aus.generation.sine_wave(440.0, 1.0, sample_rate=44100)

        # Test statistical functions
        mean_val = np.mean(audio)
        std_val = np.std(audio)
        max_val = np.max(audio)
        min_val = np.min(audio)

        # Compare with direct numpy operations
        numpy_audio = audio.to_numpy()
        np.testing.assert_almost_equal(mean_val, np.mean(numpy_audio))
        np.testing.assert_almost_equal(std_val, np.std(numpy_audio))
        np.testing.assert_almost_equal(max_val, np.max(numpy_audio))
        np.testing.assert_almost_equal(min_val, np.min(numpy_audio))

    def test_array_function_shape_operations(self):
        """Test numpy shape manipulation functions."""
        # Create multi-channel audio
        # Create stereo audio manually since we don't have a direct stereo generation function
        mono_audio = aus.generation.sine_wave(440.0, 1.0, sample_rate=44100)
        mono_data = mono_audio.to_numpy()
        stereo_data = np.vstack([mono_data, mono_data])  # Duplicate for stereo
        audio = aus.AudioSamples.new_multi(stereo_data, sample_rate=44100)

        # Test shape-related functions
        shape = np.shape(audio)
        size = np.size(audio)

        # Compare with direct numpy operations
        numpy_audio = audio.to_numpy()
        assert shape == np.shape(numpy_audio)
        assert size == np.size(numpy_audio)

    def test_array_wrap_preserves_array_type(self):
        """Test that __array_wrap__ properly handles return types."""
        # Create test audio
        audio = aus.generation.sine_wave(440.0, 1.0, sample_rate=44100)

        # Perform operations that might use array_wrap
        squared = np.square(audio)

        # Should return numpy array (current implementation)
        assert isinstance(squared, np.ndarray)


class TestDLPackProtocol:
    """Test DLPack protocol implementation."""

    def test_dlpack_device_info(self):
        """Test __dlpack_device__ returns correct device information."""
        audio = aus.generation.sine_wave(440.0, 1.0, sample_rate=44100)

        device_info = audio.__dlpack_device__()

        # Should return (device_type, device_id) for CPU
        assert len(device_info) == 2
        assert device_info[0] == 1  # CPU device type
        assert device_info[1] == 0  # First CPU device

    def test_dlpack_export(self):
        """Test __dlpack__ export functionality."""
        audio = aus.generation.sine_wave(440.0, 1.0, sample_rate=44100)

        try:
            dlpack_tensor = audio.__dlpack__()
            # If this doesn't raise an exception, DLPack export is working
            assert dlpack_tensor is not None
        except RuntimeError as e:
            # Expected if NumPy doesn't support DLPack
            assert "NumPy version doesn't support DLPack protocol" in str(e)

    def test_from_dlpack_mono(self):
        """Test creating AudioSamples from DLPack tensor (mono)."""
        # Create a numpy array and try to convert via dlpack
        np_array = np.random.randn(1000).astype(np.float32)

        try:
            # Try numpy's dlpack if available
            dlpack_tensor = np_array.__dlpack__()
            audio = aus.AudioSamples.from_dlpack(dlpack_tensor, 44100)

            assert audio.sample_rate == 44100
            assert audio.channels == 1
            assert audio.samples_per_channel() == 1000

        except (AttributeError, RuntimeError):
            # Skip if DLPack not supported
            pytest.skip("DLPack not supported in current NumPy version")

    def test_from_dlpack_multi_channel(self):
        """Test creating AudioSamples from DLPack tensor (multi-channel)."""
        # Create a 2-channel numpy array
        np_array = np.random.randn(2, 1000).astype(np.float32)

        try:
            # Try numpy's dlpack if available
            dlpack_tensor = np_array.__dlpack__()
            audio = aus.AudioSamples.from_dlpack(dlpack_tensor, 48000)

            assert audio.sample_rate == 48000
            assert audio.channels == 2
            assert audio.samples_per_channel() == 1000

        except (AttributeError, RuntimeError):
            # Skip if DLPack not supported
            pytest.skip("DLPack not supported in current NumPy version")


@pytest.mark.skipif(not TORCH_AVAILABLE, reason="PyTorch not available")
class TestPyTorchInteroperability:
    """Test PyTorch tensor interoperability."""

    def test_to_torch_mono(self):
        """Test converting mono AudioSamples to PyTorch tensor."""
        audio = aus.generation.sine_wave(440.0, 1.0, sample_rate=44100)

        tensor = audio.to_torch()

        # Check tensor properties
        assert torch.is_tensor(tensor)
        assert tensor.dim() == 1  # Mono should be 1D
        assert tensor.shape[0] == audio.samples_per_channel()

        # Check values are preserved
        np_audio = audio.to_numpy()
        np.testing.assert_allclose(tensor.numpy(), np_audio, rtol=1e-6)

    def test_to_torch_multi_channel(self):
        """Test converting multi-channel AudioSamples to PyTorch tensor."""
        # Create stereo audio manually since we don't have a direct stereo generation function
        mono_audio = aus.generation.sine_wave(440.0, 1.0, sample_rate=44100)
        mono_data = mono_audio.to_numpy()
        stereo_data = np.vstack([mono_data, mono_data])  # Duplicate for stereo
        audio = aus.AudioSamples.new_multi(stereo_data, sample_rate=44100)

        tensor = audio.to_torch()

        # Check tensor properties
        assert torch.is_tensor(tensor)
        assert tensor.dim() == 2  # Multi-channel should be 2D
        assert tensor.shape[0] == audio.channels
        assert tensor.shape[1] == audio.samples_per_channel()

        # Check values are preserved
        np_audio = audio.to_numpy()
        np.testing.assert_allclose(tensor.numpy(), np_audio, rtol=1e-6)

    def test_from_torch_mono(self):
        """Test creating AudioSamples from PyTorch tensor (mono)."""
        # Create a PyTorch tensor
        tensor = torch.randn(1000)

        audio = aus.AudioSamples.from_torch(tensor, 44100)

        # Check audio properties
        assert audio.sample_rate == 44100
        assert audio.channels == 1
        assert audio.samples_per_channel() == 1000

        # Check values are preserved
        np.testing.assert_allclose(audio.to_numpy(), tensor.numpy(), rtol=1e-6)

    def test_from_torch_multi_channel(self):
        """Test creating AudioSamples from PyTorch tensor (multi-channel)."""
        # Create a 2-channel PyTorch tensor
        tensor = torch.randn(2, 1000)

        audio = aus.AudioSamples.from_torch(tensor, 48000)

        # Check audio properties
        assert audio.sample_rate == 48000
        assert audio.channels == 2
        assert audio.samples_per_channel() == 1000

        # Check values are preserved
        np.testing.assert_allclose(audio.to_numpy(), tensor.numpy(), rtol=1e-6)

    def test_torch_roundtrip_preserves_data(self):
        """Test that converting to torch and back preserves data."""
        original = aus.sine_wave(440.0, 1.0, sample_rate=44100, channels=2)

        # Convert to torch and back
        tensor = original.to_torch()
        restored = aus.AudioSamples.from_torch(tensor, 44100)

        # Check properties are preserved
        assert restored.sample_rate == original.sample_rate
        assert restored.channels == original.channels
        assert restored.samples_per_channel() == original.samples_per_channel()

        # Check data is preserved
        original_numpy = original.to_numpy()
        restored_numpy = restored.to_numpy()
        np.testing.assert_allclose(original_numpy, restored_numpy, rtol=1e-6)

    def test_torch_different_dtypes(self):
        """Test PyTorch interop with different tensor dtypes."""
        # Test with different torch dtypes
        dtypes_to_test = [torch.float32, torch.float64]

        for dtype in dtypes_to_test:
            tensor = torch.randn(1000, dtype=dtype)
            audio = aus.AudioSamples.from_torch(tensor, 44100)

            # Should be able to create audio regardless of dtype
            assert audio.sample_rate == 44100
            assert audio.samples_per_channel() == 1000


class TestInteroperabilityIntegration:
    """Test integration between different interoperability features."""

    def test_numpy_ufunc_with_torch_conversion(self):
        """Test using numpy ufuncs then converting to PyTorch."""
        if not TORCH_AVAILABLE:
            pytest.skip("PyTorch not available")

        # Create audio, apply numpy operation, convert to torch
        audio = aus.generation.sine_wave(440.0, 1.0, sample_rate=44100)
        scaled = np.multiply(audio, 0.5)  # Use numpy ufunc

        # Convert result to torch (should work with numpy array)
        tensor = torch.from_numpy(scaled)

        # Verify the operation worked
        original_numpy = audio.to_numpy()
        expected = original_numpy * 0.5
        np.testing.assert_allclose(tensor.numpy(), expected, rtol=1e-6)

    def test_mixed_framework_operations(self):
        """Test operations mixing NumPy, AudioSamples, and PyTorch."""
        if not TORCH_AVAILABLE:
            pytest.skip("PyTorch not available")

        # Create audio
        audio = aus.generation.sine_wave(440.0, 1.0, sample_rate=44100)

        # Apply numpy operations
        mean_centered = audio.to_numpy() - np.mean(audio)

        # Convert to torch
        tensor = torch.from_numpy(mean_centered)

        # Apply torch operations
        normalized = tensor / torch.std(tensor)

        # Create new AudioSamples from result
        result_audio = aus.AudioSamples.from_torch(normalized, 44100)

        # Verify properties
        assert result_audio.sample_rate == 44100
        assert result_audio.channels == 1

        # Verify the statistical properties
        result_numpy = result_audio.to_numpy()
        assert abs(np.mean(result_numpy)) < 1e-6  # Should be near zero
        assert abs(np.std(result_numpy) - 1.0) < 1e-6  # Should be normalized


class TestNumpyArrayArithmetic:
    """Test arithmetic operations between AudioSamples and numpy arrays."""

    def test_audio_plus_numpy_array_mono(self):
        """Test AudioSamples + numpy array for mono audio."""
        # Create mono sine wave
        audio = aus.generation.sine_wave(440.0, 0.1, sample_rate=44100)

        # Create compatible numpy array (same shape)
        numpy_array = np.ones(len(audio), dtype=np.float64) * 0.1

        # Test addition
        result = audio + numpy_array

        # Check properties preserved
        assert result.sample_rate == audio.sample_rate
        assert result.channels == audio.channels
        assert len(result) == len(audio)

        # Check that values are modified correctly
        audio_np = audio.to_numpy()
        result_np = result.to_numpy()
        expected = audio_np + numpy_array
        np.testing.assert_allclose(result_np, expected, rtol=1e-5)

    def test_audio_plus_numpy_array_stereo(self):
        """Test AudioSamples + numpy array for stereo audio."""
        # Create stereo sine wave using generation functions
        left = aus.generation.sine_wave(440.0, 0.1, sample_rate=44100)
        right = aus.generation.sine_wave(880.0, 0.1, sample_rate=44100)

        # Combine into stereo (2, N) format
        left_np = left.to_numpy()
        right_np = right.to_numpy()
        stereo_data = np.vstack([left_np, right_np])
        audio = aus.AudioSamples.new_multi(stereo_data, sample_rate=44100)

        # Create compatible numpy array (2, N) shape
        numpy_array = np.ones_like(stereo_data) * 0.2

        # Test addition
        result = audio + numpy_array

        # Check properties preserved
        assert result.sample_rate == audio.sample_rate
        assert result.channels == audio.channels
        assert len(result) == len(audio)

        # Check that values are modified correctly
        audio_np = audio.to_numpy()
        result_np = result.to_numpy()
        expected = audio_np + numpy_array
        np.testing.assert_allclose(result_np, expected, rtol=1e-5)

    def test_audio_subtract_numpy_array(self):
        """Test AudioSamples - numpy array."""
        audio = aus.generation.sine_wave(440.0, 0.1, sample_rate=44100)
        numpy_array = np.full(len(audio), 0.1, dtype=np.float64)

        result = audio - numpy_array

        # Check properties preserved
        assert result.sample_rate == audio.sample_rate
        assert result.channels == audio.channels
        assert len(result) == len(audio)

        # Check arithmetic
        audio_np = audio.to_numpy()
        result_np = result.to_numpy()
        expected = audio_np - numpy_array
        np.testing.assert_allclose(result_np, expected, rtol=1e-5)

    def test_audio_multiply_numpy_array(self):
        """Test AudioSamples * numpy array (element-wise)."""
        audio = aus.generation.sine_wave(440.0, 0.1, sample_rate=44100)
        numpy_array = np.full(len(audio), 0.5, dtype=np.float64)

        result = audio * numpy_array

        # Check properties preserved
        assert result.sample_rate == audio.sample_rate
        assert result.channels == audio.channels
        assert len(result) == len(audio)

        # Check arithmetic
        audio_np = audio.to_numpy()
        result_np = result.to_numpy()
        expected = audio_np * numpy_array
        np.testing.assert_allclose(result_np, expected, rtol=1e-5)

    def test_audio_divide_numpy_array(self):
        """Test AudioSamples / numpy array (element-wise)."""
        audio = aus.generation.sine_wave(440.0, 0.1, sample_rate=44100)
        # Avoid division by zero - use values around 1.0
        numpy_array = np.full(len(audio), 2.0, dtype=np.float64)

        result = audio / numpy_array

        # Check properties preserved
        assert result.sample_rate == audio.sample_rate
        assert result.channels == audio.channels
        assert len(result) == len(audio)

        # Check arithmetic
        audio_np = audio.to_numpy()
        result_np = result.to_numpy()
        expected = audio_np / numpy_array
        np.testing.assert_allclose(result_np, expected, rtol=1e-5)


class TestNumpyArrayReverse:
    """Test reverse operations: numpy array + AudioSamples via __array_ufunc__."""

    def test_numpy_add_audio(self):
        """Test numpy.array + AudioSamples using numpy ufunc protocol."""
        audio = aus.generation.sine_wave(440.0, 0.1, sample_rate=44100)
        numpy_array = np.ones(len(audio), dtype=np.float64) * 0.2

        # Use numpy operations - this should call __array_ufunc__
        result = np.add(numpy_array, audio)

        # Should be AudioSamples
        assert isinstance(result, aus.AudioSamples)

        # Check properties preserved
        assert result.sample_rate == audio.sample_rate
        assert result.channels == audio.channels
        assert len(result) == len(audio)

    def test_numpy_multiply_audio(self):
        """Test numpy.array * AudioSamples using numpy ufunc protocol."""
        audio = aus.generation.sine_wave(440.0, 0.1, sample_rate=44100)
        numpy_array = np.full(len(audio), 0.5, dtype=np.float64)

        # Use numpy operations - this should call __array_ufunc__
        result = np.multiply(numpy_array, audio)

        # Should be AudioSamples
        assert isinstance(result, aus.AudioSamples)

        # Check properties preserved
        assert result.sample_rate == audio.sample_rate
        assert result.channels == audio.channels
        assert len(result) == len(audio)

    def test_operator_equivalence(self):
        """Test that different ways of doing the same operation give same result."""
        audio = aus.generation.sine_wave(440.0, 0.1, sample_rate=44100)
        numpy_array = np.ones(len(audio), dtype=np.float64) * 0.3

        # Different ways to add
        result1 = audio + numpy_array
        result2 = np.add(audio, numpy_array)
        result3 = np.add(numpy_array, audio)

        # All should be equivalent
        result1_np = result1.to_numpy()
        result2_np = result2.to_numpy()
        result3_np = result3.to_numpy()

        np.testing.assert_allclose(result1_np, result2_np, rtol=1e-10)
        np.testing.assert_allclose(result2_np, result3_np, rtol=1e-10)


class TestNumpyArrayInPlace:
    """Test in-place operations with numpy arrays."""

    def test_iadd_numpy_array(self):
        """Test += with numpy array."""
        audio = aus.generation.sine_wave(440.0, 0.1, sample_rate=44100)
        numpy_array = np.ones(len(audio), dtype=np.float64) * 0.1
        original_array = audio.to_numpy().copy()

        # In-place addition
        audio += numpy_array

        # Check result
        result_array = audio.to_numpy()
        expected = original_array + numpy_array
        np.testing.assert_allclose(result_array, expected, rtol=1e-5)

    def test_isub_numpy_array(self):
        """Test -= with numpy array."""
        audio = aus.generation.sine_wave(440.0, 0.1, sample_rate=44100)
        numpy_array = np.full(len(audio), 0.1, dtype=np.float64)
        original_array = audio.to_numpy().copy()

        # In-place subtraction
        audio -= numpy_array

        # Check result
        result_array = audio.to_numpy()
        expected = original_array - numpy_array
        np.testing.assert_allclose(result_array, expected, rtol=1e-5)

    def test_imul_numpy_array(self):
        """Test *= with numpy array."""
        audio = aus.generation.sine_wave(440.0, 0.1, sample_rate=44100)
        numpy_array = np.full(len(audio), 0.5, dtype=np.float64)
        original_array = audio.to_numpy().copy()

        # In-place multiplication
        audio *= numpy_array

        # Check result
        result_array = audio.to_numpy()
        expected = original_array * numpy_array
        np.testing.assert_allclose(result_array, expected, rtol=1e-5)

    def test_itruediv_numpy_array(self):
        """Test /= with numpy array."""
        audio = aus.generation.sine_wave(440.0, 0.1, sample_rate=44100)
        numpy_array = np.full(len(audio), 2.0, dtype=np.float64)
        original_array = audio.to_numpy().copy()

        # In-place division
        audio /= numpy_array

        # Check result
        result_array = audio.to_numpy()
        expected = original_array / numpy_array
        np.testing.assert_allclose(result_array, expected, rtol=1e-5)


class TestTraditionalWorkflow:
    """Test integration with traditional Python audio workflows."""

    def test_soundfile_pattern_simulation(self):
        """Test the traditional data, sr = soundfile.read() pattern with numpy operations."""
        # Simulate the traditional workflow where you get numpy arrays from soundfile

        # Step 1: Simulate loading audio (traditionally: data, sr = soundfile.read(...))
        # We'll create fake "loaded" data
        duration = 0.5
        sample_rate = 44100
        num_samples = int(duration * sample_rate)

        # Simulate stereo audio data from soundfile (shape: N, 2 for soundfile, but we use 2, N)
        t = np.linspace(0, duration, num_samples, endpoint=False)
        left_channel = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440 Hz
        right_channel = 0.3 * np.sin(2 * np.pi * 880 * t)  # 880 Hz

        # Traditional soundfile gives (N, channels), but we need (channels, N)
        # Simulate this conversion
        soundfile_format = np.column_stack([left_channel, right_channel])  # (N, 2)
        our_format = soundfile_format.T  # (2, N)

        # Step 2: Create AudioSamples from the numpy data
        audio = aus.AudioSamples.new_multi(our_format.astype(np.float64), sample_rate=sample_rate)

        # Step 3: Perform typical audio processing using numpy arrays

        # Apply gain (traditional: data *= gain)
        gain = 1.5
        gained_audio = audio * gain

        # Apply fade-in effect using numpy array
        fade_samples = int(0.05 * sample_rate)  # 50ms fade
        fade_curve = np.linspace(0, 1, fade_samples)

        # Create full fade array for both channels
        full_fade = np.ones((2, num_samples))
        full_fade[:, :fade_samples] = fade_curve

        faded_audio = gained_audio * full_fade

        # Step 4: Verify result
        assert isinstance(faded_audio, aus.AudioSamples)
        assert faded_audio.sample_rate == sample_rate
        assert faded_audio.channels == 2
        assert faded_audio.samples_per_channel() == num_samples

        # Verify fade effect applied
        result_data = faded_audio.to_numpy()
        assert np.allclose(result_data[:, 0], 0.0, atol=1e-10)  # Should start at silence
        assert not np.allclose(result_data[:, -1], 0.0)  # Should be non-zero at end

    def test_numpy_processing_chain(self):
        """Test chaining multiple numpy operations together."""
        # Start with a simple signal
        audio = aus.generation.sine_wave(440.0, 0.2, sample_rate=44100)

        # Chain of numpy-based operations

        # 1. Apply window function
        window = np.hanning(len(audio))
        windowed = audio * window

        # 2. Apply DC offset removal (traditionally: data = data - np.mean(data))
        dc_offset = np.mean(windowed.to_numpy())
        dc_removed = windowed - dc_offset

        # 3. Apply normalization
        max_val = np.max(np.abs(dc_removed.to_numpy()))
        if max_val > 0:
            normalized = dc_removed / max_val
        else:
            normalized = dc_removed

        # 4. Apply final scaling
        final_scale = 0.8
        result = normalized * final_scale

        # Verify all operations worked
        assert isinstance(result, aus.AudioSamples)
        assert result.sample_rate == audio.sample_rate
        assert result.channels == audio.channels

        # Verify processing had expected effects
        result_data = result.to_numpy()
        assert np.max(np.abs(result_data)) <= 0.8  # Should be scaled to 0.8 max


class TestNumpyCompatibility:
    """Test compatibility with different numpy array types and shapes."""

    def test_different_numpy_dtypes(self):
        """Test operations with different numpy dtypes."""
        audio = aus.generation.sine_wave(440.0, 0.1, sample_rate=44100)

        # Test with different dtypes
        for dtype in [np.int16, np.int32, np.float32, np.float64]:
            numpy_array = np.ones(len(audio), dtype=dtype) * 0.1
            result = audio + numpy_array

            assert isinstance(result, aus.AudioSamples)
            assert result.sample_rate == audio.sample_rate
            assert result.channels == audio.channels

    def test_incompatible_shapes_error(self):
        """Test that incompatible shapes raise appropriate errors."""
        audio = aus.generation.sine_wave(440.0, 0.1, sample_rate=44100)

        # Wrong length numpy array
        wrong_length = np.ones(len(audio) + 100, dtype=np.float64)

        with pytest.raises((ValueError, RuntimeError)):
            audio + wrong_length

    def test_multidimensional_numpy_arrays(self):
        """Test operations with multidimensional numpy arrays."""
        # Create stereo audio
        left = aus.generation.sine_wave(440.0, 0.1, sample_rate=44100)
        right = aus.generation.sine_wave(880.0, 0.1, sample_rate=44100)

        left_np = left.to_numpy()
        right_np = right.to_numpy()
        stereo_data = np.vstack([left_np, right_np])
        audio = aus.AudioSamples.new_multi(stereo_data, sample_rate=44100)

        # Compatible 2D numpy array
        numpy_2d = np.ones_like(stereo_data) * 0.1

        result = audio + numpy_2d
        assert isinstance(result, aus.AudioSamples)
        assert result.channels == 2


class TestNumpyErrorHandling:
    """Test error handling for edge cases with numpy arrays."""

    def test_invalid_numpy_operations(self):
        """Test operations with invalid numpy arrays."""
        audio = aus.generation.sine_wave(440.0, 0.1, sample_rate=44100)

        # 3D array should not work
        numpy_3d = np.ones((2, len(audio), 3), dtype=np.float64)

        with pytest.raises((ValueError, TypeError)):
            audio + numpy_3d

    def test_division_by_zero_numpy(self):
        """Test division by zero with numpy arrays."""
        audio = aus.generation.sine_wave(440.0, 0.1, sample_rate=44100)
        zero_array = np.zeros(len(audio), dtype=np.float64)

        with pytest.raises((ZeroDivisionError, RuntimeError)):
            audio / zero_array

    def test_mixed_operations_type_safety(self):
        """Test that mixing incompatible types produces appropriate errors."""
        audio = aus.generation.sine_wave(440.0, 0.1, sample_rate=44100)

        # String should not work
        with pytest.raises(TypeError):
            audio + "invalid"

        # List should not work directly (must be numpy array)
        with pytest.raises(TypeError):
            audio + [1, 2, 3]