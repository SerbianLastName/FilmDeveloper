# Module Imports
import utime as time
import _thread
from machine import Pin, SoftI2C
import stepper as Stepper
import ssd1306, onewire, ds18x20
# from gpiozero import Buzzer
# My Imports
import constants as CONST
from menus import menuText, menus
from tools import getNewTime, convertMs, incrementList


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
# stepper = Stepper.create(Pin(CONST.STEPPER_IN1, Pin.OUT), Pin(CONST.STEPPER_IN2, Pin.OUT), Pin(CONST.STEPPER_IN3, Pin.OUT), Pin(CONST.STEPPER_IN4, Pin.OUT), delay = 1)
stepper = Pin(22, Pin.OUT)
motor = Pin(CONST.MOTOR_PIN, Pin.OUT)
# LED/BUZZER
buzzer = Pin(CONST.BUZZER_PIN, Pin.OUT)
led = Pin(CONST.LED_PIN, Pin.OUT)


# Global Variables
lastStatus = (rotaryDtPin.value() <<1 | rotaryClkPin.value())
lastStatusTime = time.ticks_ms()
lastClick = 0
lastClickTime = time.ticks_ms()
# agitationStartTime = time.ticks_ms()
menuVal = 0
subMenuVal = 0
actionMenuVal = 0
menuState = "inMainMenu"
inMenu = True
inDevelopment = False
inAgitation = False
devState = ""
confirmationText = ""
actionMenuValList = [0,1,0,0,0]
choices = ["START", "CANCEL"]
choice = 0
lastTemp = 24.00
lastAgitation = 0


def handleSpin(pin):
    global lastStatus
    global lastStatusTime
    global menuVal
    global subMenuVal
    global actionMenuVal
    global actionMenuValList
    global choice
    global menuState
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
        if menuState == "waitingForConfirm":
            choice = incrementList(len(choices), choice, True)            
            return                    
        if menuState == "inMainMenu":
            menuVal = incrementList(len(menus[menuVal]), menuVal, True)
            return
        if menuState == "inSubMenu":
            subMenuVal = incrementList(len(menus[menuVal][1]), subMenuVal, True)
            return
        if menuState == "inActionMenu":
            actionMenuVal = incrementList(len(menus[menuVal][1][subMenuVal][1]), actionMenuVal, True)
            return
        if menuState == "inAdjustment":
            actionMenuValList[actionMenuVal] = incrementList(len(menus[menuVal][1][subMenuVal][1][actionMenuVal][1]), actionMenuValList[actionMenuVal], True)
            return
    if transition == 0b1011 or transition == 0b0100:
        lastStatusTime = now
        if menuState == "waitingForConfirm":
            choice = incrementList(len(choices), choice, False)            
            return                    
        if menuState == "inMainMenu":
            menuVal = incrementList(len(menus[menuVal]), menuVal, False)
            return
        if menuState == "inSubMenu":
            subMenuVal = incrementList(len(menus[menuVal][1]), subMenuVal, False)
            return
        if menuState == "inActionMenu":
            actionMenuVal = incrementList(len(menus[menuVal][1][subMenuVal][1]), actionMenuVal, False)
            return
        if menuState == "inAdjustment":
            actionMenuValList[actionMenuVal] = incrementList(len(menus[menuVal][1][subMenuVal][1][actionMenuVal][1]), actionMenuValList[actionMenuVal], False)
            return


