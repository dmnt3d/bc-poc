from blockchain.lib import Ledger,Transaction
import subprocess
import time
import datetime

# a = Ledger()
subprocess.call("clear")
try:
    while True:
        print ("[ GLOBAL LEDGER ] Web Reputation Current:")
        ledger = Ledger().get()
        for i in range(len(ledger)):
            if ledger[i]["enabled"] == "True":
                print("FQDN: " + ledger[i]["fqdn"] + " | Hits: " + ledger[i]["hits"])
        
        print ("")
        print ("Last Updated: "+ datetime.datetime.now().strftime("%x %X"))
        print ("")
        print("Press Ctrl-C to exit")
        time.sleep(3)
        subprocess.call("clear")
except KeyboardInterrupt:
    pass

            