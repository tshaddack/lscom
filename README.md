Autogenerated from [https://www.improwis.com/projects/sw_lscom/](https://www.improwis.com/projects/sw_lscom/)






lscom - list of available serial ports







lscom - list of available serial ports
======================================



---

[Why](#Why "#Why")  
[How](#How "How")  
      [usage](#usage "How.usage")  
      [Windows specifics](#Windowsspecifics "How.Windows specifics")  
[Files](#Files "Files")  
[Todo](#Todo "Todo")  


---

Why
---



To see the serial ports present in the system.





---

How
---



A script in python, using serial.tools.list\_ports to enumerate the ports, checking /dev, /dev/serial/by-id, and /dev/serial/by-path for symlinks
(some symlinks were not present in the list\_ports call), optionally calling fuser to check if the port is opened.



### usage



```
List serial ports available on the machine.
Uses python serial.tools.list_ports.comports() scan, augmented with other lookups

Usage: /usr/bin/lscom [-l] [-h]
Where:
  -l       list format, one port per line
  -L       list by alternative scan
  -LD      list by alternative scan, with device paths
  -N       skip alternative scan
  -a       show all port properties, alphabetically, no filtering
  -o       show process that has the port opened (call fuser -v)
  -noexec  do not execute any commands as helpers (rfcomm, bluetoothctl)
  -d       debug, trace the operations performed
  -h       help


```

In normal use, for each port the output is:
* the main device
* the aliases/symlinks if they exist
* with -o option, the OPENED BY: shows the process that has the device opened
* various properties (name, subsystem, hardware id, device paths...)
* for rfcomm ports (serial over bluetooth), the address and channel are attempted to get from /sys, then the rfcomm and bluetoothctl commands are called to get details (unless forbidden by -noexec option)
* duplicate values are trimmed from the list for better readability (can be disabled by -a)



lscom -o
```
           name: rfcomm0
                 BLUETOOTH
     BT_address: 00:15:a3:15:32:1c
     BT_channel: 1
         rfcomm: rfcomm0: B8:27:EB:BC:D8:03 -> 00:15:A3:15:32:1C channel 1 closed
   bluetoothctl: Device 00:15:A3:15:32:1C UM34C

 /dev/ttyAMA0
 = /dev/serial1
      OPENED BY: hciattach     flags=F.... PID=715 USER=root PORT=/dev/ttyAMA0:
           name: ttyAMA0
      subsystem: amba
           hwid: 3f201000.serial
    device_path: /sys/devices/platform/soc/3f201000.serial

 /dev/ttyUSB0
 = /dev/ttyMarlin
 = /dev/ttyUSB.3
 = /dev/serial/by-path/platform-3f980000.usb-usb-0:1.3:1.0-port0
 = /dev/serial/by-id/usb-Silicon_Labs_CP2102_Marlin_250000n8_0001-if00-port0
      OPENED BY: octoprint     flags=F.... PID=905 USER=pi PORT=/dev/ttyUSB0:
           name: ttyUSB0
      subsystem: usb-serial
        product: CP2102 Marlin 250000n8
   manufacturer: Silicon Labs
  serial_number: 0001
        VID:PID: 10c4:ea60
       location: 1-1.3
           hwid: USB VID:PID=10C4:EA60 SER=0001 LOCATION=1-1.3
    device_path: /sys/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.3/1-1.3:1.0/ttyUSB0
usb_device_path: /sys/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.3
usb_interface_path: /sys/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.3/1-1.3:1.0

 /dev/ttyUSB1
 = /dev/ttyUSB.5
 = /dev/ttyLoadcell
 = /dev/serial/by-path/platform-3f980000.usb-usb-0:1.5:1.0-port0
 = /dev/serial/by-id/usb-Silicon_Labs_CP2102_filament_load_cell_interface_57600_0001-if00-port0
           name: ttyUSB1
      subsystem: usb-serial
        product: CP2102 filament load cell interface 57600
   manufacturer: Silicon Labs
  serial_number: 0001
        VID:PID: 10c4:ea60
       location: 1-1.5
           hwid: USB VID:PID=10C4:EA60 SER=0001 LOCATION=1-1.5
    device_path: /sys/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.5/1-1.5:1.0/ttyUSB1
usb_device_path: /sys/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.5
usb_interface_path: /sys/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.5/1-1.5:1.0

```
lscom -l
```
 /dev/rfcomm0|rfcomm0|None|n/a
 /dev/ttyAMA0|ttyAMA0|amba|3f201000.serial
 /dev/ttyUSB0|ttyUSB0|usb-serial|USB VID:PID=10C4:EA60 SER=0001 LOCATION=1-1.3
 /dev/ttyUSB1|ttyUSB1|usb-serial|USB VID:PID=10C4:EA60 SER=0001 LOCATION=1-1.5
 /dev/ttyUSB.3|ttyUSB.3|None|LINK=/dev/ttyUSB0 LINK=/dev/ttyUSB0
 /dev/ttyUSB.5|ttyUSB.5|None|LINK=/dev/ttyUSB1 LINK=/dev/ttyUSB1

```
### Windows specifics



The code is written primarily for linux, however it works also for Windows.
Under Windows, the product string is generic, from the driver instead from the device.




The same device that looks under linux as

```
 /dev/ttyUSB0
 = /dev/ttyUSB.2.3.1
 = /dev/ttyArdu
 = /dev/serial/by-path/platform-3f980000.usb-usb-0:1.2.3.1:1.0-port0
 = /dev/serial/by-id/usb-Silicon_Labs_CP2102_Arduino_USB-serial_interface_0001-if00-port0
           name: ttyUSB0
      subsystem: usb-serial
        product: CP2102 Arduino USB-serial interface
   manufacturer: Silicon Labs
  serial_number: 0001
        VID:PID: 10c4:ea60
       location: 1-1.2.3.1
           hwid: USB VID:PID=10C4:EA60 SER=0001 LOCATION=1-1.2.3.1
    device_path: /sys/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.2/1-1.2.3/1-1.2.3.1/1-1.2.3.1:1.0/ttyUSB0
usb_device_path: /sys/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.2/1-1.2.3/1-1.2.3.1
usb_interface_path: /sys/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.2/1-1.2.3/1-1.2.3.1/1-1.2.3.1:1.0

```
looks under windows as

```
COM4
           name: COM4
    description: Silicon Labs CP210x USB to UART Bridge (COM4)
   manufacturer: Silicon Labs
  serial_number: 0001
        VID:PID: 10c4:ea60
       location: 1-3
           hwid: USB VID:PID=10C4:EA60 SER=0001 LOCATION=1-3

```




The product string is handy to customize for devices, so different hardware using the same interface chip
still looks different. (The annoyingly common CH317 has no EEPROM and no way to customize the strings.)
Same situation happens when the OS or library doesn't provide the string, and gives just a bland generic.
The location then can come to rescue for identifying the chips, by the sequence of port-(hub-hub...)-port. It is of course handy
to know the numbering on the ports on the machine and hubs. Measure once, write on the ports for later.





---

Files
-----


* [lscom.py](lscom.py "local file")



---

Todo
----


* maybe different -l format, with names
* maybe get it run better in windows?






