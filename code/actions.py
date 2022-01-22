import os
import re
import time

def startButtonAction(self, context):
            if not (context['t1Active'] or context['t2Active']):
                self.layout.manager.subLayout(2)
            elif context['interval'] == 0:
                self.layout.manager.subLayout(3)
            elif context['duration'] == 0:
                self.layout.manager.subLayout(4)
            elif context['interval'] > context['duration']:
                self.layout.manager.subLayout(5)    
            else:
                self.layout.manager.settings['runningFlag'] = True
                self.layout.manager.settings['startTime'] = time.monotonic()
                self.layout.manager.subLayout(0)
                files = sorted(os.listdir("/data"))
                # print(f"FILES: {files}")
                if len(files) >= 1:
                    for i in range(len(files)):
                        file = files[i]
                        if not re.match('^run[0-9]*.csv$', file):
                            files.pop(i)
                    # print(f"FILES AGAIN: {files}")
                    if len(files) >= 1:
                        lastFile = files[-1]
                        value = re.match('^run([0-9]*).csv', lastFile).group(1)
                        # print(f"VALUE: {int(value) + 1}")
                        self.layout.manager.settings["filename"] = f"run{int(value) + 1}.csv"
                    else:
                        self.layout.manager.settings["filename"] = "run1.csv"
                else:
                    self.layout.manager.settings["filename"] = "run1.csv"
                # print(self.layout.manager.settings['filename'])
                with open(f"/data/{self.layout.manager.settings['filename']}", 'w') as file:
                    if self.layout.manager.settings['t1Active'] and not self.layout.manager.settings['t2Active']:
                        file.write("dt [s], T1 [C]\r\n")
                    elif not self.layout.manager.settings['t1Active'] and self.layout.manager.settings['t2Active']:
                        file.write("dt [s], T2 [C]\r\n")
                    else:
                        file.write("dt [s], T1 [C], T2 [C]\r\n")
                    
def setupButtonAction(self, context):
    self.layout.manager.subLayout(0)

def intervalButtonAction(self, context):
    self.layout.manager.subLayout(1)
    self.layout.manager.activeLayout.intervalLabel.text = f"{context['interval']:05.0f} s"

def thermistorButtonAction(self, context):
    self.layout.manager.subLayout(2)

def calibrationButtonAction(self, context):
    self.layout.manager.subLayout(3)

def calDurationButtonAction(self, context):
    self.layout.manager.subLayout(0)
    self.layout.manager.activeLayout.calDurationLabel.text = f"{context['calDuration']:05.0f} s"

def calIntervalButtonAction(self, context):
    self.layout.manager.subLayout(1)
    self.layout.manager.activeLayout.calIntervalLabel.text = f"{context['calInterval']:05.0f} s"

def channelButtonAction(self, context):
    self.layout.manager.subLayout(2)

def calibrateButtonAction(self, context):
    self.layout.manager.subLayout(3)
    context["calibrationFlag"] = True
    files = sorted(os.listdir("/calibration"))
    if len(files) >= 1:
        for i in range(len(files)):
            file = files[i]
            if not re.match('^calibration[0-9]*.csv$', file):
                files.pop(i)
        if len(files) >= 1:
            lastFile = files[-1]
            value = re.match('^calibration([0-9]*).csv', lastFile).group(1)
            context["calfilename"] = f"calibration{int(value) + 1}.csv"
        else:
            context["calfilename"] = "calibration1.csv"
    else:
        context["calfilename"] = "calibration1.csv"

    with open(f"/calibration/{context['calfilename']}", 'w') as file:
        if context['ch1Active']:
            file.write("#, R_Th [Ω], R_RTD [Ω]\r\n")
        else:
            file.write("#, R_RTD [Ω], R_Th [Ω]\r\n")

def durationButtonAction(self, context):
    self.layout.manager.subLayout(0)
    self.layout.manager.activeLayout.durationLabel.text = f"{context['duration']:05.0f} s"

def durationUpAction(self, context):
    valueMap = {
        "dtenThousands":0,
        "doneThousands":1,
        "doneHundreds":2,
        "dtens":3,
        "dones":4
    }
    index = valueMap[self.name[:-2]]
    context["durationLabel"][index] = (context["durationLabel"][index] + 1) % 10
    context['duration'] = sum([context['durationLabel'][i]*10**(4-i) for i in range(5)])
    self.layout.durationLabel.text = f"{context['duration']:05.0f} s"

