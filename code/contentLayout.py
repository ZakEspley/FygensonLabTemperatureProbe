from buttons import BetterButton
import json
class Layout():
    def __init__(self, group, layout, selected, notSelected, startX=0, startY=0):
        self.group = group
        self.layout = layout
        self.x = startX
        self.y = startY
        self.activeButton = None
        if layout is not None:
            self.activeButton = layout[startY][startX]
            self.maxX = len(layout[0])
            self.maxY = len(layout)
        self.selected = selected
        self.notSelected = notSelected
        self.manager = None
        self.parent = None
        self.children = []
        for thing in group:
            if isinstance(thing, BetterButton):
                thing.layout = self
    
    def updateLayout(self, direction):
        if self.layout is not None:
            self.activeButton.outline_color = self.notSelected
            self.activeButton.label_color = self.notSelected
            if direction == "UP":
                self.y = (self.y + 1) % self.maxY
            elif direction == "DOWN":
                self.y = (self.y - 1) % self.maxY
            elif direction == "LEFT":
                self.x = (self.x - 1) % self.maxX
            elif direction == "RIGHT":
                self.x = (self.x + 1) % self.maxX
            
            
            self.activeButton = self.layout[self.y][self.x]
            self.activeButton.outline_color = self.selected
            self.activeButton.label_color = self.selected
    
    def setManager(self, manager):
        self.manager = manager
    
    def setParent(self, parent):
        self.parent = parent
    
    def addChild(self, child):
        self.children.append(child)
        child.parent = self
        child.setManager(self.manager)
    
    def addChildren(self, children):
        for child in children:
            self.addChild(child)
    


class LayoutManager():
    def __init__(self, display, layout, settings):
        # self.layouts = layouts
        # self.activeLayoutIndex = 0
        # self.previousLayoutIndex = 0
        # self.activeLayout = self.layouts[self.activeLayoutIndex]
        self.display = display
        self.activeLayout = layout
        self.settingsFile = settings
        self.readSettings()
        self.displayLayout()
        layout.setManager(self)
        
    
    def subLayout(self, layoutIndex):
        # self.previousLayoutIndex = self.activeLayoutIndex
        # self.activeLayoutIndex = layoutValue
        if len(self.activeLayout.children) != 0:
            self.activeLayout = self.activeLayout.children[layoutIndex]
            self.displayLayout()
    
    def displayLayout(self):
        self.display.show(self.activeLayout.group)

    def parentLayout(self):
        if self.activeLayout.parent is not None:
            self.activeLayout = self.activeLayout.parent
            self.displayLayout()
            self.writeSettings()
    
    def writeSettings(self):
        with open(self.settingsFile, "w") as f:
            temp = self.settings.copy()
            temp.pop("intervalSetting", None)
            temp.pop("durationSetting", None)
            temp.pop('runningFlag', None)
            temp.pop('startTime', None)
            temp.pop('calibrationFlag', None)
            f.write(json.dumps(temp))

    def readSettings(self):
        with open(self.settingsFile, "r") as f:
            data = f.read()
            self.settings = json.loads(data)


if __name__=="__main__":
    pass
        
