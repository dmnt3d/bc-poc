import json
import requests


# headers = {'Content-Type': 'application/json',
#            'Authorization': 'Bearer {0}'.format(api_token)}

def callapi (uri):
    r = requests.get('https://'+nsxmgr+ uri, verify=False,auth=(nsxuser, nsxpass))
    return r

def putapi (uri,headers,payload):
    r = requests.put('https://'+nsxmgr+ uri, verify=False, headers=headers,auth=(nsxuser, nsxpass), data=json.dumps(payload))
    return r

nsxmgr = "nsxdr.ldc.int"
nsxuser = "admin"
nsxpass = "VMware1!VMware1!"

domainID = callapi('/policy/api/v1/infra/domains/').json()['results'][0]["id"]

blockStatistics = callapi ('/policy/api/v1/infra/domains/'+domainID+'/security-policies/Block_URL/rules/Block_FQDN/statistics')

context = callapi ('/policy/api/v1/infra/context-profiles/attributes')

#print (context.json()['results'][0]["key"])

# context Profile attributes:
# /policy/api/v1/infra/context-profiles/attributes'
# DOMAIN_NAME
# TEST

# PUT https://<policy-mgr>/policy/api/v1/infra/context-profiles/testPolicyContextProfile
# {
#   "resource_type":"PolicyContextProfile",
#   "display_name":"BLOCK-office365.com",
#   "description":"Blocked by reputation",
#   "attributes":[
#    {
#         "key":"DOMAIN_NAME",
#         "value": [
#             "*.office365.com"
#           ],
#         "datatype":"STRING"
#     }
#   ]
# }

# online:
# name: ctx-fqdn
headers = {'Content-Type': 'application/json'}
payload = {"resource_type":"PolicyContextProfile","display_name":"ctx-office365","description":"Blocked by reputation","attributes":[{"key":"DOMAIN_NAME","value": ["*.office365.com"],"datatype":"STRING"}]}
code = putapi('/policy/api/v1/infra/context-profiles/ctx-office365',headers, payload)
print (code.content)

# =====
#  Get BLOCKURL ID
#foreach

#print(blockStatistics.text)


# get domain:
# GET /policy/api/v1/infra/domains/
# get security policy statistics:
# GET /policy/api/v1/infra/domains/<domain-id>/security-policies/<security-policy-id>/statistics
# get rule statistics:
# GET /policy/api/v1/infra/domains/<domain-id>/security-policies/<security-policy-id>/rules/<rule-id>/statistics


