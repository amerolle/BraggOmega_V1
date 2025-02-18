# Run it from root with `python -m devicesTests.wavemeter`

from devices.WaveMeter import Wavemeter

wavemeter = Wavemeter(base_url="http://localhost:5000")
wavemeter.get_frequency(0)