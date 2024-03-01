from machine import Pin, SPI
import os
import sdcard

sd = None
try:
    sd = sdcard.SDCard(SPI(0, sck=Pin(2), mosi=Pin(3), miso=Pin(4)), Pin(1))
except:
    pass
def sdcard_required(method):
    def wrapper(self, *args, **kwargs):
        if self.sd is None:
            print("SD card not initialized or failed to mount.")
            return
        return method(self, *args, **kwargs)
    return wrapper

class Filesystem:
    def __init__(self, sd=sd):
        self.sd = sd
        try:
            os.mount(os.VfsFat(sd), '/sd')
        except:
            print("Failed to mount SD card.")
            pass
    @sdcard_required
    def list_files(self, path):
        return os.listdir(path)
    
    @sdcard_required
    def make(self, path):
        try:
            os.mkdir(f'/{path}')
        except OSError:
            print("Directory already exists")
        os.chdir(os.getcwd() + f'/{path}')

    @sdcard_required   
    def dir_items(self):
        return os.listdir(os.getcwd())

    @sdcard_required
    def delete_files(self):
        for item in self.dir_items():
            mode = os.stat(item)[0]
            if mode == 32768:
                os.remove(os.getcwd() + '/' + item)

    @sdcard_required
    def delete_dirs(self):
        for item in self.dir_items():
            print('DEL ITEM ', item)
            mode = os.stat(item)[0]
            if mode == 16384:
                os.rmdir(f'/{item}')
            