def durationDownAction(self, context):
    valueMap = {
        "dtenThousands":0,
        "doneThousands":1,
        "doneHundreds":2,
        "dtens":3,
        "dones":4
    }
    index = valueMap[self.name[:-4]]
    context["durationLabel"][index] = (context["durationLabel"][index] - 1) % 10
    context['duration'] = sum([context['durationLabel'][i]*10**(4-i) for i in range(5)])
    self.layout.durationLabel.text = f"{context['duration']:05.0f} s"

def intervalUpAction(self, context):
    valueMap = {
        "itenThousands":0,
        "ioneThousands":1,
        "ioneHundreds":2,
        "itens":3,
        "iones":4
    }
    index = valueMap[self.name[:-2]]
    context["intervalLabel"][index] = (context["intervalLabel"][index] + 1) % 10
    context['interval'] = sum([context['intervalLabel'][i]*10**(4-i) for i in range(5)])
    self.layout.intervalLabel.text = f"{context['interval']:05.0f} s"

def intervalDownAction(self, context):
    valueMap = {
        "itenThousands":0,
        "ioneThousands":1,
        "ioneHundreds":2,
        "itens":3,
        "iones":4
    }
    index = valueMap[self.name[:-4]]
    context["intervalLabel"][index] = (context["intervalLabel"][index] - 1) % 10
    context['interval'] = sum([context['intervalLabel'][i]*10**(4-i) for i in range(5)])
    self.layout.intervalLabel.text = f"{context['interval']:05.0f} s"

def cdurationUpAction(self, context):
    valueMap = {
        "cdtenThousands":0,
        "cdoneThousands":1,
        "cdoneHundreds":2,
        "cdtens":3,
        "cdones":4
    }
    index = valueMap[self.name[:-2]]
    context["calDurationLabel"][index] = (context["calDurationLabel"][index] + 1) % 10
    context['calDuration'] = sum([context['calDurationLabel'][i]*10**(4-i) for i in range(5)])
    self.layout.calDurationLabel.text = f"{context['calDuration']:05.0f} s"

def cdurationDownAction(self, context):
    valueMap = {
        "cdtenThousands":0,
        "cdoneThousands":1,
        "cdoneHundreds":2,
        "cdtens":3,
        "cdones":4
    }
    index = valueMap[self.name[:-4]]
    context["calDurationLabel"][index] = (context["calDurationLabel"][index] - 1) % 10
    context['calDuration'] = sum([context['calDurationLabel'][i]*10**(4-i) for i in range(5)])
    self.layout.calDurationLabel.text = f"{context['calDuration']:05.0f} s"

def cintervalUpAction(self, context):
    valueMap = {
        "citenThousands":0,
        "cioneThousands":1,
        "cioneHundreds":2,
        "citens":3,
        "ciones":4
    }
    index = valueMap[self.name[:-2]]
    context["calIntervalLabel"][index] = (context["calIntervalLabel"][index] + 1) % 10
    context['calInterval'] = sum([context['calIntervalLabel'][i]*10**(4-i) for i in range(5)])
    self.layout.calIntervalLabel.text = f"{context['calInterval']:05.0f} s"

def cintervalDownAction(self, context):
    valueMap = {
        "citenThousands":0,
        "cioneThousands":1,
        "cioneHundreds":2,
        "citens":3,
        "ciones":4
    }
    index = valueMap[self.name[:-4]]
    context["calIntervalLabel"][index] = (context["calIntervalLabel"][index] - 1) % 10
    context['calInterval'] = sum([context['calIntervalLabel'][i]*10**(4-i) for i in range(5)])
    self.layout.calIntervalLabel.text = f"{context['calInterval']:05.0f} s"

def thermistorSelectButtonAction(self, context):
    thermClicked = self.name[:-6]
    if context[thermClicked]:
        self.label = " "
    else:
        self.label = "X"
    context[thermClicked] = not context[thermClicked]

def channelSelectButtonAction(self, context):
    channelClicked = self.name[:-6]
    oppositeCh = {"ch1Active":"ch2Active", "ch2Active":"ch1Active"}
    if context[channelClicked]:
        self.label = " "
        self.layout.__dict__[oppositeCh[channelClicked]+"Button"].label = "X"
    else:
        self.label = "X"
        self.layout.__dict__[oppositeCh[channelClicked]+"Button"].label = " "
    context[channelClicked] = not context[channelClicked]
    context[oppositeCh[channelClicked]] = not context[oppositeCh[channelClicked]]