from rotary import Rotary
import utime as time
from machine import Pin, SoftI2C
import stepper as Stepper
import ssd1306, onewire, ds18x20

# CONSTANTS
OLED_H = 128
OLED_V = 64
# PINS
ROTARY_CLK = 35
ROTARY_DT = 32
ROTARY_SW = 33

DISPLAY_SDA = 23
DISPLAY_SLC = 22

STEPPER_IN1 = 16
STEPPER_IN2 = 17
STEPPER_IN3 = 18
STEPPER_IN4 = 19

TEMP_DAT = 13


# Menu List
mainMenus = ["DEVELOP", "SETTINGS", "TEST"]
subMenus = [["Color C-41", "Color E-6", "B&W", "B&W Stand"], ["Sound", "Language"], ["Test Stepper"]]

# Initilize Objects
# ROTARY => Rotary(Dt, Clk, SW)
rotary = Rotary(ROTARY_DT, ROTARY_CLK, ROTARY_SW)
# OLED
i2c = SoftI2C(sda=Pin(DISPLAY_SDA), scl=Pin(DISPLAY_SLC))
display = ssd1306.SSD1306_I2C(OLED_H, OLED_V, i2c)
# TEMP PROBE
dsPin = Pin(TEMP_DAT)
dsSensor = ds18x20.DS18X20(onewire.OneWire(dsPin))
tempProbe = dsSensor.scan()[0]
# STEPPER
stepper = Stepper.create(Pin(STEPPER_IN1, Pin.OUT), Pin(STEPPER_IN2, Pin.OUT), Pin(STEPPER_IN3, Pin.OUT), Pin(STEPPER_IN4, Pin.OUT), delay = 2)
stepper.angle(360)


menuVal = 0
subMenuVal = 0
inSubMenu = False

def rotaryInput(change):
    global menuVal
    global subMenuVal
    global inSubMenu
    if change == Rotary.ROT_CW:
        if not inSubMenu:
            if menuVal < (len(mainMenus) - 1):
                menuVal = menuVal + 1
                return
            menuVal = 0
            return
        if inSubMenu:
            if subMenuVal < (len(subMenus[menuVal]) - 1):
                subMenuVal = subMenuVal + 1
                return
            subMenuVal = 0
            return
    elif change == Rotary.ROT_CCW:
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
    elif change == Rotary.SW_PRESS:
        if not inSubMenu:
            subMenuVal = 0
            inSubMenu = True
            time.sleep(0.25)
            return
        if inSubMenu:
            inSubMenu = False
            time.sleep(0.25)
            return
        
def drawDisplay():
    display.fill(0)
    display.fill_rect(0,0,128,15,1)
    display.rect(0,16,128,48,1)    
    display.text(mainMenus[menuVal], 5, 4, 0)
    if not inSubMenu:
        display.text(subMenus[menuVal][0], 3, 20, 1)
        if len(subMenus[menuVal]) >= 2:
            display.text(subMenus[menuVal][1], 3, 30, 1)
        if len(subMenus[menuVal]) >= 3:
            display.text(subMenus[menuVal][2], 3, 40, 1)
        if len(subMenus[menuVal]) >= 4:
            display.text(subMenus[menuVal][3], 3, 50, 1)
    if inSubMenu:
        if subMenuVal == 0:
            display.text("> " + subMenus[menuVal][0], 3, 20, 1)
        else:
            display.text(subMenus[menuVal][0], 3, 20, 1)
        if len(subMenus[menuVal]) >= 2:
            if subMenuVal == 1:
                display.text("> " + subMenus[menuVal][1], 3, 30, 1)
            else:
                display.text(subMenus[menuVal][1], 3, 30, 1)
        if len(subMenus[menuVal]) >= 3:
            if subMenuVal == 2:
                display.text("> " + subMenus[menuVal][2], 3, 40, 1)
            else:
                display.text(subMenus[menuVal][2], 3, 40, 1)
        if len(subMenus[menuVal]) >= 4:
            if subMenuVal == 3:
                display.text("> " + subMenus[menuVal][3], 3, 50, 1)
            else:
                display.text(subMenus[menuVal][3], 3, 50, 1)
            
    display.show()
        
rotary.add_handler(rotaryInput)



while True:
    drawDisplay()
    time.sleep(0.15)
