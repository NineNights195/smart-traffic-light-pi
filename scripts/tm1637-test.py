import tm1637
from time import sleep

# CLK -> GPIO18, DIO -> GPIO16
display = tm1637.TM1637(clk=18, dio=25)

# Set brightness (0-7)
display.brightness(3)

try:
    # Count from 0 to 9999
    for i in range(10000):
        # Format the number to 4 digits with leading zeros
        display.show(f"{i:04d}")
        sleep(0.5)

except KeyboardInterrupt:
    display.write([0,0,0,0])
    print("Stopped by user")
