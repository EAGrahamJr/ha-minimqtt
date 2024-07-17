# How to Use This Library

```python
from ha_minimqtt import CommandHandler,DeviceIdentifier
from ha_minimqtt.mqttwrapper import MQTTClientWrapper
from ha_minimqtt.number import NumberEntity

# define some things
PREFIX = "kobots_ha"
SERVO_ID = "swinger"

wrapper = MQTTClientWrapper()

class ServoHandler(CommandHandler):
    servo = None # like from adafruit_servokit

    def handle_command(self, payload:str):
        self.servo._angle = int(payload)

    def current_state(self):
        return str(self.servo.angle)

identifier = DeviceIdentifier("kobots","QtPy RP2040")
handler = ServoHandler()

# note there is no specific entity class for a thing that swings by degrees
servo_entity = NumberEntity(SERVO_ID,
                            "Swinger",
                            identifier,
                            handler,
                            minimum = 0,
                            maximum = 180,
                            unit_of_measurement = "degrees"
                            )
# and... begin
servo_entity.start(wrapper)
```
