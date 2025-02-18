# Control System for the Temporal Bragg Experiment

This repository contains a modular **experiment control system** for automating the temporal Bragg experiment with various devices, including the **Muquans laser, the Windfreak RF generator, the wavemeter, a signal generator (using a Red Pitaya), and a spectrum analyzer (Rigol SA)**.

## **Devices**

- **Laser Control**: Enable/disable, adjust EDFA power.
- **RF Generator (Windfreak SynthHD)**: Differential frequency sweep control.
- **Wavemeter**: Reads laser frequency via HTTP API.
- ** Signal Generators** choice between RP or AFG
  - **Red Pitaya (Signal Generator)**: Generates trigger pulses and provides a DC voltage.
  - **Tektro AFG**: Arbitrary waveform generator for the trigger pulse.
- **Rigol Spectrum Analyzer**: Zero-span mode, RBW/VBW, trigger, and sweep control.
- **Modular Design**: Each device has an independent driver.
- **Full Experiment Automation**: Connects, configures, runs, and shuts down the experiment.

---

## **Project Structure**

- Bragg_Omega/
  - devices/
    - `MuquansLaser.py` # Laser driver (Telnet)
    - `RFGenerator.py` # RF Generator driver (Windfreak SynthHD)
    - `WaveMeter.py` # Wavemeter driver (HTTP API)
    - `RPSignalGenerator.py` # Red Pitaya Signal Generator driver
    - `TektroAFG.py` # Tektro AFG Signal Generator driver
    - `RigolSA.py` # Rigol Spectrum Analyzer driver (LAN)
  - `bragg.py` # Main script orchestrating the experiment
  - `README.md` # Project documentation
  - `requirements.txt` # Python dependencies

---

## **Installation**

1. **Clone the repository**

   ```bash
   git clone https://github.com/quentinglorieux/Bragg_omega.git
   cd Bragg_omega
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   Required packages:

   - `pyvisa` (SCPI control)
   - `requests` (Wavemeter API)
   - `numpy` (Data processing)
   - `matplotlib` (Plotting)
   - `telnetlib` (Telnet control)
   - `windfreak` (Windfreak SynthHD control)

## Usage

### Running the Experiment

The main script initializes all devices, configures them, and runs the experiment.

```bash
python bragg.py
```

### Customizing Experiment Parameters

You can configure the experiment using the ExperimentController class and the set_experiment method in `bragg.py`.

Example:

```python
# Signal generator: "RP" (Red Pitaya) or "AFG" (Tektronix AFG3000C)
signal_gen_choice = "AFG"
exp = ExperimentController(signal_generator=signal_gen_choice)

exp.set_experiment(
    edfa_power=1.2, # EDFA power
    f_low=800e6,  # Start frequency for the sweep
    f_high=2500e6, # End frequency for the sweep
    f_step=5e6, # Frequency step
    diff_freq=10e6, # Differential frequency between A and B
    step_time=2e-3, # Time per step
    trigger_high=1.8, # Trigger high level for the RedPitaya
    trigger_low=0.0, # Trigger low level for the RedPitaya
    trigger_duty=90, # Trigger duty cycle
    sa_center_freq=10e6, # Center frequency for the SA
    rbw=1e3, # Resolution bandwidth
    vbw=1e3, # Video bandwidth
    sa_sweep_time=2 # Sweep time for the SA (not used)
)
```

By default the sweep period on the RedPitaya is set to 1.1 times the sweep duration.
`period=1.1 * sweep_duration, # Period of the trigger pulse`

### Device-Specific Controls

#### Laser Control

The laser is controlled over Telnet.

```python
self.laser.seed_on()
self.laser.set_edfa_power(1.0) # Set power to 1.0
self.laser.shutdown()
```

### RF Generator (Windfreak SynthHD)

Configure frequency sweep.

```python
self.rf_gen.configure_differential_sweep(
f_low=750e6, f_high=3000e6, f_step=2e6, diff_freq=5e6, step_time=1e-3, trigger_mode="full_sweep"
)
```

### Wavemeter

The wavemeter reads frequency via HTTP API.

```python
freq = self.wavemeter.get_frequency(channel=3)
print(f"Laser frequency: {freq} Hz")
```

### Tektro AFG (Signal Generator)

Set trigger pulses.

```python
self.signal_gen.set_trigger_pulse(high_level=1.8, low_level=0.0, period=1e-3, duty_cycle=50)
self.signal_gen.set_dc_voltage(1.5) # Voltage between -5V and +5V
```

### Alternative: Red Pitaya (Signal Generator)
Same syntax as the Tektro AFG.
Set trigger pulses and DC control voltage.

```python
self.signal_gen.set_trigger_pulse(high_level=1.8, low_level=0.0, period=1e-3, duty_cycle=50)
self.signal_gen.set_dc_voltage(1.5) # Voltage between 0V - 1.8V
```

### Rigol Spectrum Analyzer (SA)

Configure and fetch data from the SA.

```python
self.sa.set_center_frequency(5e6)
self.sa.set_rbw_vbw(rbw_hz=1e3, vbw_hz=1e3)
self.sa.enable_zero_span_mode()
self.sa.set_sweep_time(1)
self.sa.set_trigger(mode="EXT", edge="POS")
trace_data = self.sa.fetch_trace()
print(trace_data)
```

## Full Experiment Workflow

The script follows this workflow:

1. Connect to devices (connect_all)
2. Configure experiment (set_experiment)
3. Run measurement loop (run_experiment) # Commented for now
4. Shutdown all devices safely (shutdown)
