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
Database functions.
"""

import asyncpg
import logging
from shapely.wkb import loads as from_wkb

from antrak.util import to_wkb

logger = logging.getLogger(__name__)
conn = None  # TODO: use thread local context

SQL_SAVE_POINT = """
insert into position (device, timestamp, location)
values ($1, $2, $3)
"""

def tx(f):
    """
    Decorator to connect to a database and execute decorated function
    within database transaction.
    """
    async def execute(*args, **kw):
        # TODO:
        # - set to null after use
        # - reuse current connection if exists
        global conn

        # TODO: remove hardcoding
        conn = await asyncpg.connect(database='antrak')
        await conn.set_type_codec(
            'geometry', encoder=to_wkb, decoder=from_wkb, binary=True
        )
        async with conn.transaction():
            return (await f(*args, **kw))
    return execute

@tx
async def save_pos(dev, data):
    """
    Save positions to a database.

    :param dev: Device from which positions where obtained.
    :param data: Collection of positions to be saved in a database.
    """
    global conn

    data = ((dev, p.properties['timestamp'], p) for p in data)

    logger.debug('saving positions')
    await conn.executemany(SQL_SAVE_POINT, data)
    logger.debug('positions saved')

@tx
async def track_find_period(dev, start, end):
    global conn
    SQL_FIND_TRACK_PERIOD = """
select min(timestamp), max(timestamp)
from position
where device = $1 and timestamp between $2 and $3
"""
    data = await conn.fetch(SQL_FIND_TRACK_PERIOD, dev, start, end)
    return data[0]

@tx
async def track_add(dev, trip, name, start, end):
    global conn

    logger.debug('saving trip {} - {} from {} to {} (device={})'.format(
        trip, name, start, end, dev
    ))
    SQL_ADD_TRACK = """
insert into track (trip, name, device, start, "end")
values ($1, $2, $3, $4, $5)
"""
    await conn.execute(SQL_ADD_TRACK, trip, name, dev, start, end)

# vim: sw=4:et:ai
