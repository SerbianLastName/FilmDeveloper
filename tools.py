import constants as CONST


def getNewTime(temp, type):
    lowerTemp = 0
    lowerTime = 0
    higherTemp = 100
    higherTime = 0
    if type == "custom":
        pass
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
        for devTemp, devTime in CONST.tempTimes[type].items():
            if devTemp > lowerTemp:
                if devTemp < higherTemp:
                    higherTemp = devTemp
                    higherTime = devTime
    if higherTemp == 0:
        higherTemp = lowerTemp
        higherTime = lowerTime
        lowerTemp = 0
        for devTemp, devTime in CONST.tempTimes[type].items():
            if devTemp < higherTemp:
                if devTemp > lowerTemp:
                    lowerTemp = devTemp
                    lowerTime = devTime
    slope = (higherTime - lowerTime) / (higherTemp - lowerTemp)
    newTime = lowerTime + (slope * (temp - lowerTemp))   
    return round(newTime, 2)