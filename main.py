# Module Imports
import utime as time
import _thread
from machine import Pin, SoftI2C
import stepper as Stepper
import ssd1306, onewire, ds18x20
# My Imports
import constants as CONST
from menus import menuText, menus
from tools import getNewTime, convertMs


# INIT OBJECTS

# ROTARY PINS
rotaryDtPin = Pin(CONST.ROTARY_DT, Pin.IN)
rotaryClkPin = Pin(CONST.ROTARY_CLK, Pin.IN)
rotarySwPin = Pin(CONST.ROTARY_SW, Pin.IN)
# OLED
i2c = SoftI2C(sda=Pin(CONST.DISPLAY_SDA), scl=Pin(CONST.DISPLAY_SLC))
display = ssd1306.SSD1306_I2C(CONST.OLED_H, CONST.OLED_V, i2c)
# TEMP PROBE
dsPin = Pin(CONST.TEMP_DAT)
dsSensor = ds18x20.DS18X20(onewire.OneWire(dsPin))
tempProbe = dsSensor.scan()[0]
# STEPPER
stepper = Stepper.create(Pin(CONST.STEPPER_IN1, Pin.OUT), Pin(CONST.STEPPER_IN2, Pin.OUT), Pin(CONST.STEPPER_IN3, Pin.OUT), Pin(CONST.STEPPER_IN4, Pin.OUT), delay = 1)

# Global Variables
lastStatus = (rotaryDtPin.value() <<1 | rotaryClkPin.value())
lastStatusTime = time.ticks_ms()
lastClick = 0
lastClickTime = time.ticks_ms()
menuVal = 0
subMenuVal = 0
actionMenuVal = 0
inMainMenu = True
inMenu = True
inSubMenu = False
inActionMenu = False
inAdjustment = False
waitingForConfirm = False
inDevelopment = False
devState = ""
confirmationText = ""
actionMenuValList = [0,0,1,0,0]
choices = []
choice = 0
lastTemp = 24.00


def handleSpin(pin):
    global lastStatus
    global lastStatusTime
    global menuVal
    global subMenuVal
    global actionMenuVal
    global inMainMenu
    global inSubMenu
    global inActionMenu
    global actionMenuValList
    global choice
    newStatus = (rotaryDtPin.value() << 1 | rotaryClkPin.value())
    if newStatus == lastStatus:
        return
    now = time.ticks_ms()
    if abs(time.ticks_diff(lastStatusTime, now)) <= CONST.SPIN_BOUNCE:
        return
    transition = (lastStatus << 2 ) | newStatus
    lastStatus = newStatus  
    if transition == 0b1000 or transition == 0b0111:
        lastStatusTime = now
        if waitingForConfirm:
            if choice < len(choices) - 1:
                choice = choice + 1 
                return
            choice = 0
            return                    
        if inMainMenu:
            if menuVal < len(menus[menuVal]) -1 :
                menuVal = menuVal + 1
                return
            menuVal = 0
            return
        if inSubMenu:
            if subMenuVal < (len(menus[menuVal][1]) - 1):
                subMenuVal = subMenuVal + 1
                return
            subMenuVal = 0
            return
        if inActionMenu and not inAdjustment:
            if actionMenuVal < (len(menus[menuVal][1][subMenuVal][1]) - 1):
                actionMenuVal = actionMenuVal + 1
                return
            actionMenuVal = 0
            return
        if inAdjustment:
            if actionMenuValList[actionMenuVal] < (len(menus[menuVal][1][subMenuVal][1][actionMenuVal][1]) - 1):
                actionMenuValList[actionMenuVal] = actionMenuValList[actionMenuVal] + 1
                return
            actionMenuValList[actionMenuVal] = 0
            return
    if transition == 0b1011 or transition == 0b0100:
        lastStatusTime = now
        if waitingForConfirm:
            if choice >= 1:
                choice = choice - 1 
                return
            choice = len(choices) -1
            return
        if inMainMenu:
            if menuVal >= 1:
                menuVal = menuVal - 1
                return
            menuVal = (len(menus[menuVal]) - 1)
            return
        if inSubMenu:
            if subMenuVal >= 1:
                subMenuVal = subMenuVal -1
                return
            subMenuVal = (len(menus[menuVal][1]) -1)
            return
        if inActionMenu and not inAdjustment:
            if actionMenuVal >= 1:
                actionMenuVal = actionMenuVal - 1
                return
            actionMenuVal = (len(menus[menuVal][1][subMenuVal][1]) - 1)
            return
        if inAdjustment:
            if actionMenuValList[actionMenuVal] >= 1:
                actionMenuValList[actionMenuVal] = actionMenuValList[actionMenuVal] - 1
                return
            actionMenuValList[actionMenuVal] = (len(menus[menuVal][1][subMenuVal][1][actionMenuVal][1]) - 1)
            return

        

