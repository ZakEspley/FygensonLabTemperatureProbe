from contentLayout import Layout
from buttons import BetterButton
from adafruit_display_text import label
import displayio
import time
import os
import re
# from adafruit_button import Button

class StartPage(Layout):
    def __init__(self, selected, notSelected, title_font, title_color, title_scale, label_font, fill_color, startX=0, startY=0):
        self.group = displayio.Group()
        self.title_font = title_font
        self.title_scale = title_scale
        self.title_color = title_color
        self.label_font = label_font
        self.fill_color = fill_color
        self.title = label.Label(title_font, text="Temperature Probe", color=title_color, scale=title_scale, anchored_position=(14,3), anchor_point=(0,0))

        self.setupButton = BetterButton(
                        x=10,
                        y=75,
                        width=100,
                        height=50,
                        style=BetterButton.ROUNDRECT,
                        fill_color= self.fill_color,
                        outline_color = selected,
                        label="Setup",
                        label_font=self.label_font,
                        label_color=selected,
                    )

        self.startButton = BetterButton(
                        x=125,
                        y=75,
                        width=100,
                        height=50,
                        style=BetterButton.ROUNDRECT,
                        fill_color= self.fill_color,
                        outline_color = notSelected,
                        label="Start",
                        label_font=self.label_font,
                        label_color=notSelected,
                    )
        self.startButton.actionFunction = self.startButtonPress
        self.setupButton.actionFunction = self.setupButtonPress

        self.group.append(self.title)
        self.group.append(self.startButton)
        self.group.append(self.setupButton)

        self.layout = [[self.setupButton, self.startButton]]

        super(StartPage, self).__init__(self.group, self.layout, selected, notSelected, startX=0, startY=0)
    
    ## Define Actions when the buttons are selected
    def startButtonPress(self, button, context):
        if not (context['t1Active'] or context['t2Active']):
            self.manager.subLayout(2)
        elif context['interval'] == 0:
            self.manager.subLayout(3)
        elif context['duration'] == 0:
            self.manager.subLayout(4)
        elif context['interval'] > context['duration']:
            self.manager.subLayout(5)    
        else:
            self.manager.settings['runningFlag'] = True
            self.manager.settings['startTime'] = time.monotonic()
            self.manager.subLayout(0)
            files = sorted(os.listdir("/data"))
            if len(files) >= 1:
                for i in range(len(files)):
                    file = files[i]
                    if not re.match('^run[0-9]*.csv$', file):
                        files.pop(i)
                if len(files) >= 1:
                    lastFile = files[-1]
                    value = re.match('^run([0-9]*).csv', lastFile).group(1)
                    print(f"VALUE: {int(value) + 1}")
                    self.manager.settings["runfilename"] = f"run{int(value) + 1}.csv"
                else:
                    self.manager.settings["runfilename"] = "run1.csv"
            else:
                self.manager.settings["runfilename"] = "run1.csv"
            with open(f"/data/{self.manager.settings['runfilename']}", 'w') as file:
                if self.manager.settings['t1Active'] and not self.manager.settings['t2Active']:
                    file.write("dt [s], T1 [C]\r\n")
                elif not self.manager.settings['t1Active'] and self.manager.settings['t2Active']:
                    file.write("dt [s], T2 [C]\r\n")
                else:
                    file.write("dt [s], T1 [C], T2 [C]\r\n")
                

        

    def setupButtonPress(self, button, context):
        self.manager.subLayout(1)
