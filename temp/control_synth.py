from windfreak import SynthHD

class SynthHDController:
    """
    This class manages the Windfreak SynthHD RF generator,
    following the structure of RFGenerator to be fully compatible with ExperimentController.
    """

    def __init__(self, port="COM4"):
        """Initialize the SynthHD and establish a connection."""
        try:
            self.synth = SynthHD(port)
            print(f"✅ SynthHD connected on {port}")
        except Exception as e:
            print(f"❌ Connection error with SynthHD on {port}: {e}")
            self.synth = None

    def configure_differential_sweep(self, f_low=750e6, f_high=3000e6, f_step=2e6, diff_freq=5e6, 
                                     power_ch0=8, power_ch1=5, step_time=1e-3, trigger_mode="full frequency sweep"):
        """
        Configure the differential sweep on SynthHD to match RFGenerator in ExperimentController.

        Args:
            f_low (float): Start frequency (Hz).
            f_high (float): Stop frequency (Hz).
            f_step (float): Frequency step (Hz).
            diff_freq (float): Differential frequency (Hz).
            power_ch0 (float): Power level for channel 0 (dBm).
            power_ch1 (float): Power level for channel 1 (dBm).
            step_time (float): Time spent per step (s).
            trigger_mode (str): Trigger mode for the sweep.
        """
        if not self.synth:
            print("⚠️ SynthHD not connected, cannot configure.")
            return

        try:
            # Convert Hz to MHz for Windfreak SynthHD API compatibility
            f_low_mhz = f_low / 1e6
            f_high_mhz = f_high / 1e6
            f_step_mhz = f_step / 1e6
            diff_freq_mhz = diff_freq / 1e6

            # 🔹 Configure Channel 0
            self.synth.write("channel", 0)
            self.synth.write("rf_enable", True)  # Enable RF Output
            
            try:
                status = self.synth.read("rf_enable")  # Lire le statut RF
                print(f"🔍 RF Output Status: {'ON' if status else 'OFF'}")
            except Exception as e:
                print(f"❌ Error reading RF output status: {e}")
            self.synth.write("sweep_freq_low", f_low_mhz)
            self.synth.write("sweep_freq_high", f_high_mhz)
            self.synth.write("sweep_freq_step", f_step_mhz)
            self.synth.write("sweep_power_low", power_ch0)
            self.synth.write("sweep_power_high", power_ch0)
            self.synth.write("sweep_time_step", step_time)  # ✅ Ensure step time is configured

            # 🔹 Configure Channel 1
            self.synth.write("channel", 1)
            self.synth.write("sweep_freq_low", f_low_mhz)
            self.synth.write("sweep_freq_high", f_high_mhz)
            self.synth.write("sweep_freq_step", f_step_mhz)
            self.synth.write("sweep_power_low", power_ch1)
            self.synth.write("sweep_power_high", power_ch1)
            self.synth.write("sweep_time_step", step_time)  # ✅ Apply step time to channel 1
            # 🔹 Configure differential sweep
            self.synth.write("sweep_diff_meth", 1)
            self.synth.write("sweep_diff_freq", diff_freq_mhz)            
            # 🔹 Activate the sweep
            self.synth.write("trig_function", 1)            
            self.synth.sweep_enable = False
            print(f"✅ SynthHD sweep activated: {f_low_mhz}-{f_high_mhz} MHz, Δf={diff_freq_mhz} MHz, Step time={step_time}s, P0={power_ch0} dBm, P1={power_ch1} dBm.")

        except Exception as e:
            print(f"❌ Error configuring SynthHD: {e}")

    def shutdown(self):
        """Disable the sweep and properly close the connection."""
        if not self.synth:
            return

        try:
            self.synth.sweep_enable = False  # Disable sweep
            print("✅ SynthHD sweep stopped.")
        except Exception as e:
            print(f"⚠️ Error stopping SynthHD sweep: {e}")
