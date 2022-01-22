import displayio
import json
import gc
from buttons import BetterButton
from adafruit_display_text import label

class Layout():
    def __init__(self, pageInfo, manager):
        self.group = displayio.Group()
        gc.collect()
        self.manager = manager
        self.parent = pageInfo['parent']
        buttons = pageInfo['buttons']
        labels = pageInfo["labels"]
        layout = pageInfo['layout']
        self.children = pageInfo['sublayouts']
        for _label in labels:
            labelInst = label.Label(
                anchored_position=_label['position'],
                anchor_point=(0,0),
                text=_label['text'],
                **_label['typography']
            )
            setattr(self, _label['name'], labelInst)
            gc.collect()
            self.group.append(self.__dict__[_label['name']])
        for button in buttons:
            # print(f"AddingButton: {button['name']} -- {gc.mem_free()}")
            buttonInst = BetterButton(
                x=button['position'][0],
                y=button['position'][1],
                width=button['dimensions'][0],
                height=button['dimensions'][1],
                label=button['label'],
                style=BetterButton.ROUNDRECT,
                action=button['action'],
                layout=self,
                name=button['name'],
                **button['typography'],
            )
            setattr(self, button['name'], buttonInst)
            gc.collect()
            self.group.append(self.__dict__[button['name']])
            if button["active"]:
                self.activeButton = self.__dict__[button['name']]
                self.activeButton.selected = True
            gc.collect()
            # print(f"Mem after -- {gc.mem_free()}")
        

        self.layout = []
        for i, row in enumerate(layout):
            tmp = []
            for j, buttonName in enumerate(row):
                tmp.append(self.__dict__[buttonName])
                gc.collect()
                if self.__dict__[buttonName] == self.activeButton:
                    self.y = i
                    self.x = j
            self.layout.append(tmp)
            gc.collect()
        self.maxX = len(layout[0])
        self.maxY = len(layout)
    
    def updateLayout(self, direction):
        if self.layout is not None:
            self.activeButton.selected = False
            if direction == "UP":
                self.y = (self.y + 1) % self.maxY
            elif direction == "DOWN":
                self.y = (self.y - 1) % self.maxY
            elif direction == "LEFT":
                self.x = (self.x - 1) % self.maxX
            elif direction == "RIGHT":
                self.x = (self.x + 1) % self.maxX
            
            self.activeButton = self.layout[self.y][self.x]
            self.activeButton.selected = True
            gc.collect()
    
    def setManager(self, manager):
        self.manager = manager
        # for child in self.children:
        #     child.setManager(manager)
        gc.collect()
    
    def setParent(self, parent):
        self.parent = parent
        gc.collect()
    
    # def addChild(self, child):
    #     self.children.append(child)
    #     child.parent = self
    #     gc.collect()
    #     # child.setManager(self.manager)
    
    # def addChildren(self, children):
    #     for child in children:
    #         self.addChild(child)
    #     gc.collect()

    
class LayoutManager():
    def __init__(self, display, pages, activePageName, settings):
        # self.layouts = layouts
        # self.activeLayoutIndex = 0
        # self.previousLayoutIndex = 0
        # self.activeLayout = self.layouts[self.activeLayoutIndex]
        self.display = display
        self.settingsFile = settings
        self.pages = pages
        self.activePage = self.pages[activePageName]
        self.activeLayout = None
        # self.activeLayout = makePage(self.activePage)
        self.readSettings()
        self.displayLayout()
        # self.activeLayout.setManager(self)
        
    def subLayout(self, layoutIndex):
        if len(self.activePage['sublayouts']) != 0:
            self.activePage = self.pages[self.activePage['sublayouts'][layoutIndex]]
            self.displayLayout()
    
    def displayLayout(self):
        self.makePage()
        self.display.show(self.activeLayout.group)

    def parentLayout(self):
        if self.activePage['parent'] is not None:
            self.activePage = self.pages[self.activePage['parent']]
            self.displayLayout()
        self.writeSettings()
    
    def writeSettings(self):
        with open(self.settingsFile, "w") as f:
            temp = self.settings.copy()
            temp.pop("intervalSetting", None)
            temp.pop("durationSetting", None)
            temp.pop('runningFlag', None)
            temp.pop('startTime', None)
            f.write(json.dumps(temp))
        gc.collect()

    def readSettings(self):
        with open(self.settingsFile, "r") as f:
            data = f.read()
            self.settings = json.loads(data)
        gc.collect()
    
    def makePage(self):
        if self.activeLayout is not None:
            del self.activeLayout
            gc.collect()
        self.activeLayout = Layout(self.activePage, self)
        # self.activeLayout.setManager(self)

if __name__=="__main__":
    pass
        
