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

import logging
from antrak.db import tx

logger = logging.getLogger(__name__)

SQL_TRACK_SUMMARY = """
select t.trip, t.name, t.start, t.end,
    extract('epoch' from t.end - t.start) as duration, -- duration in seconds
    -- FIXME: what is best tolerance value for wgs84?
    st_length(st_simplify(st_makeline(p.location), 0.000300), false) as distance, -- length in meters
    max(speed) as max_speed
from track t
    inner join position p on t.device = p.device
        and p.timestamp between t.start and t.end
where p.device = $1 and t.trip || ' ' || t.name ~* $2
group by t.trip, t.name, t.start, t.end
order by t.trip, t.start
"""

@tx
async def track_summary(dev, query):
    # TODO: support tsearch optionally
    return (await tx.conn.fetch(SQL_TRACK_SUMMARY, dev, query))

# vim: sw=4:et:ai
