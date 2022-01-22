import gc
gc.enable()
import time
import digitalio
from analogio import AnalogIn
# import terminalio
from adafruit_display_text import label
from adafruit_debouncer import Debouncer
import math
import board as board
import displayio
from adafruit_st7789 import ST7789
import busio
from contentLayout import LayoutManager
from pages import *
print(f'PAGES_LOADED: {gc.mem_free()}')
gc.collect()

# title_font = terminalio.FONT
# title_color = 0x0000FF
# title_scale = 2

# Create colorings for all buttons
# selected = 0xFFFFFF
# notSelected = 0xAAAAAA
# fill = 0x313d78

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
gc.collect()
manager = LayoutManager(display, pageInfo['pages'], "startPage", "settings.json")

gc.collect()

# durationPage.durationLabel.text = f"{manager.settings['duration']:05.0f} s"
# intervalPage.intervalLabel.text = f"{manager.settings['interval']:05.0f} s"
# calDurationPage.calDurationLabel.text = f"{manager.settings['calDuration']:05.0f} s"
# calIntervalPage.calIntervalLabel.text = f"{manager.settings['calInterval']:05.0f} s"
manager.settings["runningFlag"] = False
manager.settings["calibrationFlag"] = False

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

def appendCalibrationFile(data):
    with open(f"/data/{manager.settings['calfilename']}", 'a') as file:
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
# measurementCounter = 1
avgLen = 5
gc.collect()
print(f"Before While: {gc.mem_free()}")
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
        calibrationPage.intervalLabel.text = f"Int: {manager.settings['interval']:.0f} s"
        calibrationPage.durationLabel.text = f"Dur: {manager.settings['duration']:.0f} s"
        now = time.monotonic()
        dt = now-manager.settings['startTime']
        if now >= previousMeasurement + manager.settings['interval']:
            t1bits =[]
            for i in range(avgLen):
                t1bits.append(getBits(T1,ground))
            t1bit = sum(t1bits)/avgLen
            t2bits = []
            for i in range(avgLen):
                t2bits.append(getBits(T2, ground))
            t2bit = sum(t2bits)/avgLen
        
            data = [dt]
            if manager.settings['ch1Active']:
                R1_r = calcR(t1bit, R_Total)
                R2_r = calcR(t2bit, R_100)
                gc.collect()
            else:
                R1_r = calcR(t1bit, R_100)
                R2_r = calcR(t2bit, R_Total)
                gc.collect()
            calibrationPage.R1_label.text = f"R1 = {R1_r:.1f} Ω"
            data.append(R1_r)
            calibrationPage.R2_label.text = f"R2 = {R2_r:.1f} Ω"
            data.append(R2_r)
            appendCalibrationFile(data)
            gc.collect()
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
        gc.collect()
    if B.fell:
        if manager.settings['calibrationFlag'] or manager.settings['runningFlag']:
            manager.settings['calibrationFlag'] = False
            manager.settings['runningFlag'] = False
            previousMeasurement = 0
        manager.parentLayout()