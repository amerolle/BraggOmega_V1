from windfreak import SynthHD


# Methods:
# enable(channel: int) - Enables the RF output for the specified channel.
# disable(channel: int) - Disables the RF output for the specified channel.
# set_frequency(channel: int, frequency: float) - Sets the frequency for the given channel.
# set_power(channel: int, power: float) - Sets the output power for the given channel.
# differential_sweep(f_low: float, f_high: float, f_step: float, diff_freq: float, step_time: float, trigger_mode: str) - Configures a differential sweep.
# enable_sweep(enable: bool) - Enables or disables the continuous frequency sweep.
# set_trigger_mode(mode: str) - Sets the trigger mode for the RF generator.
# read_parameter(channel: int, param: str) - Reads a parameter from the RF generator safely.
# shutdown() - Disables the RF generator and closes the connection.


class RFGenerator:
    """
    Driver for the Windfreak SynthHD RF generator.
    Allows configuring frequency, power, and sweep parameters.
    """

    def __init__(self, port: str = "COM4"):
        """
        Initializes the RF Generator.

        Args:
            port (str): The serial port where the Windfreak SynthHD is connected (e.g., 'COM4' or '/dev/ttyUSB0').
        """
        try:
            self.synth = SynthHD(port)  # Connect via serial
            self.synth.init()  # Initialize device state
            print(f"Connected to RF Generator on {port}")
        except Exception as e:
            print(f"Error connecting to RF Generator: {e}")
            self.synth = None

    def enable(self, channel: int):
        """
        Enables the RF output for the specified channel.

        Args:
            channel (int): The RF generator channel to enable (0 or 1).
        """
        if self.synth and channel in [0, 1]:
            self.synth[channel].enable = True
            print(f"Channel {channel}: RF output enabled.")
        else:
            print(f"Invalid channel: {channel}. Must be 0 or 1.")

    def disable(self, channel: int):
        """
        Disables the RF output for the specified channel.

        Args:
            channel (int): The RF generator channel to disable (0 or 1).
        """
        if self.synth and channel in [0, 1]:
            self.synth[channel].enable = False
            print(f"Channel {channel}: RF output disabled.")
        else:
            print(f"Invalid channel: {channel}. Must be 0 or 1.")

    def set_frequency(self, channel: int, frequency: float):
        """
        Sets the frequency for the given channel.

        Args:
            channel (int): Channel number (0 or 1).
            frequency (float): Frequency in MHz.
        """
        if self.synth:
            self.synth[channel].frequency = frequency
            print(f"Channel {channel}: Frequency set to {frequency} MHz")

    def set_power(self, channel: int, power: float):
        """
        Sets the output power for the given channel.

        Args:
            channel (int): Channel number (0 or 1).
            power (float): Power level in dBm.
        """
        if self.synth:
            self.synth[channel].power = power
            print(f"Channel {channel}: Power set to {power} dBm")

    def configure_differential_sweep(
        self,
        f_low: float,
        f_high: float,
        f_step: float,
        diff_freq: float,
        step_time: float,
        trigger_mode: str = "full_sweep",
    ):
        """
        Configures a differential sweep where Channel B follows Channel A with a fixed offset.

        Args:
            f_low (float): Start frequency for Channel A in MHz.
            f_high (float): End frequency for Channel A in MHz.
            f_step (float): Step size in MHz.
            diff_freq (float): Differential frequency in MHz (Channel B = Channel A + diff_freq).
            step_time (float): Time to spend on each step in milliseconds (min 4ms, max 10s).
            trigger_mode (str): Trigger mode for the RF generator. Options: 'no_trigger', 'full_sweep', 'step_sweep'.
        """
        if self.synth:
            # Configure Channel A sweep (Channel B follows automatically)
            self.synth[0].write("sweep_freq_low", f_low)
            self.synth[0].write("sweep_freq_high", f_high)
            self.synth[0].write("sweep_freq_step", f_step)

            # Enable Differential Mode
            self.synth.write("sweep_diff_meth", 1)  # Differential sweep mode
            self.synth.write("sweep_diff_freq", diff_freq)  # Set frequency offset

            # Set step time (ensuring it is within the valid range of 4 ms to 10s)
            if 4 <= step_time <= 10000:
                self.synth.write("sweep_time_step", step_time)
                print(f"Step time set to {step_time} ms")
            else:
                print("Invalid step_time. Must be between 4 ms and 10,000 ms.")

            # Set trigger mode
            self.set_trigger_mode(trigger_mode)

            print(
                f"Differential sweep configured: Channel A [{f_low}-{f_high} MHz], Step {f_step} MHz, Channel B offset {diff_freq} MHz"
            )

    def enable_sweep(self, enable: bool):
        """
        Enables or disables the continuous frequency sweep.

        Args:
            enable (bool): True to enable, False to disable.
        """
        if self.synth:
            self.synth.sweep_enable = enable
            print(f"Sweep {'enabled' if enable else 'disabled'}")

    def set_trigger_mode(self, mode: str = "full_sweep"):
        """
        Sets the trigger mode for the RF generator.

        Args:
            mode (str): The trigger mode to set. Available options:
                - "no_trigger" → No triggering (default behavior)
                - "full_sweep" → Full Sweep Triggering (External trigger starts a full sweep)
                - "step_sweep" → Single Sweep Step Triggering (Trigger advances one step)
        """
        if self.synth:
            mode_mapping = {
                "no_trigger": 0,  # No triggering
                "full_sweep": 1,  # Full Sweep Triggering
                "step_sweep": 2,  # Single Sweep Step Triggering
            }

            if mode not in mode_mapping:
                print(
                    f"Invalid trigger mode: {mode}. Choose from: {list(mode_mapping.keys())}"
                )
                return

            self.synth.write("trig_function", mode_mapping[mode])
            print(f"Trigger mode set to: {mode.replace('_', ' ').title()}")

    def read_parameter(self, channel: int, param: str):
        """
        Reads a parameter from the RF generator safely.

        Args:
            channel (int): Channel number (0 or 1).
            param (str): The parameter to read.

        Returns:
            The parameter value or None if it fails.
        """
        try:
            if self.synth and param in self.synth[channel].__dict__:
                value = getattr(self.synth[channel], param)
                print(f"🔹 {param} = {value}")
                return value
            else:
                print(f"Unsupported parameter: {param}")
                return None
        except Exception as e:
            print(f"Error reading {param}: {str(e)}")
            return None

    def shutdown(self):
        """
        Shutdown the RF generator and closes the connection.
        """
        if self.synth:
            self.synth.sweep_enable = False  # Ensure sweep is off
            self.synth[0].power = -80  # Set power to minimum on channel 0
            self.synth[1].power = -80  # Set power to minimum on channel 1
            self.disable(0)  # Disable channel 0
            self.disable(1)  # Disable channel 1
            self.synth.close()
            print("RF Generator shut down successfully.")
