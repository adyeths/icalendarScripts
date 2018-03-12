#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate ical for church year."""
import sys
import argparse
import datetime
from math import floor

# ---------------------------------------------------------------------------#

HEADER = '''BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//Adyeths//python ical generator//EN
CREATED;VALUE=DATE:{}
'''

FOOTER = "END:VCALENDAR"

VEVENT = '''BEGIN:VEVENT
UID:{}
DTSTART;VALUE=DATE:{}
DTEND;VALUE=DATE:{}
SUMMARY:{}
DTSTAMP:{}
TRANSP:TRANSPARENT
STATUS:CONFIRMED
END:VEVENT'''

# ---------------------------------------------------------------------------#


def whichyear(year):
    """Determine which church year starts on advent of the specified year."""
    return {
        0: "🄰",  # 🄰 🅰
        1: "🄱",  # 🄱 🅱
        2: "🄲"   # 🄲 🅲
    }.get((year - 1992) % 3)


def calceaster(year):
    """Get date as ordinal for easter using Meeus algorithm."""
    vrh = ((19 * (year % 19)) + floor(year / 100) - int(
        floor(year / 100) / 4) - (int((floor(year / 100) - int(
            (floor(year / 100) + 8) / 25) + 1) / 3)) + 15) % 30
    vrv = (32 + (2 * int(floor(year / 100) % 4)) + (2 * int(
        (year % 100) / 4)) - vrh - ((year % 100) % 4)) % 7
    vrm = int(((year % 19) + (11 * vrh) + (22 * vrv)) / 451)

    month = int((vrh + vrv + (7 * vrm) + 114) / 31)
    day = ((vrh + vrv - (7 * vrm) + 114) % 31) + 1
    return datetime.date(year, month, day).toordinal()


def getsunday(month, day, year):
    """Get first sunday on or after date."""
    dte = datetime.date(year, month, day)
    dow = 7 - dte.isoweekday()
    return {
        True: dte.toordinal(),
        False: dte.toordinal() + dow
    }.get(dow == 0)


def getsundays(year):
    """Get list of sundays in year."""
    fsv = getsunday(1, 1, year)
    eoy = datetime.date(year, 12, 31).toordinal()
    return [_ for _ in range(fsv, eoy + 1, 7)]


def idxvalue(i, dte):
    """Index helper function."""
    tmp = {
        1: "st",
        2: "nd",
        3: "rd",
        21: "st",
        22: "nd",
        23: "rd",
        31: "st",
        32: "nd",
        33: "rd"
    }.get(i, "th")
    idx = dte + (7 * (i - 1))
    return(tmp, idx)


