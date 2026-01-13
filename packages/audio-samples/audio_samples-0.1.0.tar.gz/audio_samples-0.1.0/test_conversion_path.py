#!/usr/bin/env python3
"""
Test to verify exactly which conversion path is taken for different array layouts.
"""

import numpy as np
import audio_samples_python as asp
import time


def test_which_path_is_taken():
    """Test to determine if our arrays actually trigger the NumpyInterleaved path."""

    # Test different array configurations
    test_cases = [
        ("C-contiguous planar", lambda: np.random.randn(2, 44100).astype(np.float32)),
        ("F-contiguous interleaved", lambda: np.asfortranarray(np.random.randn(44100, 2).astype(np.float32))),
        ("C-contiguous interleaved", lambda: np.ascontiguousarray(np.random.randn(44100, 2).astype(np.float32))),
        ("F-contiguous planar", lambda: np.asfortranarray(np.random.randn(2, 44100).astype(np.float32))),
    ]

    print("Testing which backing type is used for different array layouts:\n")

    for name, data_func in test_cases:
        data = data_func()

        print(f"{name}:")
        print(f"  Shape: {data.shape}")
        print(f"  C-contiguous: {data.flags.c_contiguous}")
        print(f"  F-contiguous: {data.flags.f_contiguous}")
        print(f"  Strides: {data.strides}")

        audio = asp.AudioSamples.from_array(data, 44100)

        # Test if conversion happens by looking at performance characteristics
        # If NumpyInterleaved path is taken, we should see evidence of conversion

        operations = []
        for i in range(100):
            start = time.perf_counter()
            peak = audio.peak()
            elapsed = time.perf_counter() - start
            operations.append(elapsed)

        avg_time = np.mean(operations)
        std_time = np.std(operations)

        print(f"  Average operation time: {avg_time*1000:.4f} ± {std_time*1000:.4f} ms")

        # Test numpy roundtrip
        start = time.perf_counter()
        numpy_result = audio.to_numpy()
        conversion_time = time.perf_counter() - start

        print(f"  to_numpy() time: {conversion_time*1000:.4f} ms")
        print(f"  Result shape: {numpy_result.shape}")
        print(f"  Result C-contiguous: {numpy_result.flags.c_contiguous}")
        print(f"  Result F-contiguous: {numpy_result.flags.f_contiguous}")
        print()


def create_definite_interleaved():
    """Create data that should definitely trigger NumpyInterleaved backing."""
    # Create interleaved data in the exact format that should trigger
    # the NumpyInterleaved path: (frames, channels) F-contiguous

    frames = 44100
    channels = 2

    # Create in interleaved format: each frame has all channels
    data = np.random.randn(frames * channels).astype(np.float32)

    # Reshape to (frames, channels) and ensure F-order
    interleaved = data.reshape((frames, channels), order='F')

    # Verify it's truly interleaved in memory
    print(f"Interleaved data properties:")
    print(f"  Shape: {interleaved.shape}")
    print(f"  Strides: {interleaved.strides}")
    print(f"  F-contiguous: {interleaved.flags.f_contiguous}")
    print(f"  C-contiguous: {interleaved.flags.c_contiguous}")

    # Test the conversion logic manually
    print(f"\nTesting manual deinterleave on this data:")
    start = time.perf_counter()

    # This mimics what happens in lines 5578-5583
    interleaved_slice = interleaved.flatten()  # Flatten to 1D

    # Simulate the deinterleave operation
    deinterleaved = np.empty((channels, frames), dtype=np.float32)
    for c in range(channels):
        deinterleaved[c] = interleaved_slice[c::channels]

    manual_time = time.perf_counter() - start
    print(f"  Manual deinterleave time: {manual_time*1000:.4f} ms")

    # Compare with AudioSamples
    audio = asp.AudioSamples.from_array(interleaved, 44100)

    start = time.perf_counter()
    result = audio.to_numpy()
    audio_time = time.perf_counter() - start

    print(f"  AudioSamples to_numpy() time: {audio_time*1000:.4f} ms")
    print(f"  Manual result shape: {deinterleaved.shape}")
    print(f"  AudioSamples result shape: {result.shape}")

    # Compare after accounting for potential transpose
    if deinterleaved.shape == result.shape:
        equiv = np.allclose(deinterleaved, result)
    elif deinterleaved.shape == result.T.shape:
        equiv = np.allclose(deinterleaved, result.T)
    else:
        equiv = False
    print(f"  Results equivalent: {equiv}")

    return interleaved, audio


if __name__ == "__main__":
    print("Testing Array Layout to Backing Type Mapping")
    print("=" * 50)

    test_which_path_is_taken()

    print("\n" + "=" * 50)
    print("Testing Definite Interleaved Path")
    print("=" * 50)

    interleaved_data, audio = create_definite_interleaved()

    print(f"\nFinal assessment:")
    print("If significant overhead was present, we would expect to see:")
    print("1. Much higher operation times for F-contiguous interleaved data")
    print("2. Slow to_numpy() conversion times")
    print("3. Clear performance differences between layouts")
    print("\nActual results suggest either:")
    print("- The deinterleaving overhead is negligible for this data size")
    print("- NumPy/ndarray handle strides efficiently enough that conversion isn't needed")
    print("- Our test data doesn't actually trigger the NumpyInterleaved code path")