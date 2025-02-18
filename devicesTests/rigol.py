from devices.RigolSA import RigolSA
import matplotlib.pyplot as plt
import numpy as np

sa = RigolSA(ip="192.168.0.158")
sa.connect()

# Fetch
data_str = sa.fetch_trace()
print("Raw data received")

if data_str.startswith('#'):
    parts = data_str.split(' ', 1)
    if len(parts) == 2:
        data_str = parts[1]

try:
    data_list = [float(x.strip()) for x in data_str.split(',') if x.strip()]
except Exception as e:
    print("Error parsing trace data:", e)
    data_list = []

trace = np.array(data_list)

plt.figure(figsize=(10, 4))
plt.plot(trace, marker='.', linestyle='-')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.title('Spectrum Analyzer Trace')
plt.grid(True)
plt.show()

sa.disconnect()