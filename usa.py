#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate ical calendar for us holidays."""
import sys
import argparse
import datetime
from math import floor

# ---------------------------------------------------------------------------#

HEADER = '''BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//Adyeths//python US Holiday ical generator//EN
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


def calceaster(year):
    """Get date as ordinal for easter in a given year using Meeus algorithm."""
    vrh = ((19 * (year % 19)) + floor(year / 100) - int(
        floor(year / 100) / 4) - (int((floor(year / 100) - int(
            (floor(year / 100) + 8) / 25) + 1) / 3)) + 15) % 30
    vrv = (32 + (2 * int(floor(year / 100) % 4)) + (2 * int(
        (year % 100) / 4)) - vrh - ((year % 100) % 4)) % 7
    vrm = int(((year % 19) + (11 * vrh) + (22 * vrv)) / 451)

    month = int((vrh + vrv + (7 * vrm) + 114) / 31)
    day = ((vrh + vrv - (7 * vrm) + 114) % 31) + 1
    return datetime.date(year, month, day).toordinal()


def firstday(month, year, weekday):
    """Get first date for day of week in month."""
    daykey = {
        7: "sun",
        1: "mon",
        2: "tue",
        3: "wed",
        4: "thu",
        5: "fri",
        6: "sat"
    }
    for i in range(1, 8):
        firstdt = datetime.date(year, month, i)
        if daykey[firstdt.isoweekday()] == weekday:
            break
    return firstdt.toordinal()


def lastday(month, year, weekday):
    """Get last date for day of week in month."""
    daykey = {
        7: "sun",
        1: "mon",
        2: "tue",
        3: "wed",
        4: "thu",
        5: "fri",
        6: "sat"
    }
    nmonth, nyear = {
        True: (1, year + 1),
        False: (month + 1, year)
    }[month == 12]

    endofmonth = datetime.date(nyear, nmonth, 1).toordinal() - 1
    for i in range(0, 7):
        lastdt = datetime.date.fromordinal(endofmonth - i)
        if daykey[lastdt.isoweekday()] == weekday:
            break
    return lastdt.toordinal()


def getsunday(month, day, year, before=True):
    """Get first sunday next to date."""
    sundt = datetime.date(year, month, day)
    dow = sundt.isoweekday()
    if before is True:
        return {
            True: sundt.toordinal(),
            False: sundt.toordinal() - dow
        }[dow == 7]
    else:
        return {
            True: sundt.toordinal(),
            False: sundt.toordinal() + (7 - dow)
        }[dow == 7]


def genholidays(args):
    """Generate holiday dictionaries."""
    # some variables that will hold our dates
    easter = calceaster(args.y)
    weeks = []
    dates = []
    dates2 = []

    ###########################################################################

    # federal holidays
    for i in [(1, 1, "✯ New Years Day ✯"),
              (1, 15, "✯ Martin Luther King’s Birthday ✯"),
              (2, 22, "✯ Washington’s Birthday ✯"),
              (7, 4, "✯ Independence Day ✯"),
              (10, 12, "✯ Columbus Day ✯"),
              (11, 11, "✯ Veterans’ Day ✯"),
              (12, 25, "✯ Christmas Day ✯")]:
        dates.append((datetime.date(args.y, i[0], i[1]).toordinal(),
                      i[2]))

    for i in [(1, 15, "✯ Martin Luther King’s Birthday (Observed) ✯", 14),
              (2, 22, "✯ Washington’s Birthday (Observed) ✯", 14),
              (10, 12, "✯ Columbus Day (Observed) ✯", 7)]:
        tmp = firstday(i[0], args.y, "mon") + i[3]
        if tmp != datetime.date(args.y, i[0], i[1]).toordinal():
            dates.append((tmp, i[2]))

    dates.append((lastday(5, args.y, "mon"), "✯ Memorial Day ✯"))
    dates.append((firstday(9, args.y, "mon"), "✯ Labor Day ✯"))
    dates.append((firstday(11, args.y, "thu") + 21, "✯ Thanksgiving Day ✯"))
    if args.y % 4 == 1:
        dates.append((datetime.date(args.y, 1, 20).toordinal(),
                      "✯ Inauguration day ✯"))

    # national weeks recognized by presidential proclamation
    for i in [(3, "sun", 0, "Save Your Vision Week"),
              (3, "sun", 14, "National Poison Prevention Week"),
              (5, "fri", 9, "National Transportation Week"),
              (5, "sun", 14, "World Trade Week"),
              (5, "sun", 14, "National Hurricane Preparedness Week"),
              (7, "sun", 14, "Captive Nations Week"),
              (9, "sun", 14, "National Farm Safety and Health Week"),
              (10, "sun", 7, "National School Lunch Week"),
              (10, "sun", 14, "National Character Counts Week"),
              (10, "sun", 14, "National Forest Products Week"),
              (11, "thu", 17, "National Family Week"),
              (11, "thu", 17, "National Farm-City Week")]:
        weeks.append((firstday(i[0], args.y, i[1]) + i[2], i[3]))
    for i in [(4, 14, "Pan American Week"),
              (6, 14, "National Flag Week"),
              (9, 17, "Constitution Week"),
              (10, 9, "Fire Prevention Week"),
              (12, 10, "Human Rights Week")]:
        weeks.append((getsunday(i[0], i[1], args.y), i[2]))
    for i in [(4, "sat", 6, "National Volunteer Week"),
              (5, "mon", 8, "National Safe Boating Week")]:
        weeks.append((lastday(i[0], args.y, i[1]) - i[2], i[3]))
    # additional weeks that some people celebrate
    kwanzaa = datetime.date(args.y, 12, 26).toordinal()
    weeks.append((kwanzaa, "Kwanzaa"))

    # additional holidays recognized by presidential proclamation
    for i in [(1, 16, "Religious Freedom Day"),
              (2, 15, "Susan B. Anthony Day"),
              (3, 10, "Harriet Tubman Day"),
              (3, 25, "Greek Independence Day"),
              (3, 31, "Cesar Chavez Day"),
              (4, 6, "National Tartan Day"),
              (4, 9, "National Former Prisoner of War Recognition Day"),
              (4, 14, "Pan American Day"),
              (5, 1, "Loyalty Day"),
              (5, 1, "Law Day, U.S.A."),
              (5, 15, "Peace Officers Memorial Day"),
              (5, 19, "Malcolm X Day"),
              (5, 22, "National Maritime Day"),
              (5, 25, "National Missing Childrens Day"),
              (6, 14, "Flag Day"),
              (7, 27, "National Korean War Veterans Armistice Day"),
              (8, 16, "National Airborne Day"),
              (8, 26, "Women’s Equality Day"),
              (9, 11, "Patriot Day"),
              (9, 11, "Emergency Number Day"),
              (9, 17, "Citizenship Day"),
              (9, 22, "American Business Womens Day"),
              (9, 28, "National Good Neighbor Day"),
              (10, 6, "German-American Day"),
              (10, 9, "Leif Erikson Day"),
              (10, 11, "General Pulaski Memorial Day"),
              (10, 15, "White Cane Safety Day"),
              (10, 24, "United Nations Day"),
              (11, 9, "World Freedom Day"),
              (11, 15, "National Philanthropy Day"),
              (11, 15, "America Recycles Day"),
              (12, 1, "World AIDS Day"),
              (12, 3, "International Day of Persons with Disabilities"),
              (12, 7, "National Pearl Harbor Remembrance Day"),
              (12, 10, "Human Rights Day"),
              (12, 15, "Bill of Rights Day"),
              (12, 17, "Wright Brothers Day")]:
        dates2.append((datetime.date(args.y, i[0], i[1]).toordinal(), i[2]))
    for i in [(1, "sun", 14, "National Sanctity of Human Life Day"),
              (4, "thu", 7, "National D.A.R.E. Day"),
              (5, "thu", 0, "National Day of Prayer"),
              (5, "fri", 7, "Military Spouse Day"),
              (5, "sun", 7, "Mother’s Day"),
              (5, "fri", 14, "National Defense Transportation Day"),
              (5, "sat", 14, "Armed Forces Day"),
              (6, "mon", 0, "National Child’s Day"),
              (6, "sun", 14, "Father’s Day"),
              (9, "fri", 14, "National POW/MIA Recognition Day"),
              (9, "mon", 21, "Family Day"),
              (10, "mon", 0, "Child Health Day"),
              (11, "mon", 1, "Election Day"),
              (11, "thu", 22, "Native American Heritage Day")]:
        dates2.append((firstday(i[0], args.y, i[1]) + i[2], i[3]))
    for i in [(7, "sun", "Parent’s Day"),
              (9, "sun", "Gold Star Mothers Day")]:
        dates2.append((lastday(i[0], args.y, i[1]), i[2]))

    # daylight savings time
    for i in [(3, "sun", 7, "Daylight Savings Begins"),
              (11, "sun", 0, "Daylight Savings Ends")]:
        dates2.append((firstday(i[0], args.y, i[1]) + i[2], i[3]))

    # additional unofficial observances
    dates2.append((easter - 43, "Mardi Gras"))
    for i in [(2, 2, "Groundhog Day"),
              (2, 14, "Valentine’s Day"),
              (3, 8, "International Women’s Day"),
              (3, 14, "Pi Day"),
              (3, 17, "St. Patrick’s Day"),
              (4, 1, "April Fool’s Day"),
              (4, 22, "Earth Day"),
              (5, 1, "May Day"),
              (5, 5, "Cinco de Mayo"),
              (6, 19, "Juneteenth"),
              (6, 27, "Hellen Keller Day"),
              (9, 19, "International Talk Like a Pirate Day"),
              (10, 31, "Halloween"),
              (12, 24, "Christmas Eve"),
              (12, 31, "New Years Eve")]:
        dates2.append((datetime.date(args.y, i[0], i[1]).toordinal(), i[2]))
    for i in [(4, "fri", "Arbor Day")]:
        dates2.append((lastday(i[0], args.y, i[1]), i[2]))

    # return our dates
    return (weeks, dates, dates2)


def main():
    """Parse our command line arguments and generate calendar."""
    parser = argparse.ArgumentParser(
        description="Create a US Holiday calendar for a specified year."
    )
    parser.add_argument("-y",
                        type=int,
                        required=True,
                        metavar="Year")
    parser.add_argument("-w",
                        help="Include presidential proclamation weeks",
                        action="store_true")
    parser.add_argument("-d",
                        help="Include presidential proclamation days",
                        action="store_true")
    args = parser.parse_args()

    if args.y <= 1582:
        sys.exit("Year must be greater than 1582!")

    print("Generating US Holiday calendar for {}".format(args.y))

    msg = {
        True: "Including presidential proclamation weeks.",
        False: "NOT including presidential proclamation weeks."
    }[args.w]
    print(msg)

    msg = {
        True: "Including presidential proclamation days.",
        False: "NOT including presidential proclamation days."
    }[args.d]
    print(msg)

    ###########################################################################

    # ###################################### #
    weeks, dates, dates2 = genholidays(args)

    # ### Output ical file for dates and fdates.
    with open("holidays-{}.ics".format(args.y), "w") as ofile:
        uid = args.y * 1000
        created = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")

        # ical header
        ofile.write(HEADER.format(created).replace("\n", "\r\n"))

        # output presidential proclamation weeks
        uidnum = 0
        if args.w is True:
            for i in sorted(weeks, key=lambda x: x[0]):
                uidnum += 1
                uid = "usweeks{}{:02d}@adyeths".format(args.y, uidnum)
                dtstart = datetime.date.fromordinal(i[0]).strftime("%Y%m%d")
                dtend = datetime.date.fromordinal(i[0] + 7).strftime("%Y%m%d")
                event = VEVENT.format(
                    uid,
                    dtstart,
                    dtend,
                    i[1],
                    created)
                print(event.replace("\n", "\r\n"), file=ofile, end="\r\n")

        # output federal holidays
        uidnum = 0
        for i in sorted(dates, key=lambda x: x[0]):
            uidnum += 1
            uid = "usfederal{}{:02d}@adyeths".format(args.y, uidnum)
            dtstart = datetime.date.fromordinal(i[0]).strftime("%Y%m%d")
            dtend = datetime.date.fromordinal(i[0] + 1).strftime("%Y%m%d")
            event = VEVENT.format(
                uid,
                dtstart,
                dtend,
                i[1],
                created)
            print(event.replace("\n", "\r\n"), file=ofile, end="\r\n")

        # output federal proclamation days and other dates
        uidnum = 0
        if args.d:
            for i in sorted(dates2, key=lambda x: x[0]):
                uidnum += 1
                uid = "usdays{}{:02d}@adyeths".format(args.y, uidnum)
                dtstart = datetime.date.fromordinal(i[0]).strftime("%Y%m%d")
                dtend = datetime.date.fromordinal(i[0] + 1).strftime("%Y%m%d")
                event = VEVENT.format(
                    uid,
                    dtstart,
                    dtend,
                    i[1],
                    created)
                print(event.replace("\n", "\r\n"), file=ofile, end="\r\n")

        # ical footer
        ofile.write(FOOTER.replace("\n", "\r\n"))

# ---------------------------------------------------------------------------#


if __name__ == "__main__":
    main()
