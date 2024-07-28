# CONSTANTS

# OLED SIZE.  You could use a different size, but the menu system would probably be fucked.
OLED_H = 128
OLED_V = 64

# Digita, isn't digital.
CLICK_BOUNCE = 350 # Time in MS after a click to ignore a second click
SPIN_BOUNCE = 150

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
# Motor
MOTOR_PIN = 21
# Temp Probe
TEMP_DAT = 13
# LED/BUZZER
BUZZER_PIN = 15
LED_PIN = 2
# Other GPIO pins should work, these are just what I happened to use

# Development (Film) related stuff
ANGLE_PER_SECOND = 87 # Roughly what angle the stepper can spin in one second
C41_SOAK_TIME = 60 * 1000
C41_BLIX_TIME = 8 * 60 * 1000
C41_WASH_TIME = 3 * 60 * 1000
C41_RINSE_TIME = 60 * 1000

tempTimes = {   "C-41 0": 
                {
                    22.0 : 50.00,
                    24.0 : 35.00,
                    27.0 : 21.00,
                    29.5 : 13.00,
                    32.0 : 8.50,
                    35.0 : 5.75,
                    39.0 : 3.50,
                },
                "C-41 +1" :
                {                    
                    24.0 : 50.00,
                    27.0 : 28.00,
                    29.5 : 17.00,
                    32.0 : 11.00,
                    35.0 : 7.50,
                    39.0 : 4.55,
                },
                "C-41 +2" :
                {                    
                    27.0 : 37.00,
                    29.5 : 25.00,
                    32.0 : 14.75,
                    35.0 : 10.00,
                    39.0 : 6.73,
                },
                "C-41 +3" :
                {                    
                    29.5 : 35.00,
                    32.0 : 21.00,
                    35.0 : 14.33,
                    39.0 : 8.75,
                },
                "C-41 -1" :
                {                    
                    24.0 : 27.00,
                    27.0 : 16.25,
                    29.5 : 10.00,
                    32.0 : 6.50,
                    35.0 : 4.50,
                    39.0 : 2.75,
                },
            }
