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

"""
GPX format parsing functions.
"""

import logging
from dateutil.parser import parse as date_parse
from lxml import etree as et
from shapely.geometry import Point

logger = logging.getLogger(__name__)

NS = {
    'gpx': 'http://www.topografix.com/GPX/1/1'
}

def parse_points(f):
    doc = et.parse(f)
    items = doc.iterfind('//gpx:trkpt', namespaces=NS)
    for item in items:
        lat = float(item.get('lat'))
        lon = float(item.get('lon'))

        ts = item.xpath('gpx:time/text()', namespaces=NS)
        ts = date_parse(ts[0], ignoretz=True)  # UTC assumed

        elevation = item.xpath('gpx:ele/text()', namespaces=NS)
        elevation = float(elevation[0])

        p = Point(lon, lat, elevation)
        p.properties = {}
        p.properties['timestamp'] = ts
        #p.properties['heading'] = heading
        #p.properties['speed'] = speed
        yield p

# vim: sw=4:et:ai
