import json
import requests


# headers = {'Content-Type': 'application/json',
#            'Authorization': 'Bearer {0}'.format(api_token)}

def callapi (uri):
    r = requests.get('https://'+nsxmgr+ uri, verify=False,auth=(nsxuser, nsxpass))
    return r

nsxmgr = "nsxdr.ldc.int"
nsxuser = "admin"
nsxpass = "VMware1!VMware1!"

domainID = callapi('/policy/api/v1/infra/domains/').json()['results'][0]["id"]

blockStatistics = callapi ('/policy/api/v1/infra/domains/'+domainID+'/security-policies/Block_URL/rules/Block_FQDN/statistics')
#  Get BLOCKURL ID
#foreach

print(blockStatistics.text)


# get domain:
# GET /policy/api/v1/infra/domains/
# get security policy statistics:
# GET /policy/api/v1/infra/domains/<domain-id>/security-policies/<security-policy-id>/statistics
# get rule statistics:
# GET /policy/api/v1/infra/domains/<domain-id>/security-policies/<security-policy-id>/rules/<rule-id>/statistics
