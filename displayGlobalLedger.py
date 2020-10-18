from blockchain.lib import Ledger,Transaction
import subprocess
import time
import datetime
from colorama import Fore, Back, Style 

# a = Ledger()
subprocess.call("clear")
try:
    while True:
        print ("[ " + Fore.RED + "GLOBAL LEDGER" + Style.RESET_ALL + " ] Web Reputation Current:")
        print ("")
        print ("")
        try:
            ledger = Ledger().get()
        except:
            continue
        else:
            for i in range(len(ledger)):
                if ledger[i]["enabled"] == "True":
                    print("FQDN: " +Fore.YELLOW + ledger[i]["fqdn"] + Style.RESET_ALL + " | Hits: " + Fore.GREEN + ledger[i]["hits"] + Style.RESET_ALL)
            
            print ("")
            print ("")
            print ("")
            print ("Last Updated: "+ Fore.WHITE +  datetime.datetime.now().strftime("%x %X") + Style.RESET_ALL)
            print ("")
            print("Press Ctrl-C to exit")
        time.sleep(3)
        subprocess.call("clear")
except KeyboardInterrupt:
    pass

            