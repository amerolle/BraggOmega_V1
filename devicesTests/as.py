#Run it from root with `python -m devicesTests.as`
from  devices.RPSignalGenerator import RedPitayaSignalGenerator
# Create an instance of the class
rp_gen = RedPitayaSignalGenerator(ip="192.168.0.189")

# Connect to the Red Pitaya
rp_gen.connect()

# Generate a triangular signal
rp_gen.set_triangle_ramp(high_voltage=1.0, low_voltage=-1.0, frequency=1.0)

# Measure the saturated absorption signal for 5 seconds
rp_gen.measure_absorption_saturation(duration=5)

# Disable the outputs and close the connection
rp_gen.disable_outputs()
rp_gen.disconnect()
