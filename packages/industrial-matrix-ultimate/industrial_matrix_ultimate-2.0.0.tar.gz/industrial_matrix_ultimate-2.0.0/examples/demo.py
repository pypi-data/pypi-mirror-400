#!/usr/bin/env python3
"""
Industrial Matrix Library Demo
Demonstrates the capabilities of the industrial_matrix library
"""

import industrial_matrix as im
import numpy as np
import time

def print_section(title):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def demo_system_info():
    """Display system capabilities"""
    print_section("System Information")
    info = im.system_info()
    for key, value in info.items():
        print(f"  {key:15s}: {value}")

def demo_basic_operations():
    """Demonstrate basic matrix operations"""
    print_section("Basic Matrix Operations")
    
    # Create matrices
    A = im.MatrixF64.random(3, 3, 0.0, 10.0)
    B = im.MatrixF64.ones(3, 3)
    
    print("\nMatrix A:")
    A.print()
    
    print("\nMatrix B:")
    B.print()
    
    # Operations
    print("\nA + B:")
    (A + B).print()
    
    print("\nA @ B (matrix multiplication):")
    (A @ B).print()
    
    print("\nA.transpose():")
    A.transpose().print()
    
    print(f"\nFrobenius norm of A: {A.frobenius_norm():.4f}")
    print(f"Sum of all elements in A: {A.sum():.4f}")

def demo_numpy_integration():
    """Demonstrate NumPy interoperability"""
    print_section("NumPy Integration")
    
    # Create NumPy array
    np_array = np.array([[1, 2, 3],
                         [4, 5, 6],
                         [7, 8, 9]], dtype=np.float64)
    
    print("\nOriginal NumPy array:")
    print(np_array)
    
    # Convert to Matrix
    matrix = im.MatrixF64.from_numpy(np_array)
    print("\nConverted to Matrix:")
    matrix.print()
    
    # Perform operations
    result = matrix.transpose()
    print("\nAfter transpose:")
    result.print()
    
    # Convert back to NumPy
    np_result = result.to_numpy()
    print("\nConverted back to NumPy:")
    print(np_result)

def demo_performance():
    """Benchmark matrix multiplication performance"""
    print_section("Performance Benchmark")
    
    sizes = [128, 256, 512, 1024]
    
    print(f"\n{'Size':>8s} {'Time (ms)':>12s} {'GFLOPS':>12s}")
    print('-' * 35)
    
    for size in sizes:
        result = im.benchmark(size, trials=5)
        print(f"{result['size']:>8d} {result['time_ms']:>12.2f} {result['gflops']:>12.2f}")

def demo_factory_methods():
    """Demonstrate factory methods"""
    print_section("Factory Methods")
    
    print("\nZeros matrix (3x3):")
    im.MatrixF64.zeros(3, 3).print()
    
    print("\nOnes matrix (3x3):")
    im.MatrixF64.ones(3, 3).print()
    
    print("\nIdentity matrix (4x4):")
    im.MatrixF64.identity(4).print()
    
    print("\nRandom matrix (3x3, range [0, 1]):")
    im.MatrixF64.random(3, 3, 0.0, 1.0).print()

def demo_large_computation():
    """Demonstrate computation with larger matrices"""
    print_section("Large Matrix Computation")
    
    size = 500
    print(f"\nCreating two {size}x{size} random matrices...")
    
    A = im.MatrixF64.random(size, size)
    B = im.MatrixF64.random(size, size)
    
    print("Performing matrix multiplication...")
    start = time.time()
    C = A @ B
    elapsed = time.time() - start
    
    gflops = (2.0 * size ** 3) / elapsed / 1e9
    
    print(f"Computation time: {elapsed*1000:.2f} ms")
    print(f"Performance: {gflops:.2f} GFLOPS")
    print(f"Result shape: {C.shape()}")
    print(f"Result Frobenius norm: {C.frobenius_norm():.4f}")

def demo_comparison_with_numpy():
    """Compare performance with NumPy"""
    print_section("Comparison with NumPy")
    
    size = 512
    print(f"\nMatrix size: {size}x{size}")
    
    # Create NumPy arrays
    A_np = np.random.rand(size, size)
    B_np = np.random.rand(size, size)
    
    # NumPy timing
    print("\nNumPy matrix multiplication...")
    start = time.time()
    C_np = A_np @ B_np
    numpy_time = time.time() - start
    
    # Industrial Matrix timing
    print("Industrial Matrix multiplication...")
    A_im = im.MatrixF64.from_numpy(A_np)
    B_im = im.MatrixF64.from_numpy(B_np)
    
    start = time.time()
    C_im = A_im @ B_im
    im_time = time.time() - start
    
    # Results
    print(f"\nNumPy time:             {numpy_time*1000:.2f} ms")
    print(f"Industrial Matrix time: {im_time*1000:.2f} ms")
    print(f"Speedup:                {numpy_time/im_time:.2f}x")
    
    # Verify correctness
    C_im_np = C_im.to_numpy()
    max_diff = np.max(np.abs(C_np - C_im_np))
    print(f"\nMax difference: {max_diff:.2e}")
    print("✓ Results match!" if max_diff < 1e-10 else "✗ Results differ!")

def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("  INDUSTRIAL MATRIX LIBRARY - DEMONSTRATION")
    print("="*60)
    
    try:
        demo_system_info()
        demo_factory_methods()
        demo_basic_operations()
        demo_numpy_integration()
        demo_large_computation()
        demo_performance()
        demo_comparison_with_numpy()
        
        print("\n" + "="*60)
        print("  All demos completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
