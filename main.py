# from rotary import Rotary
import utime as time
from machine import Pin, SoftI2C
import stepper as Stepper
import ssd1306, onewire, ds18x20
from menus import menuText

# CONSTANTS
OLED_H = 128
OLED_V = 64
CLICK_BOUNCE = 350 # Time in MS after a click to ignore a second click
SPIN_BOUNCE = 25

# PINS
# Rotary
# KY 070 rotary encoders from Amazon need to have grnd/+ wiring reversed to work, it's kinda silly
ROTARY_CLK = 35
ROTARY_DT = 32
ROTARY_SW = 34
# Display
DISPLAY_SDA = 23
DISPLAY_SLC = 22
# Stepper
STEPPER_IN1 = 16
STEPPER_IN2 = 17
STEPPER_IN3 = 18
STEPPER_IN4 = 19
# Temp Probe
TEMP_DAT = 13
# Other GPIO pins should work, these are just what I happened to use


# Menu List
mainMenus = [["DEVELOP", ["Color C-41", "Color E-6", "B&W", "Back"]], ["SETTINGS", ["Sound", "Language", "Back"]], ["TEST", ["Test Stepper", "Back"]]]
subMenus = [["Color C-41", "Color E-6", "B&W", "Back"], ["Sound", "Language", "Back"], ["Test Stepper", "Back"]]

# INIT OBJECTS

# ROTARY PINS
rotaryDtPin = Pin(ROTARY_DT, Pin.IN)
rotaryClkPin = Pin(ROTARY_CLK, Pin.IN)
rotarySwPin = Pin(ROTARY_SW, Pin.IN)
# OLED
i2c = SoftI2C(sda=Pin(DISPLAY_SDA), scl=Pin(DISPLAY_SLC))
display = ssd1306.SSD1306_I2C(OLED_H, OLED_V, i2c)
# TEMP PROBE
dsPin = Pin(TEMP_DAT)
dsSensor = ds18x20.DS18X20(onewire.OneWire(dsPin))
tempProbe = dsSensor.scan()[0]
# STEPPER
stepper = Stepper.create(Pin(STEPPER_IN1, Pin.OUT), Pin(STEPPER_IN2, Pin.OUT), Pin(STEPPER_IN3, Pin.OUT), Pin(STEPPER_IN4, Pin.OUT), delay = 2)

# Global Variables
lastStatus = (rotaryDtPin.value() <<1 | rotaryClkPin.value())
lastStatusTime = time.ticks_ms()
lastClick = 0
lastClickTime = time.ticks_ms()
menuVal = 0
subMenuVal = 0
actionMenuVal = 0
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
    if abs(time.ticks_diff(lastStatusTime, now)) <= SPIN_BOUNCE:
        print("Time Bounced")
        return
    transition = (lastStatus << 2 ) | newStatus
    lastStatus = newStatus  
    if transition == 0b1000 or transition == 0b0111:
        lastStatusTime = now                     
        print("CW")
        if not inSubMenu and not inActionMenu:
            if menuVal < (len(mainMenus) - 1):
                menuVal = menuVal + 1
                return
            menuVal = 0
            return
        if inSubMenu and not inActionMenu:
            if subMenuVal < (len(subMenus[menuVal]) - 1):
                subMenuVal = subMenuVal + 1
                return
            subMenuVal = 0
            return
        if inSubMenu:
            return
    if transition == 0b1011 or transition == 0b0100:
        lastStatusTime = now
        print("ACW")
        if not inSubMenu:
            if menuVal >= 1:
                menuVal = menuVal - 1
                return
            menuVal = (len(mainMenus) - 1)
            return
        if inSubMenu:
            if subMenuVal >= 1:
                subMenuVal = subMenuVal -1
                return
            subMenuVal = (len(subMenus[menuVal]) -1)
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
    if abs(time.ticks_diff(lastClickTime, now)) <= CLICK_BOUNCE:
        print(time.ticks_diff(lastClickTime, now))
        print("Click Bounced")
        return
    transition = (lastClick << 2 ) | newClick
    if transition == 0b01:
        print("Button Pressed")
        print(time.ticks_diff(lastClickTime, now))        
        lastClickTime = now
        if not inSubMenu and not inActionMenu:
            subMenuVal = 0
            inSubMenu = True
            time.sleep(0.25)
            return
        inActionMenu = True        
        handleSubMenus(subMenus[menuVal][subMenuVal])

    lastClick = newClick # I feel like this should be before the sub menu check, but it works?
    time.sleep(0.15)

        
def drawDisplay():
    display.fill(0)
    display.fill_rect(0,0,128,15,1)
    display.rect(0,16,128,48,1)    
    display.text(menuText[menuVal][0], 5, 4, 0)
    if not inSubMenu:
        for x in range(0, len(menuText[menuVal][1])):
            display.text(menuText[menuVal][1][x], 3, 20 + (x*10), 1)
        # if len(subMenus[menuVal]) >= 2:
        #     display.text(subMenus[menuVal][1], 3, 30, 1)
        # if len(subMenus[menuVal]) >= 3:
        #     display.text(subMenus[menuVal][2], 3, 40, 1)
        # if len(subMenus[menuVal]) >= 4:
        #     display.text(subMenus[menuVal][3], 3, 50, 1)
    if inSubMenu:
        for x in range(0, len(menuText[menuVal][1])):
            if subMenuVal == x:
                display.text("> " + menuText[menuVal][1][x], 3, 20 + (x*10), 1)
            else:
                display.text(menuText[menuVal][1][x], 3, 20 + (x*10), 1)
        # if len(subMenus[menuVal]) >= 2:
        #     if subMenuVal == 1:
        #         display.text("> " + subMenus[menuVal][1], 3, 30, 1)
        #     else:
        #         display.text(subMenus[menuVal][1], 3, 30, 1)
        # if len(subMenus[menuVal]) >= 3:
        #     if subMenuVal == 2:
        #         display.text("> " + subMenus[menuVal][2], 3, 40, 1)
        #     else:
        #         display.text(subMenus[menuVal][2], 3, 40, 1)
        # if len(subMenus[menuVal]) >= 4:
        #     if subMenuVal == 3:
        #         display.text("> " + subMenus[menuVal][3], 3, 50, 1)
        #     else:
        #         display.text(subMenus[menuVal][3], 3, 50, 1)
            
    display.show()


def readTemp():
    dsSensor.convert_temp()
    tempC = dsSensor.read_temp(tempProbe)
    return tempC


def handleSubMenus(menu):
    global inSubMenu
    global inActionMenu
    if menu == "Back":
        inSubMenu = False
        inActionMenu = False
        time.sleep(0.25)
        return


# Initilize Rotary Input IRQs
rotaryDtPin.irq(handler=handleSpin, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
rotaryClkPin.irq(handler=handleSpin, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
rotarySwPin.irq(handler=handleClick, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)


while True:
    drawDisplay()
    # print(rotaryDtPin.value(), rotaryClkPin.value(), rotarySwPin.value())
    time.sleep(0.1)
