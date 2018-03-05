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

import asyncio
import cairocffi as cairo
import functools
import geotiler
import logging
import math
import redis
from geotiler.cache import redis_downloader
from antrak.dao import map as map_dao
from antrak.db import tx

logger = logging.getLogger(__name__)

FMT_MAP_FILENAME = '{0[start]:%Y-%m-%d} - {0[trip]} - {0[name]}.png'.format
ALPHA = 0.5
RADIUS = 1

@tx
async def render(dev, query, provider, size):
    client = redis.Redis('localhost')
    downloader = redis_downloader(client)
    render = functools.partial(render_map, downloader, provider, size)

    data = await map_dao.load_pos(dev, query)
    tasks = (
        render(item['positions'], item['extent'], FMT_MAP_FILENAME(item))
        for item in data
    )
    return (await asyncio.gather(*tasks))

async def render_map(downloader, provider, size, positions, extent, output):
    logger.debug('rendering map {}: {}'.format(output, extent))
    mm = geotiler.Map(size=size, extent=extent, provider=provider)
    img = await geotiler.render_map_async(mm, downloader=downloader)

    buff = bytearray(img.convert('RGBA').tobytes('raw', 'BGRA'))
    surface = cairo.ImageSurface.create_for_data(
        buff, cairo.FORMAT_ARGB32, *size
    )
    cr = cairo.Context(surface)

    points = (mm.rev_geocode(p) for p in positions)
    for x, y in points:
        cr.set_source_rgba(1.0, 0.0, 0.0, ALPHA)
        cr.arc(x, y, RADIUS, 0, 2 * math.pi)
        cr.fill()
        cr.stroke()

    surface.write_to_png(output)
    logger.debug('written {}'.format(output))

# vim: sw=4:et:ai