def handleClick(pin):
    global lastClick
    global subMenuVal
    global menuState
    global lastClickTime
    global actionMenuVal
    global actionMenuValList
    newClick = rotarySwPin.value()
    if lastClick == newClick:
        return
    now = time.ticks_ms()
    if abs(time.ticks_diff(lastClickTime, now)) <= CONST.CLICK_BOUNCE:
        return
    transition = (lastClick << 2 ) | newClick
    if transition == 0b01:
        lastClickTime = now
        if menuState == "waitingForConfirm" and choices[choice] == "START":
            menuState = "confirmed"
            time.sleep(0.15)
            return
        if menuState == "inSubMenu" and menus[menuVal][1][subMenuVal][0][0] == "BACK":   
            menuState = "inMainMenu"
            time.sleep(0.15)
            return
        if menuState == "inMainMenu":
            subMenuVal = 0
            menuState = "inSubMenu"
            time.sleep(0.15)
            return
        
        if menuState == "inActionMenu" and menus[menuVal][1][subMenuVal][1][actionMenuVal][0][0] == "BACK":
            actionMenuValList = [0,0,1,0,0]
            menuState = "inSubMenu"
            return
        if menuState == "inActionMenu" and menus[menuVal][1][subMenuVal][1][actionMenuVal][0][0] == "START":
            typeString = ""
            rollsDeveloped = 0
            for x in range(0, len(menus[menuVal][1][subMenuVal][1])):
                if type(menus[menuVal][1][subMenuVal][1][x][1][actionMenuValList[x]]) == int:
                    rollsDeveloped = menus[menuVal][1][subMenuVal][1][x][1][actionMenuValList[x]]
                else:
                    typeString = typeString + (str(menus[menuVal][1][subMenuVal][1][x][1][actionMenuValList[x]])) + " "
            # For some reason, not starting the development in a new thread locks up the code, but running
            # developFilm() in the main loop with args, works fine?  WTF?
            _thread.start_new_thread(developFilm,(typeString.strip(), rollsDeveloped))
            return
        
        if menuState == "inSubMenu":
            menuState = "inActionMenu"
            actionMenuVal = 0
            time.sleep(0.15)
            return
        if menuState == "inActionMenu":
            menuState = "inAdjustment"
            time.sleep(0.15)
            return
        if menuState == "inAdjustment":
            menuState = "inActionMenu"
            time.sleep(0.15)
            return
        
        

    lastClick = newClick # I feel like this should be before the menu checks, but it works?
    # Okay, I'm pretty sure it works because the "unclick" also triggers the IRQ?
    time.sleep(0.15)


