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

import itertools
from toolz.itertoolz import sliding_window

from antrak.dao import track as track_dao
from antrak.db import tx
from antrak.nmea import parse_pos
from antrak.util import flatten

FMT_TRACK_LIST = '{:%Y-%m-%d} {} {}'.format

def filter_quality(positions):
    """
    Filter out bad quality positions.

    3D, good positions are kept - for `good` definition see Wikipedia
    article about `dilution of precision
    <https://en.wikipedia.org/wiki/Dilution_of_precision_(navigation)>`_.
    """
    return (
        p for p in positions
        if p.properties['is_3d']
            and p.properties['hdop'] < 5
            and p.properties['vdop'] < 5
            and p.properties['pdop'] < 5
    )

def check_altitude_speed(p1, p2):
    td = abs(p2.properties['timestamp'] - p1.properties['timestamp']).total_seconds()
    # TODO: make time difference and altitude speed limits configurable
    return td >= 10 or abs(p2.z - p1.z) / td < 10

def filter_altitude_speed(positions):
    return (
        p1 for p1, p2 in sliding_window(2, positions)
        if check_altitude_speed(p2, p1)
    )

@tx
def save_pos(dev, files):
    positions = flatten(parse_pos(open(fn)) for fn in files)
    positions = (p for p in positions if p)
    positions = filter_quality(positions)
    positions = filter_altitude_speed(positions)
    return track_dao.save_pos(dev, positions)

@tx
async def track_set(dev, trip, name, start, end):
    start, end = await track_dao.find_period(dev, start, end)
    task = await track_dao.add(dev, trip, name, start, end)
    return task

@tx
async def track_list(dev, query=''):
    data = await track_dao.track_list(dev, query=query)
    for item in data:
        print(FMT_TRACK_LIST(item['start'], item['trip'], item['name']))

# vim: sw=4:et:ai

