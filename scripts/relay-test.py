import RPi.GPIO as GPIO # type: ignore
import time

relay_pins = [17, 27, 22, 5, 6]

GPIO.setmode(GPIO.BCM)
for pin in relay_pins:
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)  # Start with relays OFF

try:
    while True:
        for pin in relay_pins:
            GPIO.output(pin, GPIO.LOW)   # Relay ON (active LOW)
            print(f"Relay {pin} ON")
            time.sleep(0.5)
            GPIO.output(pin, GPIO.HIGH)  # Relay OFF
            print(f"Relay {pin} OFF")
            time.sleep(0.5)
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    GPIO.cleanup()
