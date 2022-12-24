import sys
import requests
import json
import time
import tinytuya

# how to find 'deviceID's and 'local keys' of tuya devices >> youtube has answers
# if devices are deleted and reinstalled on 'smart life' app, their local key chages, device ID not.
# find tuya device addresses and that of the 'envoy' with 'advanced IP scanner' or whatever
# reserve their addresses in the router
# connect to tuya devices - pytuya Method tinytuya (https://pypi.org/project/tinytuya)
#                                                  for how to load library and many more
# tinytuya wizzard will display correct version (usually 3.3)
# then acces them as below (I have 3 devices at respective fixed addresses):
d105 = tinytuya.OutletDevice('{device ID 1}', '192.168.1.105', '{local key 1}')
d105.set_version(3.3)
d123 = tinytuya.OutletDevice('{device ID 2}', '192.168.1.123', '{local key 2}')
d123.set_version(3.3)
d124 = tinytuya.OutletDevice('{device ID 3}', '192.168.1.124', '{local key 3}')
d124.set_version(3.3)

# as tuya devices are initialising slowly, we shall allow a few cycles even if there is no answer
# it could be this small program must be restarted till it can read all three devices, after first
# correct read, usually runs further without hikkups
eval105 = False
eval123 = False
eval124 = False
# before going into an endless cycle, define address of envoy's data
target_url = f'http://titch.tplinkdns.com:65333/production.json?details=1'

# starting the endless cycle:
while True:
    # Get Status of tuya devices
    data105 = d105.status()
    data123 = d123.status() 
    data124 = d124.status()
    # as tuya devices have the unpleasant behaviour to not answer immediately 
    # after a command, we'll ignore the wrong answer until we get a proper one
    try:
        data105_1 = data105["dps"]
    except KeyError as err:
        print('jumping over IP 105:')
      #  response = os.popen(f"ping -c 4 192.168.1.105").read()
      #  print(response)
      #  time.sleep(3)
    try:
        data123_1 = data123["dps"]
    except KeyError as err:
        print('jump over IP 123')
    try:
        data124_1 = data124["dps"]
    except KeyError as err:
        print('jump over IP 124')
    eval105 = data105_1["1"]
    eval123 = data123_1["1"]
    eval124 = data124_1["1"]
    # just to see on screen on/off of respective switches
    print("IP..105:", eval105,"   IP..123:", eval123,"   IP..124:", eval124)

    # loading production and net import/export (watts) data in realtime from 
    # 'envoy's local webpage (- minus) value at 'consumption' means net export
    result = requests.get(target_url)
    json_status = json.loads(result.text)
    res_1 = json_status["production"]
    res_2 = json_status["consumption"]
    res_11 = res_1[1]
    res_21 = res_2[1]
    i_now = res_21["wNow"]
    p_now = res_11["wNow"]
    print("photovoltaic production:", p_now, "W")
    print("net (+)import/(-)export:", i_now, "W")

    # from this point downwards is specific to my home (numbers are watts):
    # the time.sleep(x) command is because at my devices commands too close to 
    # one another may temporarily interrupt connection with one or two off the devices
   

    if p_now < 1000:
        if eval123 == True:
            d123.turn_off()
            time.sleep(5)
        if eval105 == True:
            d105.turn_off()
            time.sleep(5)
        if eval124 == True:
            d124.turn_off()
            time.sleep(5)
    if p_now > 1000 and p_now < 2100 and i_now < -200:
        if eval123 == False:
            d123.turn_on()
            time.sleep(5)
        if eval105 == True:
            d105.turn_off()
            time.sleep(5)
        if eval124 == True:
            d124.turn_off()
            time.sleep(5)
    if p_now > 2100 and p_now < 6000 and i_now < -200:
        if eval123 == False:
            d123.turn_on()
            time.sleep(5)
        if eval124 == False:
            d124.turn_on()
            time.sleep(5)
        if eval105 == True:
            d105.turn_off()
            time.sleep(5)
    if p_now > 6000 and p_now < 7000 and i_now < -200:
        if eval123 == True:
            d123.turn_off()
            time.sleep(5)
        if eval124 == True:
            d124.turn_off()
            time.sleep(5)
        if eval105 == False:
            d105.turn_on()
            time.sleep(5)
    if p_now > 7000 and p_now < 8100 and i_now < -200:
        if eval123 == False:
            d123.turn_on()
            time.sleep(5)
        if eval124 == True:
            d124.turn_off()
            time.sleep(5)
        if eval105 == False:
            d105.turn_on()
            time.sleep(5)
    if p_now > 8100 and i_now < -200:
        if eval123 == False:
            d123.turn_on()
            time.sleep(5)
        if eval124 == False:
            d124.turn_on()
            time.sleep(5)
        if eval105 == False:
            d105.turn_on()
            time.sleep(5)


    print("-------------------------------------------------")
    # this is the frequency I decided for realtime readings
    # (seconds in brackets till next cycle):
    time.sleep(20)


