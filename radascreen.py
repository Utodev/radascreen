#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-

# Rasdascreen (C) Uto 2016-2021
# BMP to Radastan mode .tap converter for ZX-Uno
# This file is licensed under the GPL v3 or later license

import sys


def help():
    print('Syntax: python3 radascreeen.py <input bmp file> <output tap file>' +
          '[loader file] [/p] [/v]')
    print('        Example: python3 radascreeen.py knigthRider.bmp krider.tap')
    print(
        '        Example: python3 radascreeen.py knigthRider.bmp krider.tap' +
        ' alternative_loader.tap /p')
    print('')
    print('        /p uses proportional method instead of truncate method to' +
          'interpolate palette colors')
    print('        /v verbose mode')
    sys.exit(1)


def error(str):
    print('Error: {0}'.format(str))
    sys.exit(1)


print('Radastan mode BMP converter (C) Uto 2016-2021 v0.2')

if len(sys.argv) > 2:
    inputfile = sys.argv[1]
    outputfile = sys.argv[2]
else:
    help()

# defaults
palette_method = 'truncate'
loader_file = 'loader.tap'
verbose = 0

# Check extra arguments
i = 3
while i < len(sys.argv):
    if sys.argv[i] == '/p':
        palette_method = 'proportional'
    else:
        if sys.argv[i] == '/v':
            verbose = 1
        else:
            loader_file = sys.argv[i]
    i += 1

print('Converting {0} => {1}'.format(inputfile, outputfile))

bmp = []

try:
    f = open(inputfile, 'rb')
except FileNotFoundError:
    error('BMP file {0} not found.'.format(inputfile))

try:
    byte = f.read(1)
    while byte:
        bmp.append(ord(byte))
        byte = f.read(1)
finally:
    f.close()

if len(bmp) != 6262:
    error('File must be a 128x96 file 16 colors. Expected file size is 6262')

# Extract palette and convert to RRRGGGBB
palette = []
index = 0
if verbose:
    print('Palette interpolation: {0}'.format(palette_method))
while index <= 15:
    B = bmp[0x36 + index * 4]
    G = bmp[0x36 + index * 4 + 1]
    R = bmp[0x36 + index * 4 + 2]
    # A = bmp[0x36 + index * 4 + 3]
    if (palette_method == 'truncate'):
        G = G & 0b11100000
        B = (B >> 6) & 3
        R = (R >> 3) & 0b00011100
        RGB = R + G + B
        if verbose:
            print('COLOR {0} ==> ({1},{2},{3}) {4}'.format(
                index, R >> 2, G >> 5, B, RGB))
    else:
        R = int(round(R * 7 / 255))
        G = int(round(G * 7 / 255))
        B = int(round(B * 3 / 255))
        RGB = (G << 5) + (R << 2) + B
        if verbose:
            print('COLOR {0} ==> ({1},{2},{3}) {4}'.format(
                index, R, G, B, RGB))
    palette.append(RGB)
    index += 1

# Extract BMP scanlines data and store it in direct order
screen = []
linesProcessed = 0
screenPointer = 0x76 + 95 * 64
while linesProcessed < 96:
    for i in range(64):
        screen.append(bmp[screenPointer + i])
    linesProcessed += 1
    screenPointer -= 64

# Load the loader.tap file
output_tap = []
try:
    f = open(loader_file, 'rb')
except FileNotFoundError:
    error('loader file [{0}] missing.'.format(loader_file))
try:
    byte = f.read(1)
    while byte:
        output_tap.append(ord(byte))
        byte = f.read(1)
finally:
    f.close()

screenpos = len(output_tap)

# The screen block header for tap file, a header, plus the start of data code
# (last 0xff)
screen_header = [
    0x13, 0x00, 0x00, 0x03, 0x53, 0x43, 0x52, 0x45, 0x45, 0x4e, 0x20, 0x20,
    0x20, 0x20, 0x10, 0x18, 0x00, 0x40, 0x00, 0x80, 0xc7, 0x12, 0x18, 0xff
]

# Add screen header
output_tap.extend(screen_header)
output_tap.extend(screen)
output_tap.extend(palette)

# Calculate and append checksum (XOR of flag byte and all the screen and
# palette contents)
checksum = 0xff  # flag byte
for byte in screen:
    checksum ^= byte
for byte in palette:
    checksum ^= byte
output_tap.append(checksum)

# Save tap file
try:
    f = open(outputfile, 'wb')
except IOError:
    error('Could not open output file {0}.'.format(outputfile))

try:
    f.write(bytearray(output_tap))

finally:
    f.close()

print('Done.')
sys.exit(0)
'''
Notes:

TAP file format details: http://rk.nvg.ntnu.no/sinclair/faq/fileform.html#TAPZ

'''
