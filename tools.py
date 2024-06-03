import constants as CONST

def getNewTime(temp, type):
    lowerTemp = 0
    lowerTime = 0
    higherTemp = 100
    higherTime = 0
    if type == "custom":
        return 00.00
    for devTemp, devTime in CONST.tempTimes[type].items():
        if devTemp == temp:
            return devTime
        if devTemp < temp:
            if devTemp > lowerTemp:
                lowerTemp = devTemp
                lowerTime = devTime
        if devTemp > temp:
            if devTemp < higherTemp:
                higherTemp = devTemp
                higherTime = devTime
    if lowerTemp == 0:
        lowerTemp = higherTemp
        lowerTime = higherTime
        higherTemp = 100
        for devTemp, devTime in CONST.tempTimes[str(type).strip()].items():
            if devTemp > lowerTemp:
                if devTemp < higherTemp:
                    higherTemp = devTemp
                    higherTime = devTime
    if higherTemp == 0:
        higherTemp = lowerTemp
        higherTime = lowerTime
        lowerTemp = 0
        for devTemp, devTime in CONST.tempTimes[str(type).strip()].items():
            if devTemp < higherTemp:
                if devTemp > lowerTemp:
                    lowerTemp = devTemp
                    lowerTime = devTime
    # I don't think I need to worry about dividing by 0 here, but whatever
    if (higherTime - lowerTime) == (higherTemp - lowerTemp):
        higherTime = higherTime + 0.01    
    slope = (higherTime - lowerTime) / (higherTemp - lowerTemp) 
    newTime = lowerTime + (slope * (temp - lowerTemp))   
    return round(newTime, 2)

def halfStepPushPull(steps):
    pass
