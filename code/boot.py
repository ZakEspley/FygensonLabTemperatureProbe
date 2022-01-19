import storage
import board
import digitalio


switch = digitalio.DigitalInOut(board.GP19)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

if switch.value:
    storage.remount("/", False)


