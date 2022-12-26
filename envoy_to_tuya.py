import os
import sys
import requests
import json
import time
import tinytuya

# how find 'deviceID's and 'local keys' of tuya devices, youtube will help
# find tuya device addresses and that of the 'envoy' with 'advanced IP scanner' or whatever
# reserve their addresses in the router
# connect to tuya devices - pytuya Methodtinytuya (https://pypi.org/project/tinytuya)
# for how to load library and many more
# then acces them as below:
d105 = tinytuya.OutletDevice('device ID 1', 'local ip 1', 'local key 1')
d105.set_version(3.3)
d123 = tinytuya.OutletDevice('device ID 2', 'local ip 2', 'local key 2')
d123.set_version(3.3)
d124 = tinytuya.OutletDevice('device ID 3', 'local ip 3', 'local key 3')
d124.set_version(3.3)

# as tuya devices are initialising slowly, we shall allow a few cycles even if there is no answer
eval105 = False
eval123 = False
eval124 = False
# before going into an endless cycle, define address of envoy's data
target_url = f'http://xxx.tplinhdns.com:xxxxxx/production.json?details=1'
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
    print("IP..105:", eval105, "   IP..123:", eval123, "   IP..124:", eval124)

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

# power allocated to each radiator:
    r1 = 800
    r2 = 1300
    r3 = 6000

# calculate photovoltaic power available, regardless of radiators in use:
    if eval123 == False and eval124 == False and eval105 == False:
        disp_power = -i_now
    elif eval123 == True and eval124 == False and eval105 == False:
        disp_power = r1 - i_now
    elif eval123 == False and eval124 == True and eval105 == False:
        disp_power = r2 - i_now
    elif eval123 == True and eval124 == True and eval105 == False:
        disp_power = r1 + r2 - i_now
    elif eval123 == False and eval124 == False and eval105 == True:
        disp_power = r3 - i_now
    elif eval123 == True and eval124 == True and eval105 == True:
        disp_power = r1 + r3 - i_now
    elif eval123 == False and eval124 == True and eval105 == True:
        disp_power = r2 + r3 - i_now
    elif eval123 == True and eval124 == True and eval105 == True:
        disp_power = r1 + r2 + r3 - i_now
    print("power at our disposal:  ", disp_power, "W")
# 1 --- 0 0 0
    if disp_power < r1-200:
        if eval123 == True:
            d123.turn_off()
            time.sleep(5)
        if eval124 == True:
            d124.turn_off()
            time.sleep(5)
        if eval105 == True:
            d105.turn_off()
            time.sleep(5)
# 2 --- 1 0 0
    elif disp_power >= r1-200 and disp_power < r2-200:
        if eval123 == False:
            d123.turn_on()
            time.sleep(5)
        if eval124 == True:
            d124.turn_off()
            time.sleep(5)
        if eval105 == True:
            d105.turn_off()
            time.sleep(5)
# 3 --- 0 1 0
    elif disp_power >= r2-200 and disp_power < r1+r2-200:
        if eval123 == True:
            d123.turn_off()
            time.sleep(5)
        if eval124 == False:
            d124.turn_on()
            time.sleep(5)
        if eval105 == True:
            d105.turn_off()
            time.sleep(5)
# 4 --- 1 1 0
    elif disp_power >= r1+r2-200 and disp_power < r3-200:
        if eval123 == False:
            d123.turn_on()
            time.sleep(5)
        if eval124 == False:
            d124.turn_on()
            time.sleep(5)
        if eval105 == True:
            d105.turn_off()
            time.sleep(5)
# 5 --- 0 0 1
    elif disp_power >= r3-200 and disp_power < r1+r3-200:
        if eval123 == True:
            d123.turn_off()
            time.sleep(5)
        if eval124 == True:
            d124.turn_off()
            time.sleep(5)
        if eval105 == False:
            d105.turn_on()
            time.sleep(5)
# 6 --- 1 0 1
    elif disp_power >= r1+r3-200 and disp_power < r2+r3-200:
        if eval123 == False:
            d123.turn_on()
            time.sleep(5)
        if eval124 == True:
            d124.turn_off()
            time.sleep(5)
        if eval105 == False:
            d105.turn_on()
            time.sleep(5)
# 7 --- 0 1 1
    elif disp_power >= r2+r3-200 and disp_power < r1+r2+r3-200:
        if eval123 == True:
            d123.turn_off()
            time.sleep(5)
        if eval124 == False:
            d124.turn_on()
            time.sleep(5)
        if eval105 == False:
            d105.turn_on()
            time.sleep(5)
# 8 --- 1 1 1
    elif disp_power >= r1+r2+r3-200:
        if eval123 == False:
            d123.turn_on()
            time.sleep(5)
        if eval124 == False:
            d124.turn_on()
            time.sleep(5)
        if eval105 == False:
            d105.turn_on()
            time.sleep(5)
    print("--------------------------------------------------")
    # seconds in brackets till next cycle:
    time.sleep(30)
