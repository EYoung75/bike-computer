import random
import bluetooth
import aioble
import uasyncio as asyncio
import struct
from machine import Pin, SPI
import time
import sdcard
import filesystem
import os
import ubinascii
import math
import gc
import displaywrapper

# Hardware Initialization
display = displaywrapper.DisplayWrapper()

# Breadboard buttons
# left = Pin(22, Pin.IN, Pin.PULL_UP)
# center = Pin(21, Pin.IN, Pin.PULL_UP)
# right = Pin(20, Pin.IN, Pin.PULL_UP)

# Proto buttons
left = Pin(16, Pin.IN, Pin.PULL_UP)
center = Pin(14, Pin.IN, Pin.PULL_UP)
right = Pin(15, Pin.IN, Pin.PULL_UP)

fs = filesystem.Filesystem()
try:
    fs = filesystem.Filesystem()
except OSError as e:
    print('SD CARD ERROR', e)
    print('Mounted already')

print(fs.sd)
os.chdir('/sd')
# os.mkdir('/test')
index = 0
while len(fs.dir_items()):
    print('enum', index, os.getcwd(), os.listdir(os.getcwd()), fs.dir_items())
    try:
        os.rmdir('sd')
    except:
        print('oops')
        pass
    fs.make('sd')
    # fs.delete_dirs()
    # os.chdir(os.getcwd() + '/sd')
    index+=1
    time.sleep(1)

# fs.make('sd')
# fs.delete_dirs()
# fs.delete_files()
print("FS ", fs.dir_items())
print("OS " , os.getcwd())
# fs.make('sd')
# print('LIST DIR', fs.dir_items())

# fs.make('rides')

# print('LIST DIR after', os.getcwd())

# print("CWD ", fs.dir_items())
# time.sleep(4000)

# os.mkdir('/rides')
# Get a list of all files in the current directory
files = os.listdir(os.getcwd())

# for filename in files:
#     print('FILENAME ', filename)
#     mode = os.stat(filename)[0]
#     print('PATH ', mode)
#     if mode == 32768:  # This is a file
#         print('FILE ', filename)
#         os.remove(os.getcwd() + '/' + filename)
#     elif mode == 16384:  # This is a directory
#         print('DIR ', filename)
#         # os.rmdir(filename)
#         continue

rides = os.listdir(os.getcwd())
# for ride in rides:
#     os.remove(ride)
    # print(rides)
print('CLEARED', rides)
# for ride in rides:
#     print('RIDE ', ride)
#     with open(ride, 'r') as f:
#         print(f.read())

    
def delete_directory(directory):
    print('ENTER ', os.listdir(directory))
    for filename in os.listdir(directory):
        file_path = directory + '/' + filename[0]
        print('FILE PATH ', file_path)
        # if filename[1] == 0x8000:  # This is a file
        #     os.remove(file_path)
        # elif filename[1] == 0x4000:  # This is a directory
        #     delete_directory(file_path)
    os.rmdir(directory)
# To list files on the SD card
# delete_directory('/sd')
# time.sleep(4000)

# print('should be deleted')
# with open('/sd/rides/hello.txt', 'r') as f:
#     print(f.read())


# Save ride duration, distance, speed, cadence


start_time = time.ticks_ms()
power = 0
cadence = 0

connected = False
alive = False
connection = None
skip_connection = False


def generate_uid():
    random_number = random.getrandbits(32)
    return '{:x}'.format(random_number) 

async def find_meter():
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if(result.name() != None):
                print('found device:', result.name())
            if result.name() == '43494' or result.name() == 'PicoBLE':
                # print('Found Forerunner 935', result.services())
                for service in result.services():
                        print('Service:', service)
                # print('rssi()', result.rssi)
                print('returning ', result.name())
                return result.device
        return None
def bluetooth_screen():
    display.fill(0)
    display.centered_text("Searching...", 100, display.yellow, display.basefont)
    display.centered_text("Hold 'Right' to skip", 140, display.yellow, display.smallfont)
    display.draw_circle(display.blue, 3)


