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

from antrak.dao import track as track_dao
from antrak.db import tx
from antrak.nmea import parse_points
from antrak.util import flatten

FMT_TRACK_LIST = '{:%Y-%m-%d} {} {}'.format

@tx
def save_pos(dev, files):
    data = flatten(parse_points(open(fn)) for fn in files)
    return track_dao.save_pos(dev, data)

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

