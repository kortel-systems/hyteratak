#!/bin/bash

# for python
kaitai-struct-compiler -t python --python-package hyteratak.kaitai *.ksy ; black .

# for lua
kaitai-struct-compiler -t lua *.ksy ; mv *.lua wireshark/
