import devices.utils.redpitaya_scpi as scpi

# Methods:
# connect() - Establishes a connection to the Red Pitaya.
# set_trigger_pulse(high_level: float, low_level: float, period: float, duty_cycle: float) - Configures a pulse train on Channel 1.
# set_dc_voltage(voltage: float) - Sets a DC voltage on Channel 2 for frequency control.
# disable_outputs() - Turns off both signal generator outputs.
# disconnect() - Closes the connection to Red Pitaya.

class RedPitayaSignalGenerator:
    """
    Driver for the Red Pitaya used as a 2-channel signal generator.
    - Channel 1: PWM trigger pulse.
    - Channel 2: Fixed DC voltage.
    """

    def __init__(self, ip: str = "10.0.2.102"):
        """
        Initializes the Red Pitaya Signal Generator.
        
        Args:
            ip (str): IP address of the Red Pitaya.
        """
        self.ip = ip
        self.rp = None

    def connect(self):
        """Establishes a connection to the Red Pitaya."""
        try:
            self.rp = scpi.scpi(self.ip)
            print(f"Connected to Red Pitaya at {self.ip}")
        except Exception as e:
            print(f"Error connecting to Red Pitaya: {e}")

    def set_trigger_pulse(self, high_level: float, low_level: float, period: float, duty_cycle: float):
        """
        Configures Channel 1 as a PWM trigger pulse.

        Args:
            high_level (float): Voltage level when HIGH (e.g. 3.3 V).
            low_level (float): Voltage level when LOW (e.g. 0 V).
            period (float): Total period of the pulse in seconds (frequency = 1/period).
            duty_cycle (float): Duty cycle in percent (0 to 100).
        """
        frequency = 1 / period
        amplitude = high_level - low_level
        offset = low_level
        duty_fraction = duty_cycle / 100.0

        # Configure channel 1 for PWM output
        self.rp.tx_txt('SOUR1:FUNC PWM')
        self.rp.tx_txt('SOUR1:FREQ:FIX ' + str(frequency))
        self.rp.tx_txt('SOUR1:VOLT ' + str(amplitude))
        self.rp.tx_txt('SOUR1:VOLT:OFFS ' + str(offset))
        self.rp.tx_txt('SOUR1:DCYC ' + str(duty_fraction))
        self.rp.tx_txt('OUTPUT1:STATE ON')
        # Trigger the generator immediately:
        self.rp.tx_txt('SOUR1:TRig:INT')
        print(f"Channel 1 set to PWM: freq={frequency:.3f} Hz, amplitude={amplitude} V, offset={offset} V, duty cycle={duty_cycle}%")

    def set_dc_voltage(self, voltage: float):
        """
        Sets Channel 2 to a fixed DC voltage.

        The input voltage is clamped between -5 and 5 V, then scaled to the -1 to 1 V range.
        
        Args:
            voltage (float): Desired voltage in Volts.
        """
        # Clamp voltage to [-5, 5] then scale to [-1, 1]
        if voltage > 5:
            voltage = 5
        elif voltage < -5:
            voltage = -5
        scaled_voltage = voltage / 5.0

        if scaled_voltage >= 0:
            self.rp.tx_txt('SOUR2:FUNC DC')
            self.rp.tx_txt('SOUR2:VOLT ' + str(scaled_voltage))
        else:
            self.rp.tx_txt('SOUR2:FUNC DC_NEG')
            # For DC_NEG, set the magnitude (output becomes negative)
            self.rp.tx_txt('SOUR2:VOLT ' + str(abs(scaled_voltage)))
        self.rp.tx_txt('OUTPUT2:STATE ON')
        self.rp.tx_txt('SOUR2:TRig:INT')
        print(f"Channel 2 set to DC voltage (after amplifer): {voltage} V")

    def disable_outputs(self):
        """Turns off both signal generator outputs."""
        if self.rp:
            self.rp.tx_txt('OUTPUT1:STATE OFF')
            self.rp.tx_txt('OUTPUT2:STATE OFF')
            print("Both outputs disabled.")

    def disconnect(self):
        """Closes the connection to the Red Pitaya."""
        if self.rp:
            self.rp.close()
            self.rp = None
            print("Disconnected from Red Pitaya.")
