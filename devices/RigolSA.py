import pyvisa


# Rigol Spectrum Analyzer (DSA800 series) driver
# Supports:
# connect() - Establishes a connection to the Spectrum Analyzer.
# set_center_frequency(freq_hz: float) - Sets the center frequency.
# set_rbw_vbw(rbw_hz: float, vbw_hz: float) - Sets the RBW and VBW.
# enable_zero_span_mode() - Enables zero span mode.
# set_sweep_time(time_sec: float) - Sets the sweep time.
# set_trigger(mode: str, edge: str = "POS") - Configures the trigger mode.
# start_sweep(continuous: bool = True) - Starts the sweep.
# fetch_trace() - Fetches the spectrum data from the SA.
# disconnect() - Closes the connection to the SA.


class RigolSA:
    """
    Driver for the Rigol Spectrum Analyzer (DSA800 series) over LAN (TCP/IP).
    Uses SCPI commands to control center frequency, RBW, VBW, sweep, trigger, and zero span.
    """

    def __init__(self, ip: str):
        """
        Initializes the Spectrum Analyzer.

        Args:
            ip (str): IP address of the Rigol Spectrum Analyzer.
        """
        self.ip = ip
        self.resource = f"TCPIP::{ip}::INSTR"
        self.rm = pyvisa.ResourceManager("@py")
        self.sa = None

    def connect(self):
        """Establishes a connection to the Rigol Spectrum Analyzer."""
        try:
            self.sa = self.rm.open_resource(self.resource)
            self.sa.timeout = 5000  # Set timeout to 5 seconds
            print(f"Connected to Rigol SA at {self.ip}")
        except Exception as e:
            print(f"Error connecting to SA: {e}")

    def set_center_frequency(self, freq_hz: float):
        """
        Sets the center frequency.

        Args:
            freq_hz (float): Center frequency in Hz.
        """
        if self.sa:
            self.sa.write(f":SENSe:FREQuency:CENTer {freq_hz}")
            print(f"Center frequency set to {freq_hz / 1e6} MHz")

    def set_rbw_vbw(self, rbw_hz: float, vbw_hz: float):
        """
        Sets the resolution bandwidth (RBW) and video bandwidth (VBW).

        Args:
            rbw_hz (float): Resolution bandwidth in Hz.
            vbw_hz (float): Video bandwidth in Hz.
        """
        if self.sa:
            self.sa.write(f":SENSe:BANDwidth:RESolution {rbw_hz}")  # Set RBW
            self.sa.write(f":SENSe:BANDwidth:VIDeo {vbw_hz}")  # Set VBW
            print(f"RBW set to {rbw_hz / 1e3} kHz, VBW set to {vbw_hz / 1e3} kHz")

    def enable_zero_span_mode(self):
        """Enables zero span mode."""
        if self.sa:
            self.sa.write(":SENSe:FREQuency:SPAN 0")
            print("Zero span mode enabled")

    def set_sweep_time(self, time_sec: float):
        """
        Sets the sweep time.

        Args:
            time_sec (float): Sweep time in seconds.
        """
        if self.sa:
            self.sa.write(f":SWE:TIME {time_sec}")
            print(f"Sweep time set to {time_sec} seconds")

    def set_trigger(self, mode: str = "EXT", edge: str = "POS"):
        """
        Configures the trigger mode.

        Args:
            mode (str): Trigger mode (e.g., 'FREE', 'EXT', 'VID').
            edge (str): Trigger edge ('POS' for positive, 'NEG' for negative).
        """
        if self.sa:
            self.sa.write(f":TRIGger:SEQuence:SOURce {mode.upper()}")
            if mode.upper() == "EXT":
                self.sa.write(f":TRIGger:SEQuence:EXTernal:SLOPe {edge.upper()}")
            print(f"Trigger mode set to {mode.upper()}")

    def start_sweep(self, continuous: bool = True):
        """
        Starts the sweep.

        Args:
            continuous (bool): If True, sets continuous sweep; otherwise, single sweep.
        """
        if self.sa:
            self.sa.write(f":INITiate:CONTinuous {'ON' if continuous else 'OFF'}")
            if not continuous:
                self.sa.write(":INITiate:IMMediate")
            print(f"Sweep {'continuous' if continuous else 'single'} started")

    def fetch_trace(self):
        """
        Fetches the spectrum data from the SA.

        Returns:
            str: Data string from the analyzer.
        """
        if self.sa:
            data = self.sa.query(":TRACe:DATA? TRACE1")
            print("Fetched trace data")
            return data

    def disconnect(self):
        """Closes the connection to the SA."""
        if self.sa:
            self.sa.close()
            print("Rigol SA disconnected.")