import numpy as np
import time
import psutil
import os
from src.corrupt_tta import corrupt, corruption_dict

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024) # MB

def test_performance():
    print("Starting Performance and Memory Test...")
    img = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
    
    initial_mem = get_memory_usage()
    print(f"Initial Memory: {initial_mem:.2f} MB")
    
    batch_size = 100
    results = []
    
    for name in corruption_dict.keys():
        start_time = time.time()
        for _ in range(batch_size):
            _ = corrupt(img, severity=3, corruption_name=name)
        end_time = time.time()
        
        total_time = end_time - start_time
        fps = batch_size / total_time
        current_mem = get_memory_usage()
        
        results.append({
            "Corruption": name,
            "Total Time (100 imgs)": total_time,
            "FPS": fps,
            "Memory": current_mem
        })
        print(f"{name:20} | Time: {total_time:6.2f}s | FPS: {fps:6.1f} | Mem: {current_mem:6.2f} MB")

    final_mem = get_memory_usage()
    print(f"\nFinal Memory: {final_mem:.2f} MB")
    print(f"Memory Growth: {final_mem - initial_mem:.2f} MB")

if __name__ == "__main__":
    test_performance()
