# updates local ledger FROM global ledger
from blockchain.lib import Ledger,Node
import subprocess
import time
import datetime
import sys
from colorama import Fore, Back, Style 


def getGlobalHit(fqdn):
    globalLedger = Ledger()
    globalLedger = globalLedger.get()
    for i in range(len(globalLedger)):
        if globalLedger[i]["fqdn"] == fqdn:
            return globalLedger[i]["hits"]
    return 0
        

def main(argv):
    if len(argv) < 1:
        print ("No node supplied!")
        exit(1)
    
    try:
        node = Node(argv[1])
    except:
        print ("Node not found!")
        exit(1)
            
    subprocess.call("clear")
    try:
        while True:
            # BEGIN STEP 1:
            try:
                localLedger = node.getLocalLedger()
            except:
                continue
            else:
                print ("[ " + Fore.RED + node.name + Style.RESET_ALL +  " ] Local Ledger: Currently Applied")
                print ("")
                print ("")
                #print (len(localLedger)) 
                print("FQDN             [Local Hits/ Global Hits] ")
                for i in range(len(localLedger)):
                    print(localLedger[i]["fqdn"] + "       [ " + Fore.GREEN + "" + str(localLedger[i]["hits"]) +""+ Style.RESET_ALL + " / " + Fore.YELLOW +""+ str(getGlobalHit(localLedger[i]["fqdn"])) +""+ Style.RESET_ALL + " ]")
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
                time.sleep(5)
                subprocess.call("clear")
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
   main(sys.argv)
            