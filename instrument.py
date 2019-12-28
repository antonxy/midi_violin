import jack
from time import sleep
import serial
import threading
import evdev

client = jack.Client('Instrument')

midi_port = client.midi_outports.register('midi_out')

length = 0
vel = 0
run = True

def read_thread():
    global length, run
    with serial.Serial('/dev/ttyUSB0', 115200) as s:
        while run:
            try:
                line = s.readline().decode("utf-8")
            except UnicodeDecodeError:
                continue
            try:
                nums = line.split(' ')
                if len(nums) == 3:
                    length = int(nums[1])
            except ValueError:
                pass

def mouse_thread():
    global run, vel
    device = evdev.InputDevice('/dev/input/by-path/pci-0000:00:14.0-usb-0:1:1.0-event-mouse')
    #device = evdev.InputDevice('/dev/input/mice')
    print(device)
    for event in device.read_loop():
        if not run:
            break
        if event.code == 1 and event.type == 2:
            vel = abs(event.value)

t = threading.Thread(target=read_thread)
t.start()

t2 = threading.Thread(target=mouse_thread)
t2.start()

on = True

current_note = 0
last_velo = 0

@client.set_process_callback
def process(frames):
    global current_note, length, vel, last_velo
    vel = max(0, vel - 0.1)
    note = length // 10 + 40
    velo = last_velo * 0.5 + min(127, abs(vel) * 5) * 0.5
    print(velo)
    midi_port.clear_buffer()
    if note != current_note:
        midi_port.write_midi_event(0, (0x80, current_note, 0))
        midi_port.write_midi_event(0, (0x90, note, int(velo)))
    else:
        # If we set the vel to 0 last time we have to restart the note
        if int(last_velo) == 0:
            midi_port.write_midi_event(0, (0x90, note, int(velo)))
    midi_port.write_midi_event(0, (0xA0, note, int(velo)))

    # Pitch bend
    #midi_port.write_midi_event(0, (0xE0, 0, int(velo)))
    current_note = note 
    last_velo = velo

with client:
    print("#" * 80)
    print("press Return to quit")
    print("#" * 80)
    input()

run = False
