import requests, time, json, os.path, math

# API
EOSFLARE_API = "https://api.eosflare.io/v1/eosflare/get_actions"

# PATH
fileout = "/path/to/out/dir/"

# GLOBALS
max_per_minut = 100 # quota limit (EOSFLARE.API)
tot           = 0   

'''
    Utility function for initializing the JSON
'''
def createJSON(response):
    
    # Remove useless fields
    response.pop("head_block_num")
    response.pop("last_irreversible_block")
    
    # Write out
    response = json.dumps(response)
    with open (fileout, "w") as outf:
        outf.write(response)
        
    return


'''
    Utility function for appending to the JSON
'''
def appendJSON(response):
    
    # Get the actions list
    response = response["actions"]
    
    # Append at the end
    with open(fileout, mode="r+") as outf:
        outf.seek(os.stat(fileout).st_size - 2)
        for x in range(len(response)):
            outf.write(", {}".format(json.dumps(response[x])))
        outf.write("]}") 
        
    return

    
'''
    Utility function for a single API request 
'''
def APIRequest(account_name, pos, offset):
    global tot
    
    
    # Send POST request
    data = {"account_name": account_name, "pos": int(pos), "offset": int(offset)}
    r = requests.post(EOSFLARE_API, json.dumps(data))
    status_code = r.status_code
    print("[", tot + 1, "]: ", status_code)

    # Try again if response is not 200 (Success)
    while (status_code != 200):
        time.sleep(5)   # wait 5 seconds, avoids rejection for too fast requesting
        data = {"account_name": account_name, "pos": int(pos), "offset": int(offset)}
        r = requests.post(EOSFLARE_API, json.dumps(data))
        status_code = r.status_code
        print("[", tot + 1, "]: ", status_code)
        
    return r


''' 
    Utility function for retrieving actions (100.000 per request) 
'''
def Get_Actions(account_name, start, n, ow):
    global offset, max_per_minut, tot
    offset, times, cont  = 1000, 0, 0
    pos = start
    
    
    # Send n POST requests
    while (times != n):
        cont = 0
        print(f"TIME: {times + 1}")
        
        # Check limit rate
        while (cont != max_per_minut):
            r = APIRequest(account_name, pos, offset)
            r = r.json()
            
            if (pos == 1):      # At the beginning: Create file
                createJSON(r)
            else:               # Not at the beginning: Append to file
                appendJSON(r)
            
            # Update position, offset and counters
            pos = pos + offset
            cont = cont + 1
            tot = tot + 1

 
        times = times + 1
        print("TOTAL: ", tot)
        if (times != n or ow != 0):
            print("SLEEPING")
            time.sleep(61)      # Wait 61 seconds, for the limit rate per minut

    # If 'end' multiple of 100.000
    if (ow > 0):
        print(f"LAST POSITION: {pos - 1}")
        start = pos
        max_per_minut = math.floor(ow / 1000)
        Get_Actions(account_name, start, 1, 0)
        
    return


def main():
    global fileout
    
    # account_name, starting position, ending position
    account_name, start, end = input("Account, start, end: ").split()
    start = int(start)
    end   = int(end)

    # file
    fileout = os.path.join(fileout, (account_name + ".json"))
    
    n_times = math.floor((end - (start-1)) / 100000)    # number of blocks of 100.000 actions (100 requests)
    ow      = (end - (start-1)) % 100000                # remainder of last block
    ow2     = (end - (start-1)) % 1000                  # remainded of last single request
    
    # Get the actions
    Get_Actions(account_name, start, n_times, ow)

    # 'end' multiple of 1.000
    if (ow2 > 0):
        start = (end - ow2) + 1
        r = APIRequest(account_name, start, ow2)
        r = r.json()
        try:
            appendJSON(r)
        except FileNotFoundError:
            createJSON(r)

            
if __name__ == "__main__":
    main()
    print("|!|FINISHED|!|")
