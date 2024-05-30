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
        return "Temp too low"
    if higherTemp == 0:
        return "Temp too high"    
    slope = (higherTime - lowerTime) / (higherTemp - lowerTemp)
    newTime = lowerTime + (slope * (temp - lowerTemp))   
    return round(newTime, 2)

foo = getNewTime(31.3463, "Push 1")
print(foo)