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
    # I don't think I need to worry about dividing by 0 here, but I'd rather be safe
    if (higherTime - lowerTime) == 0:
        higherTime = higherTime + 1
    if (higherTemp - lowerTemp) == 0:
        higherTemp = higherTemp + 1
    slope = (higherTime - lowerTime) / (higherTemp - lowerTemp) 
    newTime = lowerTime + (slope * (temp - lowerTemp))   
    return round(newTime * 60 * 1000, 2)

def halfStepPushPull(steps):
    pass

def convertMs(ms):
    totalSeconds = ms // 1000
    minutes = totalSeconds // 60
    seconds = totalSeconds % 60
    formattedTime = "{:02}:{:02}".format(minutes, seconds)
    return formattedTime

def incrimentList(listLen, currentVal, up):
    if up:
        if currentVal < listLen -1:
            return currentVal + 1
        return 0
    if not up:
        if currentVal >= 1:
            return currentVal - 1
        return listLen -1