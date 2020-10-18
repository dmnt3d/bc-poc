import requests
import sys
import os
import time
import datetime


if __name__ == "__main__":
    FQDN = os.environ['FQDN']
    if not os.environ['FQDN']:
        print ("FQDN not FOUND!")
        exit (1)
    
    while True:
        print ("FQDN: "+ FQDN,file = sys.stdout)
        print("Last Updated: "+ datetime.datetime.now().strftime("%x %X"), file = sys.stdout)
        try:
            r = requests.get(FQDN)
            print (str(r.status_code),file = sys.stdout)
        except Exception as e:
            #e = sys.exc_info() [0]
            print (str(e), file = sys.stdout)
        time.sleep(5)

