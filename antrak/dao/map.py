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

from antrak.db import tx

SQL_LOAD_POS = """
select t.trip, t.name, t.start,
    array[
        min(st_x(p.location)), min(st_y(p.location)),
        max(st_x(p.location)), max(st_y(p.location))
    ] as extent,
    array_agg(array[st_x(p.location), st_y(p.location)]) as positions
from track t
    inner join position p on t.device = p.device
        and p.timestamp between t.start and t.end
where p.device = $1 and t.trip || ' ' || t.name ~* $2
group by t.trip, t.name, t.start
order by t.trip, t.start
"""

@tx
async def load_pos(dev, query):
    data = await tx.conn.fetch(SQL_LOAD_POS, dev, query)
    return data

# vim: sw=4:et:ai