def handleClick(pin):
    global lastClick
    global subMenuVal
    global inMenu
    global inMainMenu
    global inSubMenu
    global inActionMenu
    global inAdjustment
    global lastClickTime
    global actionMenuVal
    global actionMenuValList
    global waitingForConfirm
    global choice
    global choices
    newClick = rotarySwPin.value()
    if lastClick == newClick:
        return
    now = time.ticks_ms()
    if abs(time.ticks_diff(lastClickTime, now)) <= CONST.CLICK_BOUNCE:
        return
    transition = (lastClick << 2 ) | newClick
    if transition == 0b01:
        lastClickTime = now
        if waitingForConfirm:
            print(choices[choice])
        if waitingForConfirm and (choices[choice]) == "START":
            waitingForConfirm = False
            time.sleep(0.25)
            return
        if inMainMenu:
            subMenuVal = 0
            inMainMenu = False
            inSubMenu = True
            time.sleep(0.25)
            return
        if inSubMenu and menus[menuVal][1][subMenuVal][0][0] == "BACK":   
            inSubMenu = False
            inMainMenu = True
            time.sleep(0.25)
            return
        if inSubMenu:
            inSubMenu = False
            inActionMenu = True
            actionMenuVal = 0
            time.sleep(0.25)
            return
        if inActionMenu and menus[menuVal][1][subMenuVal][1][actionMenuVal][0][0] == "BACK":
            actionMenuValList = [0,0,1,0,0]
            inActionMenu = False
            inSubMenu = True
            return
        if inActionMenu and menus[menuVal][1][subMenuVal][1][actionMenuVal][0][0] == "START":
            typeString = ""
            for x in range(0, len(menus[menuVal][1][subMenuVal][1])):
                typeString = typeString + (str(menus[menuVal][1][subMenuVal][1][x][1][actionMenuValList[x]])) + " "
            typeString.strip()
            actionMenuValList = [0,0,1,0,0]
            inActionMenu = False
            inSubMenu = False
            inMenu = False
            developFilm(typeString)
            return
        if inActionMenu and not inAdjustment:
            inAdjustment = True
            time.sleep(0.25)
            return
        if inActionMenu and inAdjustment:
            inAdjustment = False
            time.sleep(0.25)
            return
        

    lastClick = newClick # I feel like this should be before the menu checks, but it works?
    # Okay, I'm pretty sure it works because the "unclick" also triggers the IRQ?
    time.sleep(0.15)

        
def drawMenuDisplay():
    display.fill(0)
    display.fill_rect(0,0,128,15,1)
    if not inSubMenu and not inActionMenu:
        display.text(menus[menuVal][0], 5, 4, 0)
        for x in range(0, len(menus[menuVal][1])):
            display.text(str(menus[menuVal][1][x][0][0]), 0, 20 + (x*10), 1)
    if inSubMenu and not inActionMenu:
        display.text(menus[menuVal][0], 5, 4, 0)
        for x in range(0, len(menus[menuVal][1])):
            if subMenuVal == x:
                display.text("> " + str(menus[menuVal][1][x][0][0]), 0, 19 + (x*9), 1)
            else:
                display.text(str(menus[menuVal][1][x][0][0]), 0, 19 + (x*9), 1)
    if inActionMenu:
        display.text(str(menus[menuVal][1][subMenuVal][0][0]), 5, 4, 0)
        for x in range(0, len(menus[menuVal][1][subMenuVal][1])):
            if actionMenuVal == x:
                if str(menus[menuVal][1][subMenuVal][1][x][0][0]) == "BACK":
                    display.text(">BACK", 0, 19 + (x*9), 1)
                elif str(menus[menuVal][1][subMenuVal][1][x][0][0]) == "START":
                    display.text(">START", 0, 19 + (x*9), 1)
                else:
                    endBracket = ""
                    if inAdjustment:
                        endBracket = "<"
                    display.text(">" +
                                str(menus[menuVal][1][subMenuVal][1][x][0][0]) +
                                "=" +
                                str(menus[menuVal][1][subMenuVal][1][x][1][actionMenuValList[x]]) +
                                endBracket,
                                0, 19 + (x*9), 1)
            else:
                if str(menus[menuVal][1][subMenuVal][1][x][0][0]) == "BACK":
                    display.text("BACK", 0, 19 + (x*9), 1)
                elif str(menus[menuVal][1][subMenuVal][1][x][0][0]) == "START":
                    display.text("START", 0, 19 + (x*9), 1)
                else:
                    display.text(str(menus[menuVal][1][subMenuVal][1][x][0][0]) +
                            "=" +
                            str(menus[menuVal][1][subMenuVal][1][x][1][actionMenuValList[x]]), 0, 19 + (x*9), 1)
                    
    display.show()

