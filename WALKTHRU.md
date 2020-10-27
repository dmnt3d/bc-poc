# DEMO

## Objective

- Show GlobalLedger getting updated

- Show FW getting updated

1. Walk thru the directory. Show strategy of each node

- node01 is ALL (means apply everything enabled). TEST VM: - 172.16.10.145

- node02 is TOP (means apply TOP only): TEST VM: - 192.168.10.136

2. Show current Global Ledger. 

 python displayGlobalLedger.py 

3. Show testVM at PROD getting blocked when accessing login.live.com
ssh root@192.168.10.136

4. Show stats in nsx.ldc.int of HITS

5. Run node02 client. Expectation:  HITs will be pulled and updated to GLOBAL LEDGER
python client.py node02

6. Artificially add new FQDN with HITS. simulate added HITS from external
ADD:
python op.py add www.evernote.com

ADD hits artificially:
python op.py add www.evernote.com 21000

7. Notice top hits is now ogone. Replaced/ update firewall. CLIENT can now access the login.live.com

8. Open Node01 - with strategy of ALL. all in the global ledger

9. SHOW in nsx-t. run consolidator. apply login.live and evernote.

10. Add new URLs and check fw
python op.py add forms.office.com

11. Disable evernote.com and check fw
python op.py disable www.evernote.com

--
CONCLUSION:

- Showcase how easy to read stats from NSX-T FW. 

- Apply appropriate action (in the form a DFW rule) that is based on CONDITIONS of the Global Ledger.

