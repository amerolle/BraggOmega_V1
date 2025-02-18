#!/usr/bin/env python3
"""
Calibration Scan Procedure
---------------------------
This script performs a calibration scan by sweeping the DC voltage on the Red Pitaya (via the
RedPitayaSignalGenerator class) over a specified range, querying the laser frequency using the
Wavemeter class, and generating a calibration lookup table (LUT). It then saves the LUT to a JSON
file and provides a function to set a target detuning by computing the required voltage from the LUT.

File structure:
  - devices/Wavemeter.py          (contains the Wavemeter class)
  - devices/RpSignalGenerator.py   (contains the RedPitayaSignalGenerator class)
  - procedures/calibScan.py         (this file)
"""

import numpy as np
import matplotlib.pyplot as plt
import time
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from devices.WaveMeter import Wavemeter
from devices.RPSignalGenerator import RedPitayaSignalGenerator

def calibrate_voltage_to_frequency(rp, wm, voltage_min=-5, voltage_max=5, num_steps=21, wait_time=1.0, poly_order=1):
    """
    Sweeps Channel 2 on the Red Pitaya from voltage_min to voltage_max, reads the corresponding
    frequency from the wavemeter, and fits a polynomial to create a LUT.

    Args:
        rp (RedPitayaSignalGenerator): Instance to control the RP.
        wm (Wavemeter): Instance to fetch frequency from the wavemeter.
        voltage_min (float): Starting voltage (default -5 V).
        voltage_max (float): Ending voltage (default 5 V).
        num_steps (int): Number of measurement steps (default 21).
        wait_time (float): Settling time (seconds) after each voltage change.
        poly_order (int): Order of the polynomial fit (default 1 for linear).

    Returns:
        dict: LUT containing 'voltages', 'frequencies', and 'poly_coeffs'.
    """
    voltages = np.linspace(voltage_min, voltage_max, num_steps)
    frequencies = []
    
    for voltage in voltages:
        rp.set_dc_voltage(voltage)
        time.sleep(wait_time)  
        freq = wm.get_frequency(channel=0)
        if freq is None:
            freq = 0
        frequencies.append(freq)
        print(f"Voltage: {voltage:.2f} V -> Measured Frequency: {freq:.3f} Hz")
    
    # Fit a polynomial: frequency = a * voltage + b
    coeffs = np.polyfit(voltages, frequencies, poly_order)
    lut = {
        'voltages': voltages.tolist(),
        'frequencies': frequencies,
        'poly_coeffs': coeffs.tolist()
    }
    return lut

def save_lut(lut, filename):
    """
    Saves the LUT dictionary to a JSON file.
    """
    with open(filename, 'w') as f:
        json.dump(lut, f)
    print(f"LUT saved to {filename}")

def plot_lut(lut):
    """
    Plots the calibration LUT.

    The LUT contains:
      - "voltages": list of voltage setpoints (V)
      - "frequencies": measured frequencies (GHz)
      - "poly_coeffs": polynomial coefficients for the fit

    This function plots the measured data points and the fitted calibration curve.
    """
    voltages = np.array(lut['voltages'])
    frequencies = np.array(lut['frequencies'])
    coeffs = np.array(lut['poly_coeffs'])
    
    # Create a fine voltage axis for the fitted curve.
    voltage_fit = np.linspace(voltages.min(), voltages.max(), 100)
    frequency_fit = np.polyval(coeffs, voltage_fit)
    
    plt.figure(figsize=(8, 6))
    plt.plot(voltages, frequencies, 'o', label='Measured Data')
    plt.plot(voltage_fit, frequency_fit, '-', label='Fitted Curve')
    plt.xlabel('Voltage (V)')
    plt.ylabel('Frequency (GHz)')
    plt.title('Calibration LUT: Voltage vs Frequency')
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    rp = RedPitayaSignalGenerator("10.0.2.102")
    wm = Wavemeter(base_url="http://localhost:5000")
    
    rp.connect()
    
    # Calibration scan settings
    voltage_min = -5   # Start voltage in Volts
    voltage_max = 2.5     # End voltage in Volts
    num_steps = 31      # Sweep in 0.5 V increments
    wait_time = 1.0     # Wait time for stabilization
    
    print("Starting calibration scan...")
    lut = calibrate_voltage_to_frequency(rp, wm, voltage_min, voltage_max, num_steps, wait_time, poly_order=3)
    
    lut_filename = "frequency_lut.json"
    save_lut(lut, lut_filename)
    
    plot_lut(lut)

    rp.disconnect()

if __name__ == "__main__":
    main()