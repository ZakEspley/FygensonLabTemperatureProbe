from contentLayout import Layout
from buttons import BetterButton
from adafruit_display_text import label
import displayio

class RunPage(Layout):
    def __init__(self, selected, notSelected, title_font, title_color, title_scale, label_font, fill_color, startX=0, startY=0):
        self.group = displayio.Group()
        self.title_font = title_font
        self.title_scale = title_scale
        self.title_color = title_color
        self.label_font = label_font
        self.fill_color = fill_color
        self.title = label.Label(title_font, text="Running", color=title_color, scale=title_scale, anchored_position=(70,0), anchor_point=(0,0))

        # Make labels to hold the text info and current temperature
        self.T1_label = label.Label(label_font, text="T1 = ...", color=title_color, scale=2)
        self.T2_label = label.Label(label_font, text="T2 = ...", color=title_color, scale=2)
        self.T1_label.x = 10
        self.T2_label.x = 10
        self.T1_label.y = 40
        self.T2_label.y = 77

        self.intervalLabel = label.Label(label_font, text=f"Interval: x s", color=title_color, scale = 1)
        self.intervalLabel.x = 10
        self.intervalLabel.y = 101

        self.durationLabel = label.Label(label_font, text=f"Duration: x s", color=title_color, scale = 1)
        self.durationLabel.x = 120
        self.durationLabel.y = 101

        self.elapsedTimeLabel = label.Label(label_font, text=f"Elapsed Time:", color=title_color, scale = 1)
        self.elapsedTimeLabel.x = 10
        self.elapsedTimeLabel.y = 126

        self.group.append(self.title)
        self.group.append(self.T1_label)
        self.group.append(self.T2_label)
        self.group.append(self.intervalLabel)
        self.group.append(self.durationLabel)
        self.group.append(self.elapsedTimeLabel)

        # self.completedLabel = label.Label(label_font, text=f"DONE!", color=0x44FF44, scale = 2)
        # self.elapsedTimeLabel.x = 10
        # self.elapsedTimeLabel.y = 125

        self.layout = None

        super(RunPage, self).__init__(self.group, self.layout, selected, notSelected, startX=0, startY=0)

