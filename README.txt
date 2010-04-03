Battlefied Bad Company 2 redirect
=================================

This tool displays in a human readable manner all BFBC2 rcon
traffic between your BFBC2 admin tool and a BFBC2 server.

It does so opening a port on localhost and redirect all TCP 
traffic to the BFBC2 server:port

Usage example :
Let say you want to watch BFBC2 rcon traffic to your BFBC2 server
which listens on 11.22.33.4:48888.

1. run the redirect tool :
    bfbc2redirect 42222 11.22.33.4 48888
    
2. now run your admin tool telling it to connect to 
localhost:42222
instead of
11.22.33.4:48888