def drawDevelopDisplay(temp, theTime):
    global choices
    global choice
    choices = ["START", "CANCEL"]
    display.fill(0)
    display.fill_rect(0,0,128,15,1)
    display.text("TEMP - " + str(temp) + "C", 5, 4, 0)
    if waitingForConfirm:
        display.text(confirmationText,0, 19, 1)
        for x in range(len(choices)):
            if x == choice:
                display.text(">" + str(choices[x]), 0, 37 + (x*9), 1)
            else:
                display.text(str(choices[x]), 0, 37 + (x*9), 1)
    if devState == "SOAK" and not waitingForConfirm:
        display.text("PRESOAK", 0, 19, 1)
        display.text(str(theTime) + " REMAINING", 0, 37, 1)

    # if inSubMenu:
    #     for x in range(0, len(menuText[menuVal][1])):
    #         if subMenuVal == x:
    #             display.text("> " + menuText[menuVal][1][x], 3, 20 + (x*10), 1)
    #         else:
    #             display.text(menuText[menuVal][1][x], 3, 20 + (x*10), 1)            
    display.show()


def readTemp():
    global lastTemp
    try:
        dsSensor.convert_temp()
        tempC = dsSensor.read_temp(tempProbe)
        lastTemp = round(tempC, 2) 
        return lastTemp
    except Exception as e:
        print(e)
        return lastTemp


def moveStepper(angle, foo): # _thread is wierd and wants a tuple for args?
    print("moving stepper, angle=" + str(angle))
    stepper.angle(angle)

def developFilm(typeString):
    isC41 = "C-41" in typeString
    if isC41:
        developC41(typeString)
        print("done developing")
        return
    # while True:
    #     temp = readTemp()
    #     newTime = getNewTime(temp, str(typeString).strip())
    #     print(newTime)
    #     time.sleep(0.5)
    # currentTemp = readTemp()
    # _thread.start_new_thread(moveStepper, (720, "foo"))   

    
def developC41(typeString):
    global waitingForConfirm
    global inDevelopment
    global confirmationText
    global devState
    soakTime = 6 * 1000
    confirmationText = "START SOAK?"
    devState = "SOAK"
    waitingForConfirm = True
    inDevelopment = True
    soakStart = 0
    elapsed = 0
    devStart = 0
    devTime = 1000000000
    devTime = 0
    agitationCycle = 30 * 1000
    initialAgitation = 10 * 1000
    initialAgitationDone = False
    blixStart = 0
    
    while inDevelopment:
        temp = readTemp()
        theTime = convertMs(0)
        if temp >= 35:
            agitationCycle = 30 * 1000
            initialAgitation = 10 * 1000
        if temp < 35 and temp >= 29.5:
            agitationCycle = 60 * 1000
            initialAgitation = 30 * 1000
        if temp < 29.5:
            agitationCycle = 120 * 1000
            initialAgitation = 60 * 1000

        if devState == "SOAK" and waitingForConfirm:
            pass
        if devState == "SOAK" and not waitingForConfirm:
            if soakStart == 0:
                soakStart = time.ticks_ms()
            if elapsed >= soakTime:
                waitingForConfirm = True
                devState = "DEV"
                confirmationText = "START DEVELOPMENT?"
            elapsed = abs(time.ticks_diff(soakStart, time.ticks_ms()))
            timeLeft = (soakTime - elapsed)
            theTime = convertMs(timeLeft)
        if devState == "DEV" and not waitingForConfirm:
            devTime = getNewTime(temp, typeString)
            if devStart == 0:
                devStart = time.ticks_ms()
            if elapsed >= soakTime:
                waitingForConfirm = True
                devState = "DEV"
                confirmationText = "START DEVELOPMENT?"
            if not initialAgitationDone:
                initialAgitationDone = True
                _thread.start_new_thread(moveStepper, ((initialAgitation / 1000) * CONST.ANGLE_PER_SECOND, "foo"))
            elapsed = abs(time.ticks_diff(devStart, time.ticks_ms()))
            timeLeft = (devTime - elapsed)
            theTime = convertMs(timeLeft)
        

        drawDevelopDisplay(temp,theTime)
        if waitingForConfirm:
            time.sleep(0.15)
        else:
            time.sleep(0.5)
    # start = time.ticks_ms()
    # time.sleep(1)
    # end = time.ticks_ms()
    # print(abs(time.ticks_diff(start,end)))
    

# Initilize Rotary Input IRQs
rotaryDtPin.irq(handler=handleSpin, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
rotaryClkPin.irq(handler=handleSpin, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
rotarySwPin.irq(handler=handleClick, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)

# _thread.start_new_thread(moveStepper, (720, "foo"))
# moveStepper(360, "foo")
# moveStepper(-360, "foo")

developFilm("C-41 NORM 0")
# stepStart = time.ticks_ms()
# stepper.angle(87)
# stepEnd = time.ticks_ms()
# duration = abs(time.ticks_diff(stepStart, stepEnd))
# durationFormated = convertMs(duration)
# print(duration)
# print(durationFormated)

# for key, val in CONST.tempTimes["C-41 NORM 0"].items():
#     print(key, val)

while inMenu == True:
    drawMenuDisplay()
    temp = readTemp()
    # print(temp)
    time.sleep(0.1)






