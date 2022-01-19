from contentLayout import Layout
from buttons import BetterButton
from adafruit_display_text import label
import displayio
import os
import re
# from adafruit_button import Button

class SetupPage(Layout):
    def __init__(self, selected, notSelected, title_font, title_color, title_scale, label_font, fill_color, startX=0, startY=0):
        self.group = displayio.Group()
        self.title_font = title_font
        self.title_scale = title_scale
        self.title_color = title_color
        self.label_font = label_font
        self.fill_color = fill_color
        self.title= label.Label(title_font, text="Setup", color=title_color, scale=title_scale, anchored_position=(80,3), anchor_point=(0,0))

        self.intervalButton = BetterButton(
            x=10,
            y=40,
            width=100,
            height=40,
            style=BetterButton.ROUNDRECT,
            fill_color= self.fill_color,
            outline_color = selected,
            label="Interval",
            label_font=self.label_font,
            label_color=selected,
        )

        self.thermistorButton = BetterButton(
            x=125,
            y=40,
            width=100,
            height=40,
            style=BetterButton.ROUNDRECT,
            fill_color= self.fill_color,
            outline_color = notSelected,
            label="Thermistors",
            label_font=self.label_font,
            label_color=notSelected,
        )

        self.calibrationButton = BetterButton(
            x=10,
            y=90,
            width=100,
            height=40,
            style=BetterButton.ROUNDRECT,
            fill_color= self.fill_color,
            outline_color = notSelected,
            label="Calibration",
            label_font=self.label_font,
            label_color=notSelected,
        )
        self.durationButton = BetterButton(
            x=125,
            y=90,
            width=100,
            height=40,
            style=BetterButton.ROUNDRECT,
            fill_color= self.fill_color,
            outline_color = notSelected,
            label="Duration",
            label_font=self.label_font,
            label_color=notSelected,
        )
        self.intervalButton.actionFunction = self.intervalButtonPress
        self.thermistorButton.actionFunction  = self.thermistorButtonPress
        self.calibrationButton.actionFunction = self.calibrationButtonPress
        self.durationButton.actionFunction = self.durationButtonPress
        

        self.group.append(self.title)
        self.group.append(self.intervalButton)
        self.group.append(self.thermistorButton)
        self.group.append(self.calibrationButton)
        self.group.append(self.durationButton)

        self.layout = [[self.intervalButton, self.thermistorButton],
                        [self.calibrationButton, self.durationButton]]

        super(SetupPage, self).__init__(self.group, self.layout, selected, notSelected, startX=0, startY=0)
    
    ## Define Actions when the buttons are selected
    def intervalButtonPress(self, button, context):
        self.manager.subLayout(0)

    def thermistorButtonPress(self, button, context):
        self.manager.subLayout(1)

    def calibrationButtonPress(self, button, context):
        self.manager.subLayout(2)
        self.manager.settings["calibrationFlag"] = True
        files = sorted(os.listdir("/calibration"))
        if len(files) >= 1:
            for i in range(len(files)):
                file = files[i]
                if not re.match('^calibration[0-9]*.csv$', file):
                    files.pop(i)
            if len(files) >= 1:
                lastFile = files[-1]
                value = re.match('^calibration([0-9]*).csv', lastFile).group(1)
                self.manager.settings["calfilename"] = f"calibration{int(value) + 1}.csv"
            else:
                self.manager.settings["calfilename"] = "calibration1.csv"
        else:
            self.manager.settings["calfilename"] = "calibration1.csv"

        with open(f"/calibration/{self.manager.settings['calfilename']}", 'w') as file:
            if self.manager.settings['t1Active'] and not self.manager.settings['t2Active']:
                file.write("#, R1 [Ω]\r\n")
            elif not self.manager.settings['t1Active'] and self.manager.settings['t2Active']:
                file.write("#, R2 [Ω]\r\n")
            else:
                file.write("#, R1 [Ω], R2 [Ω]\r\n")

    def durationButtonPress(self, button, context):
        self.manager.subLayout(3)
