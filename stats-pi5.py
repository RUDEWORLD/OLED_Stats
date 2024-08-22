import time
import gpiod
import subprocess
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import board
import busio

# Configure the GPIO chip and the reset pin line
chip = gpiod.Chip('gpiochip0')
reset_line = chip.get_line(4)  # corresponds to GPIO4 (D4 on the Raspberry Pi)

# Request the line as output
reset_line.request(consumer="oled_reset", type=gpiod.LINE_REQ_DIR_OUT)

# Set the reset pin to low and then high to reset the display
reset_line.set_value(0)
time.sleep(0.1)
reset_line.set_value(1)

# Display Parameters
WIDTH = 128
HEIGHT = 64
BORDER = 5

# Display Refresh interval
LOOPTIME = 1.0

# Initialize I2C
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=None)

# Clear the display
oled.fill(0)
oled.show()

# Create a blank image for drawing
image = Image.new("1", (oled.width, oled.height))

# Get the drawing object to draw on the image
draw = ImageDraw.Draw(image)

# Draw a white background
draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

# Load the font
font = ImageFont.truetype('PixelOperator.ttf', 16)

while True:

    # Draw a black filled box to clear the image
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

    # Execute system commands to get Raspberry Pi stats
    cmd = "hostname -I | cut -d\' \' -f1"
    IP = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
    cmd = "top -bn1 | grep load | awk '{printf \"CPU: %.2f\", $(NF-2)}'"
    CPU = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
    Disk = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
    cmd = "vcgencmd measure_temp |cut -f 2 -d '='"
    Temp = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

    # Display Raspberry Pi stats on the OLED
    draw.text((0, 0), "IP: " + IP, font=font, fill=255)
    draw.text((0, 16), CPU + " LA", font=font, fill=255)
    draw.text((80, 16), Temp, font=font, fill=255)
    draw.text((0, 32), MemUsage, font=font, fill=255)
    draw.text((0, 48), Disk, font=font, fill=255)

    # Display the image on the OLED
    oled.image(image)
    oled.show()
    time.sleep(LOOPTIME)