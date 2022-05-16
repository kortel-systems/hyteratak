# HyteraTAK - Hytera to Cursor-On-Target Gateway

This software will track your Hytera radios on WinTAK.

It connects to your Hytera repeater (tested RD965) via Ethernet cable, registers with repeater and gets radio positions (tested PD985 and PD785) to update on WinTAK.

It does not require running under root/admin user, if you bind to ports over 1024.

## Required configuration

The repeater needs to have Forward to PC enabled with your computer IP address and both Radio GPS slot ports enabled.
Radios need to have GPS Trigger enabled (time, distance or both).

## Settings file

The software should work well with the default configuration.
It is possible to change global defaults and per radio configuration.

The `settings.ini` file structure is described below:

**Sections**

* `[forward-to-pc]` - general repeater settings
    * IP as defined in repeater [0.0.0.0]
    * gps1_port, gps2_port GPS slot ports [30003,30004]
* `[hyteratak]` - general TAK server settings
    * url - TAK server url udp broadcast on default port [broadcast:239.2.3.1]
    * type - default CoT type [a-f-G-U-C]
    * stale - CoT stale in seconds [3600]
    * group - default group [Green]
    * role - default role [Team Member]
* `[100]` radio Section
    * name section as radio ID, for ID=100, section name will be [100]
    * type, stale, group, role as for global server settings
    * name - radio name to be displayed [RadioID (Hytera)]
    * uid - evant ID [HYTERA.RadioID]

## Support HyteraTAK Development

HyteraTAK has been developed for the Disaster Response, Public Safety and
Frontline Healthcare community. This software is currently provided at no-cost
to non-commercial users. Any contribution you can make to this project's development
efforts is greatly appreciated.

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
