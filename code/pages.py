import json
import gc
from contentLayout import Layout
from adafruit_bitmap_font import bitmap_font
from terminalio import FONT
from actions import *

fonts = {
    "terminal": FONT,
    "Helvetica":bitmap_font.load_font("/Helvetica-Bold-16.bdf")
}

gc.collect()

filename = "pages.json"
children = []

with open(filename, 'r') as f:
    data = f.read()
    pageInfo = json.loads(data)
gc.collect()
for name, typography in pageInfo['typography'].items():
    for key, value in typography.items():
        if "font" in key:
            pageInfo['typography'][name][key] = fonts[value]
        if "color" in key or "selected" in key:
            pageInfo['typography'][name][key] = int(value, 16)
gc.collect()
for pageName, page in pageInfo['pages'].items():
    for button in page['buttons']:
        button['typography'] = pageInfo['typography'][button['typography']]
        button['action'] = globals()[button['action']]
    gc.collect()
    for _label in page['labels']:
        _label['typography'] = pageInfo['typography'][_label['typography']]
    gc.collect()
    for index, subLayout in enumerate(page['sublayouts']):
        if subLayout in children:
            raise Exception("Sublayout can't have multiple parents.")
        # page['sublayouts'][index] = pageInfo['pages'][subLayout]
        pageInfo['pages'][subLayout]['parent'] = pageName
        children.append(subLayout)
        gc.collect()
    
for pageName in pageInfo['pages']:
    if pageName not in children:
        pageInfo['pages'][pageName]['parent'] = None
    



        