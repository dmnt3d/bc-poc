import json
import datetime
import os
import configparser
import requests
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from colorama import Fore, Back, Style 

disable_warnings(InsecureRequestWarning)

# from requests.packages.urllib3.exceptions import InsecureRequestWarning


# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

config = configparser.ConfigParser()
config.read('config.ini')
#folder  =  config['DEFAULT']['transactionFolder']
#config['DEFAULT']['transactionFolder']

class Transaction:
    # def __init__(self, url, hits, enabled):
    #     self.url = url
    #     self.hits = hits
    #     self.enabled = enabled
    
    def add(self,fqdn, hits):
        # print(config['DEFAULT']['transactionFolder'])
        filename =  datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + ".json"
        #jsonfile = os.path.join(os.getcwd(), 'global/transactions/'+filename)
        jsonfile = str(config['DEFAULT']['transactionFolder'])+filename
        data_set = {"fqdn": fqdn, "hits": hits, "enabled": "True"}
        json_dump = json.dumps(data_set)

        file1 = open(jsonfile, "w")
        file1.write(json_dump)
        return 0
    
    def enabled(self,fqdn,enabled):
        filename =  datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + ".json"
        #jsonfile = os.path.join(os.getcwd(), 'global/transactions/'+filename)
        jsonfile = config['DEFAULT']['transactionFolder']+filename

        data_set = {"fqdn": fqdn, "hits": "0", "enabled": str(enabled)}
        json_dump = json.dumps(data_set)

        file1 = open(jsonfile, "w")
        file1.write(json_dump)

        return 0
    
    @staticmethod
    def formatURL(fqdn):
        formatted = fqdn
        if fqdn[0] == '*':
            formatted = fqdn[2:]
        return formatted.replace('.','-')
    
    # create context/ rule specific methods
    @staticmethod
    def getRulePayload(fqdn):
        payload = {
            "description": "BLOCK "+ fqdn,
            "display_name": "block-"+ Transaction.formatURL(fqdn),
            "sequence_number": 1,
            "source_groups": [
            "ANY"
            ],
            "destination_groups": [
            "ANY"
            ],
            "services": [
            "ANY"
            ],
            "profiles": [
            "/infra/context-profiles/ctx-"+ Transaction.formatURL(fqdn)
            ],
            "action": "DROP"
        }
        return payload

    @staticmethod
    def getCTXPayload(fqdn):
        payload = {
            "resource_type":"PolicyContextProfile",
            "display_name":"ctx-" + Transaction.formatURL(fqdn),
            "description":"WEB REPUTATION Context",
            "attributes":[
                {"key":"DOMAIN_NAME",
                "value": [fqdn],
                "datatype":"STRING"}
                ]
        }
        return payload
    
    @staticmethod
    def getCTXURI(fqdn):
        return "/policy/api/v1/infra/context-profiles/ctx-" + Transaction.formatURL(fqdn)
    
    @staticmethod
    def getRuleURI(fqdn):
        return "/policy/api/v1/infra/domains/default/security-policies/block-url/rules/block-" + Transaction.formatURL(fqdn)
    


class Ledger:
    
    def __init__ (self):
        self.ledger = []

    def returnIndex (self,templedger,fqdn):
        for i in range(len(templedger)):
            if templedger[i]["fqdn"] == fqdn:
                return i
        return -1
        
    def get(self):
        self.ledger = []
        tempLedger = []
        transactionPath = config['DEFAULT']['transactionFolder'] # os.path.join(os.getcwd(), 'global/transactions/')
        # print (sorted(os.listdir(transactionPath), key=os.path.getctime))
        for entry in sorted(os.listdir(transactionPath)):
            with open(transactionPath + "/" + entry) as f:
                data = json.load(f)
            # manual
            if len(tempLedger) == 0:
                tempLedger.append(data)
            elif data["enabled"] == "False":
                # entry for false, update as false
                tempLedger[self.returnIndex(tempLedger,data["fqdn"])]["enabled"] = "False"
            elif self.returnIndex(tempLedger,data["fqdn"]) == -1:
                # new fqdn, append
                tempLedger.append(data)
            else:
                # new hits. just add
                tempLedger[self.returnIndex(tempLedger,data["fqdn"])]["enabled"] = data["enabled"]
                tempLedger[self.returnIndex(tempLedger,data["fqdn"])]["hits"] = str(int(tempLedger[self.returnIndex(tempLedger,data["fqdn"])]["hits"]) + int(data["hits"]))
            
            # data is disabled, update ledger
            self.ledger = tempLedger

            # self.consolidate(data)
            # print (self.ledger)
            # print ("-----")

        return self.ledger
    
    @staticmethod
    def getTop(ledger):
        index = 0
        high = 0
        for i in range(len(ledger)):
            if (int(ledger[i]["hits"]) > high) and (ledger[i]["enabled"] == "True"):
                index = i
                high = int(ledger[i]["hits"])
        
        return ledger[index]
            

