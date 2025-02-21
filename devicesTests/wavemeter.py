# Run it from root with `python -m devicesTests.wavemeter`

from devices.WaveMeter import Wavemeter

wavemeter = Wavemeter(base_url="http://192.168.0.169:5000")
wavemeter.get_frequency(0)