# HiveMind NFC Sign-In Client

The NFC client software allows users to sign in to a cabinet using NFC cards.

This uses two Raspberry Pi Zero W systems, each with buttons and lights and a USB NFC card reader. One of these also connects to the cabinet via Ethernet and runs the stats client.

## Hardware

- [ACR122U USB NFC Reader](https://www.acs.com.hk/en/products/3/acr122u-usb-nfc-reader/) x2
- [Raspberry Pi Zero W](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) x2
- 5V 2A Micro-USB power supply x2
- USB OTG adapter x2
- Ethernet adapter x1
- MicroSD card x2
- Buttons, lights, wires? Todd's stuff

## Wiring

- See [https://pinout.xyz/pinout/io_pi_zero](https://pinout.xyz/pinout/io_pi_zero) for the pin configuration. You will need to connect 12 wires - one power, one ground, and ten GPIO.
- Lights should be connected from a GPIO pin to ground.
- Buttons should be connected from a GPIO pin to power.
- Make note of the pin number of each GPIO pin used. You will need the "Physical/Board" pin number (1-40).
- Do not use pins 27 and 28. These are reserved.

## Operating System Installation

- On one Raspberry Pi, follow the [Client Setup](../CLIENT_SETUP.md) instructions. This one will use the Ethernet adapter and connect to the cabinet itself.
- On the other system, follow the instructions in the **Installing Raspberry Pi OS** and **Wireless Network Configuration** sections.

## Software Installation

```
sudo apt install python3-pip libnfc-dev
python3 -m pip install hivemind_nfc_reader

sudo tee /etc/udev/rules.d/50-usb-perms.rules <<EOF
SUBSYSTEM=="usb", ATTRS{idVendor}=="072f", ATTRS{idProduct}=="2200", GROUP="plugdev", MODE="0660"
EOF

sudo gpasswd -a pi plugdev
sudo gpasswd -a pi gpio
```

- You may need to replace the values for `ATTRS{idVendor}` and `ATTRS{idProduct}` if using a different card reader. Check the output of `lsusb`.

## Configuration File

In your home directory, create a file called `nfc-config.json`. Example contents:

```
{
    "pin_config": [
        { "player_id": 4, "button": 36, "light": 18 },
        { "player_id": 6, "button": 32, "light": 16 },
        { "player_id": 2, "button": 26, "light": 12 },
        { "player_id": 8, "button": 24, "light": 10 },
        { "player_id": 10, "button": 22, "light": 8 }
    ],
    "scene": "<scene name>",
    "cabinet": "<cabinet name>",
    "token": "<token>",
    "reader": "blue",
    "usb_device": "usb:072f:2200",
    "light_mode": "low",
    "button_mode": "high"
}
```

- `token` is on the HiveMind admin page and is the same value used by the stats client's config file.
- `usb_device` is the vendor and product ID of the card reader from the previous section.
- `reader` is `blue` or `gold`.
- `pin_config` should contain one entry per player station:
  - `player_id` is the ID of the station - for example, 2 is Blue Queen. From left to right, these are 4, 6, 2, 8, 10 on the blue side, and 3, 5, 1, 7, 9 on the gold side.
  - `button` and `light` are the pin numbers associated with the button and light for this station.
- `light_mode`: set to "high" if the common wire to the LEDs is on a +5V pin, or "low" if connected to ground.
- `button_mode`: set to "high" if the common wire to the buttons is on a +5V pin, or "low" if connected to ground.

## Run the Client

```
sudo tee /etc/systemd/system/hivemind-nfc-reader.service <<EOF
[Unit]
Description=HiveMind NFC Reader Service

[Service]
ExecStart=/home/pi/nfc-client/venv/bin/python3 /home/pi/.local/bin/hivemind-nfc-reader /home/pi/nfc-config.json
User=pi

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl start hivemind-nfc-reader
sudo systemctl enable hivemind-nfc-reader
```

# Testing Client from PC

To test the client on a PC, you can plug in a USB NFC reader directly to the PC, and use [tkgpio](https://github.com/wallysalami/tkgpio) to simulate the buttons and lights.

```
pip3 install websocket-client==1.2.1 nfcpy==1.0.3 gpiozero==1.6.2 tkgpio==0.1
python3 test.py config.json
```
