import board as board
import displayio
from adafruit_st7789 import ST7789
import busio
import time
import digitalio
from analogio import AnalogIn
import terminalio
from adafruit_display_text import label
from adafruit_button import Button
from adafruit_debouncer import Debouncer
from adafruit_bitmap_font import bitmap_font
import math
import json
from contentLayout import Layout, LayoutManager
from buttons import BetterButton
from layouts.startpage import StartPage
from layouts.runpage import RunPage
from layouts.setuppage import SetupPage
from layouts.intervalpage import IntervalPage
from layouts.thermistorpage import ThermistorPage
from layouts.durationpage import DurationPage
from layouts.underContructionpage import UnderConstructionPage
from layouts.warningpage import WarningPage
from layouts.messagepage import MessagePage
from layouts.calibrationpage import CalibrationPage
#Get Display Ready to work
def InitWSPicoLCD():
    spi = busio.SPI(clock=board.GP10, MOSI=board.GP11)

    tft_cs = board.GP9
    tft_dc = board.GP8
    tft_reset = board.GP12
    display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs,reset=tft_reset)
    
    # How do we know what's the correct value for rowstart and colstart?
    display = ST7789(
        display_bus, rotation=270, width=240, height=135, rowstart=40, colstart=53
    )
    return display

## Initialize the Screen
displayio.release_displays()
display = InitWSPicoLCD()

#Setup Physical Buttons
Apin = digitalio.DigitalInOut(board.GP15)
Apin.direction = digitalio.Direction.INPUT
Apin.pull = digitalio.Pull.UP
A = Debouncer(Apin)

Bpin = digitalio.DigitalInOut(board.GP17)
Bpin.direction = digitalio.Direction.INPUT
Bpin.pull = digitalio.Pull.UP
B = Debouncer(Bpin)

UPpin = digitalio.DigitalInOut(board.GP2)
UPpin.direction = digitalio.Direction.INPUT
UPpin.pull = digitalio.Pull.UP
UP = Debouncer(UPpin)

DOWNpin = digitalio.DigitalInOut(board.GP18)
DOWNpin.direction = digitalio.Direction.INPUT
DOWNpin.pull = digitalio.Pull.UP
DOWN = Debouncer(DOWNpin)

LEFTpin = digitalio.DigitalInOut(board.GP16)
LEFTpin.direction = digitalio.Direction.INPUT
LEFTpin.pull = digitalio.Pull.UP
LEFT = Debouncer(LEFTpin)

RIGHTpin = digitalio.DigitalInOut(board.GP20)
RIGHTpin.direction = digitalio.Direction.INPUT
RIGHTpin.pull = digitalio.Pull.UP
RIGHT = Debouncer(RIGHTpin)

Cpin = digitalio.DigitalInOut(board.GP3)
Cpin.direction = digitalio.Direction.INPUT
Cpin.pull = digitalio.Pull.UP
C = Debouncer(Cpin)
# Make a list of the buttons to loop through and
# check the status of at the start of each run
physicalButtons = [A, B, UP, DOWN, LEFT, RIGHT, C]

######################################
#####     Display Layouts      #######
######################################

# Set the color, scale and font for titles
title_font = terminalio.FONT
title_color = 0x0000FF
title_scale = 2

# Create colorings for all buttons
selected = 0xFFFFFF
notSelected = 0xAAAAAA
fill = 0x313d78
font = font = bitmap_font.load_font("/Helvetica-Bold-16.bdf")

# # Create Interval Time Label


# ## Settings to be used.


# Create Layouts
startPage = StartPage(selected, notSelected, title_font, title_color, title_scale, font, fill)
runPage = RunPage(selected, notSelected, title_font, title_color, title_scale, font, fill)
setupPage = SetupPage(selected, notSelected, title_font, title_color, title_scale, font, fill)
intervalPage = IntervalPage(selected, notSelected, title_font, title_color, title_scale, font, fill)


