# Run it from root with `python -m devicesTests.rfgenerator`
from devices.RFGenerator import RFGenerator

rf_gen = RFGenerator(port="COM4")


# Carefull
# self.write('phase_step', value) doesnt work in synth.init()
# so self.phase = 0. is commented in init(self) directly in the mambaforge package...
# Go to Definition of RFGenerator then Go to definition of SynthHD then go to SynthHDChannel.init and comment # self.phase = 0.


rf_gen.enable(1)
rf_gen.enable(0)

rf_gen.shutdown()    
