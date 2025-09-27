import os
import time
from datetime import datetime
from functools import lru_cache
from typing import List

import cv2
import easyocr
import torch

DEFAULT_NUM_THREADS = int(os.environ.get("OCR_THREADS", "2"))
os.environ.setdefault("OMP_NUM_THREADS", str(DEFAULT_NUM_THREADS))
os.environ.setdefault("OPENBLAS_NUM_THREADS", str(DEFAULT_NUM_THREADS))

torch.set_num_threads(DEFAULT_NUM_THREADS)
torch.set_num_interop_threads(1)

LANGUAGES: List[str] = ['en']


@lru_cache(maxsize=1)
def _get_easyocr_reader() -> easyocr.Reader:
    """Return a cached EasyOCR reader optimised for CPU-only inference."""
    return easyocr.Reader(LANGUAGES, gpu=False)

def detect_text(image_path: str, gpu: bool = False) -> List[str]:
    """
    Detect and return English text from an image using EasyOCR.

    Args:
        image_path (str): Path to the image file.
        gpu (bool): Whether to use GPU for inference.

    Returns:
        List[str]: List of detected text strings.
    """
    start_time = time.time()
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    if gpu:
        print("GPU acceleration requested but not available; falling back to CPU-only reader.")
    reader = _get_easyocr_reader()

    results = reader.readtext(image)
    elapsed = time.time() - start_time

    print(f"OCR on '{image_path}' completed in {elapsed:.3f} seconds")
    return [text for _, text, _ in results]

def benchmark_ocr_quality(image_path: str, output_file: str = "ocr_benchmark_results.txt", gpu: bool = False):
    """
    Benchmark OCR performance across different image resolutions.
    
    Args:
        image_path (str): Path to the original image file.
        output_file (str): Path to save benchmark results.
        gpu (bool): Whether to use GPU for inference.
    """
    if gpu:
        print("GPU benchmark requested but this device will run OCR on CPU only. Reusing cached reader.")

    # Load original image
    original_image = cv2.imread(image_path)
    if original_image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    original_height, original_width = original_image.shape[:2]
    
    # Define three different scale factors for testing
    scale_factors = [1.0, 0.5, 0.25]  # Full, Half, Quarter resolution
    
    # Create temporary directory for scaled images
    temp_dir = "temp_benchmark_images"
    os.makedirs(temp_dir, exist_ok=True)
    
    results = []
    
    print(f"Starting benchmark for image: {image_path}")
    print(f"Original resolution: {original_width}x{original_height}")
    
    try:
        for i, scale in enumerate(scale_factors):
            # Calculate new dimensions
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
            # Resize image
            scaled_image = cv2.resize(original_image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Save temporary scaled image
            temp_image_path = os.path.join(temp_dir, f"scaled_{scale:.2f}_{os.path.basename(image_path)}")
            cv2.imwrite(temp_image_path, scaled_image)
            
            print(f"\nTesting resolution {i+1}/3: {new_width}x{new_height} (scale: {scale:.2f})")
            
            # Measure OCR performance
            start_time = time.time()
            try:
                detected_text = detect_text(temp_image_path, gpu)
                end_time = time.time()
                execution_time = end_time - start_time
                
                result = {
                    'scale_factor': scale,
                    'resolution': f"{new_width}x{new_height}",
                    'execution_time': execution_time,
                    'detected_text': detected_text,
                    'text_count': len(detected_text),
                    'success': True
                }
                
                print(f"Execution time: {execution_time:.3f} seconds")
                print(f"Detected {len(detected_text)} text elements")
                
            except Exception as e:
                result = {
                    'scale_factor': scale,
                    'resolution': f"{new_width}x{new_height}",
                    'execution_time': 0,
                    'detected_text': [],
                    'text_count': 0,
                    'success': False,
                    'error': str(e)
                }
                print(f"Error during OCR: {e}")
            
            results.append(result)
            
            # Clean up temporary file
            os.remove(temp_image_path)
    
    finally:
        # Clean up temporary directory
        try:
            os.rmdir(temp_dir)
        except:
            pass
    
    # Write results to file
    with open(output_file, 'w') as f:
        f.write(f"OCR Benchmark Results\n")
        f.write(f"{'='*50}\n")
        f.write(f"Original Image: {image_path}\n")
        f.write(f"Original Resolution: {original_width}x{original_height}\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Language(s): {', '.join(LANGUAGES)}\n")
        f.write(f"GPU Enabled: {False}\n\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"Test {i}: Resolution {result['resolution']} (Scale: {result['scale_factor']:.2f})\n")
            f.write(f"{'-'*40}\n")
            
            if result['success']:
                f.write(f"Execution Time: {result['execution_time']:.3f} seconds\n")
                f.write(f"Text Elements Detected: {result['text_count']}\n")
                f.write(f"Detected Text:\n")
                if result['detected_text']:
                    for j, text in enumerate(result['detected_text'], 1):
                        f.write(f"  {j}. {text}\n")
                else:
                    f.write("  No text detected\n")
            else:
                f.write(f"Status: FAILED\n")
                f.write(f"Error: {result.get('error', 'Unknown error')}\n")
            
            f.write(f"\n")
        
        # Summary
        f.write(f"Summary\n")
        f.write(f"{'='*50}\n")
        successful_tests = [r for r in results if r['success']]
        if successful_tests:
            avg_time = sum(r['execution_time'] for r in successful_tests) / len(successful_tests)
            f.write(f"Average Execution Time: {avg_time:.3f} seconds\n")
            f.write(f"Fastest Test: {min(successful_tests, key=lambda x: x['execution_time'])['resolution']} "
                   f"({min(r['execution_time'] for r in successful_tests):.3f}s)\n")
            f.write(f"Slowest Test: {max(successful_tests, key=lambda x: x['execution_time'])['resolution']} "
                   f"({max(r['execution_time'] for r in successful_tests):.3f}s)\n")
        else:
            f.write("No successful tests completed.\n")
    
    print(f"\nBenchmark completed! Results saved to: {output_file}")
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python OCR/piOCR.py <image_path>                     - Run OCR on single image")
        print("  python OCR/piOCR.py <image_path> --benchmark         - Run benchmark test (CPU)")
        print("  python OCR/piOCR.py <image_path> --gpu               - Request GPU (ignored on Raspberry Pi)")
        print("  python OCR/piOCR.py <image_path> --benchmark --gpu   - Benchmark with GPU flag (ignored)")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Check if benchmark mode is requested
    gpu_requested = "--gpu" in sys.argv
    if gpu_requested:
        print("GPU flag detected but this build will run EasyOCR on CPU only.")

    if "--benchmark" in sys.argv:
        print("Running benchmark mode")
        benchmark_ocr_quality(image_path, gpu=gpu_requested)
    else:
        # Regular OCR mode
        detected_text = detect_text(image_path, gpu=gpu_requested)
        print("Detected text:", detected_text)