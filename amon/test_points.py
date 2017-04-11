import sys
import json
import requests

endpoints = {}
payloads = []

def process(url):
    endpoint = json.loads(url)
    base = endpoint.keys()[0]
    params = endpoint[base][1]
    if len(params) < 1:
        return

    if base not in endpoints:
        endpoints[base] = set()

    for i in params.keys():
        endpoints[base].add(i)

def exploit():
    for i in endpoints.keys():
        base = i
        params = endpoints[i]
        for pay in payloads:
            formatted = "&".join("%s=%s" % (p, pay) for p in params)
            url = "%s?%s" % (base, formatted)
            r = requests.get(url, verify=False)
            if r.status_code == 200 and "1d7eec3faf7e008f1934398b0ed8318c" in r.text:
                print url


def main():
    if len(sys.argv) < 3:
        print "Filenames expected!"

    data = file(sys.argv[1]).read().strip()
    payloads_str = file(sys.argv[2]).read().strip()
    global payloads
    payloads = payloads_str.split("\n")
    for i in data.split("\n"):
        process(i)

    exploit()

if __name__ == "__main__":
    main()