thermistorPage = ThermistorPage(selected, notSelected, title_font, title_color, title_scale, font, fill)

durationPage = DurationPage(selected, notSelected, title_font, title_color, title_scale, font, fill)

# underConstructionPage = UnderConstructionPage(selected, notSelected, title_font, title_color, title_scale, font, fill)

calibrationPage = CalibrationPage(selected, notSelected, title_font, title_color, title_scale, font, fill)


noThermistorWarningPage = WarningPage(selected, notSelected, title_font, title_color, title_scale, font, fill, "Must select\r\nat least one\r\nthermistor!")
noIntervalWarningPage = WarningPage(selected, notSelected, title_font, title_color, title_scale, font, fill, "Interval must\r\n must be >0")
noDurationWarningPage = WarningPage(selected, notSelected, title_font, title_color, title_scale, font, fill, "Duration must\r\n must be >0")
shortDurationWarningPage = WarningPage(selected, notSelected, title_font, title_color, title_scale, font, fill, "Interval must\r\n must be \r\n> duration")

completedPage = MessagePage(selected, notSelected, title_font, title_color, title_scale, font, fill, "Measurement\r\nComplete!")


#  Create a manager control when layouts are displayed.
manager = LayoutManager(display, startPage, "settings.json")
# Append children only after creating manager
startPage.addChildren([runPage, setupPage, noThermistorWarningPage, noIntervalWarningPage, noDurationWarningPage, shortDurationWarningPage])
setupPage.addChildren([intervalPage, thermistorPage, calibrationPage, durationPage])
runPage.addChild(completedPage)

value = manager.settings['interval']
intervalSetting = label.Label(title_font, text=f"{value:05.0f} s", color=title_color, scale=4, anchored_position=(50,50), anchor_point=(0,0))
manager.settings["intervalSetting"] = intervalSetting

value = manager.settings["duration"]
durationSetting = label.Label(title_font, text=f"{value:05.0f} s", color=title_color, scale=4, anchored_position=(50,50), anchor_point=(0,0))
manager.settings["durationSetting"] = durationSetting

manager.settings["runningFlag"] = False
manager.settings["calibrationFlag"] = False

if manager.settings['t1Active']:
    thermistorPage.T1Button.label="X"
else:
    thermistorPage.T1Button.label=" "

if manager.settings['t2Active']:
    thermistorPage.T2Button.label="X"
else:
    thermistorPage.T2Button.label=" "



intervalPage.group.append(intervalSetting)
durationPage.group.append(durationSetting)
######### END LAYOUT SECTIONS ############

## Define how to process data to get temperature

# This function just gets that bits from a ADC pin
# and a grounded pin and return the difference between
# them in bits
def getBits(pin, gpin):
    return pin.value - gpin.value

# This assumes that the data is best modelled as a function
# of 1/( Sqrt( Ln(R_Th) ) ). Then fits the temp data to a polynomail
# whose coeffecients were determined from a fit.
def calcT(bit, R_rel, params):
    η = 1/ math.sqrt( math.log( R_rel/(65535/bit - 1) ) )
    c1, c2, c3, c4, c5 = params
    # T = -420.928727 + 1030.9166247*η+ 2609.501093*η**2 - 6236.873146*η**3 + 3880.265142*η**4
    T = c1 + c2*η + c3*η**2 + c4*η**3 + c5*η**4
    return T

def calcR(bit, R_rel):
    return R_rel/(65535/bit - 1)

def appendDataFile(data):
    with open(f"/data/{manager.settings['runfilename']}", 'a') as file:
        if len(data) == 2:
            file.write(f"{data[0]}, {data[1]}\r\n")
        else:
            file.write(f"{data[0]}, {data[1]}, {data[2]}\r\n")


# Setup the ADC
ADC0 = board.GP26_A0
ADC1 = board.GP27_A1
ADC2 = board.GP28_A2
T1 = AnalogIn(ADC0)
T2 = AnalogIn(ADC1)
ground = AnalogIn(ADC2)

