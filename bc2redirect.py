#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Usage: bfbc2redirect PORT HOST [NEWPORT]
   Or: bfbc2redirect OPTION
Forward PORT to HOST while printing human readable BFBC2 Queries and Responses

The NEWPORT parameter may be used to redirect to a different port.

Options:
  --help        display this help and exit
  --version     output the version information and exit

Examples:
  bfbc2redirect 48888 <bfbc2 ip>
  Forward all incoming connection on localhost:48888 to <bfbc2 ip>:48888

  bfbc2redirect 42222 <bfbc2 ip> 48888
  Forward all incoming connection on localhost:42222 to <bfbc2 ip>:48888
    
"""

__author__ = "Thomas LEVEIL <thomasleveil@gmail.com>"
__version__ = "1.2"

import sys
from socket import *
from threading import Thread, Lock
import time
from bfbc2.protocol import DecodePacket
import bfbc2
from bfbc2 import humanReadablePacket

DEBUG = False
LOGGING = False

def log( s ):
    if LOGGING:
        print '%s:%s' % ( time.ctime(), s )
        sys.stdout.flush()

class PipeThread( Thread ):
    pipes = []
    def __init__( self, name, printpacketLock, source, sink ):
        Thread.__init__( self )
        self.name = name
        self.daemon = True
        self.printpacketLock = printpacketLock
        self.source = source
        self.sink = sink
        self.bfbc2PacketReader = bfbc2.PacketReader()

        log( 'Creating new pipe thread  %s ( %s -> %s )' % \
            ( self, source.getpeername(), sink.getpeername() ))
        PipeThread.pipes.append( self )
        log( '%s pipes active' % len( PipeThread.pipes ))

    def run( self ):
        while 1:
            try:
                data = self.source.recv( 1024 )
                if not data: break
                self.sink.sendall( data )
                self.bfbc2PacketReader.append( data )
                try:
                    if DEBUG:
                        print "%r" % data
                    while True:
                        packet = self.bfbc2PacketReader.getPacket()
                        if packet is None:
                            break
                        self.printPacket(packet)
                except bfbc2.IncompletePacket, err:
                    log( 'incomplete packet : %r' % err )
                    pass
            except:
                break

        log( '%s terminating' % self )
        PipeThread.pipes.remove( self )
        log( '%s pipes active' % len( PipeThread.pipes ))
        
    def printPacket(self, packet):
        try:
            self.printpacketLock.acquire()
            print "%s %s" % (self.name.rjust(4), humanReadablePacket(packet))
            sys.stdout.flush()
        finally:
            self.printpacketLock.release()
        
        
class Pinhole( Thread ):
    def __init__( self, port, newhost, newport ):
        Thread.__init__( self )
        log( 'Redirecting: localhost:%s -> %s:%s' % ( port, newhost, newport ))
        self.newhost = newhost
        self.newport = newport
        self.sock = socket( AF_INET, SOCK_STREAM )
        self.sock.bind(( '', port ))
        self.sock.listen(5)
        self.printpacketLock = Lock()
    
    def run( self ):
        nb_connections = 0
        while 1:
            newsock, address = self.sock.accept()
            nb_connections += 1
            log( 'Creating new session (c%s) for %s %s ' % ((nb_connections, ) + address) )
            fwd = socket( AF_INET, SOCK_STREAM )
            fwd.connect(( self.newhost, self.newport ))
            PipeThread('BC2 <-c%s--- Client '%nb_connections, self.printpacketLock, newsock, fwd ).start()
            PipeThread('BC2 ---c%s-> Client '%nb_connections, self.printpacketLock, fwd, newsock ).start()
       
 
 
def version():
    print """\
version %s
author : %s
""" % (__version__, __author__)
    
def usage():
    print __doc__
    

def main_is_frozen():
    """detect if the script is running from frozen
    distribution. i.e: from a py2exe build or others
    """
    import imp
    return (hasattr(sys, "frozen") or # new py2exe
        hasattr(sys, "importers") or # old py2exe
        imp.is_frozen("__main__")) # tools/freeze
    
def main():
    from getopt import getopt, GetoptError
    
    try:
        opts, args = getopt(sys.argv[1:], "ho:v", ["help", "version"])
    except GetoptError, err:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for o, a in opts:
        if o in ("--help"):
            usage()
            sys.exit()
        elif o in ("--version"):
            version()
            sys.exit()
        else:
            assert False, "unhandled option"
            
    
    port = None
    newhost = None
    newport = None
    
    if len( sys.argv ) > 1:
        port = newport = int( sys.argv[1] )
        newhost = sys.argv[2]
        if len( sys.argv ) == 4: newport = int( sys.argv[3] )
    
    if port is None or newhost is None or newport is None:
        usage()
        sys.exit(2)
    
    print "Redirecting port %s to %s:%s" % (port, newhost, newport)

    #sys.stdout = open( 'pinhole.log', 'w' )
    mainthread = Pinhole( port, newhost, newport )
    mainthread.daemon = True
    mainthread.start()
    
    import time
    try:
        while 1:
            time.sleep(1000)
    except KeyboardInterrupt:
        print "bye"
        pass
            
if __name__ == "__main__":
    import traceback
    try:
        main()
    except SystemExit:
        pass
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()
    if main_is_frozen():
        raw_input('press the [Enter] key to exit')
        
    sys.exit( 0 )