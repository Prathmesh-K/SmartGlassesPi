#!/bin/bash

# Placeholder GPIO numbers
WAKE_PIN=17
PI_SIGNAL_PIN=27

# Set WAKE_PIN as input with pull-down resistor
raspi-gpio set $WAKE_PIN ip pd

# Set PI_SIGNAL_PIN as output and set LOW
raspi-gpio set $PI_SIGNAL_PIN op dl

# Example: To set PI_SIGNAL_PIN HIGH (signal PSOC6)
# raspi-gpio set $PI_SIGNAL_PIN op dh

# Enable GPIO wake support for Raspberry Pi 5
if ! grep -q "WAKE_ON_GPIO=$WAKE_PIN" /boot/config.txt; then
    echo "WAKE_ON_GPIO=$WAKE_PIN" | sudo tee -a /boot/config.txt
    echo "Added WAKE_ON_GPIO=$WAKE_PIN to /boot/config.txt"
else
    echo "WAKE_ON_GPIO=$WAKE_PIN already set in /boot/config.txt"
fi

echo "GPIO pins configured for PSOC6 wake/signal and GPIO wake enabled."
