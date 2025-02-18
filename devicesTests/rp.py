# Run it from root with `python -m devicesTests.rp`
from  devices.RPSignalGenerator import RedPitayaSignalGenerator

rp = RedPitayaSignalGenerator(ip="10.0.2.102")
rp.connect()
rp.set_dc_voltage(3)
rp.set_trigger_pulse(0.5,0,0.01,90)