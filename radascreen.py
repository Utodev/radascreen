# This file is licensed under the GPL v3 or later license

import sys

def help():
	print "Syntax: python output_tap.py <input bmp file> <output tap file> [loader file]"
	print "        Example: python output_tap.py knigthRider.bmp krider.tap"
	print "        Example: python output_tap.py knigthRider.bmp krider.tap alternative_loader.tap"
	sys.exit(1)

def error(str):	
	print "Error: ", str
	sys.exit(1)

print "Radastanian mode BMP converter (C) Uto 2016"
if len(sys.argv) in [3,4]:
	inputfile = sys.argv[1]
	outputfile = sys.argv[2]
else:
	help()

if len(sys.argv)==4:
	loader_file = sys.argv[3]
else:
	loader_file = 'loader.tap'

print 'Converting ' ,inputfile, ' => ',outputfile


bmp = []

try:
	f = open(inputfile, "rb")
except:
	error('BMP file ',inputfile,'not found.')

try:
    byte = f.read(1)
    while byte != "":
        bmp.append(ord(byte))
        byte = f.read(1)
finally:
    f.close()

if len(bmp)!= 6262:
	error("File must be a 128x96 file 16 colors. Expected file size is 6262")



# Extract palette and convert to RRRGGGBB 
palette = []
index = 0
while index<=15 :
	B = bmp[0x36 + index * 4]
	G = bmp[0x36 + index * 4 + 1]
	R = bmp[0x36 + index * 4 + 2]
	# A = bmp[0x36 + index * 4 + 3]
	G = G & 0b11100000
	B = (B >> 6) & 3
	R = (R >> 3) & 0b00011100
	RGB = R+G+B
	palette.append(RGB)
	index+=1

# Extract BMP scanlines data and store it in direct order
screen=[]
linesProcessed = 0
screenPointer = 0x76+95*64
while linesProcessed<96:
	for i in range(64):
		screen.append(bmp[screenPointer + i])
	linesProcessed += 1
	screenPointer-=64

# Load the loader.tap file
output_tap=[]
try:
	f = open(loader_file, "rb")
except:
	error('loader file [',loader_file,'] missing.')	
try:
    byte = f.read(1)
    while byte != "":
        output_tap.append(ord(byte))
        byte = f.read(1)
finally:
    f.close()

screenpos = len(output_tap)
		
# The screen block header for tap file, a header, plus the start of data code (last 0xff)
screen_header = [0x13,0x00,0x00,0x03,0x53,0x43,0x52,0x45,0x45,0x4e,0x20,0x20,0x20,0x20,0x10,0x18,0x00,0x40,0x00,0x80,0xc7,0x12,0x18,0xff]

#Add screen header
output_tap.extend(screen_header)
output_tap.extend(screen)
output_tap.extend(palette)

#calculate and append checksum (XOR of flag byte and all the screen and palette contents)
checksum = 0xff #flag byte
for byte in screen:
	checksum = checksum ^ byte
for byte in palette:
	checksum = checksum ^ byte	
output_tap.append(checksum)


# Save tap file
try:
	f = open(outputfile, "wb")
except:
	error("Could not open output file ", outputfile, '.')	

try:
	for i in output_tap:
		f.write(chr(i))	
finally:
    f.close()


print "Done."
sys.exit(0)


'''
Notes:

- TAP file format details: http://rk.nvg.ntnu.no/sinclair/faq/fileform.html#TAPZ

'''