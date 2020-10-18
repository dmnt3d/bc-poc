import requests
import sys

def main (argv):
    url = "https://" + argv[1] #"http://google.com"
    #url = "http://account.live.com"
    if len(argv) > 2:
        iteration = int(argv[2])
    else:
        iteration = 100

    while iteration > 0:
        iteration -= 1
        try:
            r = requests.get(url)
            print (r)
        except Exception as e:
            #e = sys.exc_info() [0]
            print (str(e))




if __name__ == "__main__":
    main(sys.argv)
