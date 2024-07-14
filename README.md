# ha-minimqtt
HomeAssistant abstraction for use with minimqtt and asyncio

This library uses class-inheritance to build the basic device and entity classes, delegating to a "wrapped" MQTT client
to handle all the other nastiness.

* All entities (should) provide some sort of "state". This should be settable from the system and will be appropriately
  formatted and published to HA.
* Entities that _receive_ from HA (e.g. `CommandEntity`) also use delegation to interface with the other systems.

For the curious, start with the [base](ha-minimqtt/base.py)

**TODO** I have no clue how to do "traditional" Python packaging, so I guess I'm gonna learn...