def getdates(year):
    """Get date values for sundays in calendar year."""
    # TODO: Incorporate descriptions containing readings for the sunday.

    # Add marker to indicate which church year we are in.
    thisyear = whichyear(year - 1)
    nextyear = whichyear(year)

    # some initial calculations
    dtx = {
        "epiphany": datetime.date(year, 1, 6).toordinal(),
        "afterepiphany": getsunday(1, 7, year),
        "easter": calceaster(year),
        "lent": calceaster(year) - 42,
        "pentecost": calceaster(year) + 49,
        "christking": getsunday(11, 20, year),
        "advent": getsunday(11, 27, year),
        "afterchristmas": getsunday(12, 26, year),
        "afterchristmas1": getsunday(12, 26, year - 1),
        "afterchristmas2": getsunday(1, 6, year) - getsunday(1, 2, year)
    }
    dates = {}
    for i in getsundays(year):
        dates[i] = None

    ###########################################################################

    # afterchristmas... previous church year
    if dtx["afterchristmas1"] in dates:
        dates[dtx["afterchristmas1"]] = \
            "1st Sunday after Christmas {}".format(thisyear)
    if dtx["afterchristmas2"] != 0:
        dates[dtx["afterepiphany"] - 7] = \
            "2nd Sunday after Christmas {}".format(thisyear)

    # calculatable dates (Order is important here!)
    for i in [(dtx["afterepiphany"], 2, 10),
              (dtx["lent"], 1, 6),
              (dtx["easter"], 2, 8),
              (dtx["pentecost"] + 7, 2, 28),
              (dtx["advent"], 1, 5)]:
        for j in range(i[1], i[2]):
            tmp, idx = idxvalue(j, i[0])
            text = {
                dtx["afterepiphany"]:
                    "Sunday after the Epiphany (Lectionary {}) {}".format(
                        j, thisyear),
                dtx["lent"]: "Sunday in Lent {}".format(thisyear),
                dtx["easter"]: "Sunday of Easter {}".format(thisyear),
                dtx["pentecost"] + 7: "Sunday after Pentecost {}".format(
                    thisyear),
                dtx["advent"]: "Sunday of Advent {}".format(nextyear)
            }.get(i[0])
            dates[idx] = "{}{} {}".format(j, tmp, text)

    # specific dates (Order is important here!)
    dates[dtx["epiphany"]] = "Epiphany {}".format(thisyear)
    dates[dtx["afterepiphany"]] = \
        "Baptism of our Lord (Lectionary 1) {}".format(thisyear)
    dates[dtx["lent"] - 4] = "Ash Wednesday {}".format(thisyear)
    dates[dtx["easter"] - 7] = "Palm Sunday {}".format(thisyear)
    dates[dtx["easter"] - 3] = "Maundy Thursday {}".format(thisyear)
    dates[dtx["easter"] - 2] = "Good Friday {}".format(thisyear)
    dates[dtx["easter"] - 1] = "Easter Vigil {}".format(thisyear)
    dates[dtx["easter"]] = "Easter Sunday {}".format(thisyear)
    dates[dtx["easter"] + 39] = "Ascension of the Lord {}".format(thisyear)
    dates[dtx["pentecost"]] = "Day of Pentecost {}".format(thisyear)
    dates[dtx["pentecost"] + 7] = "Trinity Sunday {}".format(thisyear)
    dates[dtx["christking"]] = "Christ the King (Lectionary 34) {}".format(
        thisyear)
    dates[datetime.date(year, 12, 25).toordinal()] = "Christmas Day"
    if dtx["afterchristmas"] in dates:
        dates[dtx["afterchristmas"]] = "1st Sunday after Christmas {}".format(
            nextyear)

    # Add lectionary number to Sundays after Pentecost
    # this must follow the specific dates listed above!
    lect = 33
    for i in sorted(dates.keys(), reverse=True):
        if dates[i] is not None:
            if dates[i].endswith("Sunday after Pentecost {}".format(thisyear)):
                dates[i] = dates[i].replace(" {}".format(thisyear), "")
                dates[i] = "{} (Lectionary {}) {}".format(
                    dates[i], lect, thisyear)
                lect -= 1

    # return our results
    return dates


