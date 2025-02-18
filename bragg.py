from devices.MuquansLaser import MuquansLaser
from temp.control_synth import SynthHDController as RFGenerator
from devices.WaveMeter import Wavemeter
from devices.RPSignalGenerator import RedPitayaSignalGenerator
# from devices.TektroAFG import TektronixAFG3000C
from devices.RigolSA import RigolSA
import time
import matplotlib.pyplot as plt


class ExperimentController:
    """
    Orchestrates the experiment by controlling the laser, RF generator, wavemeter,
    signal generator (Red Pitaya or Tektronix AFG3000C), and spectrum analyzer (Rigol SA).
    """

    def __init__(self, signal_generator="AFG"):
        """
        Initialize all devices with their respective connections.

        Args:
            signal_generator (str): Choose between "RP" (Red Pitaya) or "AFG" (Tektronix AFG3000C).
        """
        print("Initializing experiment setup...")

        self.laser = MuquansLaser(host="10.0.2.107", port=23)
        self.rf_gen = RFGenerator(port="COM4")
        self.wavemeter = Wavemeter(base_url="http://localhost:5000")
        self.sa = RigolSA(ip="192.168.0.158")

        # Signal Generator Selection
        if signal_generator.upper() == "RP":
            self.signal_gen = RedPitayaSignalGenerator(ip="192.168.1.100")
            print("Using Red Pitaya as signal generator.")
        elif signal_generator.upper() == "AFG":
            self.signal_gen = TektronixAFG3000C(ip="192.168.0.143")
            print("Using Tektronix AFG3000C as signal generator.")
        else:
            raise ValueError("Invalid signal generator selection! Use 'RP' or 'AFG'.")
        
    def connect_all(self):
        """Connect to all devices."""
        print("\nConnecting to devices...")
        self.laser.connect()
        self.signal_gen.connect()
        self.sa.connect()
        print("All devices connected.")

    def set_experiment(
        self,
        edfa_power=1,
        f_low=750e6,
        f_high=3000e6,
        f_step=2e6,
        diff_freq=5e6,
        power_ch0 = 8,
        power_ch1 = 5,
        step_time=0.1,
        trigger_high=1.8,
        trigger_low=0.0,
        trigger_duty=98,
        dc_voltage=1.5,
        sa_center_freq=5e6,
        rbw=1e3,
        vbw=1e3,
        sa_sweep_time=1,
    ):
        """
        Configures the experiment with fully customizable parameters.

        Args:
            edfa_power (float): EDFA power setting.
            f_low (float): RF Generator - Start Frequency (Hz).
            f_high (float): RF Generator - Stop Frequency (Hz).
            f_step (float): RF Generator - Frequency Step (Hz).
            diff_freq (float): RF Generator - Differential Frequency (Hz).
            step_time (float): RF Generator - Step Time (s).
            trigger_high (float): Red Pitaya - Trigger High Level (V).
            trigger_low (float): Red Pitaya - Trigger Low Level (V).
            trigger_duty (float): Red Pitaya - Trigger Duty Cycle (%).
            sa_center_freq (float): Spectrum Analyzer - Center Frequency (Hz).
            rbw (float): Spectrum Analyzer - Resolution Bandwidth (Hz).
            vbw (float): Spectrum Analyzer - Video Bandwidth (Hz).
            sa_sweep_time (float): Spectrum Analyzer - Sweep Time (s).
        """
        print("\nConfiguring experiment parameters...")

        # Configure laser
        self.laser.seed_on()
        self.laser.set_power(edfa_power)

        # Configure RF generator (Differential Sweep)
        self.rf_gen.configure_differential_sweep(
            f_low=f_low,
            f_high=f_high,
            f_step=f_step,
            diff_freq=diff_freq,
            step_time=step_time,
            trigger_mode="full_sweep",
        )
        sweep_duration = (f_high - f_low) / f_step * step_time
        print(f"RF Generator: Sweep from {f_low/1e6} MHz to {f_high/1e6} MHz")
        print(f"RF Generator: Sweep Duration = {sweep_duration} s")

        # Configure Red Pitaya or AFG (same API) for pulses and DC output
        self.signal_gen.set_trigger_pulse(
            high_level=trigger_high,
            low_level=trigger_low,
            period=1.1 * sweep_duration,
            duty_cycle=trigger_duty,
        )
        self.signal_gen.set_dc_voltage(dc_voltage)

        # Configure Spectrum Analyzer (Rigol)
        self.sa.set_center_frequency(sa_center_freq)
        self.sa.set_rbw_vbw(rbw_hz=rbw, vbw_hz=vbw)
        self.sa.enable_zero_span_mode()
        # self.sa.set_sweep_time(sa_sweep_time)
        self.sa.set_trigger(mode="EXT", edge="POS")

        print("\nExperiment setup completed.")

    def run_experiment(self, num_steps=5, delay=1):
        """
        Runs the experiment by iterating through different control points,
        collecting wavemeter and spectrum analyzer data.
        """
        print("\nStarting experiment loop...")
        results = []

        for step in range(num_steps):
            print(f"\n--- Step {step+1}/{num_steps} ---")

            # Adjust frequency control voltage dynamically
            voltage = (step / (num_steps - 1)) * 1.8  # Ramp from 0V to 1.8V
            self.signal_gen.set_dc_voltage(voltage)

            # Read laser frequency from Wavemeter
            laser_freq = self.wavemeter.get_frequency(channel=0)

            # Trigger single sweep on the SA and fetch data
            self.sa.start_sweep(continuous=False)
            trace_data = self.sa.fetch_trace()

            # Store results
            results.append({
                "step": step,
                "voltage": voltage,
                "laser_frequency": laser_freq,
                "spectrum": trace_data
            })

            # Wait before next step
            time.sleep(delay)

        print("\nExperiment completed.")
        return results

    def shutdown(self):
        """Gracefully shut down all devices."""
        print("\nShutting down experiment...")

        self.laser.shutdown()
        self.rf_gen.shutdown()
        self.signal_gen.disable_outputs()
        self.sa.disconnect()

        self.laser.disconnect()
        self.signal_gen.disconnect()

        print("All devices shut down.")


