# updates local ledger FROM global ledger
from blockchain.lib import Ledger,Transaction,Node
import subprocess
import time
import datetime

'''
High Level Steps:
---- STEP 1:
- per FQDN: Update HITS as Transaction by:
    - READ LOCAL ledger from db.json and Read each API HITS
    - Subtract: Actual vs localDB
    - if >0, ADD new transaction
---- STEP 2:
- Get currently active FQDNs from Global Ledger
- Dump to local DB
---- STEP 3:
- Begin Operation to:
--> Re-apply FQDN block from local DB
--> Read Hits 
--> Update localDB copy
<sleep 3secs>

NOTE: Hits are incremental
'''
node = Node("node01")
globalLedger = Ledger()
subprocess.call("clear")
try:
    while True:
        # BEGIN STEP 1:
        localLedger = node.getLocalLedger()
        globalLedger = globalLedger.get()
        for i in range(len(localLedger)):
            # READ HITS
            node.createRule(localLedger[i]["fqdn"],localLedger[i]["payload"]) # create RULE

            blockStatistics = callapi ('/policy/api/v1/infra/domains/'+domainID+'/security-policies/Block_URL/rules/Block_FQDN/statistics')
        # BEGIN STEP 2:
        print ("[ " + node.name + " ] Local Ledger: Currently Applied")
        
        localLedger = []
        for i in range(len(globalLedger)):
            if globalLedger[i]["enabled"] == "True":
                print("FQDN: " + globalLedger[i]["fqdn"])
                # reset to 0 for localDB. to be populated after reading API
                globalLedger[i]["hits"] = "0"
                localLedger.append(globalLedger[i])
        
        print ("")
        print ("Last Updated: "+ datetime.datetime.now().strftime("%x %X"))
        print ("")
        print("Press Ctrl-C to exit")
        # dump to local direcotry
        node.dumpLocalLedger(localLedger)
        # begin operation

        # refresh screen
        time.sleep(3)
        subprocess.call("clear")
except KeyboardInterrupt:
    pass

            