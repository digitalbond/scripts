# This script takes a file and an offset of a suspected CRC32.
# It attempts to find which portion of the file was used to generate
# the CRC32.  Set 'debug=False' in the call to crc32find() to lessen
# the output.
#
# This script is not particularly efficient with memory and may be
# improved by modifying the original file data to replace the CRC
# just once.
#
# Reid Wightman, Digital Bond Labs, 2015

import binascii
import struct
import hexdump
import sys


def usage():
    print "Usage: %s <filename> <crc offset>" % sys.argv[0]
    exit(1)
# take a chunk of data and find a crc32 in it
# assume that the crc32 was computed with the original value \x00\x00\x00\x00 in the data

def crc32find(instring, offset = -1, debug = False):
    if offset == -1:
        print "Error: can't do autooffset yet"
    mycrc = instring[offset:offset+4]
    if debug:
        print "Searching for "
        hexdump.hexdump(mycrc)
        print "Original packet"
        hexdump.hexdump(instring)
    newstring = instring[0:offset] + "\x00\x00\x00\x00" + instring[offset + 4:]
    if debug:
        print "Searching packet"
        hexdump.hexdump(newstring)
    trimfront = 0
    trimend = 0
    while(trimend < len(instring)):
        trimfront = 0 # reset it on each pass
        while (trimfront + trimend < len(instring)):
            te = 0 - trimend
            if te == 0:
                teststring = newstring[trimfront:]
            else:
                teststring = newstring[trimfront:te]
            if debug:
                print "Trying"
                hexdump.hexdump(teststring)
            testcrc = binascii.crc32(teststring) & 0xffffffff
            testcrcbe = struct.pack(">I", testcrc)
            testcrcle = struct.pack("<I", testcrc)
            if debug:
                print "Test BE"
                hexdump.hexdump(testcrcbe)
            if testcrcbe == mycrc:
                print "Candidate found. Params: trimfront", trimfront, "trimend", trimend, "BE"
                return
            if debug:
                print "Test LE"
                hexdump.hexdump(testcrcle)            
            if testcrcle == mycrc:
                print "Candidate found. Params: trimfront", trimfront, "trimend", trimend, "LE"
                return
            trimfront += 1
        trimend += 1
        
        
if __name__ == "__main__":
    if len(sys.argv) < 3:
        usage()
    try:
        myfile = open(sys.argv[1])
    except:
        print "File not found"
        usage()
    try:
        offset = int(sys.argv[2])
    except:
        print "Invalid offset"
        usage()
    data = myfile.read()
    if len(data) < offset+4:
        print "Offset beyond end of file"
        usage()
    crc32find(data, offset, debug=False)
        
