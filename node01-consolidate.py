# updates local ledger FROM global ledger
from blockchain.lib import Ledger,Transaction,Node
import subprocess
import time
import datetime

'''
main consolidator script
        - step 1:
            get GLOBAL ledger
        - step 2:
            Get localLedger and go thru each list, IF marked as DISABLED in Global , create API to delete RULE and CTX
        - step 3: (based on RULE - highest HITS etc)       
            Go thru GLOBAL MANAGER, anything not present (and enabled), 
                add to localLedger variable
                make hits = 0
                create API to add RULE
        - step 4: go thru the HITs
            get API HITs and subtract to localLedger 
            If Hits >0, 
                - Add transaction for the FQDN with delta HITS
                - update localledger with HIT value from API
        - step 5: dump/ overwrite localledger
'''

def getGlobalStatus(fqdn,globalLedger):
    for i in range(len(globalLedger)):
        if globalLedger[i]["fqdn"] == fqdn:
            return globalLedger[i]["enabled"]
    return "False"

def checkLocalLedger (fqdn,localLedger):
    for i in range(len(localLedger)):
        if localLedger[i]["fqdn"] == fqdn:
            return True
    return False

def printOutput (message):
    print ("["+ datetime.datetime.now().strftime("%x %X") + "] " + message)


node = Node("node01")
globalLedger = Ledger()
transaction = Transaction()
# subprocess.call("clear")

try:
    while True:
        printOutput("== Start Consolidating ==")
        # STEP 1:
        globalLedger = Ledger()
        globalLedger = globalLedger.get()
        # STEP 1.5
        # consolidate local ledger with rules applied
        localLedger = node.getLocalLedger()
        for i in range(len(localLedger)):
            if not node.getRuleExists(localLedger[i]["fqdn"]):
                printOutput("Active Rule and Local Ledger inconsistent")
                printOutput("Creating Context for :" + localLedger[i]["fqdn"])
                node.createCTX (localLedger[i]["fqdn"])
                printOutput("Adding rule for :" + localLedger[i]["fqdn"])
                node.createRule(localLedger[i]["fqdn"],localLedger[i]["payload"])

        # STEP 2:
        for i in range(len(localLedger)):
            if getGlobalStatus(localLedger[i]["fqdn"],globalLedger) == "False":
                # remove from LEDGER
                printOutput("Removing from local ledger FQDN: "+ localLedger[i]["fqdn"])
                localLedger.pop(i)
                # INVOKE REMOVE API for RULE and CTX
                printOutput("Removing from Rule for FQDN: "+ localLedger[i]["fqdn"])
                node.delRule(localLedger[i]["fqdn"])
                printOutput("Removing from CTX for FQDN: "+ localLedger[i]["fqdn"])
                node.delCTX(localLedger[i]["fqdn"])
                # re-LOOP again ?
        
        # STEP 3:
        # loop thru Global Ledger FQDN that are ENABLED and see if theres NEW FQDN
        for i in range(len(globalLedger)):
            if globalLedger[i]["enabled"] == "True":
                if not checkLocalLedger(globalLedger[i]["fqdn"], localLedger):
                    printOutput("Found NEW FQDN from Global Ledger: "+ globalLedger[i]["fqdn"] + ".")
                    localLedger.append(globalLedger[i])
                    # set to 0 hits; dont copy globalLedger record on HITS
                    localLedger[len(localLedger)-1]["hits"] = 0
                    # add CTX
                    printOutput("Adding domain context for : "+ globalLedger[i]["fqdn"] + ".")
                    node.createCTX(globalLedger[i]["fqdn"])
                    # add RULE
                    printOutput("Adding rule for : "+ globalLedger[i]["fqdn"] + ".")
                    node.createRule(globalLedger[i]["fqdn"],globalLedger[i]["payload"])


        # STEP 4:
        '''
            go thru localLedger
            - get API HITs, subtract to localLedger 
            If Hits >0, 
                - Add transaction for the FQDN with delta HITS
                - update localledger with HIT value from API
        '''

        for i in range(len(localLedger)):
            # get hits per FQDN in localledger
            # get hit_count value from statistics
            
            if node.getRuleHits(localLedger[i]["fqdn"]) == "0":
                activeHits = "0"
            else:
                activeHits = node.getRuleHits(localLedger[i]["fqdn"])["hit_count"]
            
            printOutput(localLedger[i]["fqdn"] + " : ACTIVE HIT " + str(activeHits))
            if int(activeHits) > int(localLedger[i]["hits"]):
                deltahit = int(activeHits) - int(localLedger[i]["hits"])
                # add transaction
                printOutput(localLedger[i]["fqdn"] + " : Adding new Transaction with DELTA HIT " + str(deltahit))
                transaction.add(localLedger[i]["fqdn"],str(deltahit))
                # updating local ledger with API hit value
                localLedger[i]["hits"] = activeHits


        # STEP 5:
        # dump to local db.json the full localLedger file
        printOutput("Finalizing. Writing local db.json ...")
        # write local ledger to db.json
        node.dumpLocalLedger(localLedger)
        printOutput("END RUN")
        time.sleep(3)

except KeyboardInterrupt:
    pass

            