async def handle_bluetooth():
    print('Starting peripheral task')
    bluetooth_screen()
    global connected, connection, current_ctx, skip_connection, next_ctx
    connected = False
    device = await find_meter()
    if right.value() == 0:
        skip_connection = True
        print('RIGHT')
        return
    if not skip_connection:
        if not device:
            print('No device found')
            return
        try:
            print('Connecting to ', device) # <DeviceConnection>
            connection_object = await device.connect()
            print('COnnected successful', connection_object)
        except asyncio.TimeoutError:
            print('Connection failed')
            return
        connected = True
        connection = connection_object
        next_ctx = contexts["main"]

def ride():
    display.fill(0)
    display.border(display.blue, 3)
    display.text(display.smallfont, f"POWER:", 70, 60, display.yellow)
    display.text(display.basefont, f"{power}W", 70, 70, display.blue)
    display.text(display.smallfont, f"CADENCE:", 70, 110, display.yellow)
    display.text(display.basefont, f"90RPM", 70, 120, display.blue)
    display.centered_text("2/20", 20, 31797, display.smallfont)
    display.centered_text("1:45:23", 180, display.green, display.medfont)

def workout():
    print('RIDE')
    display.fill(0)
    display.text(display.basefont, f"Select workout", 10, 100, 31797)

def pair():
    print('PAIR')
    display.fill(0)
    display.text(display.basefont, f"PAIR", 10, 100, 31797)
def history():
    print('HISTORY')
    display.fill(0)
    display.text(display.basefont, f"HISTORY", 10, 100, 31797)

highlightedOption = 0



def draw_menu(options):
    display.fill(0)
    display.border()
    global highlightedOption, connected
    for index, value in enumerate(options):
        display.text(display.basefont, f"{value['label']} {'<' if index == highlightedOption else ''}", 45 if index == highlightedOption else 50, 60 + index * 32, display.yellow if index == highlightedOption else display.blue)
        if not connected:
            display.bluetooth_disconnect()
    

def navigate(target):
    global next_ctx
    next_ctx = target
def pauseRide():
    print('PAUSE RIDE')
def cycleData():
    print('CYCLE DATA')


connected = False


current_ctx = None
next_ctx = None
data = {
    "power": [],
    "cadence": []
}

async def command_handler():
    global current_ctx
    print('COMMAND HANDLER CURRENT ',  current_ctx)
    actions = current_ctx["actions"]
    while True:
        if left.value() == 0:
            print('left')
            actions["left"]()
        if right.value() == 0:
            print('right')
            actions["right"]()
        if center.value() == 0:
            print('center')
            actions["center"]()

        await asyncio.sleep_ms(150)
        
async def update_menu():
    while True:
        # print('UPDATING MENU')
        await asyncio.sleep_ms(150)

def render_menu():
    global current_ctx, connected
    display.fill(0)
    display.border()
    for index, value in enumerate(current_ctx["menu"]):
        display.text(display.basefont, f"{value['label']} {'<' if index == current_ctx['cur_index'] else ''}", 45 if index == current_ctx['cur_index'] else 50, 60 + index * 32, display.yellow if index == current_ctx['cur_index'] else display.blue)
        if not connected:
            display.bluetooth_disconnect()


def scroll_menu(dir="down"):
    print('SCROLL')
    global current_ctx
    current_ctx["cur_index"] = (current_ctx["cur_index"] + 1 if dir == 'down' else current_ctx["cur_index"] - 1) % len(current_ctx["menu"])
    render_menu()

def navigate(target):
    global next_ctx
    display.fill(0)
    display.border()
    next_ctx = contexts[target]

def select():
    global current_ctx, next_ctx
    # current_ctx = contexts[current_ctx["menu"][current_ctx["cur_index"]]["target"]]
    print('SELECTED', current_ctx["menu"][current_ctx["cur_index"]]["target"])
    target_ctx = current_ctx["menu"][current_ctx["cur_index"]]["target"]
    current_ctx["cur_index"] = 0
    next_ctx = contexts[target_ctx]
    # print('SHOULD BE CTX', next_ctx)
time_elapsed = None
cur_power = '-'
cur_cadence = '-'
ride_data = []
# previous_crank_event_time = 0
# previous_cumulative_crank_revolutions = None
initial_revolutions = None
paused = False

