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

import logging
from antrak.db import tx

logger = logging.getLogger(__name__)

SQL_SAVE_POS = """
insert into position (device, timestamp, location, heading, speed)
values ($1, $2, $3, $4, $5)
"""

SQL_FIND_TRACK_PERIOD = """
select min(timestamp), max(timestamp)
from position
where device = $1 and timestamp between $2 and $3
"""

SQL_ADD_TRACK = """
insert into track (trip, name, device, start, "end")
values ($1, $2, $3, $4, $5)
"""

SQL_TRACK_LIST = """
select trip, name, start, "end"
from track
where device = $1 {}
order by start, trip, name
"""

@tx
async def save_pos(dev, data):
    """
    Save positions to a database.

    :param dev: Device from which positions where obtained.
    :param data: Collection of positions to be saved in a database.
    """
    extract = lambda p: (
        dev,
        p.properties['timestamp'],
        p,
        p.properties['heading'],
        p.properties['speed'],
    )
    data = (extract(p) for p in data)

    logger.debug('saving positions')
    await tx.conn.executemany(SQL_SAVE_POS, data)
    logger.debug('positions saved')

@tx
async def find_period(dev, start, end):
    data = await tx.conn.fetch(SQL_FIND_TRACK_PERIOD, dev, start, end)
    return data[0]

@tx
async def add(dev, trip, name, start, end):
    logger.debug('saving trip {} - {} from {} to {} (device={})'.format(
        trip, name, start, end, dev
    ))
    await tx.conn.execute(SQL_ADD_TRACK, trip, name, dev, start, end)

@tx
async def track_list(dev, query=''):
    if query:
        cond = 'and trip || \' \' || name ~* $2'
        args = dev, query
    else:
        cond = ''
        args = (dev,)

    sql = SQL_TRACK_LIST.format(cond)
    return (await tx.conn.fetch(sql, *args))

# vim: sw=4:et:ai
