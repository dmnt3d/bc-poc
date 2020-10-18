from blockchain.lib import Ledger,Transaction,Node
import subprocess
import time
import datetime
import sys

# PULL OPERATION
# - get from GLOBAL LEDGER 
# - Update LOCAL LEDGER in MEMORY
# - no WRITE yet

    # CONSOLIDATE
    # - Updates LOCAL LEDGER in Memory with FW RULES in NSX-T
    # - Deletes/ Add RULES and CTX

# PUSH OPERATION
# - get FW STATS, add Transaction based on HITS
# - updates local hits in LocalLedger Memory

# Local Update
# Writes to localDB

def getGlobalStatus(fqdn,globalLedger):
    for i in range(len(globalLedger)):
        if globalLedger[i]["fqdn"] == fqdn:
            return globalLedger[i]["enabled"]
    return "False"

def checkLocalLedger (fqdn,ledger):
    for i in range(len(ledger)):
        if ledger[i]["fqdn"] == fqdn:
            return True
    return False


def pull(node):
    globalLedger = Ledger().get()
    localLedger = node.getLocalLedger()
    # top ONLY strategy
    if node.getStrategy() == "top":
        topFQDN = Ledger.getTop(globalLedger)
        if not localLedger:
            # if localLedger is empty, dump highest as localledger
            node.printOutput("Local Ledger not found")
            node.printOutput("Populating with TOP FQDN: "+ topFQDN["fqdn"], "add")
            localLedger.append(topFQDN)
            localLedger[0]["hits"] = "0"
            return localLedger
        
        if localLedger[0]["fqdn"] != topFQDN["fqdn"]:
            # update localLedger Memory
            node.printOutput("TOP FQDN changed to : " + topFQDN["fqdn"])
            localLedger[0]["fqdn"] = topFQDN["fqdn"]
            localLedger[0]["enabled"] = topFQDN["enabled"]
            localLedger[0]["hits"] = "0"
            return localLedger
    
    else:
        # everything that is enabled
        # go thru the localLedger and check if anything is disabled, 
        # remove accordingly
        reloop = True
        while reloop:
            for i in range(len(localLedger)):
                if getGlobalStatus(localLedger[i]["fqdn"],globalLedger) == "False":
                    # remove from LocalLEDGER
                    # INVOKE REMOVE API for RULE and CTX
                    node.printOutput("Marking as disabled in local ledger FQDN: "+ localLedger[i]["fqdn"], "remove")
                    #localLedger[i]["enabled"] = "False"
                    localLedger.pop(i)
                    # re-LOOP again ?
                    reloop = True
                    break
                reloop = False
        

        # check GlobalLedger for items not present in LocalLedger
        for i in range(len(globalLedger)):
            if globalLedger[i]["enabled"] == "True":
                if not checkLocalLedger(globalLedger[i]["fqdn"], localLedger):
                    node.printOutput("Found NEW FQDN from Global Ledger: "+ globalLedger[i]["fqdn"] + ".")
                    node.printOutput("Adding to local ledger: "+ globalLedger[i]["fqdn"], "add")
                    localLedger.append(globalLedger[i])
                    # set to 0 hits; dont copy globalLedger record on HITS
                    # get to total len -1
                    localLedger[len(localLedger)-1]["hits"] = "0"

    return localLedger

