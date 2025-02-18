import telnetlib
import time

# Available commands:
# sml780_tool Enable_Current_Laser_Diode on
# sml780_tool Enable_Current_Laser_Diode off
# sml780_tool edfa_set 2.5
# sml780_tool edfa_shutdown

# Methods:
# connect() - Establish a Telnet connection to the laser.
# disconnect() - Closes the Telnet connection.
# seed_on() - Turns ON the seed laser via Telnet.
# seed_off() - Turns OFF the seed laser via Telnet.
# set_power(power: float) - Sets the EDFA power level via Telnet.
# shutdown_edfa() - Shuts down the EDFA via Telnet.
# shutdown() - Turns OFF the EDFA and seed laser.


class MuquansLaser:
    """
    Laser driver that communicates via Telnet.
    Supports:
      - Enabling/Disabling the laser diode
      - Setting the EDFA power
      - Shutting down the EDFA
    """

    def __init__(self, host: str = '10.0.2.107', port: int = 23, timeout: int = 5):
        """
        Initializes the Laser object.

        Args:
            host (str): IP address of the laser controller. 
            port (int): Telnet port (default: 23).
            timeout (int): Connection timeout in seconds.
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.tn = None  # Telnet connection object
        self.laser_on = False
        self.current_power = 0.0

    def connect(self):
        """
        Establish a Telnet connection to the laser.
        """
        try:
            self.tn = telnetlib.Telnet(self.host, self.port, self.timeout)
            print(f"Connected to Laser at {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to connect to Laser: {e}")

    def disconnect(self):
        """
        Closes the Telnet connection.
        """
        if self.tn:
            self.tn.close()
            self.tn = None
            print("Laser connection closed.")

    def seed_on(self):
        """
        Turns ON the seed laser via Telnet.
        """
        command = "sml780_tool Enable_Current_Laser_Diode on"
        response = self._send_command(command)
        if response:
            self.laser_on = True
            print(f"Seed laser enabled. Response: {response}")

    def seed_off(self):
        """
        Turns OFF the seed laser via Telnet.
        """
        command = "sml780_tool Enable_Current_Laser_Diode off"
        response = self._send_command(command)
        if response:
            self.laser_on = False
            print(f"Seed laser disabled. Response: {response}")


    def set_power(self, power: float):
        """
        Sets the EDFA power level via Telnet.

        Args:
            power (float): Power setpoint (0 to 2.5).
        """
        if not (0.0 <= power <= 2.5):
            raise ValueError("Power must be between 0 and 2.5")

        command = f"sml780_tool edfa_set {power}"
        response = self._send_command(command)
        if response:
            self.current_power = power
            print(f"EDFA power set to {power}. Response: {response}")

    def shutdown_edfa(self):
        """
        Shuts down the EDFA via Telnet.
        """
        command = "sml780_tool edfa_shutdown"
        response = self._send_command(command)
        if response:
            self.current_power = 0.0
            print(f"EDFA shutdown. Response: {response}")

    def shutdown(self):
        """
        1. Turns OFF the EDFA
        2. Turns OFF the seed laser
        """
        print("Shutting down the laser system...")
        self.shutdown_edfa()  # Turn off the EDFA
        time.sleep(1) 
        self.seed_off()  # Turn off the seed laser
        print("Laser system shutdown complete.")

    def _send_command(self, command: str):
        """
        Sends a command via Telnet and reads the response.

        Args:
            command (str): Command to send.

        Returns:
            str: Response from the laser (if any).
        """
        if self.tn is None:
            print("Error: Not connected to laser.")
            return None

        try:
            self.tn.write(command.encode('ascii') + b"\n")
            time.sleep(0.1)  # Allow processing time
            response = self.tn.read_until(b"\n", timeout=2).decode('ascii').strip()
            return response
        except Exception as e:
            print(f"Error sending command '{command}': {e}")
            return None
