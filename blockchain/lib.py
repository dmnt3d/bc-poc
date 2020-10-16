import json
import datetime
import os
import configparser
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

config = configparser.ConfigParser()
config.read('config.ini')
#folder  =  config['DEFAULT']['transactionFolder']
#config['DEFAULT']['transactionFolder']

class Transaction:
    # def __init__(self, url, hits, enabled):
    #     self.url = url
    #     self.hits = hits
    #     self.enabled = enabled
    
    def add(self,url, hits):
        # print(config['DEFAULT']['transactionFolder'])
        filename =  datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + ".json"
        #jsonfile = os.path.join(os.getcwd(), 'global/transactions/'+filename)
        jsonfile = str(config['DEFAULT']['transactionFolder'])+filename
        data_set = {"fqdn": url, "hits": hits, "payload": self.getPayload(url), "enabled": "True"}
        json_dump = json.dumps(data_set)

        file1 = open(jsonfile, "w")
        file1.write(json_dump)
        return 0
    
    def enabled(self,url,enabled):
        filename =  datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + ".json"
        #jsonfile = os.path.join(os.getcwd(), 'global/transactions/'+filename)
        jsonfile = config['DEFAULT']['transactionFolder']+filename

        data_set = {"fqdn": url, "hits": "0", "enabled": str(enabled)}
        json_dump = json.dumps(data_set)

        file1 = open(jsonfile, "w")
        file1.write(json_dump)

        return 0
    
    def getPayload(self,url):
        payload = {
            "description": "BLOCK "+ url,
            "display_name": "block-"+ self.formatURL(url),
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
            "/infra/context-profiles/ctx-"+ self.formatURL(url)
            ],
            "action": "DROP"
        }
        return payload

    @staticmethod
    def formatURL(url):
        formatted = url
        if url[0] == '*':
            formatted = url[2:]
        return formatted.replace('.','-')
    
    # create context/ rule specific methods
    @staticmethod
    def getCTXPayload(url):
        payload = {
            "resource_type":"PolicyContextProfile",
            "display_name":"ctx-" + Transaction.formatURL(url),
            "description":"WEB REPUTATION Context",
            "attributes":[
                {"key":"DOMAIN_NAME",
                "value": [url],
                "datatype":"STRING"}
                ]
        }
        return payload
    
    @staticmethod
    def getCTXURI(url):
        return "/policy/api/v1/infra/context-profiles/ctx-" + Transaction.formatURL(url)
    
    @staticmethod
    def getRuleURI(url):
        return "/policy/api/v1/infra/domains/default/security-policies/block-url/rules/block-" + Transaction.formatURL(url)
    


class Ledger:
    
    def __init__ (self):
        self.ledger = []
        
    def get(self):
        self.ledger = []
        transactionPath = config['DEFAULT']['transactionFolder'] # os.path.join(os.getcwd(), 'global/transactions/')
        for entry in os.listdir(transactionPath):
            with open(transactionPath + entry) as f:
                data = json.load(f)
            #print (data)           
            self.consolidate(data)

        return self.ledger

    def consolidate (self,data):
        # iterate thru current ledger
        # check if ledger is Empty
        if not self.ledger:
            self.ledger.append(data)
        else:
            # check FQDN is present. and add the hits
            for i in range(len(self.ledger)):
                if self.ledger[i]["fqdn"] == data['fqdn']:
                    self.ledger[i]["hits"] = str(int(data['hits']) + int (self.ledger[i]["hits"]))
                    # update latest enabled status
                    self.ledger[i]["enabled"] = data["enabled"]
                    #print(str(data["enabled"]))
            

class Node:
    def __init__(self, name):
         self.name = name
         # initialize connetion creds to nsxmgr
         self.nsxmgr = str(config[name]['nsxmgr'])
         self.nsxuser = str(config[name]['nsxuser'])
         self.nsxpass = str(config[name]['nsxpass'])


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
        print ("del API URI " + uri)
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
    
    def createRule (self,fqdn,payload):
        # transaction = Transaction()
        # payload = {"resource_type":"PolicyContextProfile","display_name":"ctx-office365","description":"Blocked by reputation","attributes":[{"key":"DOMAIN_NAME","value": ["*.office365.com"],"datatype":"STRING"}]}
        
        code = self.putapi(Transaction.getRuleURI(fqdn), payload)
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


        # GET HIT ONLY
  #  def getActualHits(self, fqdn):





# a = Transaction()
# b = Ledger()

# # a.add('google.com','2')
# # print(b.get()[0])
# # a.add('google.com','12')
# # print(b.get()[0])
# #a.enabled('google.com',False)
# print(b.get()[0])
# a.add('google.com','12')
# print(b.get()[0])
# a.enabled('google.com',True)
# print(b.get()[0])

# # b = Ledger().get()

# # print(b[0]["hits"])
# #a.save()