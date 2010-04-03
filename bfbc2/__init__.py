

from protocol import DecodeInt32, DecodePacket
import unittest

class IncompletePacket(Exception): pass

class PacketReader(object):
    _buffer = ''

    def append(self, data):
        self._buffer += data
        
    def getPacket(self):
        """
        will only return complete bfbc2packet. Else raise IncompletePacket exception
        """        
        if len(self._buffer) == 0:
            return None
        if len(self._buffer) < 12:
            raise IncompletePacket(self._buffer)
        
        packetSize = DecodeInt32(self._buffer[4:8])
        if len(self._buffer) < packetSize:
            raise IncompletePacket(self._buffer)
        
        packetData = self._buffer[:packetSize]
        self._buffer = self._buffer[packetSize:]
        return packetData
    
        

def humanReadablePacket(packet):
    message = ''
    isFromServer, isResponse, sequence, words = DecodePacket(packet)
    
    if isFromServer:
        message += 's'
    else:
        message += 'c'
    
    if isResponse:
        message += 'R'
    else:
        message += 'Q'
        
    message += str(sequence).center(10)
        
    if words:
        message += " : "
        for word in words:
            message += '"%s" ' % word

    return message

        
####################################################################################
#                                                                                  #
#                                  T E S T S                                       #
#                                                                                  #
####################################################################################

class TestAppend(unittest.TestCase):
    
    def setUp(self):
        self.pr = PacketReader()
    
    def test_initial(self):
        self.assertEqual(self.pr._buffer, '')
    
    def test_data1(self):
        self.pr.append('123456')
        self.assertEqual(self.pr._buffer, '123456')
    
    def test_data2(self):
        self.pr.append('123456')
        self.pr.append('abcdefg')
        self.assertEqual(self.pr._buffer, '123456abcdefg')


