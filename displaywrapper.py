import gc9a01
import sysfont
import smallfont
import medfont
import basefont
from machine import Pin, SPI

cs = Pin(13, Pin.OUT)
reset = Pin(16, Pin.OUT)
dc = Pin(12, Pin.OUT)
display_spi = SPI(1, baudrate=60000000, sck=Pin(10), mosi=Pin(11))

class DisplayWrapper:
    def __init__(self, spi=display_spi, cs=cs, dc=dc, reset=reset):
        self.display = gc9a01.GC9A01(spi, 240, 240, cs=cs, dc=dc, reset=reset)
        self.display.init()
        self.display.fill(0)
        self.height = int(self.display.height())
        self.width = int(self.display.width())
        self.center_x = int(self.width / 2)
        self.center_y = int(self.height / 2)
        self.radius = int(self.width / 2)
        self.green = gc9a01.color565(43, 147, 72)
        self.blue = gc9a01.color565(18, 69, 89)
        self.red = gc9a01.color565(255, 0, 0)
        self.yellow = gc9a01.color565(255, 162, 0)
        self.basefont = basefont
        self.smallfont = smallfont
        self.medfont = medfont

    def fill(self, color=0):
        self.display.fill(color)
        # self.display.rotation(3)
    
    def text(self, font, text, x, y, color):
        self.display.text(font, text, x, y, color)

    def centered_text(self, text, y, color=gc9a01.WHITE, font=smallfont):
        char_width = 8 if font == smallfont else 15
        x = (self.width - len(text) * char_width) // 2
        self.text(font, text, x, y, color)

    def bluetooth_disconnect(self):
            self.display.rect(self.width // 2 - 10, 10, 20, 20, self.red)
            self.display.line(self.width // 2 - 10, 10, self.width // 2 + 10, 30, self.red)
            self.display.line(self.width // 2 + 10, 10, self.width // 2 - 10, 30, self.red)
    
    def fill_rect(self, x, y, width, height, color):
        self.display.fill_rect(x, y, width, height, color)

    def draw_circle(self, color, thickness=1):
        x0 = self.width // 2
        y0 = self.height // 2
        for r in range(self.radius, self.radius - thickness, -1):
            x = r
            y = 0
            err = 0

            while x >= y:
                self.display.pixel(x0 + x, y0 + y, color)
                self.display.pixel(x0 + y, y0 + x, color)
                self.display.pixel(x0 - y, y0 + x, color)
                self.display.pixel(x0 - x, y0 + y, color)
                self.display.pixel(x0 - x, y0 - y, color)
                self.display.pixel(x0 - y, y0 - x, color)
                self.display.pixel(x0 + y, y0 - x, color)
                self.display.pixel(x0 + x, y0 - y, color)

                if err <= 0:
                    y += 1
                    err += 2*y + 1
                if err > 0:
                    x -= 1
                    err -= 2*x + 1
           
    def border(self, color=gc9a01.WHITE, thickness=1):
        # self.display.rect(0, 0, self.width, self.height, color)
        self.draw_circle(gc9a01.BLUE, 3)

    def draw_filled_circle(self, x0, y0, radius, color):
        for y in range(-radius, radius):
            # This is the width of the line to draw on this row
            # It's calculated using the Pythagorean theorem
            line_width = int((radius**2 - y**2)**0.5)
            for x in range(-line_width, line_width):
                self.display.pixel(x0 + x, y0 + y, color)