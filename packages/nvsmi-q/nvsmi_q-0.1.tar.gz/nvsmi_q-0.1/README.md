# nvsmi-q

    Yet another python wrapper for nvidia-smi, keep it simple & stupid ;)

----

### Examples

⚪ Use in Shell

```shell
# list up all GPU devices
$ python -m nvsmi -L
[{
  "device id": 0,
  "model": "NVIDIA GeForce RTX 3060",
  "uuid": "GPU-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}]

# show brief info for all GPU devices
$ python -m nvsmi -B
[0] Name: NVIDIA GeForce RTX 3060, Power: 25.77W, Temp: 44°C, Fan: 0%, Usage: 7%

# query one GPU device, show info tree as json
$ python -m nvsmi       # defaults to the first GPU device)
$ python -m nvsmi -i 2  # specify device_id
{
  "Product Name": "NVIDIA GeForce RTX 3060",
  "Product Brand": "GeForce",
  "Product Architecture": "Ampere",
  "GPU UUID": "GPU-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "GPU PDI": "0x012345678901234",
  "VBIOS Version": "94.06.2f.00.f5",
  "MultiGPU Board": "No",
  "Board ID": "0x123",
  "GPU Part Number": "1024-512-C9",
  "PCI": ...
  "FB Memory Usage": ...
  "BAR1 Memory Usage": ...
  "Temperature": ...
  "GPU Power Readings": ...
  "Max Clocks": ...
  "Timestamp": "Fri Jan  9 16:37:37 2026",
  "Driver Version": "581.08",
  "CUDA Version": "13.0",
  "Display Attached": "Yes",
  "Display Active": "Enabled",
  "Driver Model": ...
  "Fan Speed": ...
  "Performance State": ...
  "Utilization": ...
  "Clocks": ...
}

# show static info only
$ python -m nvsmi -S
$ python -m nvsmi -S -i 2
# show dynamic info only
$ python -m nvsmi -D
```

⚪ Use in interactive Python console

