# Run it from root with `python -m devicesTests.laser`
from  devices.MuquansLaser import MuquansLaser

laser = MuquansLaser(host="10.0.2.107", port=23)
laser.connect()
laser.seed_on()
laser.set_power(1)
laser.disconnect()