def consolidate(node, localLedger):
    # CONSOLIDATE
    # - Updates LOCAL LEDGER in Memory with FW RULES in NSX-T
    # - Deletes/ Add RULES and CTX
    # appliedLedger is the FILE SYSTEM
    # localLedger is the modified localLedger
    appliedLedger = node.getLocalLedger()
    if node.getStrategy() == "top":
        if not appliedLedger:
                    # apply the localLedger rules
            node.printOutput("Creating Context for : " + localLedger[0]["fqdn"], "add")
            node.createCTX (localLedger[0]["fqdn"])
            node.printOutput("Adding rule for : " + localLedger[0]["fqdn"], "add")
            node.createRule(localLedger[0]["fqdn"])
        
        elif appliedLedger[0]["fqdn"] != localLedger[0]["fqdn"]:
            node.printOutput("TOP FQDN changed to : " + localLedger[0]["fqdn"])
            node.printOutput("Removing previous top FQDN:", "remove")
            node.printOutput("Removing from Rule for FQDN: "+ appliedLedger[0]["fqdn"], "remove")
            node.delRule(appliedLedger[0]["fqdn"])
            node.printOutput("Removing from CTX for FQDN: "+ appliedLedger[0]["fqdn"], )
            node.delCTX(appliedLedger[0]["fqdn"])
            # apply the localLedger rules
            node.printOutput("Creating Context for : " + localLedger[0]["fqdn"], "add")
            node.createCTX (localLedger[0]["fqdn"])
            node.printOutput("Adding rule for : " + localLedger[0]["fqdn"], "add")
            node.createRule(localLedger[0]["fqdn"])
        
        
    else:
        # all the rules 
        if not appliedLedger:
            # empty
            # apply all localLedger
            for i in range(len(localLedger)):
                node.printOutput("Creating Context for : " + localLedger[i]["fqdn"], "add")
                node.createCTX (localLedger[i]["fqdn"])
                node.printOutput("Adding rule for : " + localLedger[i]["fqdn"], "add")
                node.createRule(localLedger[i]["fqdn"])
        else:
            # check applied ledger
            # not present in localLedger
            # reverse loop. if not present in appliedLedger
            # add RULE
            for i in range(len(localLedger)):
                found = 1
                for x in range(len(appliedLedger)):
                    
                    if localLedger[i]["fqdn"] == appliedLedger[x]["fqdn"]:
                        found = 1
                        break
                    found = 0

                if found == 0:
                    # localLedger not found
                    # create RULE
                    node.printOutput("Creating Context for : " + localLedger[i]["fqdn"], "add")
                    node.createCTX (localLedger[i]["fqdn"])
                    node.printOutput("Adding rule for : " + localLedger[i]["fqdn"],"add")
                    node.createRule(localLedger[i]["fqdn"])


            # delete rule/ctx
            # nested loop appliedLedger vs LocalLedger
            for i in range(len(appliedLedger)):
                found = 1
                for x in range(len(localLedger)):
                    if appliedLedger[i]["fqdn"] == localLedger[x]["fqdn"]:
                        found = 1
                        break
                    found = 0

                if found == 0:
                    # appliedLedger not found in LocalLedger
                    # delete CTX and RULE
                    node.printOutput("Removing from Rule for FQDN: "+ appliedLedger[i]["fqdn"], "remove")
                    node.delRule(appliedLedger[i]["fqdn"])
                    node.printOutput("Removing from CTX for FQDN: "+ appliedLedger[i]["fqdn"], "remove")
                    node.delCTX(appliedLedger[i]["fqdn"])
            
            # revalidate applied rules
            for i in range(len(localLedger)):
                if not node.getRuleExists(localLedger[i]["fqdn"]):
                    node.printOutput("Active Rule and Local Ledger inconsistent", "add")
                    node.printOutput("Creating Context for : " + localLedger[i]["fqdn"], "add")
                    node.createCTX (localLedger[i]["fqdn"])
                    node.printOutput("Adding rule for : " + localLedger[i]["fqdn"], "add")
                    node.createRule(localLedger[i]["fqdn"])

    return localLedger

def push(node, localLedger):
    # PUSH OPERATION
    # - get FW STATS, add Transaction based on HITS
    # - updates local hits in LocalLedger Memory
    transaction = Transaction()
    for i in range(len(localLedger)):
        if node.getRuleHits(localLedger[i]["fqdn"]) == "0":
            activeHits = "0"
        else:
            activeHits = node.getRuleHits(localLedger[i]["fqdn"])["hit_count"]
                
        node.printOutput(localLedger[i]["fqdn"] + " : ACTIVE HIT " + str(activeHits))
        if int(activeHits) > int(localLedger[i]["hits"]):
            deltahit = int(activeHits) - int(localLedger[i]["hits"])
                    # add transaction
            node.printOutput(localLedger[i]["fqdn"] + " : Adding new Transaction with DELTA HIT " + str(deltahit), "add")
            transaction.add(localLedger[i]["fqdn"],str(deltahit))
            # updating local ledger with API hit value
            localLedger[i]["hits"] = activeHits
    
    return localLedger


if __name__ == "__main__":

    if len(sys.argv) < 1:
        print ("No node supplied!")
        exit(1)
    
    try:
        node = Node(sys.argv[1])
    except:
        print ("Node not found!")
        exit(1)
    try:
        while True:
            node.printOutput("start PULL Operation","core")
            time.sleep(2)
            localLedger = pull(node)
            node.printOutput("end PULL Operation", "core")
            node.printOutput("start CONSOLIDATE operation", "core")
            time.sleep(2)
            localLedger = consolidate(node, localLedger)
            node.printOutput("start PUSH operation", "core")
            time.sleep(2)
            localLedger = push(node, localLedger)
            node.printOutput("Writing to local db.json", "core")
            node.dumpLocalLedger(localLedger)
        time.sleep(4)

    except KeyboardInterrupt:
        pass
