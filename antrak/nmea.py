#
# AnTrak - Activity and location data analysis
#
# Copyright (C) 2017 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Parsing of GPS positions stored in NMEA format.
"""

import itertools
import logging
import pynmea2
from datetime import timezone
from shapely.geometry import Point

logger = logging.getLogger(__name__)

def parse_pos(f):
    """
    Read GPS positions from file-like object serving NMEA sentences. 
    """
    counter = Counter()
    data = (pynmea2.parse(line) for line in f)
    data = itertools.groupby(data, counter)
    data = (
        {v.identifier()[:-1]: v for v in items}
        for _, items in data
    )
    return (to_pos(v) for v in data)

def to_pos(item):
    """
    Convert dictionary of NMEA sentences into position objects.
    """
    rmc = item.get('GPRMC')
    gga = item.get('GPGGA')
    vtg = item.get('GPVTG')
    gsa = item.get('GPGSA')

    if not (rmc and gga and vtg and gsa):
        logger.warning('cannot parse {}'.format(item))
        return None
    ts = rmc.datetime.replace(tzinfo=timezone.utc)

    p = Point(rmc.longitude, rmc.latitude, gga.altitude)
    p.properties = {}
    p.properties['timestamp'] = ts
    p.properties['heading'] = vtg.true_track
    p.properties['speed'] = vtg.spd_over_grnd_kmph
    p.properties['is_3d'] = gsa.mode_fix_type == '3'
    p.properties['hdop'] = float(gsa.hdop)
    p.properties['vdop'] = float(gsa.vdop)
    p.properties['pdop'] = float(gsa.pdop)

    return p

class Counter:
    """
    `GPRMC` NMEA sentence counter.

    Creates a callable, which counts number of GPRMC sentences.

    The object can be used with `itertools.groupby` function to group
    `GPRMC` sentences with other NMEA sentences.
    """
    def __init__(self):
        self.counter = 0

    def __call__(self, v):
        # see https://github.com/Knio/pynmea2/issues/61
        # if v.identifier() == 'GPRMC':
        if v.identifier().startswith('GPRMC'):
            self.counter += 1

        return self.counter

# vim: sw=4:et:ai
