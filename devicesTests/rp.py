#Run it from root with `python -m devicesTests.rp`
from  devices.RPSignalGenerator import RedPitayaSignalGenerator

rp = RedPitayaSignalGenerator(ip="192.168.0.189")
rp.disable_outputs()
rp.disconnect()
rp.connect()
rp.set_triangle_ramp(high_voltage=1.0, low_voltage=-1.0, frequency=1.0)
#rp.set_triangle_ramp2(high_voltage=1.0, low_voltage=-1.0, frequency=1.0)

# rp.set_dc_voltage(-1)
rp.set_trigger_pulse(0.5,0,1,90)
# rp.disable_outputs()
# rp.disconnect()

