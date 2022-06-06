# HyteraCoT - Hytera to Cursor-On-Target Gateway

The HyteraCoT Hytera to Cursor-On-Target Gateway transforms Hytera radio position information into Cursor On Target (COT) Position Location Information (PLI) for display on Situational Awareness (SA) applications such as the Android Team Awareness Kit (ATAK), WinTAK, RaptorX, TAKX, iTAK, et al.

For more information on the TAK suite of tools, see: https://www.tak.gov/


## Support HyteraTAK Development

HyteraTAK has been developed for the Disaster Response, Public Safety and
Frontline Healthcare community. This software is currently provided at no-cost
to non-commercial users. Any contribution you can make to this project's development
efforts is greatly appreciated.

[![Support HyteraTAK development: Buy me a coffee!](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/kortel)


## How it works

The HyteraCoT Hytera to Cursor-On-Target Gateway connects to your Hytera repeater (tested RD965) via Ethernet cable, registers with repeater and transforms Hytera radio positions (tested PD985 and PD785) tinto Cursor On Target format to be displayed on Situational Awareness apps.

It can also forward all packets it receives to a list of hosts. All packets received on one of slot ports will be forwarded to all listed hosts on the same port number.

It does not require running under root/admin user, if you bind to ports over 1024.


## Required configuration

The repeater needs to have Forward to PC enabled with your computer IP address and both Radio GPS slot ports enabled.
Radios need to have GPS Trigger enabled (time, distance and/or both).


## Settings file

The software should work well with the default configuration.
It is possible to change global defaults and per radio configuration.

The `settings.ini` file structure is described below:

**Sections**

* `[forward-to-pc]` - general repeater settings
    * IP as defined in repeater [0.0.0.0] (it will listen on all available addresses by default)
    * gps1_port, gps2_port GPS slot ports [30003,30004]
    * forward_to list of hosts to forward packets ""
* `[hyteratak]` - general TAK server settings
    * url - TAK server url udp broadcast on default port [broadcast://239.2.3.1] (it uses the default WinTAK multicast address 239.2.3.1 and port 6969)
    * type - default CoT type [a-f-G-U-C]
    * stale - CoT stale in seconds [3600]
    * group - default group [Green]
    * role - default role [Team Member]
* `[100]` radio Section
    * name section as radio ID, for ID=100, section name will be [100]
    * type, stale, group, role as for global server settings
    * name - radio name to be displayed [RadioID (Hytera)]
    * uid - evant ID [HYTERA.RadioID]


## Other connection options

You can use other options for sending to CoT server and use IP or hostnames.

**UDP protocol**
```
[hyteratak]
url=udp://192.168.1.2:1234
```

**TCP protocol**
```
[hyteratak]
url=tcp://192.168.1.2:2345
```


## Packet forwarding

HyteraCoT can forward all received packets to a defined list of hosts.
You can use packet forwarding if you use another servers to receive Hytera packets.
All packets received on one slot ports will be forwarded to each host from the defined list on the same port number.
So all gps1 packets received on port 30003 will be forwarded to each host from the list to port 30003.
You define the host list using `forward_to` in `[forward-to-pc]` section as a comma-separated list of host names and/or IP addresses.

**Packet forwarding**

```
[forward-to-pc]
forward_to=host1,192.168.1.3
```


## Servers and protocols

HyteraTAK is compatible with the following:

Servers:

* `TAK Server <https://tak.gov/>`
* `taky <https://github.com/tkuester/taky>`
* `Free TAK Server (FTS/FreeTAKServer) <https://github.com/FreeTAKTeam/FreeTakServer>`

Clients:

* `WinTAK <https://tak.gov/>`
* `ATAK <https://tak.gov/>`
* `iTAK <https://tak.gov/>`
* `TAKX <https://tak.gov/>`
* RaptorX

HyteraTAKsupports the following network protocols:

* TCP Unicast
* TLS Unicast
* UDP Unicast
* UDP Broadcast


## Installation

Hytera is provided by a command-line tool called `hyteratak`, which can be installed 
from the Python Package Index, or directly from this source tree.

### Simple install

Install from the Python Package Index (PyPI)

You need to have Python3 installed, at least version 3.7

```bash
# You need to have Python3 installed, at least version 3.7
$ python3 -m pip install pip wheel setuptools --upgrade
$ python3 -m pip install hyteratak --upgrade
# download config file
$ curl "https://raw.githubusercontent.com/kortel-systems/hyteratak/master/settings.ini.example" -o settings.ini
# Now edit settings.ini
# forward-to-pc: You may provide Forward to PC IP
# hyteratak: You may provide global defaults
# See "settings.ini.example" for configuration
$ hyteratak <optional path to settings.ini> <optional path to logging.ini>
```

### Install from this source tree

```bash
git clone https://github.com/kortel-systems/hyteratak.git
cd hyteratak/
python3 setup.py install
```

### Install on Windows

To get software running on Windows, you need to install appropriate Python 3.7+ package (depending on your Windows version).

Then you should be able to use **Simple install**

```shell
# From standard Windows Command Line (cmd.exe)
$ python -m pip install pip wheel setuptools --upgrade
$ python -m pip install hyteratak --upgrade
# download config file
$ curl "https://raw.githubusercontent.com/kortel-systems/hyteratak/master/settings.ini.example" -o settings.ini
# Now edit settings.ini
# forward-to-pc: You may provide Forward to PC IP
# hyteratak: You may provide global defaults
# See "settings.ini.example" for configuration
$ hyteratak <optional path to settings.ini> <optional path to logging.ini>
```


## Usage

To run `hyteratak` from command-line supply the program with settings file.

```bash
hyteratak settings.ini
```
