
BASE COMMAND:
> curl -LI https://login.live.com -o /dev/null -w '%{http_code}\n' -s

TAIL kubectl logs
kubectl logs --follow <pod>


# Crete std-out
docker build -t gubi:latest .



TEST VM:
DR:
testVM1-DR
- 172.16.10.145

PROD:
testVM2-PROD
- 192.168.10.136


DOCKER pull:
docker pull harbor.letsdocloud.com/gubi/queryurl:latest

Initiate docker run
docker run -d -e FQDN=http://login.live.com harbor.letsdocloud.com/gubi/queryurl:latest