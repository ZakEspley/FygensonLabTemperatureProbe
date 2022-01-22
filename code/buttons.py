from adafruit_button import Button
import gc

class BetterButton(Button):
    def __init__(self,action=None, layout=None, name=None, **kwargs):
        self.actionFunction = action
        self.layout = layout
        super(BetterButton, self).__init__(**kwargs)
        self.name = name
        gc.collect()
    
    def action(self, context):
        if self.actionFunction is not None:
            self.actionFunction(self, context)