```python
>>> from nvsmi import NVSMI

# list up all GPU devices
>>> entries = NVSMI.list_gpus()
>>> print(entries)
[{
  "device id": 0,
  "model": "NVIDIA GeForce RTX 3060",
  "uuid": "GPU-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}]

# query one GPU device
>>> nvsmi = NVSMI.query_gpu(entries[0].device_id)
>>> print(nvsmi.brief)    # brief in one-line
[0] Name: NVIDIA GeForce RTX 3060 Power: 24.89W Temp: 45°C Fan: 0% Usage: 19%
>>> nvsmi                 # detailed & formatted json string
{
  "Product Name": "NVIDIA GeForce RTX 3060",
  "Product Brand": "GeForce",
  "Product Architecture": "Ampere",
  "GPU UUID": "GPU-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "GPU PDI": "0x012345678901234",
  "VBIOS Version": "94.06.2f.00.f5",
  "MultiGPU Board": "No",
  "Board ID": "0x123",
  "GPU Part Number": "1024-512-C9",
  "PCI": {
    "GPU Link Info": {
      "PCIe Generation": {
        "Max": 4,
        "Device Max": 4,
        "Current": 1,
        "Device Current": 1,
        "Host Max": 4
      },
      "Link Width": {
        "Max": "16x",
        "Current": "16x"
      }
    },
    "Bus": "0x01",
    "Device": "0x00",
    "Domain": "0x0000",
    "Device Id": "0xDEADBEEF",
    "Bus Id": "00000000:01:00.0",
    "Sub System Id": "0x10086110",
    "Tx Throughput": 100,
    "Rx Throughput": 50
  },
  "FB Memory Usage": {
    "Total": 12288,
    "Reserved": 173,
    "Used": 1979,
    "Free": 10137
  },
  "BAR1 Memory Usage": {
    "Total": 256,
    "Used": 228,
    "Free": 28
  },
  "Temperature": {
    "GPU Shutdown Temp": 98,
    "GPU Slowdown Temp": 95,
    "GPU Max Operating Temp": 93,
    "GPU Target Temperature": 83,
    "GPU Current Temp": 45
  },
  "GPU Power Readings": {
    "Current Power Limit": 160,
    "Requested Power Limit": 160,
    "Default Power Limit": 170,
    "Min Power Limit": 100,
    "Max Power Limit": 212,
    "Average Power Draw": 25.46,
    "Instantaneous Power Draw": 25.16
  },
  "Max Clocks": {
    "Graphics": 2130,
    "SM": 2130,
    "Memory": 7501,
    "Video": 1950
  },
  "Timestamp": "Fri Jan  9 16:37:37 2026",
  "Driver Version": "581.08",
  "CUDA Version": "13.0",
  "Display Attached": "Yes",
  "Display Active": "Enabled",
  "Driver Model": {
    "Current": "WDDM",
    "Pending": "WDDM"
  },
  "Fan Speed": 0,
  "Performance State": "P8",
  "Utilization": {
    "GPU": 11,
    "Memory": 16,
    "Encoder": 0,
    "Decoder": 0,
    "JPEG": 0,
    "OFA": 0
  },
  "Clocks": {
    "Graphics": 210,
    "SM": 210,
    "Memory": 405,
    "Video": 555
  }
}

# access static or dynamic part alone
>>> print(nvsmi.nvs)
>>> print(nvsmi.nvd)

# access certain values on tree
>>> print(f'Name: {nvsmi.nvs.Product_Name}')
>>> print(f'Power: {nvsmi.nvd.GPU_Power_Readings.Average_Power_Draw}W')
>>> print(f'Temp: {nvsmi.nvd.Temperature.GPU_Current_Temp}°C')
>>> print(f'Fan: {nvsmi.nvd.Fan_Speed}%')
>>> print(f'Usage: {nvsmi.nvd.Utilization.GPU}%')
Name: NVIDIA GeForce RTX 3060
Power: 25.66W
Temp: 44°C
Fan: 0%
Usage: 0%

# omit the intermediate nvs/nvd (although not friendly to code auto-complete :(
>>> print(f'Usage: {nvsmi.Utilization.GPU}%')        # the same result
# or access like a python dict
>>> print(f'Usage: {nvsmi["Utilization"]["GPU"]}%')  # the same result
```

### Features

- Lightweight: single file, no 3rd-party dependences!
- Divide the whole info tree into **static** and **dynamic** parts, better focus on dynamics tracing
  - static: physical intrinsics of GPU core and PCIe connection, **CANNOT** be changed once the GPU is powered-up and initailized
  - dynamic: options that **COULD** be dynamically tuned with `nvidia-smi`, or sensors reading values

### TODO

- [x] `nvidia-smi` info tree parse
- [ ] dynamic statistics monitoring
- [ ] list GPU processes

### Install

ℹ Requires `nvidia-smi` and Python3.8+ installed
⚠ Naming conflicts with pmav99's nvsmi: https://github.com/pmav99/nvsmi

⚪ From PyPI

- `pip install nvsmi-q`
- run `python -m nvsmi` to verify installation

⚪ From source

- `git clone https://github.com/Kahsolt/nvsmi-q`
- `cd nvsmi-q`
- `pip install .`
- run `python -m nvsmi` to verify installation

### Other projects wandering all around NVML and nvidia-smi..

- nvtop (most popular🔥): https://github.com/Syllo/nvtop
- nvidia-ml-py (nvidia official)
  - https://developer.nvidia.com/management-library-nvml
  - https://pypi.org/project/nvidia-ml-py/
  - https://pypi.org/project/clore-pynvml/
- nvidia-smi: https://pypi.org/project/nvidia-smi/
- nvidia-smi-remote: https://github.com/ive2go/nvidia-smi-remote
- gputil: https://github.com/anderskm/gputil
- nvsmi: https://github.com/pmav99/nvsmi
- nvsmifs (recommended👏): https://github.com/initiateit/nvsmifs
- pynmvl (deprecated⚠): https://github.com/gpuopenanalytics/pynvml

----
by Armit
周五 2026/01/09
