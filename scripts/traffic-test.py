from gpiozero import LED, TrafficLights
from time import sleep

# Traffic light module
lights = TrafficLights(red=17, amber=27, green=22)

# Pedestrian lights
ped_red1 = LED(24)
ped_green1 = LED(23)
ped_red2 = LED(6)
ped_green2 = LED(5)

try:
    while True:
        print("Phase 1: Cars RED, Pedestrians WALK")
        lights.red.on()
        lights.amber.off()
        lights.green.off()
        ped_red1.off()
        ped_green1.on()
        ped_red2.off()
        ped_green2.on()
        sleep(5)

        print("Phase 1.5: Pedestrian warning")
        ped_green1.blink(on_time=0.5, off_time=0.5, n=5, background=True)
        ped_green2.blink(on_time=0.5, off_time=0.5, n=5, background=False)

        print("Phase 2: Cars GREEN, Pedestrians DON'T WALK")
        lights.red.off()
        lights.amber.off()
        lights.green.on()
        ped_red1.on()
        ped_green1.off()
        ped_red2.on()
        ped_green2.off()
        sleep(5)

        print("Phase 3: Cars YELLOW, Pedestrians DON'T WALK")
        lights.red.off()
        lights.amber.on()
        lights.green.off()
        ped_red1.on()
        ped_green1.off()
        ped_red2.on()
        ped_green2.off()
        sleep(2)

except KeyboardInterrupt:
    print("Stopped by user")
finally:
    lights.off()
    ped_red1.off()
    ped_green1.off()
    print("Lights turned off")
