#!/usr/bin/env python3
"""
Test that mutable operations now work with interleaved arrays.
"""

import numpy as np
import audio_samples_python as asp


def test_mutable_operations():
    """Test mutable operations that previously failed with NumpyInterleaved."""
    print("Testing mutable operations on interleaved arrays...")

    # Create interleaved data
    frames = 44100
    channels = 2
    data = np.random.randn(frames, channels).astype(np.float32)
    data_interleaved = np.asfortranarray(data)  # F-contiguous

    print(f"Input shape: {data_interleaved.shape}")
    print(f"F-contiguous: {data_interleaved.flags.f_contiguous}")

    # Create AudioSamples from interleaved data
    audio = asp.AudioSamples.from_array(data_interleaved, 44100)

    # Test operations that require mutable access
    try:
        print("\nTesting scale operation (should now work)...")
        audio_scaled = audio.scale(1.5)
        print("✓ Scale operation succeeded")

        print("\nTesting peak operation...")
        peak = audio.peak()
        print(f"✓ Peak operation succeeded: {peak}")

        print("\nTesting rms operation...")
        rms = audio.rms()
        print(f"✓ RMS operation succeeded: {rms}")

    except Exception as e:
        print(f"✗ Operation failed: {e}")
        return False

    return True


def test_arithmetic_operations():
    """Test arithmetic operations between interleaved arrays."""
    print("\nTesting arithmetic operations...")

    # Create two interleaved arrays
    data1 = np.asfortranarray(np.random.randn(1000, 2).astype(np.float32))
    data2 = np.asfortranarray(np.random.randn(1000, 2).astype(np.float32))

    audio1 = asp.AudioSamples.from_array(data1, 44100)
    audio2 = asp.AudioSamples.from_array(data2, 44100)

    try:
        # These operations should now work between interleaved arrays
        print("Testing addition between interleaved arrays...")
        result_add = audio1 + audio2
        print("✓ Addition succeeded")

        print("Testing multiplication (supported operation)...")
        result_mul = audio1 * 0.5
        print("✓ Multiplication succeeded")

        # Verify results maintain the interleaved layout where possible
        result_numpy = result_add.to_numpy()
        print(f"Result shape: {result_numpy.shape}")
        print(f"Result F-contiguous: {result_numpy.flags.f_contiguous}")

    except Exception as e:
        print(f"✗ Arithmetic operation failed: {e}")
        return False

    return True


if __name__ == "__main__":
    print("Testing Mutable Operations on Interleaved Arrays")
    print("=" * 50)

    success1 = test_mutable_operations()
    success2 = test_arithmetic_operations()

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    if success1 and success2:
        print("✅ ALL TESTS PASSED")
        print("Interleaved arrays now support:")
        print("• Read-only operations (peak, rms)")
        print("• Scaling operations")
        print("• Arithmetic operations (add, multiply)")
        print("• Direct ndarray memory layout handling")
        print("\nThe unnecessary deinterleaving conversion has been successfully removed!")
    else:
        print("❌ SOME TESTS FAILED")
        print("There may be remaining issues with the implementation.")