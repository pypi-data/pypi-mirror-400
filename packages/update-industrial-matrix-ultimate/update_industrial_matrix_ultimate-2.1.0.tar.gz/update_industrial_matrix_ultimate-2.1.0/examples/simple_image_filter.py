#!/usr/bin/env python3
"""
Simplified Image Processing Example
Safe version using basic operations only
"""

import industrial_matrix as im
import numpy as np
import cv2

def main():
    print("="*60)
    print("  INDUSTRIAL MATRIX - Image Processing Example")
    print("="*60)
    
    # System info
    info = im.system_info()
    print(f"\n🖥️  System Info:")
    print(f"   OpenMP: {info['openmp']} ({info['threads']} threads)")
    print(f"   SIMD: {info['simd']}")
    
    # Create a simple test image
    print("\n📸 Creating test image (300x300)...")
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    
    # Add gradients
    for i in range(300):
        for j in range(300):
            img[i, j, 0] = int((i / 300) * 255)  # Blue gradient
            img[i, j, 1] = int((j / 300) * 255)  # Green gradient
            img[i, j, 2] = 128  # Constant red
    
    # Add circle
    cv2.circle(img, (150, 150), 60, (255, 255, 0), -1)
    cv2.putText(img, "TEST", (100, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    
    # Save original
    cv2.imwrite('original.jpg', img)
    print("✅ Saved: original.jpg")
    
    # Convert to grayscale
    print("\n🔄 Converting to grayscale...")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Process with Industrial Matrix - Brightness adjustment
    print("✨ Adjusting brightness (1.3x)...")
    mat_gray = im.MatrixF64.from_numpy(gray.astype(np.float64))
    bright_mat = mat_gray.scalar_multiply(1.3)
    bright = np.clip(bright_mat.to_numpy(), 0, 255).astype(np.uint8)
    
    bright_color = cv2.cvtColor(bright, cv2.COLOR_GRAY2BGR)
    cv2.imwrite('bright.jpg', bright_color)
    print("✅ Saved: bright.jpg")
    
    # Darken
    print("🌙 Adjusting brightness (0.7x)...")
    dark_mat = mat_gray.scalar_multiply(0.7)
    dark = np.clip(dark_mat.to_numpy(), 0, 255).astype(np.uint8)
    
    dark_color = cv2.cvtColor(dark, cv2.COLOR_GRAY2BGR)
    cv2.imwrite('dark.jpg', dark_color)
    print("✅ Saved: dark.jpg")
    
    # Inverse 
    print("🔄 Creating negative image...")
    ones_mat = im.MatrixF64.ones(gray.shape[0], gray.shape[1])
    max_mat = ones_mat.scalar_multiply(255.0)
    neg_mat = mat_gray.scalar_multiply(-1.0)
    negative_mat = max_mat.elementwise_add(neg_mat)
    negative = np.clip(negative_mat.to_numpy(), 0, 255).astype(np.uint8)
    
    negative_color = cv2.cvtColor(negative, cv2.COLOR_GRAY2BGR)
    cv2.imwrite('negative.jpg', negative_color)
    print("✅ Saved: negative.jpg")
    
    # Create comparison
    print("\n📊 Creating comparison collage...")
    row1 = np.hstack([img, bright_color])
    row2 = np.hstack([dark_color, negative_color])
    collage = np.vstack([row1, row2])
    
    # Add labels
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(collage, "ORIGINAL", (10, 30), font, 0.7, (255, 255, 255), 2)
    cv2.putText(collage, "BRIGHT", (310, 30), font, 0.7, (255, 255, 255), 2)
    cv2.putText(collage, "DARK", (10, 330), font, 0.7, (255, 255, 255), 2)
    cv2.putText(collage, "NEGATIVE", (310, 330), font, 0.7, (255, 255, 255), 2)
    
    cv2.imwrite('comparison.jpg', collage)
    print("✅ Saved: comparison.jpg")
    
    # Performance test
    print("\n⚡ Performance Test:")
    result = im.benchmark(256, trials=3)
    print(f"   Matrix size: 256x256")
    print(f"   Time: {result['time_ms']:.2f} ms")
    print(f"   Performance: {result['gflops']:.2f} GFLOPS")
    
    print("\n" + "="*60)
    print("  ✅ COMPLETE! Check the generated images:")
    print("     • original.jpg")
    print("     • bright.jpg")
    print("     • dark.jpg")
    print("     • negative.jpg")
    print("     • comparison.jpg")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