def getfdates(year):
    """Get fixed dates in calendar year."""
    fdates = {}
    fdates[datetime.date(year, 1, 1).toordinal()] = "Name of Jesus"
    fdates[datetime.date(year, 1, 18).toordinal()] = "Confession of Peter"
    fdates[datetime.date(year, 1, 25).toordinal()] = "Conversion of Paul"
    fdates[datetime.date(year, 2, 2).toordinal()] = "Presentation of the Lord"
    fdates[datetime.date(year, 3, 19).toordinal()] = \
        "Joseph, Guardian of Jesus"
    fdates[datetime.date(year, 3, 25).toordinal()] = "Annunciation of Our Lord"
    fdates[datetime.date(year, 4, 25).toordinal()] = "Mark, Evangelist"
    fdates[datetime.date(year, 5, 1).toordinal()] = \
        "Philip and James, Apostles"
    fdates[datetime.date(year, 5, 14).toordinal()] = "Matthias, Apostle"
    fdates[datetime.date(year, 5, 31).toordinal()] = \
        "Visitation of Mary to Elizabeth"
    fdates[datetime.date(year, 6, 11).toordinal()] = "Barnabas, Apostle"
    fdates[datetime.date(year, 6, 24).toordinal()] = "John the Baptist"
    fdates[datetime.date(year, 6, 29).toordinal()] = "Peter and Paul, Apostles"
    fdates[datetime.date(year, 7, 3).toordinal()] = "Thomas, Apostle"
    fdates[datetime.date(year, 7, 22).toordinal()] = "Mary Magdalene, Apostle"
    fdates[datetime.date(year, 7, 25).toordinal()] = "James, Apostle"
    fdates[datetime.date(year, 8, 15).toordinal()] = "Mary, Mother of Our Lord"
    fdates[datetime.date(year, 8, 24).toordinal()] = "Bartholomew, Apostle"
    fdates[datetime.date(year, 9, 14).toordinal()] = "Holy Cross Day"
    fdates[datetime.date(year, 9, 21).toordinal()] = \
        "Matthew, Apostle and Evangelist"
    fdates[datetime.date(year, 9, 29).toordinal()] = "Michael and All Angels"
    fdates[datetime.date(year, 10, 18).toordinal()] = "Luke, Evangelist"
    fdates[datetime.date(year, 10, 28).toordinal()] = \
        "Simon and Jude, Apostles"
    fdates[datetime.date(year, 10, 31).toordinal()] = "Reformation Day"
    fdates[datetime.date(year, 11, 1).toordinal()] = "All Saints Day"
    fdates[datetime.date(year, 11, 30).toordinal()] = "Andrew, Apostle"
    fdates[datetime.date(year, 12, 24).toordinal()] = "Christmas Eve"
    fdates[datetime.date(year, 12, 26).toordinal()] = \
        "Stephen, Deacon and Martyr"
    fdates[datetime.date(year, 12, 27).toordinal()] = \
        "John, Apostle and Evangelist"
    fdates[datetime.date(year, 12, 28).toordinal()] = \
        "The Holy Innocents, Martyrs"
    return fdates


def main():
    """Main routine to generate a yearly calendar for the church year."""
    parser = argparse.ArgumentParser(
        description='''
            Generate church year calendar for calendar year.
        ''',
    )
    parser.add_argument("-y",
                        type=int,
                        metavar="Year",
                        default=datetime.date.today().year)
    args = parser.parse_args()

    if args.y <= 1992:
        print("Year must be greater than or equal to 1992!")
        sys.exit()

    print("Generating church calendar for {}".format(args.y),
          file=sys.stderr)

    ###########################################################################

    # ## sundays in the year...
    dates = getdates(args.y)

    # ## fixed dates... lesser festivals.
    fdates = getfdates(args.y)

    # Output ical file for dates and fdates.
    with open("elca-{}.ics".format(args.y), "w") as ofile:
        created = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")

        # ical header
        ofile.write(HEADER.format(created).replace("\n", "\r\n"))

        # output sundays
        uidnum = 0
        for i in sorted(dates.keys()):
            uidnum += 1
            uid = "elcasundays{}{:03d}@adyeths".format(args.y, uidnum)
            dtstart = datetime.date.fromordinal(i).strftime("%Y%m%d")
            dtend = datetime.date.fromordinal(i + 1).strftime("%Y%m%d")
            event = VEVENT.format(
                uid,
                dtstart,
                dtend,
                dates[i],
                created)
            print(event.replace("\n", "\r\n"), file=ofile, end="\r\n")

        # output lesser festivals
        uidnum = 0
        for i in sorted(fdates.keys()):
            uidnum += 1
            uid = "elcalesser{}{:03d}@adyeths".format(args.y, uidnum)
            dtstart = datetime.date.fromordinal(i).strftime("%Y%m%d")
            dtend = datetime.date.fromordinal(i + 1).strftime("%Y%m%d")
            event = VEVENT.format(
                uid,
                dtstart,
                dtend,
                fdates[i],
                created)

            print(event.replace("\n", "\r\n"), file=ofile, end="\r\n")
        # ical footer
        ofile.write(FOOTER.replace("\n", "\r\n"))

# ---------------------------------------------------------------------------#


if __name__ == "__main__":
    main()
