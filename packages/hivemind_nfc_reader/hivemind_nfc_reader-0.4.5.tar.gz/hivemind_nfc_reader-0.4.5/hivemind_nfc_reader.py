"""
HiveMind NFC reader client
"""
import collections
import json
import logging
import math
import signal
import sys
import threading
import time
from datetime import datetime, timedelta

import gpiozero
import nfc
import requests
import websocket
from nfc.clf import ContactlessFrontend, transport
from nfc.clf.acr122 import Chipset, Device
from py532lib.mifare import Mifare

__version__ = "0.4.5"

state = {
    "card": None,
    "time": None,
    "register_data": None,
    "register_time": None,
    "register_complete_time": None,
    "startup_time": None,
    "cabinet_id": None,
    "lights_on": {},
    "initialized": set(),
    "initialized_time": None,
    "buttons": {},
    "lights": {},
    "button_held": {},
    "clip_requested_time": None,
    "api_requests": collections.deque(),
    "players_with_pending_requests": {},
}

with open(sys.argv[1]) as in_file:
    settings = json.load(in_file)

DOMAIN = settings.get("domain", "kqhivemind.com")
IS_SECURE = settings.get("secure", True)
PORT = settings.get("port", 443 if IS_SECURE else 80)
API_PROTOCOL = "https" if IS_SECURE else "http"
API_BASE_URL = f"{API_PROTOCOL}://{DOMAIN}:{PORT}/api"
API_URL = f"{API_BASE_URL}/stats/signin/nfc/"
WS_PROTOCOL = "wss" if IS_SECURE else "ws"
WS_URL = f"{WS_PROTOCOL}://{DOMAIN}:{PORT}/ws/signin"
USE_GPIO = "pin_config" in settings
PIN_ORDER = {
    1: 3,
    2: 3,
    3: 1,
    4: 1,
    5: 2,
    6: 2,
    7: 4,
    8: 4,
    9: 5,
    10: 5,
}
HOLD_TIME = 0.8
BRIGHTNESS = max(min(settings.get("brightness", 10) / 10, 1.0), 0.0)
DRIVER = settings.get("driver", "acr1252u")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter("[%(asctime)s]  %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

if settings.get("log_file"):
    file_handler = logging.FileHandler(settings.get("log_file"))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


if USE_GPIO:
    # light_mode defaults to "low": common wire is ground, set pin high to turn on
    LED_MODE = settings.get("light_mode", "low").strip().lower() != "high"

    # button mode defaults to "high": common wire is +v, set pull-down resistor, detect +v on common
    BUTTON_MODE = settings.get("button_mode", "high").strip().lower() == "low"


def pin_id(num):
    return f"BOARD{num}"

def register_card(card_id, register_data):
    data = {
        "action": "nfc_register_tapped",
        "card": card_id,
        **register_data,
    }

    state["api_requests"].append(data)

def sign_in(card_id, player_id):
    if settings.get("test_mode"):
        light_pins = { i["player_id"]: i["light"] for i in settings["pin_config"] }
        pin = light_pins.get(int(player_id))
        if pin:
            state["lights_on"][pin] = True

        return

    data = {
        "action": "sign_in",
        "card": card_id,
        "player": player_id,
    }

    state["api_requests"].append(data)
    state["players_with_pending_requests"][player_id] = datetime.now()

def sign_out(player_id):
    if settings.get("test_mode"):
        light_pins = { i["player_id"]: i["light"] for i in settings["pin_config"] }
        pin = light_pins.get(int(player_id))
        if pin:
            state["lights_on"][pin] = False

        return

    data = {
        "action": "sign_out",
        "player": player_id,
    }

    state["api_requests"].append(data)
    state["players_with_pending_requests"][player_id] = datetime.now()

def create_clip(player_id):
    logger.info("Creating Twitch clip from player {}".format(player_id))
    state["clip_requested_time"] = datetime.now()

    user_id = None
    cabinet_id = get_cabinet_id()

    url = f"{API_BASE_URL}/game/cabinet/{cabinet_id}/signin/"
    req = requests.get(f"{API_BASE_URL}/game/cabinet/{cabinet_id}/signin/")
    for user in req.json()["signed_in"]:
        if user["player_id"] == player_id:
            user_id = user["user_id"]

    postdata = {
        "cabinet": cabinet_id,
        "token": settings["token"],
        "created_by": user_id,
    }

    req = requests.post(f"{API_BASE_URL}/video/video-clip/", data=postdata)

def card_read(uid):
    logger.info("Card read: UID {}".format(uid))

    if state["register_data"] and state["register_time"] and \
       state["register_time"] > datetime.now() - timedelta(minutes=1):

        register_card(uid, state["register_data"])
        state["register_data"] = None
        state["register_complete_time"] = datetime.now()
    else:
        state["card"] = uid
        state["time"] = datetime.now()

def listen_card():
    if DRIVER == "acr1252u":
        return listen_card_acr1252u()
    if DRIVER == "pn532_i2c":
        return listen_card_pn532_i2c()

def listen_card_acr1252u():
    chipset = Chipset.__new__(Chipset)
    found = transport.USB.find(settings["usb_device"])
    vid, pid, bus, dev = found[0]
    logger.warning("device {}: vid {}, pid {}, bus {}, dev {}".format(settings["usb_device"], *found[0]))
    chipset.transport = transport.USB(bus, dev)

    frame = bytearray.fromhex("62000000000000000000")
    chipset.transport.write(frame)
    chipset.transport.read(100)

    chipset.ccid_xfr_block(bytearray.fromhex("FF00517F00"))
    chipset.set_buzzer_and_led_to_default()

    device = Device.__new__(Device)
    device.chipset = chipset
    device.log = logger

    def connected(llc):
        card_read(llc.identifier.hex())

        chipset.ccid_xfr_block(bytearray.fromhex("FF00400D0403000101"), timeout=1)
        chipset.ccid_xfr_block(bytearray.fromhex("FF00400E0400000000"), timeout=1)

        while llc.is_present:
            time.sleep(0.1)

        return False

    while True:
        clf = ContactlessFrontend.__new__(ContactlessFrontend)
        clf.device = device
        clf.lock = threading.Lock()

        state["initialized"].add("card")

        try:
            clf.connect(rdwr={"on-connect": connected})
        except KeyboardInterrupt:
            clf.close()
        except Exception as err:
            logger.exception("Unhandled exception in on-connect: {}".format(err))
            time.sleep(1)

def listen_card_pn532_i2c():
    mifare = Mifare()
    mifare.SAMconfigure()
    state["initialized"].add("card")

    while True:
        try:
            uid = mifare.scan_field()
            uid_hex = "".join('{:02x}'.format(i) for i in uid)
            card_read(uid_hex)

        except KeyboardInterrupt:
            logger.warning("Keyboard interrupt")
            return
        except Exception as err:
            logger.exception("Unhandled exception in listen_card: {}".format(err))

        time.sleep(1)

def button_pressed(button):
    player_id = state["buttons"].get(button.pin)
    state["button_held"][player_id] = False
    logger.info("Button pressed on player {} ({})".format(player_id, button.pin))

def button_held(button):
    player_id = state["buttons"].get(button.pin)
    state["button_held"][player_id] = True
    logger.info("Button held on player {} ({})".format(player_id, button.pin))
    if settings.get("enable_clips"):
        create_clip(player_id)

def button_released(button):
    player_id = state["buttons"].get(button.pin)
    logger.info("Button released on player {} ({})".format(player_id, button.pin))
    if state["button_held"].get(player_id):
        return

    if state["card"] and state["time"] > datetime.now() - timedelta(seconds=15):
        sign_in(state["card"], player_id)
        state["card"] = None
        state["time"] = None
        state["register_data"] = None
        state["register_time"] = None
    else:
        sign_out(player_id)

def listen_buttons():
    state["buttons"] = {}
    buttons_configured = set()

    for pin in settings.get("pins_low", []):
        output = gpiozero.OutputDevice(pin_id(pin), initial_value=False)
        logger.info("Setting pin {} low".format(output.pin))

    for pin in settings.get("pins_high", []):
        output = gpiozero.OutputDevice(pin_id(pin), initial_value=True)
        logger.info("Setting pin {} high".format(output.pin))

    all_buttons = []

    while len(buttons_configured) < len(settings["pin_config"]):
        for i, pin in enumerate(settings["pin_config"]):
            if not pin.get("button"):
                pins_configured.add(i)
                continue

            if i in buttons_configured:
                continue

            try:
                button = gpiozero.Button(
                    pin_id(pin["button"]),
                    pull_up=BUTTON_MODE,
                    hold_time=HOLD_TIME,
                )
                button.when_pressed = button_pressed
                button.when_held = button_held
                button.when_released = button_released

                state["buttons"][button.pin] = pin["player_id"]
                logger.info("Listening on pin {} for player {}".format(button.pin, pin["player_id"]))
                buttons_configured.add(i)

                all_buttons.append(button)

            except Exception as e:
                logger.error("Error listening on pin {}: {}".format(pin, e))
                time.sleep(1)

    signal.pause()

def on_message(ws, message_text):
    try:
        logger.debug(message_text)
        message = json.loads(message_text)

        if settings.get("scene") and settings.get("cabinet"):
            if message.get("scene_name") != settings.get("scene").lower() or \
               message.get("cabinet_name") != settings.get("cabinet").lower():
                return

        if settings.get("device"):
            if settings["device"] not in message.get("device_ids"):
                return

        if message.get("type") == "nfc_register":
            if message["reader_id"] == settings["reader"]:
                state["register_data"] = {k: v for k, v in message.items()
                                          if k not in ["type", "scene_name", "cabinet_name", "reader_id"]}
                state["register_time"] = datetime.now()

                logger.info("Got register request: {}".format(
                    ", ".join([f"{k}={v}" for k, v in state["register_data"].items()]),
                ))

        else:
            light_pins = { i["player_id"]: i["light"] for i in settings["pin_config"] }
            pin = light_pins.get(int(message["player_id"]))
            if pin:
                value = message["action"] == "sign_in"
                logger.info("Setting {} to {} (player {})".format(pin, value, message["player_id"]))
                state["lights_on"][pin] = value

    except Exception as e:
        logger.exception("Exception in on_message")

def send_api_requests():
    if len(state["api_requests"]) > 0:
        data = state["api_requests"].popleft()
        data["scene_name"] = settings.get("scene")
        data["cabinet_name"] = settings.get("cabinet")
        data["device_id"] = settings.get("device")
        data["token"] = settings["token"]

        req = requests.post(API_URL, json=data)
        if "player" in data and data["player"] in state["players_with_pending_requests"]:
            del state["players_with_pending_requests"][data["player"]]

def send_api_requests_thread():
    while True:
        try:
            send_api_requests()
        except Exception as e:
            logger.exception(e)

        time.sleep(0.1)

def on_ws_error(ws, error):
    logger.error("Error in websocket connection: {}".format(error))
    ws.close()

def on_ws_close(ws, close_status_code, close_msg):
    logger.error("Websocket closed ({})".format(close_msg))

def get_cabinet_id():
    if state.get("cabinet_id"):
        return state["cabinet_id"]

    if settings.get("scene") and settings.get("cabinet"):
        req = requests.get(f"{API_BASE_URL}/game/scene/", params={"name": settings["scene"].lower()})
        scene_id = req.json()["results"][0]["id"]

        req = requests.get(f"{API_BASE_URL}/game/cabinet/",
                           params={"scene": scene_id, "name": settings["cabinet"].lower()})
        cabinet_id = req.json()["results"][0]["id"]
        state["cabinet_id"] = cabinet_id

        return cabinet_id

def set_lights_from_api():
    if settings.get("test_mode"):
        return

    cabinet_id = get_cabinet_id()

    if cabinet_id:
        req = requests.get(f"{API_BASE_URL}/game/cabinet/{cabinet_id}/signin/")
        signed_in = {i["player_id"] for i in req.json()["signed_in"]}

    elif settings.get("device"):
        device_id = settings["device"]
        req = requests.get(f"{API_BASE_URL}/game/client-device/{device_id}/signin/")

    if req:
        signed_in = {i["player_id"] for i in req.json()["signed_in"]}

        for row in settings["pin_config"]:
            if row.get("player_id") and row.get("light"):
                value = row["player_id"] in signed_in
                state["lights_on"][row["light"]] = value

def set_lights():
    logger.info("Starting lights thread.")
    lights = {}

    for pin in settings["pin_config"]:
        if pin.get("light"):
            lights[pin["light"]] = gpiozero.PWMLED(pin_id(pin["light"]), active_high=LED_MODE)

    while True:
        mode = None
        blink_rate = 1
        animation_time = None

        if "card" in state["initialized"] and "websocket" in state["initialized"]:
            if state["initialized_time"] is None:
                state["initialized_time"] = datetime.now()

            if state["initialized_time"] > datetime.now() - timedelta(seconds=3):
                mode = "sweep"
                animation_time = state["initialized_time"]

        if state["card"] and state["time"] > datetime.now() - timedelta(seconds=15):
            mode = "blink"
            blink_rate = 6

        if state["register_data"] and state["register_time"] and \
           state["register_time"] > datetime.now() - timedelta(minutes=1):
            mode = "blink"
            blink_rate = 2

        if state["register_complete_time"] and \
           state["register_complete_time"] > datetime.now() - timedelta(seconds=0.75):
            mode = "happy"
            animation_time = state["register_complete_time"]

        if state["clip_requested_time"] and \
           state["clip_requested_time"] > datetime.now() - timedelta(seconds=0.75):
            mode = "happy"
            animation_time = state["clip_requested_time"]

        for pin in filter(lambda i: i.get("light"), settings["pin_config"]):
            if mode == "blink":
                if(state["lights_on"].get(pin["light"])):
                    value = BRIGHTNESS
                else:
                    value = BRIGHTNESS * (math.sin(time.monotonic() * blink_rate) + 1) * .5

            elif mode == "sweep":
                t = datetime.now()
                idx = PIN_ORDER.get(pin["player_id"], 0)
                on_time = animation_time + timedelta(seconds=idx * 0.1)
                fade_time = on_time + timedelta(seconds=0.2)
                off_time = on_time + timedelta(seconds=0.6)
                if t > on_time and t < fade_time:
                    value = BRIGHTNESS
                elif t > fade_time and t < off_time:
                    value = BRIGHTNESS * ((1 - (t - fade_time).total_seconds()) / (off_time - fade_time).total_seconds())
                else:
                    value = 0

            elif mode == "happy":
                frame = math.floor((datetime.now() - animation_time) / timedelta(seconds=0.15))
                frames_on_by_idx = {
                    1: {2},
                    2: {1, 3},
                    3: {0, 4},
                    4: {1, 3},
                    5: {2},
                }

                idx = PIN_ORDER.get(pin["player_id"], 0)
                value = BRIGHTNESS if frame in frames_on_by_idx.get(idx, {}) else 0

            elif mode == "bounce":
                frame = math.floor((datetime.now() - animation_time) / timedelta(seconds=0.15)) % 16
                frames_on_by_idx = {
                    1: {0, 1, 15},
                    2: {1, 2, 3, 13, 14, 15},
                    3: {3, 4, 5, 11, 12, 13},
                    4: {5, 6, 7, 9, 10, 11},
                    5: {7, 8, 9}
                }

                idx = PIN_ORDER.get(pin["player_id"], 0)
                value = BRIGHTNESS if frame in frames_on_by_idx.get(idx, {}) else 0

            elif state["players_with_pending_requests"].get(pin["player_id"]):
                elapsed = datetime.now() - state["players_with_pending_requests"].get(pin["player_id"])
                value = BRIGHTNESS * ((math.sin(elapsed.total_seconds() * 4) + 1) / 4 + 0.5)
            else:
                value = BRIGHTNESS if state["lights_on"].get(pin["light"], False) else 0

            value = float(min(max(value, 0.0), 1.0))
            lights[pin["light"]].value = value

        time.sleep(0.01)

def listen_ws():
    if settings.get("test_mode"):
        state["initialized"].add("websocket")
        return

    logger.info("Starting websocket thread.")

    while True:
        try:
            if USE_GPIO:
                set_lights_from_api()

            wsapp = websocket.WebSocketApp(WS_URL, on_message=on_message, on_error=on_ws_error,
                                           on_close=on_ws_close)
            logger.info("Websocket connection online.")
            state["initialized"].add("websocket")
            wsapp.run_forever()

        except Exception as e:
            logger.exception("Exception in wsapp.run_forever")

        time.sleep(1)


def main():
    state["startup_time"] = datetime.now()

    card_thread = threading.Thread(target=listen_card, name="card", daemon=True)
    card_thread.start()

    ws_thread = threading.Thread(target=listen_ws, name="websocket", daemon=True)
    ws_thread.start()

    api_thread = threading.Thread(target=send_api_requests_thread, name="api", daemon=True)
    api_thread.start()

    if USE_GPIO:
        button_thread = threading.Thread(target=listen_buttons, name="buttons", daemon=True)
        button_thread.start()

        lights_thread = threading.Thread(target=set_lights, name="lights", daemon=True)
        lights_thread.start()

    while True:
        time.sleep(1)

    logger.info("Exiting.")


if __name__ == "__main__":
    main()