def rideLeft():
    global paused
    if paused:
        print('STOPPED from ride')
        navigate('ride_summary')
    print('LEFT from ride')

def rideCenter():
    global paused
    paused = not paused

def rideRight():
    print('RIGHT from ride')


def format_time(elapsed_seconds):
    hours, remainder = divmod(elapsed_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"


def update_ride_screen():
    global time_elapsed, cur_power, cur_cadence, paused
    if paused:
        display.text(display.basefont, f"-W", 70, 70, display.blue)
        display.text(display.basefont, f"-RPM", 70, 120, display.blue)
        formatted_time = format_time(time_elapsed)
        display.centered_text("PAUSED", 170, display.red, display.smallfont)
        display.centered_text(f"{formatted_time}", 180, display.red, display.medfont)
    else:
        # Clear and redraw the power value
        display.fill_rect(70, 70, 100, 30, 0)  
        display.text(display.basefont, f"{cur_power}W", 70, 70, display.blue)

        # Clear and redraw the cadence value
        display.fill_rect(70, 120, 100, 30, 0)  
        display.text(display.basefont, f"{cur_cadence}RPM", 70, 120, display.blue)

        # Clear and redraw the time elapsed
        display.fill_rect(180, 180, 100, 30, 0)  
        display.fill_rect(57, 167, 130, 48, 0)

        formatted_time = format_time(time_elapsed)
        display.centered_text(f"{formatted_time}", 180, display.green, display.medfont)
async def receive_data():
    global cur_power, cur_cadence, connection, paused
    previous_crank_time = None
    previous_crank_revs = None

    async with connection:
        print('CONNECTION ', connection)
        PWR_UUID = bluetooth.UUID(0x1818)
        power_service = await connection.service(PWR_UUID)
        print('POWER SERVICE ', power_service)
        characteristic = await power_service.characteristic(bluetooth.UUID(0x2a63))
        print('POWER CHAR ', characteristic)
        # print('GOT CHAR ', characteristic)
        await characteristic.subscribe(notify=True)
        running_total_power = 0
        running_total_cadence = 0
        iterations = 0
        while True:
            data = await characteristic.notified()
            flags, instantaneous_power = struct.unpack('<HH', data[:4])
            cur_power = instantaneous_power
            torque = None
            index = 4
            parsed_data = {'instantaneous_power': instantaneous_power}
            # Power Balance
            if flags & (1 << 0):
                parsed_data['power_balance'] = struct.unpack('<B', data[index:index + 1])[0]
                index += 1
            # if flags & (1 << 1):
            #     parsed_data['power_balance_reference'] = 'left' if flags & (1 << 1) else 'right'
            
            if flags & (1 << 2):
                torque = struct.unpack('<H', data[index:index + 2])[0]
                parsed_data['accumulated_torque'] = torque
                index += 2            
            # if flags & (1 << 3):
            #     parsed_data['accumulated_torque_source'] = 'crank' if flags & (1 << 3) else 'wheel'
                
            if flags & (1 << 4):
                parsed_data['cumulative_wheel_revs'] = struct.unpack('<I', data[index:index + 4])[0]
                index += 4
                parsed_data['last_wheel_event_time'] = struct.unpack('<H', data[index:index + 2])[0] / 1024
                index += 2
            # Crank Revolutions
            if flags & (1 << 5):
                current_crank_revolutions = struct.unpack('<H', data[index:index + 2])[0]
                parsed_data['cumulative_crank_revs'] = current_crank_revolutions
                index += 2
                current_crank_time = struct.unpack('<H', data[index:index + 2])[0] / 1024
                parsed_data['current_crank_time'] = current_crank_time
                index += 2

                if previous_crank_revs is not None and previous_crank_time is not None and previous_crank_time != current_crank_time:
                    # Calculate the cadence
                    delta_revs = current_crank_revolutions - previous_crank_revs
                    delta_time = current_crank_time - previous_crank_time

                    # Account for possible rollover
                    if delta_time < 0:
                        delta_time += 65536  # 64 seconds in 1/1024 second units
                    print('DELTA TIME ', delta_time)
                    # Convert time to seconds and calculate cadence
                    time_seconds = delta_time
                    print('TIME SECONDS ', time_seconds)
                    print('Without multiplier ', delta_revs / time_seconds)
                    if time_seconds > 0:
                        cur_cadence = round((delta_revs / time_seconds) * 60)
                        running_total_cadence += cur_cadence
                    else:
                        cur_cadence = 0
                # else:
                #     cur_cadence = 0
                ride_data.append({})
                # Update the previous crank data
                previous_crank_revs = current_crank_revolutions
                previous_crank_time = current_crank_time
                parsed_data['cumulative_crank_revs'] = current_crank_revolutions
                parsed_data['last_crank_event_time'] = current_crank_time / 1024
                running_total_power += instantaneous_power or 0
                iterations += 1
                running_average_power = running_total_power / iterations
                running_average_cadence = running_total_cadence / iterations
                formatted_data = {'time': time_elapsed, 'power': cur_power, 'cadence': cur_cadence, 'torque': torque, 'running_average_power': running_average_power, 'running_average_cadence': running_average_cadence}
                ride_data.append(formatted_data)
            print('PARSED DATA ', parsed_data)
                
    
async def start_timer():
    start_time = time.ticks_ms()
    paused_time = 0
    # display.fill(0)
    global time_elapsed, cur_power, cur_cadence, connection, paused
    while True:
        if paused:
            paused_start = time.ticks_ms()
            while paused:
                display.fill_rect(70, 70, 100, 30, 0)  
                display.fill_rect(70, 120, 100, 30, 0)  
                display.fill_rect(57, 167, 130, 48, 0)
                await asyncio.sleep(.5)
                update_ride_screen()
                await asyncio.sleep(.5)
            paused_time += time.ticks_diff(time.ticks_ms(), paused_start)
            print('PAUSED TIME ', paused_time)
        else:
            time_elapsed = (time.ticks_diff(time.ticks_ms(), start_time) - paused_time) // 1000
            update_ride_screen()
            await asyncio.sleep(1)

def mkdir_p(path):
    dirs = path.split('/')
    if dirs[0] == '':
        dirs[0] = '/'
    print('DIRS ', dirs)
    while dirs and not os.listdir(dirs[0]):
        try:
            os.mkdir(dirs[0])
        except OSError:
            print('err ', e)
            pass
        dirs.pop(0)
# showSummary()
# os.chdir('/sd')
# os.chdir('/rides')
# Remove all files in the rides directory

# print('CURR DIR', os.getcwd())
# rides = os.listdir(os.getcwd())
# for ride in rides:
#     os.remove(ride)
# print('CLEARED', rides)
# for ride in rides:
#     print('RIDE ', ride)
#     with open(ride, 'r') as f:
#         print(f.read())
# time.sleep(4000)
def saveRide(data):
    print('SAVING RIDE')
    display.fill(0)
    display.border()
    display.centered_text("SAVING RIDE DATA...", 100, display.yellow, display.medfont)
    uid = generate_uid()
    os.chdir('/sd')
    print('CURR DIR', os.getcwd())
    print(os.listdir(os.getcwd()))
    try:
        os.mkdir('/rides')
    except OSError as e:
        pass
    os.chdir('/rides')

    print('NEW', os.getcwd())
    print(os.listdir(os.getcwd()))
    # os.chdir('/rides')
    print('NEW', os.getcwd())

    directory = '/rides/'
    filename = f'{directory}{uid}.csv'
    mkdir_p(directory)

    with open(filename, 'w') as f:
        f.write(','.join(data[0].keys()) + '\n')
        # Write the data
        for row in data:
            f.write(','.join(str(value) for value in row.values()) + '\n')
        # print(f.read())
    with open(filename, 'r') as f:
        print(f.read())

async def summary_handler():
    global ride_data
    index = 0
    start = 0  # The index of the first data point currently being displayed
    update = True
    base_metric = ride_data[-1]
    hours, remainder = divmod(time_elapsed, 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_time =  '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
    data_points = [{'name': 'AVG POWER', 'value': base_metric['power']}, {'name': 'AVG CADENCE', 'value': base_metric['cadence']}, {'name': 'DISTANCE', 'value': '-MI'}, {'name': 'DURATION', 'value': formatted_time}, {'name': 'AVG SPEED', 'value': '-MPH'}]

    while True:
        if left.value() == 0:
            print('left')
            start = max(0, start - 1)  # Scroll up, but don't go past the first data point
            update = True
        if right.value() == 0:
            print('right')
            start = min(len(data_points) - 3, start + 1)  # Scroll down, but don't go past the last data point
            update = True
        if center.value() == 0:
            saveRide(ride_data)
        if update:
            print('INDEX ', index)
            print('START ', start)
            display.fill(0)  # Clear the display
            num_presses = math.ceil(len(data_points) / 3.0) + 1
            display.centered_text("SUMMARY", 20, display.yellow, display.smallfont)
            for i in range(start, min(start + 3, len(data_points))):  # Display three data points at a time
                point = data_points[i]
                display.text(display.smallfont, f"{point['name']}", 50, 50 + (i - start) * 50, display.yellow)
                display.text(display.medfont, f"{point['value']}", 40, 60 + (i - start) * 50, display.blue)   
                    # Draw a filled in circle
            for j in range(num_presses):  # Draw three dots
                print('J ', j)
                display.draw_filled_circle(20, 100 + j * 20, 5, display.green if j == start else display.blue)  

            update = False
        await asyncio.sleep_ms(150)

# asyncio.run(summary_handler())
# time.sleep(4000)
def startRide():
    print('STATR RIDE')
    global next_ctx
    display.fill(0)
    display.text(display.smallfont, f"POWER:", 70, 60, display.yellow)
    display.text(display.smallfont, f"CADENCE:", 70, 110, display.yellow)
    # display.centered_text("2/20", 20, 31797, display.smallfont)
    display.border()
    next_ctx = contexts["ride"]

def goBack():
    global next_ctx
    next_ctx = contexts["main"]
    # draw_menu(screens["main"]["menu"])
def initRide():
    display.fill(0)
    display.border()
    display.centered_text("PRESS", 70, display.yellow, display.medfont)
    display.centered_text("RIGHT TO", 100, display.yellow, display.medfont)
    display.centered_text("START RIDE", 130, display.yellow, display.medfont)

def skip_bluetooth():
    global skip_connection
    skip_connection = True
    print('SKIPPING')

def textScroll(dir = 'down'):
    print('scrolling data')

def showSummary():
    display.fill(0)
    display.border()
    display.centered_text("RIDE", 15, display.yellow, display.smallfont)
    display.centered_text("SUMMARY", 30, display.yellow, display.smallfont)
    display.text(display.smallfont, f"AVG POWER", 40, 50, display.red)
    display.text(display.medfont, f"175W", 30, 65, display.blue)
    display.text(display.smallfont, f"AVG CADENCE", 20, 110, display.red)
    display.text(display.sysfont, f"90RPM", 25, 125, display.blue)
    display.text(display.smallfont, f"DISTANCE", 40, 160, display.red)
    display.text(display.medfont, f"15.3 MI", 50, 175, display.blue)

async def history_browser():
    display.fill(0)
    os.chdir('/sd')
    os.chdir('/rides')
    os.listdir(os.getcwd())
    print('CURR DIR', os.getcwd())
    files = os.listdir(os.getcwd())
    for i, file in enumerate(files):
        print('FILE ', file.replace('.csv', ''))
        display.centered_text(f"{file.replace('.csv', '')}", 20 + i * 20, 31797, display.smallfont)
        # display.text(display.smallfont, f"{file.replace('.csv', '')}", 50, 20 + i * 20, 31797)
        # with open(file, 'r') as f:
        #     print(f.read())
        # await asyncio.sleep(.2)


# This handles the structure for the menu and navigation of the application.
# Each context resembles a screen or a state of the application and has the following characteristics:
        # 1) If it is navigable and has sub menus, it will have a "cur_index" for tracking highlighted
        # options for selection, and well as a corresponding "menu" list for the further navigation options.
        # Option objects within this list will have an "label" key for the label of the option, an "action" key corresponding
        # to the function that should execute when the option is selected, and a "target" key for the next context to navigate to.
        # 2) an "entry" list for functions that should execute when the context is entered
        # 3) a "tasks" list for async functions that should run in the background while the context is active
        # 4) an "actions" object for mapping the physical buttons to actions that should execute when the buttons are pressed in this context.
contexts = {
    "main": {
        "cur_index": 0,
        "tasks": [
            command_handler,
            update_menu
        ],
        "entry": [
            display.border,
        ],
        "menu": [
            {"label": "RIDE", "action": ride, "target": "start_ride"},
            {"label": "WORKOUT", "action": workout, "target": "workout"},
            {"label": "PAIR", "action": pair, "target": "pair"},
            {"label": "HISTORY", "action": history, "target": "history"}
        ],
        "actions": {
            "left": lambda: scroll_menu('up'),
            "center": select,
            "right": lambda: scroll_menu('down'),
        }
    },
    "start_ride": {
        "entry": [
            initRide
        ],
        "tasks": [
            command_handler
        ],
        "actions": {
            "left": goBack,
            "center": goBack,
            "right": startRide
        }
    },
    "ride": {
        "tasks": [
            start_timer,
            receive_data,
            command_handler
        ],
        "actions": {
            "left": rideLeft,
            "center": rideCenter,
            "right": rideRight
        }
    },
    "workout": {
        "cur_index": 0,
        "menu": [
            {"label": "SHOWOO", "action": ride, "target": "ride"},
            {"label": "BAKOO", "action": workout, "target": "main"},
            {"label": "SDFHIH", "action": pair, "target": "main"},
            {"label": "NSDFK", "action": history, "target": "main"}
        ],
        "tasks": [command_handler],
        "entry": [render_menu],
        "actions": {
            "left": goBack,
            "center": select,
            "right": lambda: scroll_menu('down'),
        }
    },
    "init": {
        "entry": [
            bluetooth_screen
        ],
        "tasks": [
            handle_bluetooth,
            command_handler
        ],
         "actions": {
            "left": skip_bluetooth,
            "center": skip_bluetooth,
            "right": skip_bluetooth,
        }
    },
    "ride_summary": {
        # "entry": [
        #     showSummary
        # ],
        "tasks": [
            summary_handler,
            # command_handler
        ],
        "actions": {
            "left": lambda: textScroll('up'),
            "center": saveRide,
            "right": lambda: textScroll('up')
        }
    
    },
    "history": {
        "tasks": [
            history_browser
        ]
    }
}

gc.collect()
async def main_loop():
    while True:
        global current_ctx, next_ctx, connected, skip_connection
        # Either enter bluetooth scan or main loop
        if not skip_connection and not connected:
            bluetooth_screen()
            await handle_bluetooth()
        else:
            draw_menu(contexts["main"]["menu"])
            current_ctx = None
            tasks = []
            # Main loop works like this:
            # Set the intial value for the next context to be the main screen.
            # If the next context is different from the current context, cancel
            # all of the current running tasks from the current context and
            # start new async tasks for the new context. Additionally, execute
            # any entry functions for the new context. Entry functions handle things
            # like rendering the initial screen for a context.
            next_ctx = contexts["main"]
            while True:
                global current_ctx, next_ctx, connected, skip_connection
                if next_ctx != current_ctx:
                    try:
                        if len(tasks) > 0:
                            for task in tasks:
                                task.cancel()
                                print('CANCELLED')
                            tasks = []
                            print('BEFORE ', gc.mem_free())
                            gc.collect()
                            print('AFTER ', gc.mem_free())

                    except:
                        print('Task threw an exception on exit')
                    # tasks = []
                    current_ctx = next_ctx
                    if "tasks" in current_ctx:
                        for task in current_ctx["tasks"]:
                            tasks.append(asyncio.create_task(task()))
                    if "entry" in current_ctx:
                        for entry in current_ctx["entry"]:
                            entry()
                await asyncio.sleep_ms(150)
            await asyncio.gather(*tasks)  
while True:
    asyncio.run(main_loop())

