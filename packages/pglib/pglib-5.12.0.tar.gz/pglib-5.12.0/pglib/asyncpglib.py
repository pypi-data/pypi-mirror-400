# Design
# ======
#
# Normal commands like `execute` wait on the `_wait_for` method.  This method creates a new
# Future for each call and waits on it before returning.  A reader or writer is added to the
# libpq socket that completes the future.  When `_wait_for` wakes up from the future it removes
# the reader and writer.
#
# This is designed for executing a single command at a time.  Since the methods are designed
# for "yield from" this should be fine.
#
# Notifications, however, require a reader to be attached at all times.  If it is possible for
# the reader/writer callback to determine if it was triggered due to notifications or not,
# notifications and execute could be mixed.  In the current design, a connection can either be
# used for executing or listening.

import asyncio, logging
from asyncio import Future, wait_for, TimeoutError
from time import time
from _pglib import async_connect, PGRES_POLLING_READING, PGRES_POLLING_WRITING, PGRES_POLLING_OK

logger = logging.getLogger('pglib')

WANT_NOTIFICATIONS = 0x01
WANT_RESULTS = 0x02


async def connect_async(conninfo, loop=None):
    if not loop:
        loop = asyncio.get_event_loop()
    cnxn = AsyncConnection(async_connect(conninfo), loop)
    await cnxn._wait_for_connect()
    return cnxn


