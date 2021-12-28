# Supported Devices

In the following table "I" means the sensor is internal to the USB stick and
"E" means the sensor is on a cable that is plugged into the USB stick.

Product    |    Id     |  Firmware       | Temp | Hum | Notes
-----------|-----------|-----------------|------|-----|---------------
TEMPer     | 0c45:7401 | TEMPerF1.4      | I    |     | Metal
TEMPer     | 413d:2107 | TEMPerGold_V3.1 | I    |     | Metal
TEMPer     | 1a86:e025 | TEMPerGold_V3.3 | I    |     | Metal
TEMPerHUM  | 413d:2107 | TEMPerX_V3.1    | I    | I   | White plastic
TEMPer2    | 413d:2107 | TEMPerX_V3.3    | I,E  |     | White plastic
TEMPer1F   | 413d:2107 | TEMPerX_V3.3    | E    |     | White plastic
TEMPerX232 | 1a86:5523 | TEMPerX232_V2.0 | I,E  | I   | White plastic

The 1a86:5523 device may identify as 413d:2107 depending on button presses,
but it cannot be used successfully when in that mode.

If you try other software that uses libusb, the hidraw device may be
disconnected. In this case, remove and re-insert the USB stick.

The TEMPer1F has only an external sensor, but it is not possible to detect
that it is external, so it is reported as an internal temperature.

### TEMPer

This is a metal USB stick marked "TEMPer" with thermometer logo on one side,
and "TEMPer" on the other side. The end opposite the USB connector has a screw
hole. There is *no* humidity detector, but it appears water proof and I have
submerged mine momentarily in ice water and in boiling water.

### TEMPerHUM

This is a white plastic USB stick marked "TEMPerHUM", "-40C - +85C", and
"0-100%RH"; with *blue button* marked "TXT". On the reverse, "PCsensor". This
model does *not* have a jack on the end.

When the button is pressed the red LED will blink as messages of the following
style are sent (the temperature line repeats every second).

```
www.pcsensor.com
temperx v3.1
caps lock:on/off/++
num lock:off/on/--
type:inner-h2
inner-temperinner-humidityinterval
32.73 [c]36.82 [%rh]1s
```
When the button is pressed again, the LED will either be off or be solid red.
This is the mode that meditemp uses.

### TEMPer2

physical description: White plastic USB stick marked "TEMPer2",
"-40C - +125C"; with red button marked "TXT". On the reverse, "PCsensor".
This model has a jack for an external sensor on the end.

notes: When the button is pressed, the red LED will blink as messages
of the following form are sent (the temperature line repeats every
second).

Without an external sensor:
```
www.pcsensor.com
temperx v3.3
caps lock:on/off/++
num lock:off/on/--
type:inner-tx
inner-tempinterval
27.93 [c]1s
```

With an external sensor:
```
www.pcsensor.com
temperx v3.3
caps lock:on/off/++
num lock:off/on/--
type:inner-tx;outer-tx
inner-tempintervalinterval
27.18 [c]29.62 [c]1s
```

This program uses the mode where the LED is either off or solid red.

### TEMPer1F

White plastic USB stick marked "TEMPer1F", "-40C - +125C"; with pink button
marked "TXT'. On the reverse, "PCsensor". This model has a jack for an
external sensor and does *not* have an internal sensor.

When the button is pressed, the red LED will blink as messages
of the following form are sent (the temperature line repeats every 1
second).

Without the probe inserted:
```
www.pcsensor.com
temperx v3.3
caps lock:on/off/++
num lock:off/on/--
type:unknown
1s
```

With the probe inserted:
```
www.pcsensor.com
temperx v3.3
caps lock:on/off/++
num lock:off/on/--
type:outer-tx
outer-tempinterval
24.93 [c]1s
```

This program uses the mode where the LED is either off or solid red.

### TEMPerX232

White plastic USB stick marked "TEMPerX232", "0-100%RH",
and "-40 - +85C"; with a *green button* marked "press". On the reverse,
"PCsensor". On the end opposite the USB connector, there is a jack for an
external temperature sensor (which I do not have and did not try).

When the button is pressed and held down until the red LED is solid, a blue
LED will flash every second. In this mode, the USB vendor:product changes to
413d:2107, but only one HID device is available, and protocol sent to the
hidraw device is rejected with an error.

When the LED is flashing blue, and the button is pressed momentarily,
the following are sent (the temperature line repeats every second).

```
www.PCsensor.com
TEMPerX232-V2.0
type:inner-H2
inner-temperinner-humidityinterval
30.48 [C]40.19 [%RH]1
```

When the button is pressed and held down until the red LED is solid, a green
LED will flash every second. This is the mode temper.py uses. In this mode, if
"Help" is sent to the serial device, the following will be sent back:

```
   >>PCsensor<<
Welcome to use TEMPerX232!
Firmware Version:TEMPerX232_V2.0
The command is:
    ReadTemp                     -->read temperature,temp_value = sensor_value + calibration
    ReadCalib                    -->read calibration
    SetCalib-type:xx.x,xx.x>     -->set calibration, xx.x(-10.0~+10.0)
    EraseFlash                   -->erase calibration
    Version                      -->read firmware version
    ReadType                     -->read the sensor type
    ReadAlert-Temp               -->read temp alert value
    SetTempUpperAlert-type:xx.xx>-->set temp upper alert value,xx.xx(-40.00~+85.00)
    SetTempLowerAlert-type:xx.xx>-->set temp lower alert value,xx.xx(-40.00~+85.00)
    ReadAlert-Hum                -->read hum alert value
    SetHumUpperAlert-type:xx.xx> -->set hum upper alert value,xx.xx(00.00~99.99)
    SetHumLowerAlert-type:xx.xx> -->set hum lower alert value,xx.xx(00.00~99.99)
    SetMode-Temp:x>              -->set tempmode, x(0~1)
    ReadMode-Temp                -->read tempmode
    Help                         -->command help
    ?                            -->command help
The COM configuration is:
    Mode:       ASCII
    Baud Rate:  9600bps
    Data Bit:   8
    Parity Bit: None
    Stop Bit:   1
SHENZHEN RDing Tech CO.,LTD
www.PCsensor.com
```

This is the mode that meditemp uses. Attempts to get this device
to respond to any commands sent via the HID device where not successful.
