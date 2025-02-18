#!/usr/bin/env python3
"""
Set Detuning Procedure

This script loads a calibration LUT (generated previously) that maps Channel 2 voltage to
laser frequency (in GHz). It then calculates the voltage required to achieve a target detuning
(relative to an absolute reference frequency, set here to 384229.0 GHz), sets that voltage on
the Red Pitaya, verifies the resulting laser frequency via the wavemeter, and (optionally)
plots the calibration LUT.

The calibration LUT may be generated using a higher order polynomial fit (e.g. poly order 3).
In this case the inversion is performed numerically.
"""

import time
import json
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from devices.WaveMeter import Wavemeter
from devices.RPSignalGenerator import RedPitayaSignalGenerator

def load_lut(filename):
    """
    Loads the LUT from a JSON file.
    """
    if not os.path.exists(filename):
        print(f"File {filename} does not exist.")
        return None
    with open(filename, 'r') as f:
        lut = json.load(f)
    return lut

def predict_frequency(voltage, lut):
    """
    Uses the LUT's polynomial coefficients to predict the frequency (GHz) for a given voltage.
    """
    coeffs = np.array(lut['poly_coeffs'])
    return np.polyval(coeffs, voltage)

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

def set_target_detuning(rp, detuning, lut, ref_frequency):
    """
    Sets Channel 2 output to achieve a laser frequency corresponding to a desired detuning from an
    absolute reference frequency.

    Args:
        rp (RedPitayaSignalGenerator): Instance to control the RP.
        detuning (float): Desired detuning in GHz (e.g. 2 for 2 GHz).
        lut (dict): Calibration LUT. Its "poly_coeffs" may represent a linear (order 1) or higher
                    order polynomial fit.
        ref_frequency (float): The absolute reference frequency (GHz) to use.
    
    The target frequency is calculated as:
          target_frequency = ref_frequency + detuning
    And the required voltage is determined by solving:
          poly(voltage) = target_frequency
    """
    coeffs = lut.get('poly_coeffs', [])
    target_frequency = ref_frequency + detuning

    if len(coeffs) == 2:
        # Linear case: frequency = a * voltage + b, so voltage = (target_frequency - b) / a
        a, b = coeffs[0], coeffs[1]
        voltage = (target_frequency - b) / a
    else:
        # Higher order: Solve poly(voltage) - target_frequency = 0
        poly_coeffs = np.array(coeffs)
        poly_coeffs[-1] -= target_frequency
        roots = np.roots(poly_coeffs)
        # Filter to only real roots
        real_roots = [r.real for r in roots if np.isreal(r)]
        if not real_roots:
            raise ValueError("No real voltage solution found for the given target frequency.")
        # Optionally, choose the real root within the typical voltage range [-5, 5]
        valid_roots = [r for r in real_roots if -5 <= r <= 5]
        if valid_roots:
            voltage = min(valid_roots, key=lambda r: abs(r))
        else:
            voltage = min(real_roots, key=lambda r: abs(r))
    print(f"Setting target frequency: {target_frequency:.3f} GHz (detuning: {detuning:.3f} GHz) requires voltage: {voltage:.3f} V")
    rp.set_dc_voltage(voltage)
    return voltage, target_frequency

def main(detuning):
    rp = RedPitayaSignalGenerator("10.0.2.102")
    rp.connect()
    wm = Wavemeter(base_url="http://localhost:5000")
    
    lut_filename = "frequency_lut.json"
    lut = load_lut(lut_filename)
    if lut is None:
        print("Calibration LUT not found. Exiting.")
        rp.disconnect()
        return
    
    # Optionally, plot the calibration LUT for visual inspection:
    # plot_lut(lut)
    
    absolute_ref = 384229.0  # GHz
    ref_frequency = absolute_ref
    print(f"Using absolute reference frequency: {ref_frequency:.3f} GHz")
    
    voltage, target_frequency = set_target_detuning(rp, detuning, lut, ref_frequency)
    
    time.sleep(1.0)
    
    measured_frequency = wm.get_frequency(channel=0)
    print(f"Measured frequency from wavemeter: {measured_frequency:.3f} GHz")
    
    error = (target_frequency - measured_frequency) * 1000
    print(f"Frequency error: {error:.0f} MHz") 
    
    rp.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set detuning (in GHz) for the laser.")
    parser.add_argument("detuning", type=float, help="Desired detuning in GHz (e.g., 1 for 1 GHz)")
    args = parser.parse_args()
    main(args.detuning)