class Node:
    def __init__(self, name):
         self.name = name
         # initialize connetion creds to nsxmgr
         self.nsxmgr = str(config[name]['nsxmgr'])
         self.nsxuser = str(config[name]['nsxuser'])
         self.nsxpass = str(config[name]['nsxpass'])
         #self.strategy = config[name]['strategy']
    
    
    def getStrategy(self):
        return str(config[self.name]['strategy'])


    def getapi (self,uri):
        # print ("getAPI URI " + uri)
        r = requests.get('https://'+self.nsxmgr+ uri, verify=False,auth=(self.nsxuser, self.nsxpass))
        return r

    def putapi (self,uri,payload):
        headers = {'Content-Type': 'application/json'}
        # print ("putAPI URI " + uri + " PAYLOAD - "+ payload)
        r = requests.put('https://'+self.nsxmgr+ uri, verify=False, headers=headers,auth=(self.nsxuser, self.nsxpass), data=json.dumps(payload))
        return r
    

    def delapi(self,uri):
        # DELETE https://<policy-mgr>/policy/api/v1/infra/domains/vmc/security-policies/application-section-1/rules/ce-1
        # ACTUAL: /policy/api/v1/infra/domains/default/security-policies/block-url/rules/block-*FQDN*
        r = requests.delete('https://'+self.nsxmgr+ uri, verify=False, auth=(self.nsxuser, self.nsxpass))
        return r

    def delRule(self,fqdn):
        # DELETE https://<policy-mgr>/policy/api/v1/infra/domains/vmc/security-policies/application-section-1/rules/ce-1
        # ACTUAL: /policy/api/v1/infra/domains/default/security-policies/block-url/rules/block-*FQDN*
        # uri = "/policy/api/v1/infra/domains/default/security-policies/block-url/rules/block-" + Transaction.formatURL(fqdn)
        r = self.delapi (Transaction.getRuleURI(fqdn))
        return r
    
    def delCTX(self,fqdn):
        # DELETE https://<policy-mgr>/policy/api/v1/infra/domains/vmc/security-policies/application-section-1/rules/ce-1
        # ACTUAL: /policy/api/v1/infra/domains/default/security-policies/block-url/rules/block-*FQDN*
        # OR delapi(Transaction.getCTXURI(fqdn))
        # uri = "/policy/api/v1/infra/context-profiles/ctx-" + Transaction.formatURL(fqdn)
        r = self.delapi(Transaction.getCTXURI(fqdn))
        return r

    def dumpLocalLedger (self,localLedger):
        # print(config['DEFAULT']['transactionFolder'])
        #filename =  datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + ".json"
        #jsonfile = os.path.join(os.getcwd(), 'global/transactions/'+filename)
        jsonfile = str(config['DEFAULT']['rootFolder'])+self.name+"/db.json"
        #data_set = {"fqdn": url, "hits": hits, "payload": self.getPayload(url), "enabled": "True"}
        json_dump = json.dumps(localLedger)
        file1 = open(jsonfile, "w")
        file1.write(json_dump)
        return 0
    
    def getLocalLedger(self):
        localLedgerPath = config['DEFAULT']['rootFolder'] + self.name + "/db.json" 
        with open(localLedgerPath) as f:
            data = json.load(f)
        return data
    
    def createCTX (self,fqdn):
        #payload = {"resource_type":"PolicyContextProfile","display_name":"ctx-office365","description":"Blocked by reputation","attributes":[{"key":"DOMAIN_NAME","value": ["*.office365.com"],"datatype":"STRING"}]}
        code = self.putapi(Transaction.getCTXURI(fqdn), Transaction.getCTXPayload(fqdn))
        if code:
            return 0
        else:
            return 1
    
    def createRule (self,fqdn):
        # transaction = Transaction()
        # payload = {"resource_type":"PolicyContextProfile","display_name":"ctx-office365","description":"Blocked by reputation","attributes":[{"key":"DOMAIN_NAME","value": ["*.office365.com"],"datatype":"STRING"}]}
        
        code = self.putapi(Transaction.getRuleURI(fqdn), Transaction.getRulePayload(fqdn))
        if code:
            return 0
        else:
            return 1
    
    def getRuleExists(self,fqdn):
        #uri = "/policy/api/v1/infra/domains/default/security-policies/block-url/rules/block-" + Transaction.formatURL(fqdn)
        result = self.getapi(Transaction.getRuleURI(fqdn))
        # print ("STATUS CODE" + str(result.status_code))
        if result.status_code == 404:
            return False
        else:
            return True

        
    def getRuleHits(self,fqdn):
        # URI /policy/api/v1/infra/domains/default/security-policies/block-url/rules/Block_FQDN/statistics
        uri = Transaction.getRuleURI(fqdn) + "/statistics"
        # for TEST:
        # uri = "/policy/api/v1/infra/domains/default/security-policies/Block_URL/rules/Block_FQDN/statistics"
        #print ("URI for stats: " + uri)
        result = self.getapi(uri)
        # print ("STATUS CODE" + str(result.status_code))
        if result.status_code == 404:
            #print ("404 FOUND")
            return "0"
        #print ("WOW")
        statResults =  result.json()['results']
        for i in range(len(statResults)):
            # local enforcement to filter-out GLobal Manager eforcements
            if statResults[i]["enforcement_point"] == "/infra/sites/default/enforcement-points/default":
                return statResults[i]["statistics"] 

        return "0"
        # SPECIFIC:
        # results - LIST
        #   WHERE enforcement_point = /infra/sites/default/enforcement-points/default
        #   get STATISTICS: ["hit_count"]


    def printOutput (self,message,type="normal"):
        if type == "add":
            color = Fore.GREEN
        elif type == "remove":
            color = Fore.RED
        elif type == "core":
            color = Fore.CYAN
        else:
            color = Fore.WHITE
        
        # print ("[" + self.name + "]["+ datetime.datetime.now().strftime("%x %X") + "] " + message)
        print ("[" + Fore.YELLOW + self.name + Style.RESET_ALL + "]["+ datetime.datetime.now().strftime("%x %X") + "] " + color + message)
        print(Style.RESET_ALL)

 