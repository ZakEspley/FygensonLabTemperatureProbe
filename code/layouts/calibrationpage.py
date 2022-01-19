from contentLayout import Layout
from buttons import BetterButton
from adafruit_display_text import label
import displayio
import os

class CalibrationPage(Layout):
    def __init__(self, selected, notSelected, title_font, title_color, title_scale, label_font, fill_color, startX=0, startY=0):
        self.group = displayio.Group()
        self.title_font = title_font
        self.title_scale = title_scale
        self.title_color = title_color
        self.label_font = label_font
        self.fill_color = fill_color
        self.title = label.Label(title_font, text="Calbration Mode", color=title_color, scale=title_scale, anchored_position=(70,0), anchor_point=(0,0))
        self.data = None
        # Make labels to hold the text info and current resistance
        self.R1_label = label.Label(label_font, text="R1 = ...", color=title_color, scale=2)
        self.R2_label = label.Label(label_font, text="R2 = ...", color=title_color, scale=2)
        self.R1_label.x = 10
        self.R2_label.x = 10
        self.R1_label.y = 40
        self.R2_label.y = 77

        self.recordButton = BetterButton(
                        x=70,
                        y=100,
                        width=70,
                        height=28,
                        style=BetterButton.ROUNDRECT,
                        fill_color= self.fill_color,
                        outline_color = selected,
                        label="Record",
                        label_font=self.label_font,
                        label_color=selected,
                    )
        
        self.recordButton.actionFunction = self.recordButtonPress

        self.group.append(self.title)
        self.group.append(self.R1_label)
        self.group.append(self.R2_label)
        self.group.append(self.recordButton)

        
        self.layout = [[self.recordButton]]

        super(CalibrationPage, self).__init__(self.group, self.layout, selected, notSelected, startX=0, startY=0)

    def recordButtonPress(self, button, context):
        with open(f"/calibration/{self.manager.settings['calfilename']}", 'a') as file:
            print(f"DATA: {self.data}")
            if len(self.data) == 2:
                file.write(f"{self.data[0]}, {self.data[1]}\r\n")
            else:
                file.write(f"{self.data[0]}, {self.data[1]}, {self.data[2]}\r\n")
