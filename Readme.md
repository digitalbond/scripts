# Random Scripts

###Digital Bond's Random Script Repository

These scripts are occasionally handy for tasks such as reverse engineering proprietary protocols, learning about binary file formats, and otherwise violating your End User License Agreement.

Please only use these tools for research purposes, and only to help the Good Guys.

Each script is documented below and available in this repository.

* [crc32tester.py] Identify how a CRC32 is produced in a piece of binary data.

###crc32tester.py

####Authors

Reid Wightman [Digital Bond, Inc](http://www.digitalbond.com)

####Prerequisite packages

This tool was built assuming that one has the binascii, struct, sys, and
hexdump Python libraries installed.

All but hexdump are part of a default Python 2.7 install.  Hexdump
is not required if you do not wish to see debugging/troubleshooting
output, and you may comment out the 'import hexdump' line if you do not
plan to use debugging.

####Purpose and Description

This script determines how a CRC32 is generated when its position is known inside of a piece of binary data.

If you are analyzing a protocol or file format and believe that you have identified a 4-byte CRC, you can use this tool to determine how the CRC was generated.

The script assumes that the CRC location provided is correct. It tries little-endian and big-endian byte orders for the CRC, and assumes that the CRC was calculated by placing all null bytes into the CRC field when the CRC was calculated.

####Sample usage

Let's analyze an uncommon protocol.  The file 'codesysv3-crc32.bin', included
in this repository, is the data payload from a single CoDeSys V3 protocol
packet.

This packet was generated from Wireshark by observing a TCP session packet,
selecting the unrecognized data payload, and choosing "Export Packet Bytes".

If we analyze several of these packets, we notice that there appears to be a
CRC32 located at offset 44 (hex 0x2C).  These four bytes change values, and
the values vary greatly from one packet to the next.

We run the crc32tester with:

$ python crc32tester.py codesysv3-crc32.bin 44

Candidate found. Params: trimfront 48 trimend 0 LE

The output means that we trim the first 48 bytes off of the packet in order to
calculate the CRC32.  If bytes were also trimmed off of the end of the packet,
the tool would have discovered this also. Now we can produce our own packets,
since we know how to calculate the CRC in this proprietary protocol.

