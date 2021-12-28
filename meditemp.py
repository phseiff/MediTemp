#!/usr/bin/python3

"""
You gotta run this with sudo!!

optional arguments:
* supply with --no-notifs if you don't want to use telegram-sent to get notifications.
* supply with --no-logfile to disable printing.
* supply with --no-gnuplot to disable gnuplot.

For a full documentation on how to use this and how to set it up, see README.md
"""


import sys
import os
import time
from datetime import datetime
import subprocess
import re
import urllib.parse
import shutil
import pwd
import getpass
import traceback
import warnings
import textwrap

import temper

if "--no-notifs" not in sys.argv:
    import telegram_send

ALREADY_DETECTED_INFUNCTIONAL_GNUPLOT = False
CACHED_FILES = dict()


if not (os.path.exists("gnuplot.cached_files") and os.path.isdir("gnuplot.cached_files")):
    os.mkdir("gnuplot.cached_files")
else:
    shutil.rmtree("gnuplot.cached_files")
    os.mkdir("gnuplot.cached_files")

try:
    with open("meditemp-log.txt", "r") as log_file:
        log = log_file.read()
except FileNotFoundError:
    open("meditemp-log.txt", "w").close()
    log = str()


def log_print(*args, log_into_file=True):
    if "--no-logfile" not in sys.argv and log_into_file:
        global log
        log += " ".join(args) + "\n"
    print(*args)


def get_user():
    """Try to find the user who called sudo/pkexec.
    Taken from https://unix.stackexchange.com/a/626389 ."""
    try:
        return os.getlogin()
    except OSError:
        # failed in some ubuntu installations and in systemd services
        pass

    try:
        user = os.environ['USER']
    except KeyError:
        # possibly a systemd service. no sudo was used
        return getpass.getuser()

    if user == 'root':
        try:
            return os.environ['SUDO_USER']
        except KeyError:
            # no sudo was used
            pass

        try:
            pkexec_uid = int(os.environ['PKEXEC_UID'])
            return pwd.getpwuid(pkexec_uid).pw_name
        except KeyError:
            # no pkexec was used
            pass

    return user


def file_name_to_cached_file_name(file_name: str) -> str:
    return "gnuplot.cached_files/" + urllib.parse.quote(file_name).replace("/", "___")


def generate_graph():
    # run gnuplot
    if "--no-gnuplot" in sys.argv:
        return
    try:
        subprocess.run("gnuplot meditemp.gnuplot".split(), check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        global ALREADY_DETECTED_INFUNCTIONAL_GNUPLOT
        if not ALREADY_DETECTED_INFUNCTIONAL_GNUPLOT:
            ALREADY_DETECTED_INFUNCTIONAL_GNUPLOT = True
            log_print(
                datetime.now().strftime("%m/%d/%Y, %H:%M")
                + ": Gnuplot doesn't seem to be installed; data is collected, but won't be plotted for now."
            )
        return

    # cache things:
    with open("med_temp.html", "r") as f:
        html = f.read()
    srcs = re.findall(r'(?=src)src=\"(?P<src>[^\"]+)', html)
    srcs = [(src[7:] if src.startswith("file://") else src) for src in srcs]
    for src in srcs:
        if src not in CACHED_FILES:
            if src != "excanvas.js":
                src_new = file_name_to_cached_file_name(src)
                shutil.copy(src, src_new)
                shutil.chown(src_new, get_user())
                CACHED_FILES[src] = src_new
    # uncache things:
    for src in CACHED_FILES:
        if src not in srcs:
            os.remove(CACHED_FILES[src])
            del CACHED_FILES[src]

    # redirect links and make them compatible to Firefox:
    for src, src_new in CACHED_FILES.items():
        for qt in "\"\'":
            for protocol in ("file://", ""):
                html = html.replace("src=" + qt + protocol + src + qt, 'src="' + src_new + '"')

    # safe modified html:
    with open("med_temp.html", "w") as f:
        f.write(html)

    # set ownership to everyone:
    shutil.chown("gnuplot.cached_files", get_user())


def mainloop():
    last_error = None

    while True:
        start_time = time.time()
        date_time = datetime.now().strftime("%m/%d/%Y, %H:%M")
        warning_list = list()
        temper_driver_warnings = list()
        try:
            # get device and temperature:
            t = temper.Temper()
            with warnings.catch_warnings(record=True) as caught_warnings:
                results = t.read(verbose=False)
                temper_driver_warnings = list(caught_warnings)

            results = [result for result in results if "error" not in result and "firmware" in result]
            results_simplified = [
                (r['internal temperature'], r.get('internal humidity'))
                for r in results
            ]
            results_simplified = list(set(results_simplified))  # <- get rid of doubled results
            assert len(results_simplified) != 0, "no TEMPer devices found. Run temper.py for debugging."
            assert len(results_simplified) <= 1, ": multiple TEMPer devices found. Run `temper.py -l` for debugging."
            temperature, humidity = results_simplified.pop()
            # note time:
            new_data_line = date_time + "; " + str(temperature)
            if humidity is not None:  # <- important 'cause it could be zero
                new_data_line += "; " + str(humidity)
            if not (os.path.exists("med_temp.csv") and os.path.isfile("med_temp.csv")):
                open("med_temp.csv", "w").close()
            with open("med_temp.csv", "r") as f_in:
                data = f_in.read()
            data += "\n" + new_data_line
            with open("med_temp.csv", "w") as f_out:
                f_out.write(data)

            # alert if alarming:
            if temperature < 15 or temperature > 25:
                warning_list.append("Temperature alert: " + str(temperature) + "°")
            if humidity and humidity > 0.6:
                warning_list.append("Humidity alert: " + str(humidity * 100) + "%")
            if warning_list and "--no-notif" in sys.argv:
                telegram_send.send(messages=warning_list)

            # print relevant info:
            for loggable_line in (warning_list + [new_data_line]):
                log_print(loggable_line, log_into_file=False)

            # run gnuplot:
            generate_graph()

            last_error = None

        except AssertionError as e:
            with open("meditemp-log.txt", "w") as log_file:
                for exc_text in [w.message.__str__() for w in temper_driver_warnings] + [str(e)]:
                    log_print(date_time + ": " + exc_text)
                    log_file.write(log)
            shutil.chown("meditemp-log.txt", get_user())

        except Exception as e:
            exc_str = traceback.format_exc()
            if exc_str == last_error:
                exc_str = "same as above."
            else:
                last_error = exc_str
                exc_str = "\n" + exc_str
            log_print(date_time + ": an unknown error occured: " + textwrap.indent(exc_str, "    "))
            with open("meditemp-log.txt", "w") as log_file:
                log_file.write(log)
            shutil.chown("meditemp-log.txt", get_user())

        # wait for the next test:
        try:
            time.sleep(10 * 60 - (time.time() - start_time))
        except KeyboardInterrupt:
            log_print(date_time + ": exited program.")
            with open("meditemp-log.txt", "w") as log_file:
                log_file.write(log)
            shutil.chown("meditemp-log.txt", get_user())
            shutil.chown("med_temp.csv", get_user())
            shutil.chown("gnuplot.cached_files", get_user())
            exit(0)


def main():
    mainloop()


if __name__ == "__main__":
    main()
