# This file is licensed under the GPL v3 or later license

import sys

def help():
	print "Syntax: python radascreen_tap.py <input bmp file> <output tap file>"
	print "        Example: python radascreen_tap.py knigthRider.bmp krider.tap"
	sys.exit(1)

def error(str):	
	print "Error: ", str
	sys.exit(1)

print "Radastanian mode BMP converter (C) Uto 2016"
if len(sys.argv)==3 :
	inputfile = sys.argv[1]
	outputfile = sys.argv[2]
else:
	help()

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

# Load the radascreen_tap.tap file
radascreen_tap=[]
try:
	f = open('radascreen.tap', "rb")
except:
	error('radascreen.tap file missing.')	

try:
    byte = f.read(1)
    while byte != "":
        radascreen_tap.append(ord(byte))
        byte = f.read(1)
finally:
    f.close()

# Replace palette
for i in range(16):
	radascreen_tap[len(radascreen_tap) -1 -1 -i] = palette[15-i] # -1 twice, once because last elemnt it's allways array length -1, and twice cause last byte in tap file blocks is checksum, not data

# Replace image
for i in range (6144):
	radascreen_tap[len(radascreen_tap) -1 -1 -16 -i] = screen[6143-i] ## Again, -1 twice, and -16 for the palette

#calculate new checksum	
checksum = 0
for i in range(6144 + 16 + 1):   # 6144 data, 16 palette, 1 for flag byte (FF in not header block in tap file)
	checksum = checksum ^ radascreen_tap[len(radascreen_tap) -1 -1 - i]   ## Once more, -1 twice to avoid the checksum itself
radascreen_tap[len(radascreen_tap) -1]	=checksum

# Save updated tap file
try:
	f = open(outputfile, "wb")
except:
	error("Could not open output file ", outputfile, '.')	

try:
	for i in radascreen_tap:
		f.write(chr(i))	
finally:
    f.close()


print "Done."
sys.exit(0)


'''
Notes:

- TAP file format details: http://rk.nvg.ntnu.no/sinclair/faq/fileform.html#TAPZ

'''