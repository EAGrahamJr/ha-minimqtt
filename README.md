# ha-minimqtt
HomeAssistant abstraction for use with MQTT. **Specifically** aimed at using [CircuitPython](https://learn.adafruit.com/welcome-to-circuitpython) on microcontrollers with `asyncio` and `minimqtt`, but _should_ be playable on other platforms.

<sup>_Note: I really just wanted an "easy" learning IR remote, but not apparently available open-source._</sup>

* Defines HA _entities_ so that actual MQTT communication is abstracted
* Uses the HA [discovery](https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery) mechanism to register and un-register entities
* Wraps an MQTT client with delegation
  * Swap out clients easier
  * Allows use with things like _asyncio_ without modifying entities
  * Testing!

## How to Use This Library

The [CircuitPython Client](src/ha_minimqtt/cp_mqtt.py) contains a static factory that creates a "wrapper" that can be used with the HA entities.

### Sample `settings.toml`
```toml
CIRCUITPY_WIFI_SSID="MY SSID"
CIRCUITPY_WIFI_PASSWORD="MY PASSWORD"
HAMM_BROKRE="192.168.1.4"

# default values
HAMM_BROKER_PORT = 1883     # int
HAMM_LOOP_SLEEP = 0.1       # seconds as float
HAMM_LOOP_TIMEOUT = 1.0     # seconds as float
HAMM_RECONNECT_DELAY = 5.0  # seconds as float

# if not set, will use CircuitPython defaults
# (really should be set)
HAMM_CLIENT_ID = "my_name"
```
### Sample Code
1. Copy the `utils.py` file to your `CIRCUITPY` drive
2. Copy the appropriate example file to `CIRCUITPY/code.py`
3. Should be running

* [Light Entity](examples/neopixel_light.py) -- listed first because it's the one you're probably looking for
* [Number Entity](examples/simple_number.py)
* [Binary Sensor](examples/esp_button.py)
* [Analog Sensor](examples/analog_tof.py)
* [Select/Options](examples/select_logger.py)
* [Text Entry](examples/text_me.py)

Note that updating handlers/entities "states" via public methods _should_ follow up by **manually** invoking the entity `send_current_state`.

## Design Philosophy

* This is **not** intended to replace [ESPHome](https://esphome.io/), but rather provide an easier _programming_ interface for HA.
* It is primarily intended for the CircuitPython environment, but _should_ (?) work elsewhere.
* * This module is heavily "class-based" as state needs to be preserved and consistent across all the things.
* State should be settable from the system and should be appropriately formatted and "automagically" published to HA where possible.
* Entities that _receive_ from HA should use delegation (e.g. `CommandHandler`) to interface with the other systems.
* Everything is extensible: this is a _start_ -- I do not have all 20+ MQTT entities **currently** supported by HA, so ... have fun?

## Current Status
I _think_ I have the [project](https://github.com/users/EAGrahamJr/projects/3) set up correctly?

## Origin
Since I come from an Object-Oriented and _functional_ background, I originally crafted these classes in [Kotlin](EAGrahamJr/kobots-parts). I ran across a situation where I could _not_ run a JVM, so I turned to the "next easiest thing" that seemed logical and went with Python. And, since I am more familiar with and using [CircuitPython](https://learn.adafruit.com/welcome-to-circuitpython), a conversion of sorts seemed pretty straight-forward.

This is where it got interesting -- I used a couple of different "AI code converters" to migrate the Kotlin code to Python. It was a decent **starting** point, but it is _not_ anywhere near complete, nor does it actually capture the complexities of the _Python_ language. (Throw in `pylint` and you've got a right nightmare.)
