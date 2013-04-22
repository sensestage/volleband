#! /usr/bin/python

"""
dispatch_async.py

By Paul Malmsten, 2010
pmalmsten@gmail.com

This example continuously reads the serial port and dispatches packets
which arrive to appropriate methods for processing in a separate thread.
"""

from xbee import XBee
from xbee.helpers.dispatch import Dispatch
import time
import serial
import struct

import OSC

#destinations = [1,2,3,4,5]   # destination xbees
destinations = [1]   # destination xbees
PORT = '/dev/ttyACM3'
hostip = '127.0.0.1'
hostport = 57120

deltatime = 0.05 # should be more than 0.005 (since we send five messages at 0.001 interval
verbose = False

BAUD_RATE = 57600

oschost = OSC.OSCClient()
send_address = ( hostip, hostport )
oschost.connect( send_address )

# Open serial port
ser = serial.Serial(PORT, BAUD_RATE)

def ByteToHex( byteStr ):
    """
    Convert a byte string to it's hex string representation e.g. for output.
    """
    
    # Uses list comprehension which is a fractionally faster implementation than
    # the alternative, more readable, implementation below
    #   
    #    hex = []
    #    for aChar in byteStr:
    #        hex.append( "%02X " % ord( aChar ) )
    #
    #    return ''.join( hex ).strip()        

    return ''.join( [ "%02X" % ord( x ) for x in byteStr ] ).strip()

def sendMessage( path, args ):
    msg = OSC.OSCMessage()
    msg.setAddress( path )
    #print args
    for a in args:
      msg.append( a )
    try:
      oschost.send( msg )
      if verbose:
	print( "sending message", msg )
    except OSC.OSCClientError:
      print( "error sending message", msg )    

# Create handlers for various packet types
def status_handler(name, packet):
    print "Status Update - Status is now: ", packet['status']


def rx_handler(name, packet):
    if verbose:
      print "RX: ", int( ByteToHex( packet['source_addr'] ), 16 ), ord( packet['rssi'] ), packet
    sendMessage( "/rx/rssi", [ int( ByteToHex( packet['source_addr'] ), 16 ), ord( packet['rssi'] ), ord( packet['rf_data'][0] ) ] )

def txstatus_handler( name, packet ):
    if verbose:
      print "TXStatus Received: ", packet
    #if packet['status'] == 0:
      #self.ack_cnt = self.ack_cnt - 1
    #elif self.verbose:
      #if packet['status'] == 1:
	#print( "TX, No ACK (Acknowledgement) received" )
      #elif packet['status'] == 2:
	#print( "TX, CCA failure" )
      #elif packet['status'] == 3:
	#print( "TX, Purged" )
      ##0 = Success
      ##1 = No ACK (Acknowledgement) received
      ##2 = CCA failure
      ##3 = Purged


# When a Dispatch is created with a serial port, it will automatically
# create an XBee object on your behalf for accessing the device.
# If you wish, you may explicitly provide your own XBee:
#
#  xbee = XBee(ser)
#  dispatch = Dispatch(xbee=xbee)
#
# Functionally, these are the same.
dispatch = Dispatch(ser)

# Register the packet handlers with the dispatch:
#  The string name allows one to distinguish between mutiple registrations
#   for a single callback function
#  The second argument is the function to call
#  The third argument is a function which determines whether to call its
#   associated callback when a packet arrives. It should return a boolean.
dispatch.register(
    "status", 
    status_handler, 
    lambda packet: packet['id']=='status'
)

dispatch.register(
    "rfdata", 
    rx_handler,
    lambda packet: packet['id']=='rx'
)

dispatch.register(
    "tx_status",
    txstatus_handler, 
    lambda packet: packet['id']=='tx_status'
)

# Create API object, which spawns a new thread
# Point the asyncronous callback at Dispatch.dispatch()
#  This method will dispatch a single XBee data packet when called
xbee = XBee(ser, callback=dispatch.dispatch)

framecnt = 0

# Do other stuff in the main thread
while True:
    try:
	framecnt = framecnt + 1
	if framecnt == 16:
	  framecnt = 1
	msgid = chr( framecnt )
	datalist = [ msgid ]
	#//datalist.extend( datalistin )
	data = ''.join( datalist )
	for dest in destinations:
	  hrm = struct.pack('>H', dest )
	  xbee.send('tx',
	    dest_addr=hrm,
	    data=data,
	    frame_id=msgid,
	    options='\x02'
	  )
	  time.sleep( 0.001 )

	# Wait for response
	#response = xbee.wait_read_frame()
	#print response

        time.sleep(deltatime - 0.005)
    except KeyboardInterrupt:
        break

# halt() must be called before closing the serial
# port in order to ensure proper thread shutdown
xbee.halt()
ser.close()
