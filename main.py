# Module Imports
import utime as time
import _thread
from machine import Pin, SoftI2C
import stepper as Stepper
import ssd1306, onewire, ds18x20
# My Imports
import constants as CONST
from menus import menuText, menus


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
inMenu = True
inSubMenu = False
inActionMenu = False


def handleSpin(pin):
    global lastStatus
    global lastStatusTime
    global menuVal
    global subMenuVal
    global actionMenuVal
    global inSubMenu
    global inActionMenu
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
        if not inSubMenu and not inActionMenu:
            print(len(menus[menuVal]))
            if menuVal < len(menus[menuVal]) -1 :
                menuVal = menuVal + 1
                return
            menuVal = 0
            return
        if inSubMenu and not inActionMenu:
            if subMenuVal < (len(menus[menuVal][1]) - 1):
                subMenuVal = subMenuVal + 1
                return
            subMenuVal = 0
            return
        if inSubMenu:
            return
    if transition == 0b1011 or transition == 0b0100:
        lastStatusTime = now
        if not inSubMenu:
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
        

def handleClick(pin):
    global lastClick
    global subMenuVal
    global inSubMenu
    global inActionMenu
    global lastClickTime
    newClick = rotarySwPin.value()
    if lastClick == newClick:
        return
    now = time.ticks_ms()
    if abs(time.ticks_diff(lastClickTime, now)) <= CONST.CLICK_BOUNCE:
        return
    transition = (lastClick << 2 ) | newClick
    if transition == 0b01:
        lastClickTime = now
        if not inSubMenu and not inActionMenu:
            subMenuVal = 0
            inSubMenu = True
            time.sleep(0.25)
            return
        if inSubMenu and menus[menuVal][1][subMenuVal][0][0] == "BACK":   
            inSubMenu = False
            time.sleep(0.25)
            return

    lastClick = newClick # I feel like this should be before the sub menu check, but it works?
    time.sleep(0.15)

        
def drawMenuDisplay():
    display.fill(0)
    display.fill_rect(0,0,128,15,1)
    display.rect(0,16,128,48,1)    
    display.text(menus[menuVal][0], 5, 4, 0)
    if not inSubMenu:
        for x in range(0, len(menus[menuVal][1])):
            display.text(str(menus[menuVal][1][x][0][0]), 3, 20 + (x*10), 1)
    if inSubMenu:
        for x in range(0, len(menus[menuVal][1])):
            if subMenuVal == x:
                display.text("> " + str(menus[menuVal][1][x][0][0]), 3, 20 + (x*10), 1)
            else:
                display.text(str(menus[menuVal][1][x][0][0]), 3, 20 + (x*10), 1)            
    display.show()

def drawActionMenuDisplay():
    display.fill(0)
    display.fill_rect(0,0,128,15,1)
    display.rect(0,16,128,48,1)    
    display.text(menuText[menuVal][0], 5, 4, 0)
    if not inSubMenu:
        for x in range(0, len(menuText[menuVal][1])):
            display.text(menuText[menuVal][1][x], 3, 20 + (x*10), 1)
    if inSubMenu:
        for x in range(0, len(menuText[menuVal][1])):
            if subMenuVal == x:
                display.text("> " + menuText[menuVal][1][x], 3, 20 + (x*10), 1)
            else:
                display.text(menuText[menuVal][1][x], 3, 20 + (x*10), 1)            
    display.show()


def readTemp():
    dsSensor.convert_temp()
    tempC = dsSensor.read_temp(tempProbe)
    return round(tempC, 2)


def handleSubMenus(menu):
    global inSubMenu
    global inActionMenu
    if menu == "BACK":
        inSubMenu = False
        inActionMenu = False
        time.sleep(0.25)
        return
    if menu == "DEVELOP COLOR":
        inSubMenu = False
        inActionMenu = True
        type = ""
        exposure = 2
        agitation = ""

        
    

def moveStepper(angle, foo): # _thread is wierd and wants a tuple for args?
    stepper.angle(angle)

def developColor(type, exposure, agitation):
    currentTemp = readTemp()
    _thread.start_new_thread(moveStepper, (720, "foo"))   
    

    

# Initilize Rotary Input IRQs
rotaryDtPin.irq(handler=handleSpin, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
rotaryClkPin.irq(handler=handleSpin, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
rotarySwPin.irq(handler=handleClick, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)

_thread.start_new_thread(moveStepper, (720, "foo"))

while inMenu == True:
    drawMenuDisplay()
    temp = readTemp()
    # print(temp)
    time.sleep(0.1)






