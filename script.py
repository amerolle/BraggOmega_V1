from  devices.RPSignalGenerator import RedPitayaSignalGenerator

rp = RedPitayaSignalGenerator(ip="10.0.2.102")
rp.connect()
rp.set_dc_voltage(0)
# rp.set_trigger_pulse(0.5,0,0.01,90)
# rp.set_triangle_ramp(0,0,1)