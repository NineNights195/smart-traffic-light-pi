import tm1637
import time

# CLK -> GPIO18, DIO -> GPIO16
display = tm1637.TM1637(clk=18, dio=16)

display.brightness(2)

try:
    # Count up 0000 -> 9999
    for i in range(10000):
        display.show(f"{i:04d}")
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopped by user")
    display.show("----")