class AsyncConnection:

    def __init__(self, cnxn, loop):
        logger.debug('creating %d', id(self))
        self.cnxn = cnxn
        self.loop = loop
        self.sock = cnxn.socket

        self._read_future = None
        # If present, this future will be completed when the socket can be read.

        self._write_future = None
        # When we are trying to write, we set this future which is completed when the socket
        # is ready to write.

        # We don't create an instance of this class until the connection is already made.
        # At this point we can start receiving.
        self.loop.add_reader(self.sock, self._ready_to_read)

    def _ready_to_read(self):
        """
        Called whenever there is data on the socket that is ready to read.

        Even if we are not expecting command data, we might be receiving a notification.
        """
        if self._read_future and not self._read_future.done():
            self._read_future.set_result(None)

    def _ready_to_write(self):
        """
        Called when the socket is ready to write.

        This is only added when we know there is data to write.  Otherwise it would constantly
        be called.
        """
        if self._write_future and not self._write_future.done():
            # The result value is not actually used.
            self._write_future.set_result(None)

    def __del__(self):
        try:
            self.close()
        except:
            pass

    def close(self):
        logger.debug('closing %d', id(self))
        try:
            self.loop.remove_reader(self.sock)
        except:
            pass

        try:
            self.loop.remove_writer(self.sock)
        except:
            pass

        self.cnxn.close()
        logger.debug('closed %d', id(self))

    def __repr__(self):
        return '<AsyncConnection socket={} waiting=0x{:x}>'.format(self.cnxn.socket, getattr(self, '_waiting', 0))

    async def _wait_for_connect(self):
        """
        Called internally by connect_async to wait for the connection to complete.
        """
        try:
            added_writer = False

            while 1:
                flags = self.cnxn._connectPoll()
                if flags == PGRES_POLLING_OK:
                    return

                if flags == PGRES_POLLING_WRITING:
                    # We need to write
                    self._write_future = Future()
                    if not added_writer:
                        self.loop.add_writer(self.sock, self._ready_to_write)
                        added_writer = True
                    await self._write_future
                    self._write_future = None
                    flags = PGRES_POLLING_OK  # cause us to remove the writer below

                if flags != PGRES_POLLING_WRITING:
                    if added_writer:
                        self.loop.remove_writer(self.sock)
                        added_writer = False

                if flags == PGRES_POLLING_READING:
                    self._read_future = Future()
                    await self._read_future
                    self._read_future = None

        finally:
            self._read_future = None
            self._write_future = None
            if added_writer:
                self.loop.remove_writer(self.sock)

    async def listen(self, *channels):
        for channel in channels:
            await self.execute('listen ' + channel)

    async def notify(self, channel, payload=None):
        await self.execute('select pg_notify($1, $2)', channel, payload)

    async def notifications(self, timeout=None):
        """
        Asynchronously wait for one or more notifications.  Since multiple notifications are
        possible, a list is always returned.

        If `timeout` is provided, it is the maximum number of seconds to wait for
        notifications.  If the timeout expires, an empty list is returned.
        """
        assert self._read_future is None, 'Already reading?'

        stop = timeout and (time() + timeout) or None

        try:
            while 1:
                more = self.cnxn._asyncNotifications()
                if more:
                    return more

                if stop:
                    timeout = max(0, stop - time())

                self._read_future = Future()
                await wait_for(self._read_future, timeout)
                self._read_future = None

        except TimeoutError:
            return []

        finally:
            if self._read_future:
                if not self._read_future.done():
                    self._read_future.cancel()
                self._read_future = None

    async def execute(self, *args):
        assert self._read_future is None, 'Already reading?'
        assert self._write_future is None, 'Already writing?'

        if not self.cnxn._sendQueryParams(*args):
            # The query could not be completely sent.  Wait until the socket becomes writable
            # again and try to flush.

            self._write_future = Future()
            self.loop.add_writer(self.sock, self._ready_to_write)

            try:
                # while 1:
                for i in range(3):
                    await self._write_future

                    if not self.cnxn._flush():
                        break

                    # Sent some but there is more.  Since futures cannot be reused (can
                    # they?), make another.
                    self._write_future = Future()

            finally:
                self._write_future = None
                self.loop.remove_writer(self.sock)

        try:
            # while 1:
            for i in range(9):
                result = self.cnxn._asyncGetResult()

                # False is a special indicator meaning we have not received results yet.  Wait
                # for more data on the socket and try again.

                if result is not False:
                    return result

                self._read_future = Future()
                await self._read_future
                self._read_future = None
        finally:
            self._read_future = None

    async def script(self, SQL):
        """
        Executes multiple SQL statements separated by semicolons.  Returns None.

        Parameters are not accepted because PostgreSQL's function that will
        execute multiple statements (PQsendQuery) doesn't accept them and the
        one that does accept parameters (PQsendQueryParams) doesn't execute
        multiple statements.
        """
        if self.use:
            raise Exception('The connection is already in use (%s)' % self._USE_TEXT[self.use])

        c = self.cnxn
        flush = c._sendQuery(SQL)

        while flush == 1:
            which = await self._wait_for(PGRES_POLLING_READING | PGRES_POLLING_WRITING)
            if which == PGRES_POLLING_READING:
                c._consumeInput()
            flush = c._flush()

        results = []

        try:
            while 1:
                while not c._consumeInput():
                    await self._wait_for(PGRES_POLLING_READING)
                c._getResult()

        except StopIteration:
            pass

    async def fetchrow(self, *args):
        """
        Executes the given SQL and returns the first row.  Returns None if no rows
        are returned.
        """
        rset = await self.execute(*args)
        return (rset[0] if rset else None)

    async def fetchval(self, *args):
        """
        Executes the given SQL and returns the first column of the first row.
        Returns None if no rows are returned.
        """
        rset = await self.execute(*args)
        return (rset[0][0] if rset else None)

    async def fetchvals(self, *args):
        """
        Executes the given SQL and returns the first column of each row.
        Returns an empty list if no rows are returned.
        """
        rset = await self.execute(*args)
        return [row[0] for row in rset]

    async def begin(self):
        await self.execute("BEGIN")

    async def commit(self):
        await self.execute("COMMIT")

    async def rollback(self):
        await self.execute("ROLLBACK")

    @property
    def transaction_status(self):
        return self.cnxn.transaction_status

    @property
    def server_version(self):
        return self.cnxn.server_version

    @property
    def protocol_version(self):
        return self.cnxn.protocol_version

    @property
    def server_encoding(self):
        return self.cnxn.server_encoding

    @property
    def client_encoding(self):
        return self.cnxn.client_encoding

    @property
    def status(self):
        return self.cnxn.status