## 100Ω Resistor for RTD Setting
R_100 = 100
## 10kΩ Values used
R_10k = (22130)/2 #Two 22kΩ in parallel
#Both in series
R_Total= R_10k + R_100

previousMeasurement = 0
measurementCounter = 1
avgLen = 5
while True:
    for button in physicalButtons:
        button.update()
    if manager.settings['runningFlag']:
        runPage.intervalLabel.text = f"Int: {manager.settings['interval']:.0f} s"
        runPage.durationLabel.text = f"Dur: {manager.settings['duration']:.0f} s"
        now = time.monotonic()
        dt = now-manager.settings['startTime']
        if now >= previousMeasurement + manager.settings['interval']:
            t1bits = []
            if manager.settings['t1Active']:
                for i in range(avgLen):
                    t1bits.append(getBits(T1, ground))
                t1bit = sum(t1bits)/avgLen
            t2bits = []
            if manager.settings['t2Active']:
                for i in range(avgLen):
                    t2bits.append(getBits(T2, ground))
                t2bit = sum(t2bits)/avgLen
            data = [dt]
            if manager.settings['t1Active']:
                T1_temp = calcT(t1bit, R_Total, manager.settings['t1Params'])
                runPage.T1_label.text = f"T1 = {T1_temp:.2f} C"
                data.append(T1_temp)
            if manager.settings['t2Active']:
                T2_temp = calcT(t2bit, R_Total, manager.settings['t2Params'])
                runPage.T2_label.text = f"T2 = {T2_temp:.2f} C"
                data.append(T2_temp)
            appendDataFile(data)
            previousMeasurement = now
        
        if dt >= manager.settings['duration']:
            manager.settings['runningFlag'] = False
            previousMeasurement = 0
            manager.subLayout(0)
        if dt >= 1:
            runPage.elapsedTimeLabel.text = f"Elapsed Time: {dt:.0f} s" 
    
    elif manager.settings['calibrationFlag']:
        now = time.monotonic()
        dt = now-previousMeasurement
        if dt >=1:
            t1bits =[]
            if manager.settings['t1Active']:
                for i in range(avgLen):
                    t1bits.append(getBits(T1,ground))
                t1bit = sum(t1bits)/avgLen
            t2bits = []
            if manager.settings['t2Active']:
                for i in range(avgLen):
                    t2bits.append(getBits(T2, ground))
                t2bit = sum(t2bits)/avgLen
        
            data = [measurementCounter]
            if manager.settings['t1Active']:
                R1_r = calcR(t1bit, R_Total)
                calibrationPage.R1_label.text = f"R1 = {R1_r:.1f} Ω"
                data.append(R1_r)
            if manager.settings['t2Active']:
                R2_r = calcR(t2bit, R_Total)
                calibrationPage.R2_label.text = f"R2 = {R2_r:.1f} Ω"
                data.append(R2_r)
            manager.activeLayout.data = data
            previousMeasurement = now

        
    
    if RIGHT.fell:
        manager.activeLayout.updateLayout("RIGHT")
    if LEFT.fell:
        manager.activeLayout.updateLayout("LEFT")
    if UP.fell:
        manager.activeLayout.updateLayout("UP")
    if DOWN.fell:
        manager.activeLayout.updateLayout("DOWN")
    if A.fell and manager.activeLayout.activeButton is not None:
        manager.activeLayout.activeButton.action(manager.settings)
        if isinstance(manager.activeLayout, CalibrationPage):
            measurementCounter += 1
    if B.fell:
        if manager.settings['calibrationFlag'] or manager.settings['runningFlag']:
            manager.settings['calibrationFlag'] = False
            manager.settings['runningFlag'] = False
            previousMeasurement = 0
            measurementCounter = 1
        manager.parentLayout()