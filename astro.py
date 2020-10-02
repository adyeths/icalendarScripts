#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate ical calendar for basic astronomical events."""
import sys
import argparse
import datetime
from math import pi
import ephem
from ephem import _find_moon_phase as find_moon_phase

# ---------------------------------------------------------------------------#

HEADER = """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//Adyeths//python ical generator//EN
CREATED;VALUE=DATE:{}
"""

FOOTER = "END:VCALENDAR"

VEVENT = """BEGIN:VEVENT
UID:{}
DTSTART:{}
DTEND:{}
SUMMARY:{}
DTSTAMP:{}
TRANSP:TRANSPARENT
STATUS:CONFIRMED
END:VEVENT"""

TIMEDELTA = datetime.timedelta(seconds=1)

# ---------------------------------------------------------------------------#


# pyephem contains functions to find new, full, and quarter moons.
# lets add additional functions to find intermediary phases.


def next_waxcres(date):
    """Waxing crescent."""
    return find_moon_phase(date, pi * 2.0, pi / 4.0)


def next_waxgib(date):
    """Waxing gibbous."""
    return find_moon_phase(date, pi * 2.0, pi - (pi / 4.0))


def next_wangib(date):
    """Waning gibbous."""
    return find_moon_phase(date, pi * 2.0, pi + (pi / 4.0))


def next_wancres(date):
    """Waning crescent."""
    return find_moon_phase(date, pi * 2.0, (pi * 2.0) - (pi / 4.0))


def firstday(month, year, weekday):
    """Get first date for day of week in month."""
    daykey = {
        7: "sun",
        1: "mon",
        2: "tue",
        3: "wed",
        4: "thu",
        5: "fri",
        6: "sat",
    }
    for i in range(1, 8):
        firstdt = datetime.date(year, month, i)
        if daykey[firstdt.isoweekday()] == weekday:
            break
    return firstdt.toordinal()


def gendates(args: argparse.Namespace):
    """Generate lists of events."""
    # a variable to hold our dates.
    dates = []

    ###########################################################################

    # ### equinoxes and solstices

    # start at beginning of year.
    dte = ephem.Date("{}/1/1 0:0".format(args.y))

    # get date and time of equinox and solstice events
    for i in range(0, 4):
        fnc, mystr = {
            0: (ephem.next_equinox, "♈ Vernal Equinox"),
            1: (ephem.next_solstice, "♋ Summer Solstice"),
            2: (ephem.next_equinox, "♎ Autumn Equinox"),
            3: (ephem.next_solstice, "♑ Winter Solstice"),
        }[i]
        dte = fnc(dte)
        dtn = [int(_) for _ in dte.tuple()]
        # dt1 = datetime.datetime(dtn[0], dtn[1], dtn[2], dtn[3], dtn[4], dtn[5])
        dt1 = datetime.datetime(dtn[0], dtn[1], dtn[2], dtn[3], dtn[4], 0)
        dt2 = dt1 + TIMEDELTA
        # dt2 = dt1
        dates.append(
            (
                dt1.strftime("%Y%m%dT%H%M%SZ"),
                dt2.strftime("%Y%m%dT%H%M%SZ"),
                "{}".format(mystr),
            )
        )

    # ### moon phases
    for i in range(0, 8):
        fnc, mystr = {
            0: (ephem.next_new_moon, "🌚"),
            1: (next_waxcres, "🌒"),
            2: (ephem.next_first_quarter_moon, "🌓"),
            3: (next_waxgib, "🌔"),
            4: (ephem.next_full_moon, "🌝"),
            5: (next_wangib, "🌖"),
            6: (ephem.next_last_quarter_moon, "🌗"),
            7: (next_wancres, "🌘"),
        }[i]

        # start at beginning of year
        dte = ephem.Date("{}/1/1 0:0".format(args.y))

        # get date and time of moon phases
        while True:
            dte = fnc(dte)
            dtn = [int(_) for _ in dte.tuple()]
            # dt1 = datetime.datetime(
            #     dtn[0], dtn[1], dtn[2], dtn[3], dtn[4], dtn[5]
            # )
            dt1 = datetime.datetime(
                dtn[0], dtn[1], dtn[2], dtn[3], dtn[4], 0
            )
            dt2 = dt1 + TIMEDELTA
            # dt2 = dt1
            if dte.triple()[0] <= args.y:
                dates.append(
                    (
                        dt1.strftime("%Y%m%dT%H%M%SZ"),
                        dt2.strftime("%Y%m%dT%H%M%SZ"),
                        "{}".format(mystr),
                    )
                )
            else:
                break

    # ### return our dates
    return sorted(dates)


def main():
    """Parse our command line arguments and generate calendar."""
    parser = argparse.ArgumentParser(
        description="Create an astronomical event calendar."
    )
    parser.add_argument("-y", type=int, required=True, metavar="Year")
    args = parser.parse_args()

    print("Generating calendar for {}".format(args.y), file=sys.stderr)

    ###########################################################################

    # ###################################### #
    dates = gendates(args)

    # ### Output ical file for dates and fdates.
    with open("astro-{}.ics".format(args.y), "w") as ofile:
        created = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")

        # ical header
        ofile.write(HEADER.format(created).replace("\n", "\r\n"))

        # output our calendar dates
        uid = 0
        for i in sorted(dates, key=lambda x: x[0]):
            uid += 1
            dtstart = i[0]
            dtend = i[1]
            event = VEVENT.format(
                "astro{}{:03d}@adyeths".format(args.y, uid),
                dtstart,
                dtend,
                i[2],
                created,
            )
            print(event.replace("\n", "\r\n"), file=ofile, end="\r\n")

        # ical footer
        ofile.write(FOOTER.replace("\n", "\r\n"))


# ---------------------------------------------------------------------------#


if __name__ == "__main__":
    main()
