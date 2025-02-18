import pyvisa

# Methods:
# connect() - Establishes a connection to the AFG3000C.
# set_trigger_pulse(high_level, low_level, period, duty_cycle) - Configures a pulse train on Channel 1.
# set_dc_voltage(voltage) - Sets a DC voltage on Channel 2 for frequency control.
# disable_outputs() - Turns off both signal generator outputs.
# disconnect() - Closes the connection to AFG3000C.


class TektronixAFG3000C:
    """
    Driver for the Tektronix AFG3000C Arbitrary Function Generator.
    - Channel 1: Pulse train for triggering.
    - Channel 2: DC voltage for frequency control.
    """

    def __init__(self, ip: str):
        """
        Initializes the Tektronix AFG3000C Signal Generator.

        Args:
            ip (str): VISA resource string (e.g., 'TCPIP0::ip::INSTR').
        """
        self.ip = ip
        self.resource = f"TCPIP::{ip}::INSTR"
        self.rm = pyvisa.ResourceManager()
        self.instrument = None

    def connect(self):
        """Establishes a connection to the AFG3000C."""
        try:
            self.instrument = self.rm.open_resource(self.resource)
            self.instrument.write("*RST")  # Reset the instrument
            print(f"Connected to AFG3000C at {self.resource}")
        except Exception as e:
            print(f"Error connecting to AFG3000C: {e}")

    def set_trigger_pulse(
        self, high_level: float, low_level: float, period: float, duty_cycle: float
    ):
        """
        Configures a pulse train on Channel 1.

        Args:
            high_level (float): Voltage for HIGH state (V).
            low_level (float): Voltage for LOW state (V).
            period (float): Total period of the pulse in seconds.
            duty_cycle (float): Duty cycle percentage (0-100%).
        """
        if not self.instrument:
            print("Not connected to AFG3000C!")
            return

        # Ensure valid input values
        if not (0 <= duty_cycle <= 100):
            print("Invalid duty cycle! Must be between 0% and 100%.")
            return
        if period <= 0:
            print("Invalid period! Must be greater than 0.")
            return

        # Configure Pulse on Channel 1
        self.instrument.write("SOURce1:FUNCtion PULSe")
        self.instrument.write(f"SOURce1:PULSe:PERiod {period}")
        self.instrument.write(f"SOURce1:PULSe:DCYCle {duty_cycle}")
        self.instrument.write(f"SOURce1:VOLTage:HIGH {high_level}")
        self.instrument.write(f"SOURce1:VOLTage:LOW {low_level}")

        print(
            f"Pulse set: High {high_level}V, Low {low_level}V, Period {period}s, Duty {duty_cycle}%"
        )

    def set_dc_voltage(self, voltage: float):
        """
        Sets a DC voltage on Channel 2 for frequency control.

        Args:
            voltage (float): Voltage in Volts (-5V to +5V).
        """
        if not self.instrument:
            print("Not connected to AFG3000C!")
            return

        # Limit to the supported range (-5V to +5V)
        voltage = max(-5, min(5, voltage))

        # Configure DC Output on Channel 2
        self.instrument.write("SOURce2:FUNCtion DC")
        self.instrument.write(f"SOURce2:VOLTage:OFFSet {voltage}")

        print(f"DC output set to {voltage} V")

    def disable_outputs(self):
        """Turns off both signal generator outputs."""
        if not self.instrument:
            print("Not connected to AFG3000C!")
            return

        self.instrument.write("OUTPut1 OFF")
        self.instrument.write("OUTPut2 OFF")

        print("Outputs disabled.")

    def disconnect(self):
        """Closes the connection to AFG3000C."""
        if self.instrument:
            self.instrument.close()
            print("AFG3000C disconnected.")
