
# Components
Consolidator : consolidates local vs global
---> Delete disabled
---> Adds stats
Transaction Adder : adds transaction





[ GLOBAL LEDGER ]
- contains FQDNs (both enabled/ disabled)
- TOTAL consolidated HITS
    |
    |
    |   displayLedger (GLOBAL LEDGER  + Consolidated HITS)
    |
    |
[ LOCAL LEDGER ]
- contains locally applied FQDNS (only enabled)
- Total-LOCAL hits
    |
    |   local-display : to display APPLIED FQDNS with LOCALHITS vs TOTAL HITS (from GlobalManager)
    |   consolidator
        - step 1:
            get GLOBAL Manager ledger
        - step 2:
            Get localLedger and go thru each list, IF marked as DISABLED in Global Manager, create API to delete RULE
        - step 3: (based on RULE - highest HITS etc)       
            Go thru GLOBAL MANAGER, anything not present (and enabled), add to localLedger variable, make hits = 0
        - step 4: go thru the HITs
            get API HITs and subtract to localLedger 
            If Hits >0, 
                - Add transaction for the FQDN with delta HITS
                - update localledger with HIT value from API
        - step 5: dump/ overwrite localledger

