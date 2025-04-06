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


def make_log_from_starter(starter) -> bool:
    try:
        name = id_to_person(starter["id"])
    except KeyError:
        eprint(f"skipped unnamed starter")
        return False

    current = starter.get("current")
    if current == None:
        eprint(f"skipped {name}, because there was no 'current' object")
        return False

    try:
        time_stamp = dt.datetime.fromisoformat(current["time"].replace("Z", "+01:00"))
    except:
        eprint(f"failed to get time for {name}")
        time_stamp = dt.datetime.now()

    speed = current.get("speedRaw")

    try:
        lat = current["lat"]
        lng = current["lng"]
    except KeyError:
        eprint(f"skipped {name} because it did not contain position")
        return False

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
            f"{time_stamp.isoformat()}, {speed}, ({lat}, {lng}), {battery}, {online}\n"
        )
    return True


def log_cycle():
    try:
        response = requests.get(API_URL, timeout=2)
    except requests.exceptions.ConnectTimeout:
        eprint("connection timed out")
        return
    if response.status_code != 200:
        eprint(f"got response code {response.status_code}\n    {response.text}")
        return
    try:
        obj = json.loads(response.text)
    except json.decoder.JSONDecodeError:
        # pray to the gods this doesn't happen
        eprint("encountered malformed json")
        return

    success = True

    for starter in obj["starters"]:
        success = success and make_log_from_starter(starter)
    if success:
        eprint("successfully loged all participants")


def main():
    while True:
        start_time = dt.datetime.now()
        for i in range(10):
            try:
                log_cycle()
                break
            except:
                eprint(f"this log cycle failed {i+1} times")
                time.sleep(5)
        else:
            eprint("gave up for this log cycle")
        delta = dt.datetime.now() - start_time
        time.sleep((dt.timedelta(minutes=1.5) - delta).total_seconds())


if __name__ == "__main__":
    main()
