#!/usr/bin/env python3
import subprocess
import serial
import time
import os

# Path to the GPIO setup script
GPIO_SETUP_SCRIPT = "./boot_gpio_setup.sh"

# UART configuration (use correct device and baudrate for your setup)
UART_PORT = "/dev/serial0"  # Change if needed
UART_BAUDRATE = 115200

# Run GPIO setup script
subprocess.run([GPIO_SETUP_SCRIPT], check=True)

# Initialize UART
ser = serial.Serial(UART_PORT, UART_BAUDRATE, timeout=None)  # Blocking read
print("UART listener started.")

try:
    while True:
        data = ser.read(size=1)  # Blocking read for 1 byte
        if data:
            instruction = data.decode(errors='ignore').strip()
            print(f"Received instruction: {instruction}")
            if instruction == "SLEEP":
                print("Suspending Pi...")
                os.system("sudo systemctl suspend")
            # Add more instructions as needed
except KeyboardInterrupt:
    print("Exiting main loop.")
finally:
    ser.close()