class TestPacketReader(unittest.TestCase):

    okPacket = '\x05\x00\x00\x40\x13\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00OK\x00'

    def setUp(self):
        self.pr = PacketReader()

    def test_nodata(self):
        self.assertRaises(IncompletePacket, self.pr.getPacket)

    def test_2bytes(self):
        self.pr.append('..')
        self.assertRaises(IncompletePacket, self.pr.getPacket)

    def test_lessthan12bytes(self):
        i = 1
        while i <= 12:
            self.pr._buffer = self.okPacket[0:i]
            self.assertRaises(IncompletePacket, self.pr.getPacket)
            i += 1

    def test_imcompleteOkPacket(self):
        self.pr._buffer = self.okPacket[:18]
        self.assertRaises(IncompletePacket, self.pr.getPacket)
    
    def test_okPacket(self):
        self.pr._buffer = self.okPacket 
        packet = self.pr.getPacket()
        self.assertEqual(packet, self.okPacket)
        
    def test_okPacket_andMore(self):
        self.pr._buffer = self.okPacket + 'more junk'
        
        self.assertEqual(self.pr.getPacket(), self.okPacket)
        
        self.assertEqual(self.pr._buffer, 'more junk')
        
        self.assertRaises(IncompletePacket, self.pr.getPacket)

    def test_pb_sv_list_response(self):
        pbresponse = '\x17:\x00\x80\x9a\x00\x00\x00\x02\x00\x00\x00\x14\x00\x00\x00punkBuster.onMessage\x00p\x00\x00\x00PunkBuster Server: Player List: [Slot #] [GUID] [Address] [Status] [Power] [Auth Rate] [Recent SS] [O/S] [Name]\n\x00\x18:\x00\x80\x95\x00\x00\x00\x02\x00\x00\x00\x14\x00\x00\x00punkBuster.onMessage\x00k\x00\x00\x00PunkBuster Server: 1  xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(-) 11.222.333.444:10000 OK   1 3.0 0 (W) "AdmSmith"\n\x00\x19:\x00\x80\x98\x00\x00\x00\x02\x00\x00\x00\x14\x00\x00\x00punkBuster.onMessage\x00n\x00\x00\x00PunkBuster Server: 2  xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(-) 11.222.33.444:10000 OK   1 3.0 0 (W) "-S.H.A.D.O.-"\n\x00\x1a:\x00\x80\x96\x00\x00\x00\x02\x00\x00\x00\x14\x00\x00\x00punkBuster.onMessage\x00l\x00\x00\x00PunkBuster Server: 3  xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(-) 11.222.33.444:10000 OK   1 3.0 0 (W) "[ LECTOR ]"\n\x00\x1b:\x00\x80\x92\x00\x00\x00\x02\x00\x00\x00\x14\x00\x00\x00punkBuster.onMessage\x00h\x00\x00\x00PunkBuster Server: 4  xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(-) 11.222.33.444:10000 OK   1 3.0 0 (W) "Tramal"\n\x00\x1c:\x00\x80\x96\x00\x00\x00\x02\x00\x00\x00\x14\x00\x00\x00punkBuster.onMessage\x00l\x00\x00\x00PunkBuster Server: 5  xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(-) 11.22.33.444:10000 OK   1 3.6 0 (W) "Inferno1980"\n\x00\x1d:\x00\x80\\\x00\x00\x00\x02\x00\x00\x00\x14\x00\x00\x00punkBuster.onMessage\x002\x00\x00\x00PunkBuster Server: End of Player List (5 Players)\n\x00and more junk'
        self.pr._buffer = pbresponse

        self.assertEqual(self.pr.getPacket(), '\x17:\x00\x80\x9a\x00\x00\x00\x02\x00\x00\x00\x14\x00\x00\x00punkBuster.onMessage\x00p\x00\x00\x00PunkBuster Server: Player List: [Slot #] [GUID] [Address] [Status] [Power] [Auth Rate] [Recent SS] [O/S] [Name]\n\x00')
        self.assertEqual(self.pr.getPacket(), '\x18:\x00\x80\x95\x00\x00\x00\x02\x00\x00\x00\x14\x00\x00\x00punkBuster.onMessage\x00k\x00\x00\x00PunkBuster Server: 1  xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(-) 11.222.333.444:10000 OK   1 3.0 0 (W) "AdmSmith"\n\x00')
        self.assertEqual(self.pr.getPacket(), '\x19:\x00\x80\x98\x00\x00\x00\x02\x00\x00\x00\x14\x00\x00\x00punkBuster.onMessage\x00n\x00\x00\x00PunkBuster Server: 2  xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(-) 11.222.33.444:10000 OK   1 3.0 0 (W) "-S.H.A.D.O.-"\n\x00')
        self.assertEqual(self.pr.getPacket(), '\x1a:\x00\x80\x96\x00\x00\x00\x02\x00\x00\x00\x14\x00\x00\x00punkBuster.onMessage\x00l\x00\x00\x00PunkBuster Server: 3  xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(-) 11.222.33.444:10000 OK   1 3.0 0 (W) "[ LECTOR ]"\n\x00')
        self.assertEqual(self.pr.getPacket(), '\x1b:\x00\x80\x92\x00\x00\x00\x02\x00\x00\x00\x14\x00\x00\x00punkBuster.onMessage\x00h\x00\x00\x00PunkBuster Server: 4  xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(-) 11.222.33.444:10000 OK   1 3.0 0 (W) "Tramal"\n\x00')
        self.assertEqual(self.pr.getPacket(), '\x1c:\x00\x80\x96\x00\x00\x00\x02\x00\x00\x00\x14\x00\x00\x00punkBuster.onMessage\x00l\x00\x00\x00PunkBuster Server: 5  xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(-) 11.22.33.444:10000 OK   1 3.6 0 (W) "Inferno1980"\n\x00')
        self.assertEqual(self.pr.getPacket(), '\x1d:\x00\x80\\\x00\x00\x00\x02\x00\x00\x00\x14\x00\x00\x00punkBuster.onMessage\x002\x00\x00\x00PunkBuster Server: End of Player List (5 Players)\n\x00')
        
        self.assertRaises(IncompletePacket, self.pr.getPacket)
        
        self.assertEqual(self.pr._buffer, 'and more junk')
        
        
class TestHumanReadablePacket(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(humanReadablePacket('\x05\x00\x00@\x13\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00OK\x00'),\
                          '   -R-> 5\t : "OK" ')
        
    def test_version_query(self):
        self.assertEqual(humanReadablePacket('\x03\x00\x00\x00\x18\x00\x00\x00\x01\x00\x00\x00\x07\x00\x00\x00version\x00'),\
                          '<-Q-    3\t : "version" ') 
        
    def test_version_response(self):
        self.assertEqual(humanReadablePacket('\x03\x00\x00@(\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00OK\x00\x05\x00\x00\x00BFBC2\x00\x06\x00\x00\x00521715\x00'),\
                          '   -R-> 3\t : "OK" "BFBC2" "521715" ')
    
    
if __name__ == '__main__':
    unittest.main()