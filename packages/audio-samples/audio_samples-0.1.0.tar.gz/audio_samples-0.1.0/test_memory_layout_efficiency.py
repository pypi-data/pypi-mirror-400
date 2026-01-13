#!/usr/bin/env python3
"""
Test to investigate whether ndarray/numpy can handle different memory layouts
efficiently without requiring explicit interleaving/deinterleaving.
"""

import numpy as np
import time
import audio_samples_python as asp


def create_test_data():
    """Create test audio data in different memory layouts."""
    channels = 2
    frames = 44100 * 5  # 5 seconds at 44.1kHz

    # Create planar data (C-order, row-major)
    planar = np.random.randn(channels, frames).astype(np.float32)

    # Create interleaved data (F-order, column-major)
    interleaved = np.asfortranarray(planar.T)  # Transpose and make F-contiguous

    return planar, interleaved


def test_numpy_operations_directly():
    """Test how numpy handles operations on different memory layouts."""
    print("Testing NumPy operations on different memory layouts...")

    planar, interleaved = create_test_data()

    # Test addition on planar data
    start = time.time()
    planar_result = planar + 0.1
    planar_time = time.time() - start

    # Test addition on interleaved data (should work directly)
    start = time.time()
    interleaved_result = interleaved + 0.1
    interleaved_time = time.time() - start

    print(f"Planar layout (C-order): {planar_time:.4f}s")
    print(f"Interleaved layout (F-order): {interleaved_time:.4f}s")
    print(f"Memory layouts - Planar: {planar.flags}, Interleaved: {interleaved.flags}")

    # Verify results are equivalent (accounting for transpose)
    expected_interleaved = (planar + 0.1).T
    np.testing.assert_allclose(interleaved_result, expected_interleaved, rtol=1e-7)
    print("✓ Results are equivalent")

    return planar_time, interleaved_time


def test_audio_samples_operations():
    """Test how our current implementation handles different layouts."""
    print("\nTesting audio_samples_python operations...")

    planar, interleaved = create_test_data()

    # Create AudioSamples objects
    planar_audio = asp.AudioSamples.from_array(planar, 44100)
    interleaved_audio = asp.AudioSamples.from_array(interleaved, 44100)

    # Test scale operation (this will trigger our current conversion logic)
    start = time.time()
    planar_result = planar_audio.scale(1.1)
    planar_time = time.time() - start

    start = time.time()
    interleaved_result = interleaved_audio.scale(1.1)
    interleaved_time = time.time() - start

    print(f"Planar AudioSamples: {planar_time:.4f}s")
    print(f"Interleaved AudioSamples: {interleaved_time:.4f}s")

    # Test if the arrays maintain their backing
    planar_numpy = planar_audio.to_numpy()
    interleaved_numpy = interleaved_audio.to_numpy()
    print(f"Planar result is C-contiguous: {planar_numpy.flags.c_contiguous}")
    print(f"Interleaved result is F-contiguous: {interleaved_numpy.flags.f_contiguous}")

    return planar_time, interleaved_time


def test_ndarray_views():
    """Test if ndarray can work with different strides efficiently."""
    print("\nTesting ndarray stride handling...")

    # Create a large 2D array in C-order
    data_c = np.random.randn(2, 100000).astype(np.float32)

    # Create the same data in F-order
    data_f = np.asfortranarray(data_c)

    # Test element-wise operations
    start = time.time()
    result_c = data_c * 2.0 + 1.0
    time_c = time.time() - start

    start = time.time()
    result_f = data_f * 2.0 + 1.0
    time_f = time.time() - start

    print(f"C-order operation: {time_c:.4f}s")
    print(f"F-order operation: {time_f:.4f}s")

    # Verify results are the same
    np.testing.assert_allclose(result_c, result_f, rtol=1e-7)
    print("✓ Results are equivalent")

    return time_c, time_f


if __name__ == "__main__":
    print("Memory Layout Efficiency Investigation")
    print("=" * 50)

    # Test 1: Direct numpy operations
    numpy_planar_time, numpy_interleaved_time = test_numpy_operations_directly()

    # Test 2: Current audio_samples_python implementation
    asp_planar_time, asp_interleaved_time = test_audio_samples_operations()

    # Test 3: Basic ndarray stride handling
    ndarray_c_time, ndarray_f_time = test_ndarray_views()

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    print(f"NumPy direct operations:")
    print(f"  Planar (C-order): {numpy_planar_time:.4f}s")
    print(f"  Interleaved (F-order): {numpy_interleaved_time:.4f}s")
    print(f"  Ratio (F/C): {numpy_interleaved_time/numpy_planar_time:.2f}x")

    print(f"\nAudioSamples operations:")
    print(f"  Planar: {asp_planar_time:.4f}s")
    print(f"  Interleaved: {asp_interleaved_time:.4f}s")
    print(f"  Ratio (Interleaved/Planar): {asp_interleaved_time/asp_planar_time:.2f}x")

    print(f"\nNdarray stride operations:")
    print(f"  C-order: {ndarray_c_time:.4f}s")
    print(f"  F-order: {ndarray_f_time:.4f}s")
    print(f"  Ratio (F/C): {ndarray_f_time/ndarray_c_time:.2f}x")

    if asp_interleaved_time > asp_planar_time * 2:
        print(f"\n⚠️  FINDING: Our current implementation shows {asp_interleaved_time/asp_planar_time:.1f}x slowdown")
        print("   This suggests the deinterleaving/conversion overhead is significant.")
        print("   NumPy can handle the different layouts with minimal overhead.")
    else:
        print(f"\n✓ Our implementation shows reasonable performance parity.")