def plot_results(self, results):
    """
    Plot the experiment results.

    Args:
        results (list): List of dictionaries containing experiment data.
    """
    if not results:
        print("⚠️ No results to plot.")
        return

    steps = [r["step"] for r in results]
    voltages = [r["voltage"] for r in results]
    frequencies = [r["laser_frequency"] for r in results]

    # 🎯 Plot Voltage vs Steps
    plt.figure(figsize=(8, 5))
    plt.plot(steps, voltages, marker='o', linestyle='-', label="Voltage (V)")
    plt.xlabel("Step")
    plt.ylabel("Voltage (V)")
    plt.title("Voltage Variation During Experiment")
    plt.legend()
    plt.grid(True)
    plt.show()

    # 🎯 Plot Laser Frequency vs Steps
    plt.figure(figsize=(8, 5))
    plt.plot(steps, frequencies, marker='s', linestyle='-', color='r', label="Laser Frequency (THz)")
    plt.xlabel("Step")
    plt.ylabel("Laser Frequency (THz)")
    plt.title("Laser Frequency Variation")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    # Signal generator: "RP" (Red Pitaya) or "AFG" (Tektronix AFG3000C)
    signal_gen_choice = "AFG"
    exp = ExperimentController(signal_generator=signal_gen_choice)
    exp.connect_all()
    exp.set_experiment(
        edfa_power=1,
        f_low=750e6, f_high=3000e6, f_step=5e5, diff_freq=5e6,power_ch0=8, power_ch1=5, 
        step_time=0.1, trigger_high=1.8, trigger_low=0.0, trigger_duty=90,
        sa_center_freq=10e6, rbw=1e3, vbw=1e3, sa_sweep_time=2
    )

    # results = exp.run_experiment(num_steps=5, delay=2)
    # exp.shutdown()

    # Print results
    #for r in results:
    #    print(r)
    #exp.plot_results(results)


##RF ENABLE ????
##Bouton on/of du tektronik? 
#timeout pour results avec qu'avant pas de probleme 