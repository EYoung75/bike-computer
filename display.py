import gc9a01
from machine import Pin, SPI

display_spi = SPI(1, baudrate=60000000, sck=Pin(10), mosi=Pin(11))
class Display:
    def __init__(self, spi, cs, dc, rst):
        self.display = gc9a01.GC9A01(spi, cs, dc, rst)
        self.display.init()
        self.display.fill(0)
        self.display.rotation(3)