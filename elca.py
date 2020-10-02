#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate ical for church year."""
import sys
import argparse
import datetime
from math import floor

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
DTSTART;VALUE=DATE:{}
DTEND;VALUE=DATE:{}
SUMMARY:{}
DTSTAMP:{}
TRANSP:TRANSPARENT
STATUS:CONFIRMED
END:VEVENT"""

# ---------------------------------------------------------------------------#


def whichyear(year):
    """Determine which church year starts on advent of the specified year."""
    return {0: "🄰", 1: "🄱", 2: "🄲"}.get((year - 1992) % 3)
    # 🄰 🅰  🄱 🅱  🄲 🅲


def calceaster(year):
    """Get date as ordinal for easter using Meeus algorithm."""
    vrh = (
        (19 * (year % 19))
        + floor(year / 100)
        - int(floor(year / 100) / 4)
        - (int((floor(year / 100) - int((floor(year / 100) + 8) / 25) + 1) / 3))
        + 15
    ) % 30
    vrv = (
        32
        + (2 * int(floor(year / 100) % 4))
        + (2 * int((year % 100) / 4))
        - vrh
        - ((year % 100) % 4)
    ) % 7
    vrm = int(((year % 19) + (11 * vrh) + (22 * vrv)) / 451)

    month = int((vrh + vrv + (7 * vrm) + 114) / 31)
    day = ((vrh + vrv - (7 * vrm) + 114) % 31) + 1
    return datetime.date(year, month, day).toordinal()


def getsunday(month, day, year):
    """Get first sunday on or after date."""
    dte = datetime.date(year, month, day)
    dow = 7 - dte.isoweekday()
    return {True: dte.toordinal(), False: dte.toordinal() + dow}.get(dow == 0)


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
        33: "rd",
    }.get(i, "th")
    idx = dte + (7 * (i - 1))
    return (tmp, idx)


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
        "afterchristmas2": getsunday(1, 6, year) - getsunday(1, 2, year),
    }
    dates = {}
    for i in getsundays(year):
        dates[i] = None

    ###########################################################################

    # afterchristmas... previous church year
    if dtx["afterchristmas1"] in dates:
        dates[dtx["afterchristmas1"]] = "1st Sunday after Christmas 🅦 {}".format(
            thisyear
        )
    if dtx["afterchristmas2"] != 0:
        dates[dtx["afterepiphany"] - 7] = "2nd Sunday after Christmas 🅦 {}".format(
            thisyear
        )

    # calculatable dates (Order is important here!)
    for i in [
        (dtx["afterepiphany"], 2, 10),
        (dtx["lent"], 1, 6),
        (dtx["easter"], 2, 8),
        (dtx["pentecost"] + 7, 2, 28),
        (dtx["advent"], 1, 5),
    ]:
        for j in range(i[1], i[2]):
            tmp, idx = idxvalue(j, i[0])
            text = {
                dtx[
                    "afterepiphany"
                ]: "Sunday after the Epiphany (Lectionary {}) 🅖 {}".format(j, thisyear),
                dtx["lent"]: "Sunday in Lent 🅟 {}".format(thisyear),
                dtx["easter"]: "Sunday of Easter 🅦 {}".format(thisyear),
                dtx["pentecost"] + 7: "Sunday after Pentecost 🅖 {}".format(thisyear),
                dtx["advent"]: "Sunday of Advent 🅑 {}".format(nextyear),
            }.get(i[0])
            dates[idx] = "{}{} {}".format(j, tmp, text)

    # specific dates (Order is important here!)
    dates[dtx["epiphany"]] = "Epiphany 🅦 {}".format(thisyear)
    dates[dtx["afterepiphany"]] = "Baptism of our Lord (Lectionary 1) 🅦 {}".format(
        thisyear
    )
    dates[dtx["lent"] - 4] = "Ash Wednesday 🅟 {}".format(thisyear)
    dates[dtx["easter"] - 7] = "Palm Sunday 🅢🅟 {}".format(thisyear)
    dates[dtx["easter"] - 3] = "Maundy Thursday 🅢🅦 {}".format(thisyear)
    dates[dtx["easter"] - 2] = "Good Friday {}".format(thisyear)
    dates[dtx["easter"] - 1] = "Easter Vigil {}".format(thisyear)
    dates[dtx["easter"]] = "Resurrection of Our Lord 🅦G {}".format(thisyear)
    dates[dtx["easter"] + 39] = "Ascension of the Lord 🅦 {}".format(thisyear)
    dates[dtx["pentecost"]] = "Day of Pentecost 🅡 {}".format(thisyear)
    dates[dtx["pentecost"] + 7] = "The Holy Trinity 🅦 {}".format(thisyear)
    dates[dtx["christking"]] = "Christ the King (Lectionary 34) 🅦 {}".format(thisyear)
    dates[datetime.date(year, 12, 25).toordinal()] = "Nativity of Our Lord 🅦"
    if dtx["afterchristmas"] in dates:
        dates[dtx["afterchristmas"]] = "1st Sunday after Christmas 🅦 {}".format(
            nextyear
        )

    # Add lectionary number to Sundays after Pentecost
    # this must follow the specific dates listed above!
    lect = 33
    for i in sorted(dates.keys(), reverse=True):
        if dates[i] is not None:
            if dates[i].endswith("Sunday after Pentecost 🅖 {}".format(thisyear)):
                dates[i] = dates[i].replace(" 🅖 {}".format(thisyear), "")
                dates[i] = "{} (Lectionary {}) 🅖 {}".format(dates[i], lect, thisyear)
                lect -= 1

    # return our results
    return dates


def getfdates(year):
    """Get fixed dates in calendar year for lesser festivals."""
    return (
        (datetime.date(year, 1, 1).toordinal(), "NAME OF JESUS 🅦"),
        (datetime.date(year, 1, 18).toordinal(), "CONFESSION OF PETER 🅦"),
        (datetime.date(year, 1, 25).toordinal(), "CONVERSION OF PAUL 🅦"),
        (datetime.date(year, 2, 2).toordinal(), "PRESENTATION OF OUR LORD 🅦"),
        (datetime.date(year, 3, 19).toordinal(), "JOSEPH, GUARDIAN OF JESUS 🅦"),
        (datetime.date(year, 3, 25).toordinal(), "ANNUNCIATION OF OUR LORD 🅦"),
        (datetime.date(year, 4, 25).toordinal(), "MARK, EVANGELIST 🅢🅡"),
        (datetime.date(year, 5, 1).toordinal(), "PHILIP AND JAMES, APOSTLES 🅢🅡"),
        (datetime.date(year, 5, 14).toordinal(), "MATTHIAS, APOSTLE 🅢🅡"),
        (datetime.date(year, 5, 31).toordinal(), "VISITATION OF MARY TO ELIZABETH 🅦"),
        (datetime.date(year, 6, 11).toordinal(), "BARNABAS, APOSTLE 🅢🅡"),
        (datetime.date(year, 6, 24).toordinal(), "JOHN THE BAPTIST 🅦"),
        (datetime.date(year, 6, 29).toordinal(), "PETER AND PAUL, APOSTLES 🅢🅡"),
        (datetime.date(year, 7, 3).toordinal(), "THOMAS, APOSTLE 🅢🅡"),
        (datetime.date(year, 7, 22).toordinal(), "MARY MAGDALENE, APOSTLE 🅦"),
        (datetime.date(year, 7, 25).toordinal(), "JAMES, APOSTLE 🅢🅡"),
        (datetime.date(year, 8, 15).toordinal(), "MARY, MOTHER OF OUR LORD 🅦"),
        (datetime.date(year, 8, 24).toordinal(), "BARTHOLOMEW, APOSTLE 🅢🅡"),
        (datetime.date(year, 9, 14).toordinal(), "HOLY CROSS DAY 🅢🅡"),
        (datetime.date(year, 9, 21).toordinal(), "MATTHEW, APOSTLE AND EVANGELIST 🅢🅡"),
        (datetime.date(year, 9, 29).toordinal(), "MICHAEL AND ALL ANGELS 🅦"),
        (datetime.date(year, 10, 18).toordinal(), "LUKE, EVANGELIST 🅢🅡"),
        (datetime.date(year, 10, 28).toordinal(), "SIMON AND JUDE, APOSTLES 🅢🅡"),
        (datetime.date(year, 10, 31).toordinal(), "REFORMATION DAY 🅡"),
        (datetime.date(year, 11, 1).toordinal(), "ALL SAINTS DAY 🅦"),
        (datetime.date(year, 11, 30).toordinal(), "ANDREW, APOSTLE 🅢🅡"),
        (datetime.date(year, 12, 26).toordinal(), "STEPHEN, DEACON AND MARTYR 🅢🅡"),
        (datetime.date(year, 12, 27).toordinal(), "JOHN, APOSTLE AND EVANGELIST 🅦"),
        (datetime.date(year, 12, 28).toordinal(), "THE HOLY INNOCENTS, MARTYRS 🅢🅡"),
    )


def getfdates2(year):
    """Get fixed dates in calendar year for commemorations."""
    return (
        (
            datetime.date(year, 1, 2).toordinal(),
            "Johann Konrad Wilhelm Loehe, renewer of the church, 1872 🅦",
        ),
        (
            datetime.date(year, 1, 15).toordinal(),
            "Martin Luther King Jr., renewer of society, martyr, 1968 🅢🅡",
        ),
        (
            datetime.date(year, 1, 17).toordinal(),
            "Antony of Egypt, renewer of the church, c.356 🅦",
        ),
        (
            datetime.date(year, 1, 17).toordinal(),
            "Pachomius, renewer of the church, 346 🅦",
        ),
        (
            datetime.date(year, 1, 18).toordinal(),
            "Week of Prayer for Christian Unity begins",
        ),
        (
            datetime.date(year, 1, 19).toordinal(),
            "Henry, Bishop of Uppsala, martyr, 1156 🅢🅡",
        ),
        (datetime.date(year, 1, 21).toordinal(), "Agnes, martyr, c.304 🅢🅡"),
        (
            datetime.date(year, 1, 25).toordinal(),
            "Week of Prayer for Christian Unity ends",
        ),
        (
            datetime.date(year, 1, 26).toordinal(),
            "Timothy, Titus, and Silas, missionaries 🅦",
        ),
        (
            datetime.date(year, 1, 27).toordinal(),
            "Lydia, Dorcas, and Phoebe, witnesses to the faith 🅦",
        ),
        (datetime.date(year, 1, 28).toordinal(), "Thomas Aquinas, teacher, 1274 🅦"),
        (
            datetime.date(year, 2, 3).toordinal(),
            "Ansgar, Bishop of Hamburg, missionary to Denmark and Sweden, 865 🅦",
        ),
        (datetime.date(year, 2, 5).toordinal(), "The Martyrs of Japan, 1597 🅢🅡"),
        (
            datetime.date(year, 2, 14).toordinal(),
            "Cyril, monk, 869; Methodius, bishop, 885; missionaries to the Slavs 🅦",
        ),
        (
            datetime.date(year, 2, 18).toordinal(),
            "Martin Luther, renewer of the church, 1546 🅦",
        ),
        (
            datetime.date(year, 2, 23).toordinal(),
            "Polycarp, Bishop of Smyrna, martyr, 156 🅢🅡",
        ),
        (datetime.date(year, 2, 25).toordinal(), "Elizabeth Fedde, deaconess, 1921 🅦"),
        (datetime.date(year, 3, 1).toordinal(), "George Herbert, hymnwriter, 1633 🅦"),
        (
            datetime.date(year, 3, 2).toordinal(),
            "John Wesley, 1791; Charles Wesley, 1788; renewers of the church 🅦",
        ),
        (
            datetime.date(year, 3, 7).toordinal(),
            "Perpetua and Felicity and companions, martyrs at Carthage, 202 🅢🅡",
        ),
        (
            datetime.date(year, 3, 10).toordinal(),
            "Harriet Tubman, 1913; Sojourner Truth, 1883; renewers of society 🅦",
        ),
        (
            datetime.date(year, 3, 12).toordinal(),
            "Gregory the Great, Bishop of Rome, 604 🅦",
        ),
        (
            datetime.date(year, 3, 17).toordinal(),
            "Patrick, bishop, missionary to Ireland, 461 🅦",
        ),
        (
            datetime.date(year, 3, 21).toordinal(),
            "Thomas Cranmer, Bishop of Canterbury, martyr, 1556 🅢🅡",
        ),
        (
            datetime.date(year, 3, 22).toordinal(),
            "Jonathan Edwards, teacher, missionary to American Indians, 1758 🅦",
        ),
        (
            datetime.date(year, 3, 24).toordinal(),
            "Oscar Arnulfo Romero, Bishop of El Salvador, martyr, 1980 🅢🅡",
        ),
        (
            datetime.date(year, 3, 29).toordinal(),
            "Hans Nielsen Hauge, renewer of the church, 1824 🅦",
        ),
        (datetime.date(year, 3, 31).toordinal(), "John Donne, poet, 1631 🅦"),
        (
            datetime.date(year, 4, 4).toordinal(),
            "Benedict the African, confessor, 1589 🅦",
        ),
        (
            datetime.date(year, 4, 6).toordinal(),
            "Albrecht Dürer, 1528; Matthias Grünewald, 1529; Lucas Cranach, 1553; artists 🅦",
        ),
        (
            datetime.date(year, 4, 9).toordinal(),
            "Dietrich Bonhoeffer, theologian, 1945 🅦",
        ),
        (
            datetime.date(year, 4, 10).toordinal(),
            "Mikael Agricola, Bishop of Turku, 1557 🅦",
        ),
        (
            datetime.date(year, 4, 19).toordinal(),
            "Olavus Petri, priest, 1552; Laurentius Petri, Bishop of Uppsala, 1572; renewers of the church 🅦",
        ),
        (
            datetime.date(year, 4, 21).toordinal(),
            "Anselm, Bishop of Canterbury, 1109 🅦",
        ),
        (
            datetime.date(year, 4, 23).toordinal(),
            "Toyohiko Kagawa, renewer of society, 1960 🅦",
        ),
        (
            datetime.date(year, 4, 29).toordinal(),
            "Catherine of Siena, theologian, 1380 🅦",
        ),
        (
            datetime.date(year, 5, 2).toordinal(),
            "Athanasius, Bishop of Alexandria, 373 🅦",
        ),
        (datetime.date(year, 5, 4).toordinal(), "Monica, mother of Augustine, 387 🅦"),
        (
            datetime.date(year, 5, 8).toordinal(),
            "Julian of Norwich, renewer of the church c.1416 🅦",
        ),
        (
            datetime.date(year, 5, 9).toordinal(),
            "Nicolaus Ludwig von Zinzendorf, renewer of the church, hymnwriter, 1760 🅦",
        ),
        (
            datetime.date(year, 5, 18).toordinal(),
            "Erik, King of Sweden, martyr, 1160 🅢🅡",
        ),
        (
            datetime.date(year, 5, 21).toordinal(),
            "Helena, mother of Constantine, c.330 🅦",
        ),
        (
            datetime.date(year, 5, 24).toordinal(),
            "Nicolaus Copernicus, 1543; Leonhard Euler, 1783; scientists 🅦",
        ),
        (
            datetime.date(year, 5, 27).toordinal(),
            "John Calvin, renewer of the church, 1564 🅦",
        ),
        (datetime.date(year, 5, 29).toordinal(), "Jiří Třanovský, hymnwriter, 1637 🅦"),
        (datetime.date(year, 6, 1).toordinal(), "Justin, martyr at Rome, c.165 🅢🅡"),
        (datetime.date(year, 6, 3).toordinal(), "The Martyrs of Uganda, 1886 🅢🅡"),
        (datetime.date(year, 6, 3).toordinal(), "John XXIII, Bishop of Rome, 1963 🅦"),
        (
            datetime.date(year, 6, 5).toordinal(),
            "Boniface, Bishop of Mainz, missionary to Germany, martyr, 754 🅢🅡",
        ),
        (
            datetime.date(year, 6, 7).toordinal(),
            "Seattle, chief of the Duwamish Confederacy, 1866 🅦",
        ),
        (
            datetime.date(year, 6, 9).toordinal(),
            "Columba, 597; Aidan, 651, Bede, 735; renewers of the church 🅦",
        ),
        (
            datetime.date(year, 6, 14).toordinal(),
            "Basil the Great, Bishop of Caesarea, 379 🅦",
        ),
        (datetime.date(year, 6, 14).toordinal(), "Gregory, Bishop of Nyssa, c.385 🅦"),
        (
            datetime.date(year, 6, 14).toordinal(),
            "Gregory of Nazianzus, Bishop of Constantinople, c.389 🅦",
        ),
        (datetime.date(year, 6, 14).toordinal(), "Macrina, teacher, c.379 🅦"),
        (
            datetime.date(year, 6, 21).toordinal(),
            "Onesimos Nesib, translator, evangelist, 1931 🅦",
        ),
        (
            datetime.date(year, 6, 25).toordinal(),
            "Presentation of the Augsburg Confession, 1530 🅦",
        ),
        (
            datetime.date(year, 6, 25).toordinal(),
            "Philipp Melanchthon, renewer of the church, 1560 🅦",
        ),
        (datetime.date(year, 6, 27).toordinal(), "Cyril, Bishop of Alexandria, 444 🅦"),
        (datetime.date(year, 6, 28).toordinal(), "Irenaeus, Bishop of Lyons, c.202 🅦"),
        (
            datetime.date(year, 7, 1).toordinal(),
            "Catherine winkworth, 1878; John Mason Neale, 1866; hymn translators 🅦",
        ),
        (datetime.date(year, 7, 6).toordinal(), "Jan Hus, martyr, 1415 🅢🅡 "),
        (
            datetime.date(year, 7, 11).toordinal(),
            "Benedict of Nursia, Abbot of Monte Cassino, c.540 🅦",
        ),
        (
            datetime.date(year, 7, 12).toordinal(),
            "Nathan Söderblom, Bishop of Uppsala, 1931 🅦",
        ),
        (
            datetime.date(year, 7, 17).toordinal(),
            "Bartolemé de Las Casas, missionary to the Indies, 1566 🅦",
        ),
        (
            datetime.date(year, 7, 23).toordinal(),
            "Birgitta of Sweden, renewer of the church, 1373 🅦",
        ),
        (
            datetime.date(year, 7, 28).toordinal(),
            "Johann Sebastian Bach, 1750; Heinrich Schütz, 1672; George Frederick Handel, 1759; musicians 🅦",
        ),
        (
            datetime.date(year, 7, 29).toordinal(),
            "Mary, Martha, and Lazarus of Bethany 🅦",
        ),
        (
            datetime.date(year, 7, 29).toordinal(),
            "Olaf, King of Norway, martyr, 1030 🅢🅡",
        ),
        (
            datetime.date(year, 8, 8).toordinal(),
            "Dominic, founder of the Order of Preachers (Dominicans), 1221 🅦",
        ),
        (datetime.date(year, 8, 10).toordinal(), "Lawrence, deacon, martyr, 258 🅢🅡"),
        (
            datetime.date(year, 8, 11).toordinal(),
            "Clare, Abbess of San Damiano, 1253 🅦",
        ),
        (
            datetime.date(year, 8, 13).toordinal(),
            "Florence Nightingale, 1910; Clara Maass, 1901; renewers of society 🅦",
        ),
        (
            datetime.date(year, 8, 14).toordinal(),
            "Maximilian Kolbe, 1941; Kaj Munk, 1944; martyrs 🅢🅡",
        ),
        (datetime.date(year, 8, 20).toordinal(), "Bernard, Abbot of Clairvaux, 1153 🅦"),
        (datetime.date(year, 8, 28).toordinal(), "Augustine, Bishop of Hippo, 430 🅦"),
        (
            datetime.date(year, 8, 28).toordinal(),
            "Moses the Black, monk, martyr, c.400 🅢🅡",
        ),
        (
            datetime.date(year, 9, 2).toordinal(),
            "Nikolai Frederik Severin Grundtvig, bishop, renewer of the church, 1872 🅦",
        ),
        (
            datetime.date(year, 9, 9).toordinal(),
            "Peter Claver, priest, missionary to Colombia 1654 🅦",
        ),
        (
            datetime.date(year, 9, 13).toordinal(),
            "John Chrysostom, Bishop of Constantinople, 407 🅦",
        ),
        (
            datetime.date(year, 9, 16).toordinal(),
            "Cyprian, Bishop of Carthage, martyr, c.258 🅢🅡",
        ),
        (datetime.date(year, 9, 17).toordinal(), "Hildegard, Abbess of Bingen, 1179 🅦"),
        (
            datetime.date(year, 9, 18).toordinal(),
            "Dag Hammarskjöld, renewer of society, 1961 🅦",
        ),
        (datetime.date(year, 9, 30).toordinal(), "Jerome, translator, teacher, 420 🅦"),
        (
            datetime.date(year, 10, 4).toordinal(),
            "Francis of Assisi, renewer of the church, 1226 🅦",
        ),
        (
            datetime.date(year, 10, 4).toordinal(),
            "Theodor Fliedner, renewer of society, 1864 🅦",
        ),
        (
            datetime.date(year, 10, 6).toordinal(),
            "William Tyndale, translator, martyr, 1536 🅢🅡",
        ),
        (
            datetime.date(year, 10, 7).toordinal(),
            "Henry Melchior Muhlenberg, pastor in North America, 1787 🅦",
        ),
        (
            datetime.date(year, 10, 15).toordinal(),
            "Teresa of Avila, teacher, renewer of the church, 1582 🅦",
        ),
        (
            datetime.date(year, 10, 17).toordinal(),
            "Ignatius, Bishop of Antioch, martyr, c.115 🅢🅡",
        ),
        (
            datetime.date(year, 10, 23).toordinal(),
            "James of Jerusalem, martyr, c.62 🅢🅡",
        ),
        (
            datetime.date(year, 10, 26).toordinal(),
            "Philipp Nicolai, 1608; Johann Heermann, 1647; Paul Gerhardt, 1676; hymnwriters 🅦",
        ),
        (
            datetime.date(year, 11, 3).toordinal(),
            "Martín de Porres, renewer of society, 1639 🅦",
        ),
        (
            datetime.date(year, 11, 7).toordinal(),
            "John Christian Frederick Heyer, 1873; Bartholomaeus Ziegenbalg, 1719; Ludwig Nommensen, 1918; missionaries 🅦",
        ),
        (datetime.date(year, 11, 11).toordinal(), "Martin, Bishop of Tours, 397 🅦"),
        (
            datetime.date(year, 11, 11).toordinal(),
            "Søren Aabye Kierkegaard, teacher, 1855 🅦",
        ),
        (
            datetime.date(year, 11, 17).toordinal(),
            "Elizabeth of Hungary, renewer of society, 1231 🅦",
        ),
        (datetime.date(year, 11, 23).toordinal(), "Clement, Bishop of Rome, c.100 🅦"),
        (
            datetime.date(year, 11, 23).toordinal(),
            "Miguel Agustín Pro, martyr, 1927 🅢🅡",
        ),
        (
            datetime.date(year, 11, 24).toordinal(),
            "Justus Falckner, 1723; Jehu Jones, 1852; William Passavant, 1894; Pastors in North America 🅦",
        ),
        (datetime.date(year, 11, 25).toordinal(), "Isaac Watts, hymnwriter, 1748 🅦"),
        (
            datetime.date(year, 12, 3).toordinal(),
            "Francis Xavier, missionary to Asia, 1552 🅦",
        ),
        (
            datetime.date(year, 12, 4).toordinal(),
            "John of Damascus, theologian and hymnwriter, c.749 🅦",
        ),
        (datetime.date(year, 12, 6).toordinal(), "Nicholas, Bishop of Myra, c.342 🅦"),
        (datetime.date(year, 12, 7).toordinal(), "Ambrose, Bishop of Milan, 397 🅦"),
        (datetime.date(year, 12, 13).toordinal(), "Lucy, martyr, 304 🅢🅡"),
        (
            datetime.date(year, 12, 14).toordinal(),
            "John of the Cross, renewer of the church, 1591 🅦",
        ),
        (
            datetime.date(year, 12, 20).toordinal(),
            "Katharina von Bora Luther, renewer of the church, 1552 🅦",
        ),
    )


def main():
    """Main routine to generate a yearly calendar for the church year."""
    parser = argparse.ArgumentParser(
        description="""
            Generate church year calendar for calendar year.
        """
    )
    parser.add_argument(
        "-y", type=int, metavar="Year", default=datetime.date.today().year
    )
    args = parser.parse_args()

    if args.y <= 1992:
        print("Year must be greater than or equal to 1992!")
        sys.exit()

    print("Generating church calendar for {}".format(args.y), file=sys.stderr)

    ###########################################################################

    # ## sundays in the year...
    dates = getdates(args.y)

    # ## fixed dates for lesser festivals.
    fdates = getfdates(args.y)

    # ## fixed dates for commemorations.
    fdates2 = getfdates2(args.y)

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
            event = VEVENT.format(uid, dtstart, dtend, dates[i], created)
            print(event.replace("\n", "\r\n"), file=ofile, end="\r\n")

        # output lesser festivals
        uidnum = 0
        for i in fdates:
            uidnum += 1
            uid = "elcalesser{}{:03d}@adyeths".format(args.y, uidnum)
            dtstart = datetime.date.fromordinal(i[0]).strftime("%Y%m%d")
            dtend = datetime.date.fromordinal(i[0] + 1).strftime("%Y%m%d")
            event = VEVENT.format(uid, dtstart, dtend, i[1], created)
            print(event.replace("\n", "\r\n"), file=ofile, end="\r\n")

        # output commemorations
        uidnum = 0
        for i in fdates2:
            uidnum += 1
            uid = "elcacommemorations{}{:03d}@adyeths".format(args.y, uidnum)
            dtstart = datetime.date.fromordinal(i[0]).strftime("%Y%m%d")
            dtend = datetime.date.fromordinal(i[0] + 1).strftime("%Y%m%d")
            event = VEVENT.format(uid, dtstart, dtend, i[1], created)
            print(event.replace("\n", "\r\n"), file=ofile, end="\r\n")

        # ical footer
        ofile.write(FOOTER.replace("\n", "\r\n"))


# ---------------------------------------------------------------------------#


if __name__ == "__main__":
    main()
