#!/usr/bin/env python3
"""
Test to specifically investigate the deinterleaving conversion overhead
mentioned in src/lib.rs lines 5578-5583.
"""

import numpy as np
import time
import audio_samples_python as asp


def create_forced_interleaved_data():
    """Create data that will be stored as NumpyInterleaved internally."""
    channels = 2
    frames = 44100 * 5  # 5 seconds

    # Create interleaved data - this should trigger NumpyInterleaved storage
    # when passed to from_array
    data = np.random.randn(frames, channels).astype(np.float32)
    data_interleaved = np.asfortranarray(data)  # F-contiguous

    # Create equivalent planar data
    data_planar = data.T  # Transpose to get (channels, frames)
    data_planar = np.ascontiguousarray(data_planar)  # Ensure C-contiguous

    return data_planar, data_interleaved


def test_views_vs_operations():
    """Test the difference between just creating views and doing operations."""
    print("Testing view creation vs operations with different layouts")

    planar, interleaved = create_forced_interleaved_data()

    print(f"Planar shape: {planar.shape}, C-contiguous: {planar.flags.c_contiguous}")
    print(f"Interleaved shape: {interleaved.shape}, F-contiguous: {interleaved.flags.f_contiguous}")

    # Test 1: Just create AudioSamples objects (should be fast)
    start = time.time()
    planar_audio = asp.AudioSamples.from_array(planar, 44100)
    planar_creation_time = time.time() - start

    start = time.time()
    interleaved_audio = asp.AudioSamples.from_array(interleaved, 44100)
    interleaved_creation_time = time.time() - start

    print(f"\nCreation times:")
    print(f"  Planar: {planar_creation_time:.6f}s")
    print(f"  Interleaved: {interleaved_creation_time:.6f}s")

    # Test 2: Convert back to numpy (should trigger conversion for interleaved)
    start = time.time()
    planar_numpy = planar_audio.to_numpy()
    planar_conversion_time = time.time() - start

    start = time.time()
    interleaved_numpy = interleaved_audio.to_numpy()
    interleaved_conversion_time = time.time() - start

    print(f"\nto_numpy() times:")
    print(f"  Planar: {planar_conversion_time:.6f}s")
    print(f"  Interleaved: {interleaved_conversion_time:.6f}s")

    # Test 3: Perform operation that requires views (should trigger deinterleaving)
    # Use multiple operations to amplify the effect
    ops_count = 10

    start = time.time()
    for _ in range(ops_count):
        peak = planar_audio.peak()
    planar_ops_time = time.time() - start

    start = time.time()
    for _ in range(ops_count):
        peak = interleaved_audio.peak()
    interleaved_ops_time = time.time() - start

    print(f"\n{ops_count}x peak() operations:")
    print(f"  Planar: {planar_ops_time:.6f}s ({planar_ops_time/ops_count*1000:.2f}ms per op)")
    print(f"  Interleaved: {interleaved_ops_time:.6f}s ({interleaved_ops_time/ops_count*1000:.2f}ms per op)")

    if interleaved_ops_time > planar_ops_time * 1.5:
        print(f"\n⚠️  SIGNIFICANT OVERHEAD: Interleaved operations are {interleaved_ops_time/planar_ops_time:.1f}x slower")
        print("   This suggests deinterleaving conversion is happening on each operation.")
    else:
        print(f"\n✓ Reasonable performance: Ratio is {interleaved_ops_time/planar_ops_time:.1f}x")

    return (planar_creation_time, interleaved_creation_time,
            planar_conversion_time, interleaved_conversion_time,
            planar_ops_time, interleaved_ops_time)


def test_operation_with_large_data():
    """Test with larger data to make conversion overhead more apparent."""
    print("\n" + "="*60)
    print("Testing with larger dataset (20 seconds of audio)")

    channels = 2
    frames = 44100 * 20  # 20 seconds

    data = np.random.randn(frames, channels).astype(np.float32)
    data_interleaved = np.asfortranarray(data)  # F-contiguous
    data_planar = np.ascontiguousarray(data.T)  # C-contiguous (channels, frames)

    planar_audio = asp.AudioSamples.from_array(data_planar, 44100)
    interleaved_audio = asp.AudioSamples.from_array(data_interleaved, 44100)

    # Test an operation that should trigger with_view many times
    operations = ['peak', 'rms', 'mean']

    for op_name in operations:
        print(f"\nTesting {op_name}() operation:")

        op = getattr(planar_audio, op_name)
        start = time.time()
        result_planar = op()
        planar_time = time.time() - start

        op = getattr(interleaved_audio, op_name)
        start = time.time()
        result_interleaved = op()
        interleaved_time = time.time() - start

        print(f"  Planar: {planar_time:.4f}s")
        print(f"  Interleaved: {interleaved_time:.4f}s")
        print(f"  Ratio: {interleaved_time/planar_time:.2f}x")

        # Verify results are equivalent
        if isinstance(result_planar, (int, float)):
            assert abs(result_planar - result_interleaved) < 1e-5, f"Results differ: {result_planar} vs {result_interleaved}"
        else:
            np.testing.assert_allclose(result_planar, result_interleaved, rtol=1e-5)


if __name__ == "__main__":
    print("Investigating Interleaving/Deinterleaving Conversion Overhead")
    print("=" * 60)

    results = test_views_vs_operations()
    test_operation_with_large_data()

    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)

    (planar_creation, interleaved_creation,
     planar_conversion, interleaved_conversion,
     planar_ops, interleaved_ops) = results

    print("Key findings:")
    print(f"1. Creation overhead: {interleaved_creation/planar_creation:.1f}x for interleaved")
    print(f"2. to_numpy() overhead: {interleaved_conversion/planar_conversion:.1f}x for interleaved")
    print(f"3. Operation overhead: {interleaved_ops/planar_ops:.1f}x for interleaved")

    if interleaved_ops > planar_ops * 2:
        print("\n🔍 CONCLUSION: Significant overhead detected!")
        print("   The deinterleaving conversion in with_view() is creating performance impact.")
        print("   Consider investigating if NumPy can handle F-order arrays directly for operations.")
    elif interleaved_conversion > planar_conversion * 2:
        print("\n🔍 CONCLUSION: Conversion overhead mainly in to_numpy()")
        print("   The overhead is primarily in conversion back to numpy, not in operations.")
    else:
        print("\n✓ CONCLUSION: Current implementation is reasonably efficient")
        print("   No significant overhead detected. Current approach may be optimal.")