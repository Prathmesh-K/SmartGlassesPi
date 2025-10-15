#!/usr/bin/env python3
"""
Memory monitoring script for SmartGlasses project
"""

import os
import subprocess
import psutil
import time

def get_memory_info():
    """Get detailed memory information"""
    # System memory info
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    print(f"📊 Memory Status")
    print(f"=" * 40)
    print(f"💾 Total RAM: {mem.total / (1024**3):.1f} GB")
    print(f"🟢 Available: {mem.available / (1024**3):.1f} GB ({mem.percent:.1f}% used)")
    print(f"🔴 Used: {mem.used / (1024**3):.1f} GB")
    print(f"🟡 Free: {mem.free / (1024**3):.1f} GB")
    print(f"📀 Swap: {swap.used / (1024**3):.1f} GB / {swap.total / (1024**3):.1f} GB")
    
    return mem, swap

def get_process_memory():
    """Get memory usage of current processes"""
    print(f"\n🔍 Top Memory Users:")
    print(f"-" * 40)
    
    # Get top 5 processes by memory
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Sort by memory percentage
    top_processes = sorted(processes, key=lambda x: x['memory_percent'] or 0, reverse=True)[:5]
    
    for proc in top_processes:
        memory_mb = (proc['memory_info'].rss / (1024**2)) if proc['memory_info'] else 0
        memory_pct = proc['memory_percent'] or 0
        print(f"{proc['name'][:20]:20} {memory_mb:6.1f} MB ({memory_pct:4.1f}%)")

def monitor_python_process():
    """Monitor current Python process"""
    current_process = psutil.Process()
    memory_info = current_process.memory_info()
    
    print(f"\n🐍 Current Python Process:")
    print(f"-" * 40)
    print(f"Memory: {memory_info.rss / (1024**2):.1f} MB")
    print(f"Virtual: {memory_info.vms / (1024**2):.1f} MB")

def check_available_for_ocr():
    """Check if enough memory is available for OCR"""
    mem = psutil.virtual_memory()
    available_gb = mem.available / (1024**3)
    
    print(f"\n🤖 SmartGlasses Memory Check:")
    print(f"-" * 40)
    
    # EasyOCR typically needs 1-2GB
    if available_gb >= 2.0:
        print(f"✅ Sufficient memory for full workflow ({available_gb:.1f} GB available)")
    elif available_gb >= 1.0:
        print(f"⚠️ Limited memory - may work but could be slow ({available_gb:.1f} GB available)")
    else:
        print(f"❌ Low memory - OCR likely to fail ({available_gb:.1f} GB available)")
        print(f"💡 Consider:")
        print(f"   - Closing other applications")
        print(f"   - Adding swap space")
        print(f"   - Using lighter OCR models")

def continuous_monitor(seconds=10):
    """Monitor memory usage continuously"""
    print(f"\n🔄 Monitoring memory for {seconds} seconds...")
    print(f"Press Ctrl+C to stop")
    
    try:
        for i in range(seconds):
            mem = psutil.virtual_memory()
            print(f"Memory: {mem.percent:4.1f}% used, {mem.available/(1024**3):4.1f} GB free", end='\r')
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n🛑 Monitoring stopped")

if __name__ == "__main__":
    import sys
    
    print("🖥️ SmartGlasses Memory Monitor")
    print("=" * 50)
    
    # Basic memory info
    get_memory_info()
    
    # Process info
    get_process_memory()
    
    # Current Python process
    monitor_python_process()
    
    # OCR readiness check
    check_available_for_ocr()
    
    # Continuous monitoring option
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        continuous_monitor(30)
    else:
        print(f"\n💡 Run with 'monitor' argument for continuous monitoring")
        print(f"   python3 memory_check.py monitor")