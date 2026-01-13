from tkgpio import TkCircuit

import hivemind_nfc_reader

config = {
    "width": 600,
    "height": 100,
    "leds": [
        {"x": 50, "y": 25, "name": "ST_LED", "pin": "BOARD21"},
        {"x": 150, "y": 25, "name": "AB_LED", "pin": "BOARD16"},
        {"x": 250, "y": 25, "name": "QN_LED", "pin": "BOARD18"},
        {"x": 350, "y": 25, "name": "SK_LED", "pin": "BOARD15"},
        {"x": 450, "y": 25, "name": "CX_LED", "pin": "BOARD23"},
    ],
    "buttons": [
        {"x": 50, "y": 75, "name": "ST_BTN", "pin": "BOARD22"},
        {"x": 150, "y": 75, "name": "AB_BTN", "pin": "BOARD12"},
        {"x": 250, "y": 75, "name": "QN_BTN", "pin": "BOARD19"},
        {"x": 350, "y": 75, "name": "SK_BTN", "pin": "BOARD13"},
        {"x": 450, "y": 75, "name": "CX_BTN", "pin": "BOARD24"},
    ],
}
circuit = TkCircuit(config)

@circuit.run
def main():
    hivemind_nfc_reader.main()

if __name__ == "__main__":
    main()
