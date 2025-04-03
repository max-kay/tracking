import datetime as dt
import requests
import time
import sys
import json


def eprint(*args, **kwargs) -> None:
    print(f"[{dt.datetime.now()}]", *args, **kwargs, file=sys.stderr)


BASE_URL = "https://racemap.com/api/data/v1"
SAMPLE_EVENT_ID = "66bf4318d1c783279d183dd3"
END_POINT = "current"
OPTIONS = "?interpolation=false"
API_URL = f"{BASE_URL}/{SAMPLE_EVENT_ID}/{END_POINT}{OPTIONS}"


def id_to_person(id: int) -> str:
    match id:
        case 860201061315183:
            return "Flavio"
        case 860201061324110:
            return "Clarissa"
        case 860201061337625:
            return "Ivo"
        case 860201061320068:
            return "Takashi"
        case 860201061320308:
            return "Louis"
        case 860201061230630:
            return "Marc"
        case 860201061159557:
            return "Luca"
        case 860201062330074:
            return "Safety-Car"
        case 860201062373355:
            return "Reserve"
    eprint("encountered unmapped key")
    return str(id)


LOGS_DIR = "./logs/"


def make_log_from_starter(starter) -> None:
    try:
        name = id_to_person(starter["id"])
    except KeyError:
        eprint(f"skipped unnamed starter")
        return

    current = starter.get("current")
    if current == None:
        eprint(f"skipped {name}, because there was no 'current' object")
        return

    try:
        time = dt.datetime.fromisoformat(current["time"].replace("Z", "+01:00"))
    except:
        eprint(f"failed to get time for {name}")
        time = dt.datetime.now()

    speed = current.get("speedRaw")

    try:
        lat = current["lat"]
        lng = current["lng"]
    except KeyError:
        eprint(f"skipped {name} because it did not contain position")
        return

    # this can be null in json
    device = starter.get("device")
    if device == None:
        battery = None
        online = None
    else:
        battery = device.get("battery")
        online = device.get("online")

    # also creates a file if it doesn't exist
    with open(f"logs/{name}.txt", mode="a") as file:
        file.write(
            f"{time.isoformat()}, {speed}, ({lat}, {lng}), {battery}, {online}\n"
        )


def log_cycle():
    response = requests.get(API_URL)
    if response.status_code != 200:
        eprint(f"got response code {response.status_code}\n    {response.text}")
        return
    try:
        obj = json.loads(response.text)
    except json.decoder.JSONDecodeError:
        # pray to the gods this doesn't happen
        eprint("encountered malformed json")
        return

    for starter in obj["starters"]:
        make_log_from_starter(starter)


def main():
    while True:
        for i in range(10):
            try:
                log_cycle()
                break
            except:
                eprint(f"this log cycle failed {i+1} times")
                time.sleep(5)
        else:
            eprint("gave up for this log cycle")
        time.sleep(60 * 1.5)


if __name__ == "__main__":
    main()
