# ha-minimqtt
HomeAssistant abstraction for use with MQTT. **Specifically** aimed at using [CircuitPython](https://learn.adafruit.com/welcome-to-circuitpython) on microcontrollers with `asyncio` and `minimqtt`, but _should_ be playable on other platforms.

* Defines HA _entities_ so that actual MQTT communication is abstracted
* Uses the HA [discovery](https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery) mechanism to register and un-register entities
* Wraps an MQTT client with delegation
  * Swap out clients easier
  * Allows use with things like _asyncio_ without modifying entities
  * Testing!

## How to Use This Library

### Sample `settings.toml`
```toml
CIRCUITPY_WIFI_SSID="MY SSID"
CIRCUITPY_WIFI_PASSWORD="MY PASSWORD"
HAMM_BROKRE="192.168.1.4"

# default values
HAMM_BROKER_PORT = 1883     # int
HAMM_LOOP_SLEEP = 1.0       # seconds as float
HAMM_LOOP_TIMEOUT = 1.0     # seconds as float
HAMM_RECONNECT_DELAY = 5.0  # seconds as float
```
### Sample Code
* [NumberEntity](examples/simple_number.py)

## Design Philosophy
This module is heavily "class-based" as state needs to be preserved and consistent across all the things.

* All entities (should) provide some sort of "state". This should be settable from the system and will be appropriately formatted and published to HA.
* Entities that _receive_ from HA (e.g. `CommandEntity`) also use delegation to interface with the other systems.
* Everything is extensible: this is a _start_ -- I do not have all 20+ MQTT entities **currently** supported by HA, so ... have fun?

## Current Status
I _think_ I have the [project](https://github.com/users/EAGrahamJr/projects/3) set up correctly?

* Most of the basic code is written for the HA entities, but not tested
* Need to determine what's on a micro and what's not (see [_compatibility](src/ha_minimqtt/_compatibility.py) - h/t @elpekenin)
* `pylint` and `black` are being run manually
* Figure out how to unit test (that's why the decorator:bangbang:)
* Publish docs?
* Either add to Adafruit community bundle(s) or publish to PyPi

## Origin
Since I come from an Object-Oriented and _functional_ background, I originally crafted these classes in [Kotlin](EAGrahamJr/kobots-parts). I ran across a situation where I could _not_ run a JVM, so I turned to the "next easiest thing" that seemed logical and went with Python. And, since I am more familiar with and using [CircuitPython](https://learn.adafruit.com/welcome-to-circuitpython), a conversion of sorts seemed pretty straight-forward.

This is where it got interesting -- I used a couple of different "AI code converters" to migrate the Kotlin code to Python. It was a decent **starting** point, but it is _not_ anywhere near complete, nor does it actually capture the complexities of the _Python_ language. (Throw in `pylint` and you've got a right nightmare.)
