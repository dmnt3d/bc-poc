from blockchain.lib import Ledger,Transaction,Node
import subprocess
import time
import datetime


node = Node("node01") 

r = node.getRuleHits("BLOCK-FQDN")
#print (r.type())
#print(r.json()['results'][0])
print (r["hit_count"])