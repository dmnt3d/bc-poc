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
    print ("[" + node.name + "]["+ datetime.datetime.now().strftime("%x %X") + "] " + message)


node = Node("node01")
globalLedger = Ledger()
transaction = Transaction()
# subprocess.call("clear")

try:
    while True:
        printOutput(" ---- START Consolidating ---- ")
        # STEP 1:
        globalLedger = Ledger().get()
        #globalLedger = globalLedger.get()
        # STEP 1.5
        # consolidate local ledger with rules applied
        # check STRATEGY, 
        # if TOP, rebaseline rules, update local ledger
        localLedger = node.getLocalLedger()
        if node.getStrategy() == "top":
            topFQDN = Ledger.getTop(globalLedger)
            if not localLedger:
                # if localLedger is empty, dump highest as localledger
                printOutput("Local Ledger not found")
                printOutput("Populating with TOP FQDN: "+ topFQDN["fqdn"])
                localLedger.append(topFQDN)
                localLedger[0]["hits"] = "0"
            elif localLedger[0]["fqdn"] != topFQDN["fqdn"]:
                # top HIT changed.
                printOutput("TOP FQDN changed to : " + topFQDN["fqdn"])
                printOutput("Removing previous top FQDN:")
                printOutput("Removing from Rule for FQDN: "+ localLedger[0]["fqdn"])
                node.delRule(localLedger[0]["fqdn"])
                printOutput("Removing from CTX for FQDN: "+ localLedger[0]["fqdn"])
                node.delCTX(localLedger[0]["fqdn"])
                printOutput("Changing Local Ledger to : " + topFQDN["fqdn"])
                localLedger[0]["fqdn"] = topFQDN["fqdn"]
                localLedger[0]["enabled"] = topFQDN["enabled"]
                localLedger[0]["hits"] = "0"

            else:
                # update hits from FW
                if node.getRuleHits(localLedger[0]["fqdn"]) == "0":
                    activeHits = "0"
                else:
                    activeHits = node.getRuleHits(localLedger[0]["fqdn"])["hit_count"]
                
                printOutput(localLedger[0]["fqdn"] + " : ACTIVE HIT " + str(activeHits))
                if int(activeHits) > int(localLedger[0]["hits"]):
                    deltahit = int(activeHits) - int(localLedger[0]["hits"])
                    # add transaction
                    printOutput(localLedger[0]["fqdn"] + " : Adding new Transaction with DELTA HIT " + str(deltahit))
                    transaction.add(localLedger[0]["fqdn"],str(deltahit))
                    # updating local ledger with API hit value
                    localLedger[0]["hits"] = activeHits
                
                #---- REVIEW TOP
        else: 
            for i in range(len(localLedger)):
                if not node.getRuleExists(localLedger[i]["fqdn"]):
                    printOutput("Active Rule and Local Ledger inconsistent")
                    printOutput("Creating Context for : " + localLedger[i]["fqdn"])
                    node.createCTX (localLedger[i]["fqdn"])
                    printOutput("Adding rule for : " + localLedger[i]["fqdn"])
                    node.createRule(localLedger[i]["fqdn"])

            # STEP 2:
            reloop = True
            while reloop:
                for i in range(len(localLedger)):
                    if getGlobalStatus(localLedger[i]["fqdn"],globalLedger) == "False":
                        # remove from LEDGER
                        # INVOKE REMOVE API for RULE and CTX
                        printOutput("Removing from Rule for FQDN: "+ localLedger[i]["fqdn"])
                        node.delRule(localLedger[i]["fqdn"])
                        printOutput("Removing from CTX for FQDN: "+ localLedger[i]["fqdn"])
                        node.delCTX(localLedger[i]["fqdn"])
                        printOutput("Removing from local ledger FQDN: "+ localLedger[i]["fqdn"])
                        localLedger.pop(i)
                        # re-LOOP again ?
                        reloop = True
                        break
                    reloop = False
                    
            
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
                        node.createRule(globalLedger[i]["fqdn"])

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
        printOutput("Finalizing. Writing local db.json")
        # write local ledger to db.json
        node.dumpLocalLedger(localLedger)
        printOutput(" ---- END Consolidating ---- ")
        time.sleep(3)

except KeyboardInterrupt:
    pass

            