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
from tools import getNewTime, convertMs, incrimentList


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
# LED/BUZZER
buzzer = Pin(CONST.BUZZER_PIN, Pin.OUT)
led = Pin(CONST.LED_PIN, Pin.OUT)


# Global Variables
lastStatus = (rotaryDtPin.value() <<1 | rotaryClkPin.value())
lastStatusTime = time.ticks_ms()
lastClick = 0
lastClickTime = time.ticks_ms()
menuVal = 0
subMenuVal = 0
actionMenuVal = 0
menuState = "inMainMenu"
inMenu = True
inDevelopment = False
devState = ""
confirmationText = ""
actionMenuValList = [0,0,1,0,0]
choices = ["START", "CANCEL"]
choice = 0
lastTemp = 24.00
lastAgitation = 0
inAgitation = False


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
            choice = incrimentList(len(choices), choice, True)            
            return                    
        if menuState == "inMainMenu":
            menuVal = incrimentList(len(menus[menuVal]), menuVal, True)
            return
        if menuState == "inSubMenu":
            subMenuVal = incrimentList(len(menus[menuVal][1]), subMenuVal, True)
            return
        if menuState == "inActionMenu":
            actionMenuVal = incrimentList(len(menus[menuVal][1][subMenuVal][1]), actionMenuVal, True)
            return
        if menuState == "inAdjustment":
            actionMenuValList[actionMenuVal] = incrimentList(len(menus[menuVal][1][subMenuVal][1][actionMenuVal][1]), actionMenuValList[actionMenuVal], True)
            return
    if transition == 0b1011 or transition == 0b0100:
        lastStatusTime = now
        if menuState == "waitingForConfirm":
            choice = incrimentList(len(choices), choice, False)            
            return                    
        if menuState == "inMainMenu":
            menuVal = incrimentList(len(menus[menuVal]), menuVal, False)
            return
        if menuState == "inSubMenu":
            subMenuVal = incrimentList(len(menus[menuVal][1]), subMenuVal, False)
            return
        if menuState == "inActionMenu":
            actionMenuVal = incrimentList(len(menus[menuVal][1][subMenuVal][1]), actionMenuVal, False)
            return
        if menuState == "inAdjustment":
            actionMenuValList[actionMenuVal] = incrimentList(len(menus[menuVal][1][subMenuVal][1][actionMenuVal][1]), actionMenuValList[actionMenuVal], True)
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
            print("confirmed")
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
            for x in range(0, len(menus[menuVal][1][subMenuVal][1])):
                typeString = typeString + (str(menus[menuVal][1][subMenuVal][1][x][1][actionMenuValList[x]])) + " "
            # For some reason, not starting the development in a new thread locks up the code, but running
            # developFilm() in the main loop with args, works fine?  WTF?
            _thread.start_new_thread(developFilm,(typeString.strip(), "foo"))
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
        lastTemp = round(tempC, 2) 
        return lastTemp
    except Exception as e:
        return lastTemp


def moveStepper(angle, foo): # _thread is wierd and wants a tuple for args?
    global lastAgitation
    global inAgitation
    inAgitation = True
    stepper.angle(angle)
    lastAgitation = time.ticks_ms()
    inAgitation = False

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
                
    


def developFilm(typeString, foo):
    global menuState
    isC41 = "C-41" in typeString
    if isC41:
        menuState = "waitingForConfirm"
        developC41(typeString)
        return

    
