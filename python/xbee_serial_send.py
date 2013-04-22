#! /usr/bin/python

from xbee import XBee
import serial

import struct
import time


"""
serial_example.py
By Paul Malmsten, 2010

Demonstrates reading the low-order address bits from an XBee Series 1
device over a serial port (USB) in API-mode.
"""

destination = 2   # destination xbee
serialport = '/dev/ttyACM3' # serial port string

def main():
    """
    Sends an API AT command to read the lower-order address bits from 
    an XBee Series 1 and looks for a response
    """
    try:
        
        # Open serial port
        ser = serial.Serial( serialport, 57600)
        
        # Create XBee Series 1 object
        xbee = XBee(ser)
        
        framecnt = 0
        while True:
	  framecnt = framecnt + 1
	  if framecnt == 16:
	    framecnt = 1
	  msgid = chr( framecnt )
	  datalist = [ msgid ]
	  #//datalist.extend( datalistin )
	  data = ''.join( datalist )
	  hrm = struct.pack('>H', destination )
	  xbee.send('tx',
	    dest_addr=hrm,
	    data=data,
	    frame_id=msgid,
	    options='\x02'
          )

	  # Wait for response
	  response = xbee.wait_read_frame()
	  print response
	  time.sleep( 0.1 )
                
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()
    
if __name__ == '__main__':
    main()
