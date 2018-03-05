#
# AnTrak - Activity and location data analysis
#
# Copyright (C) 2017-2018 by Artur Wroblewski <wrobell@riseup.net>
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
import operator
from datetime import timedelta

from antrak.dao import report as report_dao
from antrak.db import tx

FMT_TRACK_STATS = ' {:%Y-%m-%d} {:%H:%M:%S} {:%H:%M:%S}  {:30}  {}  {:4} km {:4} km/h'.format

async def track_stats(dev, query):
    data = await report_dao.track_summary(dev, query)
    data = itertools.groupby(data, operator.itemgetter('trip'))

    for trip, items in data:
        print(trip)
        for item in items:
            print_track(item)

def print_track(item):
    duration = timedelta(seconds=item['duration'])
    distance = round(item['distance'] / 1000)
    max_speed = round(item['max_speed'])

    s = FMT_TRACK_STATS(
        item['start'], item['start'], item['end'],
        item['name'],
        duration, distance,
        max_speed
    )
    print(s)

# vim: sw=4:et:ai