def developC41(typeString):
    global waitingForConfirm
    global inDevelopment
    global confirmationText
    global devState
    global inMenu
    global menuState
    inMenu = False
    soakTime = 10 * 1000
    confirmationText = "START SOAK?"
    devState = "SOAK"
    inDevelopment = True
    soakStart = 0
    elapsed = 0
    devStart = 0
    devTime = 1000000000
    devTime = 0
    agitationCycle = 30 * 1000
    initialAgitation = 10 * 1000
    agitationTime = 10 * 1000
    initialAgitationDone = False
    blixStart = 0
    blixTime = 8 * 60 * 1000
    washStart = 0
    washTime = 3* 60 * 1000
    rinseStart = 0
    rinseTime = 60 * 1000
    rinseAgitation = 15 * 1000
    

    while inDevelopment:
        temp = readTemp()
        theTime = convertMs(0)
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
                soakStart = time.ticks_ms()
            elapsed = abs(time.ticks_diff(soakStart, time.ticks_ms()))
            timeLeft = (soakTime - elapsed)
            theTime = convertMs(timeLeft)
            if elapsed >= soakTime:
                menuState = "waitingForConfirm"
                devState = "DEVELOP"
                confirmationText = "START DEV?"
                lightsAndBuzzer()
            
        if devState == "DEVELOP" and menuState == "confirmed":
            if devStart == 0:
                devStart = time.ticks_ms()         
            devTime = getNewTime(temp, typeString)
            now = time.ticks_ms()
            elapsed = abs(time.ticks_diff(devStart, now))
            agitationElapsed = abs(time.ticks_diff(lastAgitation, now))
            timeLeft = (devTime - elapsed)
            theTime = convertMs(timeLeft)            
            if elapsed >= devTime and not inAgitation:
                menuState = "waitingForConfirm"
                devState = "BLIX"
                confirmationText = "START BLIX?"
                lightsAndBuzzer()

            if not initialAgitationDone:
                initialAgitationDone = True
                _thread.start_new_thread(moveStepper, ((initialAgitation / 1000) * CONST.ANGLE_PER_SECOND, "foo"))
            if agitationElapsed >= agitationCycle and not inAgitation:
                if agitationTime <= timeLeft * 0.85:
                    _thread.start_new_thread(moveStepper, ((agitationTime / 1000) * CONST.ANGLE_PER_SECOND, "foo"))
                else:
                    # need to experiment a bit, since I can probably get a higher percentage of last agitation done.
                    _thread.start_new_thread(moveStepper, (timeLeft * 0.85, "foo"))
        
        if devState == "BLIX" and menuState == "confirmed":
            if blixStart == 0:
                blixStart = time.ticks_ms()
                initialAgitationDone = False
            now = time.ticks_ms()
            elapsed = abs(time.ticks_diff(blixStart, now))
            agitationElapsed = abs(time.ticks_diff(lastAgitation, now))
            timeLeft = (blixTime - elapsed)
            theTime = convertMs(timeLeft)
            if elapsed >= blixTime and not inAgitation:
                menuState = "waitingForConfirm"
                devState = "WASH"
                confirmationText = "START WASH?"
                lightsAndBuzzer()

            if not initialAgitationDone:
                initialAgitationDone = True
                _thread.start_new_thread(moveStepper, ((initialAgitation / 1000) * CONST.ANGLE_PER_SECOND, "foo"))
            if agitationElapsed >= agitationTime and not inAgitation:
                if agitationTime <= timeLeft * 0.85:
                    _thread.start_new_thread(moveStepper, ((agitationTime / 1000) * CONST.ANGLE_PER_SECOND, "foo"))
                else:
                    # need to experiment a bit, since I can probably get a higher percentage of last agitation done.
                    _thread.start_new_thread(moveStepper, (timeLeft * 0.85, "foo"))
        
        if devState == "WASH" and menuState == "confirmed":
            if washStart == 0:
                washStart = time.ticks_ms()
            now = time.ticks_ms()
            elapsed = abs(time.ticks_diff(washStart, now))
            timeLeft = (washTime - elapsed)
            theTime = convertMs(timeLeft)
            if elapsed >= washTime and not inAgitation:
                menuState = "waitingForConfirm"
                devState = "RINSE"
                confirmationText = "START RINSE?"
                lightsAndBuzzer()

        
        if devState == "RINSE" and menuState == "confirmed":
            if rinseStart == 0:
                rinseStart = time.ticks_ms()
                initialAgitationDone = False
            now = time.ticks_ms()
            elapsed = abs(time.ticks_diff(blixStart, now))
            timeLeft = (blixTime - elapsed)
            theTime = convertMs(timeLeft)
            if elapsed >= rinseTime and not inAgitation:
                menuState = "waitingForConfirm"
                devState = "DONE"
                confirmationText = "GO AGAIN?"
                lightsAndBuzzer()

            if not initialAgitationDone:
                initialAgitationDone = True
                _thread.start_new_thread(moveStepper, ((rinseAgitation / 1000) * CONST.ANGLE_PER_SECOND, "foo"))
            

        drawDevelopDisplay(temp,theTime)

        if inAgitation:
            time.sleep(0.5)
        else:
            time.sleep(0.15)
    

# Initilize Rotary Input IRQs
rotaryDtPin.irq(handler=handleSpin, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
rotaryClkPin.irq(handler=handleSpin, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
rotarySwPin.irq(handler=handleClick, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)

# developFilm("C-41 NORM 0")
# lightsAndBuzzer()

while inMenu == True:
    drawMenuDisplay()
    time.sleep(0.15)






