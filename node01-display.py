# updates local ledger FROM global ledger
from blockchain.lib import Ledger,Node
import subprocess
import time
import datetime


def getGlobalHit(fqdn):
    globalLedger = Ledger()
    globalLedger = globalLedger.get()
    for i in range(len(globalLedger)):
        if globalLedger[i]["fqdn"] == fqdn:
            return globalLedger[i]["hits"]
    return 0
        


node = Node("node01")
subprocess.call("clear")
try:
    while True:
        # BEGIN STEP 1:
        localLedger = node.getLocalLedger()
        
        print ("[ " + node.name + " ] Local Ledger: Currently Applied")
        print (len(localLedger)) 
        print("FQDN             [Local Hits/ Global Hits] ")
        for i in range(len(localLedger)):
             print(localLedger[i]["fqdn"] + "       [ " + localLedger[i]["hits"] + " / " + getGlobalHit(localLedger[i]["fqdn"]) + " ]")
        
        print ("")
        print ("")
        print ("")
        print ("Last Updated: "+ datetime.datetime.now().strftime("%x %X"))
        print ("")
        print("Press Ctrl-C to exit")
        # dump to local direcotry
        #node.dumpLocalLedger(localLedger)
        # begin operation

        # refresh screen
        time.sleep(3)
        subprocess.call("clear")
except KeyboardInterrupt:
    pass

            