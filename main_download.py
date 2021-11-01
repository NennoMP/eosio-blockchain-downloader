import requests, time, json, os.path, math

#API
EOSFLARE_API = "https://api.eosflare.io/v1/eosflare/get_actions"

#path
fileout = "/path/to/out/dir/"

#global values
max_per_minut = 100 # quota limit (EOSFLARE.API)
tot           = 0

#utility function for initializing the JSON
def createJSON (response):
    response.pop("head_block_num")
    response.pop("last_irreversible_block")
    response = json.dumps(response)
    with open (fileout, "w") as outf:
        outf.write(response)
    outf.close()
    return

#utility function for appending to the JSON
def appendJSON (response):
    response = response["actions"]
    with open(fileout, mode="r+") as outf:
        outf.seek(os.stat(fileout).st_size - 2)
        for x in range(len(response)):
            outf.write( ", {}".format(json.dumps(response[x])))
        outf.write("]}")
    outf.close()

#utility function for a single API request
def APIRequest (account_name, pos, offset):
    global tot
    data = {"account_name": account_name, "pos": int(pos), "offset": int(offset)}
    r = requests.post(EOSFLARE_API, json.dumps(data))
    status_code = r.status_code
    print("[", tot + 1, "]: ", status_code)

    while (status_code != 200):
        print(r.content)
        time.sleep(5)
        data = {"account_name": account_name, "pos": int(pos), "offset": int(offset)}
        r = requests.post(EOSFLARE_API, json.dumps(data))
        status_code = r.status_code
        print("[", tot + 1, "]: ", status_code)
    return r

#utility function for retrieving actions (100.000 per request)
def Get_Actions (account_name, start, n, ow):
    global offset, max_per_minut, tot
    offset, times, cont  = 1000, 0, 0
    pos = start
    
    while (times != n):
        print("TIME: ", times + 1)
        cont = 0
        # check limit rate
        while (cont != max_per_minut):
            r = APIRequest(account_name, pos, offset)

            r = r.json()
            if (pos == 1):
                createJSON(r)
            else:
                appendJSON(r)
                
            pos = pos + offset
            cont = cont + 1
            tot = tot + 1

        times = times + 1
        print("TOTAL: ", tot)
        if (times != n or ow != 0):
            print("SLEEPING")
            time.sleep(61)

    # if 'end' multiple of 100.000
    if (ow > 0):
        print("ULTIMA POSIZIONE: ", pos - 1)
        start = pos
        max_per_minut = math.floor(ow / 1000)
        Get_Actions(account_name, start, 1, 0)
    return

def main():
    account_name, start, end = input("Account, start, end: ").split()
    start = int(start)
    end   = int(end)

    global fileout
    fileout = os.path.join(fileout, (account_name + ".json"))

    n_times = math.floor((end - (start-1)) / 100000) # number of blocks of 100.000 actions (100 requests)
    ow      = (end - (start-1)) % 100000 # remainder of last block
    ow2     = (end - (start-1)) % 1000 # remainded of last single request
    Get_Actions(account_name, start, n_times, ow)

    #if 'end' multiple of 1.000
    if (ow2 > 0):
        start = (end - ow2) + 1
        r = APIRequest(account_name, start, ow2)
        r = r.json()
        try:
            appendJSON(r)
        except(FileNotFoundError):
            createJSON(r)



if __name__ == "__main__":
    main()
    print("|!|FINISHED|!|")