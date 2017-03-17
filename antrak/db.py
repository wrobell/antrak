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

class TxManager:
    """
    Decorative database connection and transaction manager.

    An instance of the class is a decorator. Decorated functions can be
    called one within each other and they will share the same database
    connection and transaction.

    :var conn: Database connection.
    :var dsn: Database connection string.
    :var _nested: Counter to track nested calls. Close connection when
        equals to zero.
    """
    def __init__(self):
        self.conn = None

        # TODO: remove hardcoding
        self.dsn = 'postgres:antrak'
        self._nested = 0

    def __call__(self, f):
        """
        Decorator to connect to a database and execute decorated function
        within database transaction.
        """
        async def execute(*args, **kw):
            try:
                self._nested += 1
                if self.conn is None:
                    logger.debug('create db connection')
                    self.conn = await asyncpg.connect(self.dsn)
                    await self.conn.set_type_codec(
                        'geometry', encoder=to_wkb, decoder=from_wkb, binary=True
                    )
                else:
                    logger.debug('reusing db connection')

                async with self.conn.transaction():
                    return (await f(*args, **kw))
            finally:
                self._nested -= 1
                if self.conn and self._nested == 0:
                    logger.debug('closing connection')
                    await self.conn.close()
                    self.conn = None

                assert self._nested >= 0 and (
                    self.conn and self._nested > 0
                    or not self.conn and self._nested == 0
                ), (self.conn, self._nested)
        return execute

tx = TxManager()  # TODO: use thread local context

# vim: sw=4:et:ai
