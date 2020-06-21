#!/usr/local/bin/python3.7
"""
This is to be used with https://github.com/paulmaunders/delivery-slot-bot/
"""

import argparse
import subprocess
import os
import re
import http.client
import urllib
import time
from datetime import datetime

NODE_BIN = "/usr/local/bin/node"
PO_API_TOKEN = ""
PO_USER_KEY = ""
SLEEP_TIME = 120
PTTRN = re.compile(r"start: (?P<start>[^,]+), end: (?P<end>[^ ]+)")


class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def define_po_keys():
    global PO_API_TOKEN, PO_USER_KEY
    try:
        PO_API_TOKEN = os.environ["PO_API_TOKEN"]
        PO_USER_KEY = os.environ["PO_USER_KEY"]
    except KeyError as err:
        print(
            f"Error: {err}."
            "Check if your environment defines PO_API_TOKEN and PO_USER_KEY"
        )
        exit(1)


def check_tesco(dtb_path) -> list:
    with cd(dtb_path):
        result = subprocess.run(
            [NODE_BIN, "delivery-slots.js"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    if result.stderr:
        print(f"ERROR, unfortunately.")
        return []

    result_list = result.stdout.split("\n")
    return result_list


def process_tesco(t_list, days_list) -> str:
    return_str = ""
    if len(t_list) == 0:
        return return_str
    no_slots_count = t_list.count("No slots")
    if no_slots_count == 3:
        return return_str

    print(f"Slots found, let me check if they may suit your needs.")
    ret_set = set()
    for elem in t_list:
        re_group = PTTRN.search(elem)
        if re_group is None:
            continue
        re_start = re_group.group("start")
        re_end = re_group.group("end")
        if re_start[:10] != re_end[:10]:
            print(f"Something is fishy here: start {re_start} != end {re_end}")
        if re_start[:10] in days_list:
            ret_set.add(f"{re_start} - {re_end}")

    if len(ret_set):
        return_str = " || ".join(ret_set)
    return return_str


def send_po(message) -> bool:
    if not message:
        return True

    print(f"Sending: {message}")
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request(
        "POST",
        "/1/messages.json",
        urllib.parse.urlencode(
            {"token": PO_API_TOKEN, "user": PO_USER_KEY, "message": message}
        ),
        {"Content-type": "application/x-www-form-urlencoded"},
    )
    res = conn.getresponse()
    if res.status not in range(200, 300):
        return False
    return True


def main_argparse() -> list:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", dest="days", type=str, nargs="+", required=True)
    parser.add_argument("--dtb-path", dest="dtb_path", type=str, required=True)
    args = parser.parse_args()
    return (args.days, args.dtb_path)


def main() -> None:
    (days_list, dtb_path) = main_argparse()
    print(f"Searching for slots in: {' - '.join(days_list)}")
    define_po_keys()
    while True:
        now = datetime.now()
        print(f"Running at: {now.strftime('%Y/%m/%d %H:%M:%S')}")
        res_tesco = check_tesco(dtb_path)
        message = process_tesco(res_tesco, days_list)
        send_po(message) if message else print(f"No slots yet...")
        print(f"Sleeping for {SLEEP_TIME} seconds...")
        time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    main()