def drawMenuDisplay():
    display.fill(0)
    display.fill_rect(0,0,128,15,1)
    if menuState == "inMainMenu":
        display.text(menus[menuVal][0], 5, 4, 0)
        for x in range(0, len(menus[menuVal][1])):
            display.text(str(menus[menuVal][1][x][0][0]), 0, 20 + (x*10), 1)
    if menuState == "inSubMenu":
        display.text(menus[menuVal][0], 5, 4, 0)
        for x in range(0, len(menus[menuVal][1])):
            if subMenuVal == x:
                display.text("> " + str(menus[menuVal][1][x][0][0]), 0, 19 + (x*9), 1)
            else:
                display.text(str(menus[menuVal][1][x][0][0]), 0, 19 + (x*9), 1)
    if menuState == "inActionMenu":
        display.text(str(menus[menuVal][1][subMenuVal][0][0]), 5, 4, 0)
        for x in range(0, len(menus[menuVal][1][subMenuVal][1])):
            if actionMenuVal == x:
                if str(menus[menuVal][1][subMenuVal][1][x][0][0]) == "BACK":
                    display.text(">BACK", 0, 19 + (x*9), 1)
                if str(menus[menuVal][1][subMenuVal][1][x][0][0]) == "START":
                    display.text(">START", 0, 19 + (x*9), 1)
                else:
                    display.text(">" +
                                str(menus[menuVal][1][subMenuVal][1][x][0][0]) +
                                "=" +
                                str(menus[menuVal][1][subMenuVal][1][x][1][actionMenuValList[x]]),
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
    if menuState == "inAdjustment":
        display.text(str(menus[menuVal][1][subMenuVal][0][0]), 5, 4, 0)
        for x in range(0, len(menus[menuVal][1][subMenuVal][1])):
            if actionMenuVal == x:
                display.text(">" +
                            str(menus[menuVal][1][subMenuVal][1][x][0][0]) +
                            "=" +
                            str(menus[menuVal][1][subMenuVal][1][x][1][actionMenuValList[x]]) +
                            "<",
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
    display.fill(0)
    display.fill_rect(0,0,128,15,1)
    display.text("TEMP - " + str(temp) + "C", 5, 4, 0)
    if menuState == "waitingForConfirm":
        display.text(confirmationText,0, 19, 1)
        for x in range(len(choices)):
            if x == choice:
                display.text(">" + str(choices[x]), 0, 37 + (x*9), 1)
            else:
                display.text(str(choices[x]), 0, 37 + (x*9), 1)
    if menuState == "confirmed":
        display.text(str(devState), 0, 19, 1)
        display.text(str(theTime) + " REMAINING", 0, 37, 1)
        if inAgitation:
            display.text("AGITATING", 0, 46, 1)


    display.show()


def readTemp():
    global lastTemp
    # The temp probe will occasionally throw an error, so we do this in a try loop.
    try:
        dsSensor.convert_temp()
        tempC = dsSensor.read_temp(tempProbe)
        newTemp = round(tempC, 2)
        return newTemp
    except Exception as e:
        return lastTemp

def lightsAndBuzzer():
    x = 100
    beeps = 5
    while x > 0:
        buzzer.value(1)
        led.value(1)
        time.sleep(0.001)
        buzzer.value(0)
        led.value(0)
        time.sleep(0.001)
        x = x -1
        if x == 0:
            if beeps > 0:
                x = 100
                beeps = beeps -1
                time.sleep(0.25)

def developFilm(typeString, rollsDeveloped):
    global menuState
    isC41 = "C-41" in typeString
    if isC41:
        menuState = "waitingForConfirm"
        developC41(typeString, rollsDeveloped)
        return

   
def developC41(typeString, rollsDeveloped):
    global waitingForConfirm
    global inDevelopment
    global confirmationText
    global devState
    global inMenu
    global menuState
    global stepper
    lastAgitation = 0
    # agitationStartTime = 0
    inMenu = False
    confirmationText = "START SOAK?"
    devState = "SOAK"
    inDevelopment = True
    soakStart = 0
    elapsed = 0
    devStart = 0
    devTime = 0
    agitationCycle = 30 * 1000
    initialAgitation = 10 * 1000
    agitationTime = 10 * 1000
    initialAgitationDone = False
    # doingInitialAgitation = False
    blixStart = 0
    washStart = 0
    rinseStart = 0
    # rinseAgitation = 15 * 1000
    # agitationStartTime = 0
    # currentAgitationTime = 0
    lastAgitation = 0
    # spinning = False
    # inAgitation = False
    
    
    
    
    
    def checkAgitation():
        now = time.ticks_ms()
        global inAgitation
        nonlocal lastAgitation
        nonlocal initialAgitationDone
        nonlocal agitationTime
        nonlocal timeLeft
        def agitate():
            nonlocal lastAgitation
            global inAgitation
            motor.value(1)
            lastAgitation = now
            inAgitation = True        
        if not inAgitation:            
            if not initialAgitationDone:
                agitationTime = initialAgitation
                agitate()
            if abs(time.ticks_diff(lastAgitation, now)) >= agitationCycle:                
                if (timeLeft * 0.85) >= agitationTime and initialAgitationDone:
                    agitate()
                if (timeLeft * 0.85) < agitationTime and initialAgitationDone:
                    agitationTime = (timeLeft * 0.85)
                    agitate()
        if inAgitation:
            if abs(time.ticks_diff(lastAgitation, now)) >= agitationTime:
                motor.value(0)
                inAgitation = False
                initialAgitationDone = True
                

    while inDevelopment:
        temp = readTemp()
        theTime = convertMs(0)
        now = time.ticks_ms()        
        # This is a place for R&D, need to think of an elegant way to make a curve for this.
        if temp >= 35:
            agitationCycle = 30 * 1000
            initialAgitation = 10 * 1000
        if temp < 35 and temp >= 29.5:
            agitationCycle = 60 * 1000
            initialAgitation = 30 * 1000
        if temp < 29.5:
            agitationCycle = 120 * 1000
            initialAgitation = 60 * 1000
        
        if devState == "SOAK" and menuState == "confirmed":
            if soakStart == 0:
                print("SOAK START", now)
                soakStart = now
            
            elapsed = abs(time.ticks_diff(soakStart, now))
            timeLeft = (CONST.C41_SOAK_TIME - elapsed)
            theTime = convertMs(timeLeft)
            print(elapsed)
            if elapsed >= CONST.C41_SOAK_TIME:
                menuState = "waitingForConfirm"
                devState = "DEVELOP"
                confirmationText = "START DEV?"
                lightsAndBuzzer()
            
        if devState == "DEVELOP" and menuState == "confirmed":
            
            if devStart == 0:
                devStart = now

            newTime = getNewTime(temp, typeString) * (1 + ((rollsDeveloped * 2) / 100))

            if devTime == 0:
                devTime = newTime

            if newTime < 2.75 * 60 * 1000:
                devTime = 2.75 * 60 * 1000
            # elif abs(devTime - newTime) > 10 * 60 * 1000:
            #     devTime = (newTime + devTime + devTime) / 3
            else:
                devTime = newTime
            
            elapsed = abs(time.ticks_diff(devStart, now))
            timeLeft = (devTime - elapsed)
            theTime = convertMs(timeLeft)

            if elapsed >= devTime and not inAgitation:
                menuState = "waitingForConfirm"
                devState = "BLIX"
                confirmationText = "START BLIX?"
                lightsAndBuzzer()
            
            checkAgitation()

        if devState == "BLIX" and menuState == "confirmed":
            if blixStart == 0:
                blixStart = now
                initialAgitationDone = False
            
            elapsed = abs(time.ticks_diff(blixStart, now))
            timeLeft = (CONST.C41_BLIX_TIME - elapsed)
            theTime = convertMs(timeLeft)
            
            if elapsed >= CONST.C41_BLIX_TIME and not inAgitation:
                menuState = "waitingForConfirm"
                devState = "WASH"
                confirmationText = "START WASH?"
                lightsAndBuzzer()
            
            checkAgitation()
        
        if devState == "WASH" and menuState == "confirmed":
            if washStart == 0:
                washStart = now
                
            elapsed = abs(time.ticks_diff(washStart, now))
            timeLeft = (CONST.C41_WASH_TIME - elapsed)
            theTime = convertMs(timeLeft)
            
            if elapsed >= CONST.C41_WASH_TIME and not inAgitation:
                menuState = "waitingForConfirm"
                devState = "RINSE"
                confirmationText = "START RINSE?"
                lightsAndBuzzer()

        
        if devState == "RINSE" and menuState == "confirmed":
            if rinseStart == 0:
                rinseStart = now
                initialAgitationDone = False
                
            elapsed = abs(time.ticks_diff(rinseStart, now))
            timeLeft = (CONST.C41_RINSE_TIME - elapsed)
            theTime = convertMs(timeLeft)
            agitationCycle = (CONST.C41_RINSE_TIME * 2)
            
            if elapsed >= CONST.C41_RINSE_TIME and not inAgitation:
                menuState = "waitingForConfirm"
                devState = "DONE"
                confirmationText = "GO AGAIN?"
                lightsAndBuzzer()
                
        checkAgitation()

        drawDevelopDisplay(temp,theTime)

        time.sleep(0.25)
     

# Initilize Rotary Input IRQs
rotaryDtPin.irq(handler=handleSpin, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
rotaryClkPin.irq(handler=handleSpin, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
rotarySwPin.irq(handler=handleClick, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)

developFilm("C-41 NORM 0", 0)
# lightsAndBuzzer()

# moveStepper(-360, "foo")

while inMenu == True:
    drawMenuDisplay()
    time.sleep(0.15)






