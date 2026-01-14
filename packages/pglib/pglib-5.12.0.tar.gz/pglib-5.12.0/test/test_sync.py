# Run with pytest.

# pylint: disable=missing-function-docstring,redefined-outer-name,unidiomatic-typecheck

import sys, threading, gzip, uuid, locale, tempfile, csv
from time import sleep
from os.path import join, dirname, exists
from decimal import Decimal
from datetime import date, time, datetime, timedelta
from pathlib import Path
import pytest

from .import testutils
testutils.add_to_path()

import pglib

CONNINFO = 'dbname=test'

STR_FENCEPOST_SIZES = [0, 1, 255, 256, 510, 511, 512, 1023, 1024, 2047, 2048, 4000, 4095, 4096,
                       4097, 10 * 1024, 20 * 1024]
STR_FENCEPOSTS = [testutils.generate_test_string(size) for size in STR_FENCEPOST_SIZES]


@pytest.fixture()
def cnxn():
    # Warning: If I don't manually close the connection, they are not getting deleted.  I don't
    # know if pytest saves them in some test context for each test or what.

    # Note that I'm not using "if exists" because that annoyingly prints a notice.
    cnxn = pglib.connect(CONNINFO)
    for i in range(3):
        try:
            cnxn.execute(f"drop table t{i}")
        except:                 # noqa
            pass
    yield cnxn
    cnxn.close()


def _test_strtype(cnxn, sqltype, value, resulttype=None, colsize=None):
    assert colsize is None or isinstance(colsize, int), colsize
    assert colsize is None or (value is None or colsize >= len(value))

    if colsize:
        sql = f"create table t1(s {sqltype}({colsize}))"
    else:
        sql = f"create table t1(s {sqltype})"

    if resulttype is None:
        resulttype = type(value)

    cnxn.execute(sql)
    cnxn.execute("insert into t1 values($1)", value)
    v = cnxn.fetchval("select * from t1")
    assert type(v) == resulttype

    if value is not None:
        assert len(v) == len(value)

    # To allow buffer --> db --> bytearray tests, always convert the input to the expected
    # result type before comparing.
    if type(value) is not resulttype:
        value = resulttype(value)

    assert v == value


def _test_type(cnxn, type, values, round_to=None, check_comparison=True):
    """
    A generic function for testing inserting and selecting a single data type.

    type: The data type, such as "boolean".

    values: Either a single value or a list of values to insert and select.
        A column is created or each value.
    """
    if not isinstance(values, (tuple, list)):
        values = [values]

    cols = [chr(ord('a') + i) for i in range(len(values))]
    markers = ['$%s' % i for i in range(1, len(values) + 1)]

    create = "create table t1({})".format(','.join('%s %s' % (col, type) for col in cols))
    insert = "insert into t1 values ({})".format(','.join(markers))
    select = "select {} from t1".format(','.join(cols))
    # Make sure "==" works and we don't get size complaints from int2 vs int4, etc.
    compare = "select 1 from t1 where " + ' and '.join(
        '{}={}'.format(col, marker)
        for (col, marker) in zip(cols, markers))

    cnxn.execute(create)
    cnxn.execute(insert, *values)
    rset = cnxn.execute(select)
    row = rset[0]
    for (expected, value) in zip(values, row):
        if round_to:
            value = round(value, round_to)
        assert value == expected

    if check_comparison:
        val = cnxn.fetchval(compare, *values)
        assert val, 'Comparison did not work: type %r values=%r' % (type, values)


def test_execute_ddl(cnxn):
    """
    Ensure we can execute a DDL command and that it returns None.
    """
    r = cnxn.execute("create table t1(a int, b int)")
    assert r is None


def test_iter(cnxn):
    cnxn.execute("create table t1(a varchar(20))")
    cnxn.execute("insert into t1 values ('abc')")
    rset = cnxn.execute("select * from t1")
    for row in rset:
        assert row.a == 'abc'
        assert row[0] == 'abc'


def test_iter_twice(cnxn):
    "Ensure results can be iterated over multiple times"
    cnxn.execute("create table t1(a varchar(20))")
    cnxn.execute("insert into t1 values ('abc')")
    rset = cnxn.execute("select * from t1")
    for row in rset:
        assert row.a == 'abc'
        assert row[0] == 'abc'
    count = 0
    for row in rset:
        count += 1
    assert count == 1


def test_script(cnxn):
    """
    Ensure a script (multiple statements) can be executed.
    """
    sql = """
    select 1;
    select 2;
    select 3;
    """
    cnxn.script(sql)


#
# copy to
#

def test_copytocsv(cnxn):
    # Write a table to a CSV file.
    #
    # It isn't as efficient as I'd like since we can no longer get ahold of the file
    # descriptor.  I think we'll want to make this accept a string filename for a more
    # efficient write.  For now, make sure the output file is opened in text mode.

    cnxn.execute("create table t1(a text, b text)")
    cnxn.execute("insert into t1 values ('1', 'one'), ('2', 'two'), ('3', 'three')")

    with tempfile.NamedTemporaryFile(mode='w', encoding='utf8') as tf:
        print(tf.name)
        count = cnxn.copy_to_csv('t1', tf, header=1)
        assert count == 3

        tf.seek(0)
        with open(tf.name, mode='r', encoding='utf8') as fd:
            reader = csv.reader(fd)
            rows = []
            for row in reader:
                print('ROW=', row)
                rows.append(row)

            assert rows == [['a', 'b'], ['1', 'one'], ['2', 'two'], ['3', 'three']]


def test_copy_to(cnxn):
    # Test copy_to with a full command, including a subquery.
    cnxn.execute("create table t1(a int, b text)")
    cnxn.execute("insert into t1 values (1, 'one'), (2, 'two'), (3, 'three')")

    with tempfile.NamedTemporaryFile(mode='w', encoding='utf8') as tf:
        # Use a subquery to only copy rows where a > 1
        count = cnxn.copy_to('copy (select * from t1 where a > 1 order by a) to stdout csv header', tf)
        assert count == 2

        tf.flush()
        with open(tf.name, mode='r', encoding='utf8') as fd:
            reader = csv.reader(fd)
            rows = list(reader)
            assert rows == [['a', 'b'], ['2', 'two'], ['3', 'three']]


def test_copy_to_table(cnxn):
    # Test copy_to with a simple table copy (no subquery).
    cnxn.execute("create table t1(a int, b text)")
    cnxn.execute("insert into t1 values (1, 'one'), (2, 'two')")

    with tempfile.NamedTemporaryFile(mode='w', encoding='utf8') as tf:
        count = cnxn.copy_to('copy t1 to stdout csv', tf)
        assert count == 2

        tf.flush()
        with open(tf.name, mode='r', encoding='utf8') as fd:
            reader = csv.reader(fd)
            rows = list(reader)
            assert rows == [['1', 'one'], ['2', 'two']]


#
# copy from
#

def _datapath(filename):
    path = join(dirname(__file__), filename)
    assert exists(path)
    return path


def test_copyfromcsv_csv(cnxn):
    cnxn.execute("create table t1(a int, b varchar(20))")
    with open(_datapath('test-noheader.csv')) as fd:
        count = cnxn.copy_from_csv("t1", fd)
    assert count == 2
    assert cnxn.fetchval("select count(*) from t1") == 2
    row = cnxn.fetchrow("select a,b from t1 where a=2")
    assert row.a == 2
    assert row.b == 'two'


def test_copyfromcsv_csv_header(cnxn):
    cnxn.execute("create table t1(a int, b varchar(20))")
    with open(_datapath('test-header.csv')) as fd:
        count = cnxn.copy_from_csv("t1", fd, header=True)
    assert count == 2
    assert cnxn.fetchval("select count(*) from t1") == 2
    row = cnxn.fetchrow("select a,b from t1 where a=2")
    assert row.a == 2
    assert row.b == 'two'


def test_copyfromcsv_csv_error(cnxn):
    """
    Ensure an error copying raises a Python error.
    """
    # We'll make the second column too small.
    cnxn.execute("create table t1(a int, b varchar(1) not null)")
    with pytest.raises(pglib.Error):
        with open(_datapath('test-noheader.csv')) as fd:
            cnxn.copy_from_csv("t1", fd)


def test_copyfromcsv_csv_gzip(cnxn):
    # I don't remember why this test is here.  We're feeding it unzipped data.
    cnxn.execute("create table t1(a int, b varchar(20))")
    with gzip.open(_datapath('test-header.csv.gz')) as fd:
        cnxn.copy_from_csv("t1", fd, header=True)
    assert cnxn.fetchval("select count(*) from t1") == 2
    row = cnxn.fetchrow("select a,b from t1 where a=2")
    assert row.a == 2
    assert row.b == 'two'


def test_copyfromcsv_csv_string(cnxn):
    cnxn.execute("create table t1(a int, b varchar(20))")
    count = cnxn.copy_from_csv("t1", '1,"one"\n2,"two"')
    assert count == 2
    row = cnxn.fetchrow("select a,b from t1 where a=2")
    assert row.a == 2
    assert row.b == 'two'


def test_copyfromcsv_csv_string_cols(cnxn):
    cnxn.execute("create table t1(a int, b varchar(20))")
    count = cnxn.copy_from_csv("t1(b, a)", '"one",1\n"two",2')  # reverse order of cols
    assert count == 2
    row = cnxn.fetchrow("select a,b from t1 where a=2")
    assert row.a == 2
    assert row.b == 'two'


def test_copyfromcsv_psv_string(cnxn):
    cnxn.execute("create table t1(a int, b varchar(20))")
    count = cnxn.copy_from_csv("t1", '1|"one"\n2|"two"', delimiter='|')
    assert count == 2
    row = cnxn.fetchrow("select a,b from t1 where a=2")
    assert row.a == 2
    assert row.b == 'two'

def test_copyfromcsv_psv_quote(cnxn):
    # Send in some data with a quote in it as part of the string like 1/2".  We'll change the
    # quotes to something not in the data (a bel/7 character) and ensure it considered the quote
    # as part of the data.

    cnxn.execute("create table t1(a int, b varchar(20))")
    count = cnxn.copy_from_csv("t1", '1|1/2"\n2|3/4"', delimiter='|', quote="\x07")
    assert count == 2
    row = cnxn.fetchrow("select a,b from t1 where a=2")
    assert row.a == 2
    assert row.b == '3/4"'

def test_copy_from_psv_quote(cnxn):
    cmd = "copy t1 from stdin with csv delimiter '|' quote '\x07'"

    cnxn.execute("create table t1(a int, b varchar(20))")
    count = cnxn.copy_from(cmd, '1|1/2"\n2|3/4"')
    assert count == 2
    row = cnxn.fetchrow("select a,b from t1 where a=2")
    assert row.a == 2
    assert row.b == '3/4"'

#
# row
#


def test_row_zero(cnxn):
    cnxn.execute("create table t1(a int)")
    value = cnxn.fetchrow("select a from t1")
    assert value is None


def test_row_one(cnxn):
    cnxn.execute("create table t1(a int)")
    cnxn.execute("insert into t1 values (2)")
    value = cnxn.fetchrow("select a from t1")
    assert value[0] == 2


def test_row_many(cnxn):
    cnxn.execute("create table t1(a int)")
    cnxn.execute("insert into t1 values (1), (2)")
    with pytest.raises(pglib.Error):
        cnxn.fetchrow("select a from t1")


def test_fetchrow(cnxn):
    cnxn.execute("create table t1(a int)")
    cnxn.execute("insert into t1 values (2)")
    value = cnxn.fetchrow("select a from t1")
    assert value[0] == 2


def test_fetchrow_none(cnxn):
    cnxn.execute("create table t1(a int)")
    value = cnxn.fetchrow("select a from t1")
    assert value is None


def test_fetchval(cnxn):
    cnxn.execute("create table t1(a int)")
    cnxn.execute("insert into t1 values (2)")
    value = cnxn.fetchval("select a from t1")
    assert value == 2


def test_fetchval_none(cnxn):
    cnxn.execute("create table t1(a int)")
    value = cnxn.fetchval("select a from t1")
    assert value is None


def test_fetchvals(cnxn):
    cnxn.execute("create table t1(a int, b text)")
    cnxn.execute("insert into t1 values (1, 'one'), (2, 'two'), (3, 'three')")

    values = cnxn.fetchvals("select a from t1 order by a")
    assert values == [1, 2, 3]

    values = cnxn.fetchvals("select a, b from t1 order by a")
    assert values == [1, 2, 3]

#
# resultset
#


def test_rset_length(cnxn):
    """
    Ensure the len(ResultSet) returns the number of rows.
    """
    cnxn.execute("create table t1(i int)")
    count = 4
    for i in range(count):
        cnxn.execute("insert into t1 values ($1)", i)
    rset = cnxn.execute("select * from t1")
    assert len(rset) == 4


def test_rset_index(cnxn):
    """
    Ensure we can indexing into the ResultSet returns a Row.
    """
    cnxn.execute("create table t1(i int)")
    count = 4
    for i in range(count):
        cnxn.execute("insert into t1 values ($1)", i)
    rset = cnxn.execute("select * from t1")
    row = rset[2]
    assert row[0] == 2


def test_rset_nonzero(cnxn):
    """
    Ensure a resultset with no rows is "falsey".
    """
    cnxn.execute("create table t1(i int)")
    rset = cnxn.execute("select * from t1")
    assert rset is not None
    assert not rset

    cnxn.execute("insert into t1 values (1), (2)")
    rset = cnxn.execute("select * from t1")
    assert rset is not None
    assert rset


#
# fetchval
#

def test_fetchval_zero(cnxn):
    """
    Ensure cnxn.fetchval() returns None if no rows are selected.
    """
    cnxn.execute("create table t1(a int)")
    value = cnxn.fetchval("select a from t1")
    assert value is None


def test_fetchval_one(cnxn):
    """
    Ensure cnxn.fetchval() returns the first column if one row is selected.
    """
    cnxn.execute("create table t1(a int)")
    cnxn.execute("insert into t1 values (1)")
    value = cnxn.fetchval("select a from t1")
    assert value == 1


def test_fetchval_many(cnxn):
    """
    Ensure cnxn.fetchval() raises an exception if multiple rows are selected.
    """
    cnxn.execute("create table t1(a int)")
    cnxn.execute("insert into t1 values (1), (2)")
    with pytest.raises(pglib.Error):
        cnxn.fetchval("select a from t1")


#
# tuple
#


def test_row_to_tuple(cnxn):
    cnxn.execute("create table t1(a varchar(20), b int)")
    cnxn.execute("insert into t1 values ('one', 1)")
    rset = cnxn.execute("select a,b from t1")
    for row in rset:
        t = tuple(row)
        assert t == ('one', 1)

#
# boolean
#


def test_boolean(cnxn):
    _test_type(cnxn, 'boolean', [True, False])


#
# numeric
#


def test_smallint(cnxn):
    _test_type(cnxn, 'smallint', [-32768, -2, -1, 0, 1, 2, 32767])


def test_integer(cnxn):
    _test_type(cnxn, 'integer', [-2147483648, -32768, -2, -1, 0, 1, 2, 32767, 2147483647])


def test_bigint(cnxn):
    _test_type(cnxn, 'bigint',
               [-9223372036854775808, -2147483648, -32768, -2, -1, 0,
                1, 2, 32767, 2147483647, 9223372036854775807])


def test_float4(cnxn):
    # Careful.  Python doesn't have a float4 datatype, so an float8 is returned.  Unfortunately this means values
    # won't always match even though they "look" like they do when you print them.
    _test_type(cnxn, 'float4', [1.2, -3.4], round_to=2, check_comparison=False)


def test_float8(cnxn):
    _test_type(cnxn, 'float8', [1.2, -3.4], check_comparison=False)


def test_decimal_fixed(cnxn):
    values = [Decimal(s) for s in ['123', '-3.0000000', '0', '123456.7890']]
    _test_type(cnxn, 'decimal(100,7)', values)


def test_decimal_any(cnxn):
    values = [Decimal(s) for s in ['123', '-3.0000000', '0', '123456.7890']]
    _test_type(cnxn, 'decimal', values)


def test_money(cnxn):
    values = [Decimal(s) for s in ['1.23', '0.0', '123.45', '-12.34']]
    _test_type(cnxn, 'money', values, check_comparison=False)


# Decimal objects are constructed by first making a string, which we make in
# English ("12.34").  Make sure that changing the locale to one that uses
# "," doesn't trip us up.  (I'm not sure why it doesn't.  Ideally we should
# work on using a different constructor.)  You'll notice that Decimal still
# parses the values we pass as strings before we even get to pglib.


@pytest.mark.skip('LC_ALL locale does not exist')
def test_decimal_german(cnxn):
    locale.setlocale(locale.LC_ALL, 'de_DE')
    values = [Decimal(s) for s in ['-3.0000000', '123456.7890']]
    _test_type(cnxn, 'decimal(100,7)', values)


@pytest.mark.skip('LC_ALL locale does not exist')
def test_money_german(cnxn):
    locale.setlocale(locale.LC_ALL, 'de_DE')
    values = [Decimal(s) for s in ['1.23', '0.0', '123.45', '-12.34']]
    _test_type(cnxn, 'money', values, check_comparison=False)


def test_decimal_nan(cnxn):
    dec = Decimal('NaN')
    cnxn.execute("create table t1(a decimal(100,7))")
    cnxn.execute("insert into t1 values($1)", dec)
    result = cnxn.fetchval("select a from t1")
    assert type(result) == Decimal
    assert result.is_nan()


def test_serial(cnxn):
    cnxn.execute("create table t1(a serial, b varchar(20))")
    cnxn.execute("insert into t1(b) values ('one')")
    cnxn.execute("insert into t1(a, b) values (2147483647, 'max')")
    for value in [1, 2147483647]:
        result = cnxn.fetchval("select a from t1 where a=$1", value)
        assert result == value


#
# varchar
#


def test_varchar_null(cnxn):
    _test_strtype(cnxn, 'varchar', None, colsize=100)


# Generate a test for each fencepost size: test_varchar_0, etc.

def _maketest(value):
    def t(cnxn):
        _test_strtype(cnxn, 'varchar', value, colsize=len(value))
    return t


for value in STR_FENCEPOSTS:
    locals()['test_varchar_%s' % len(value)] = _maketest(value)

#
# char
#


def test_char_null(cnxn):
    _test_strtype(cnxn, 'char', None, colsize=100)


# Generate a test for each fencepost size: test_char_1, etc.
#
# Note: There is no test_char_0 since they are blank padded.

def _maketest(value):
    def t(cnxn):
        _test_strtype(cnxn, 'char', value, colsize=len(value))
    return t


for value in [v for v in STR_FENCEPOSTS if len(v) > 0]:
    locals()['test_char_%s' % len(value)] = _maketest(value)


#
# bytea / bytearray
#


def test_bytea(cnxn):
    # Add a NULL byte in the middle to ensure strcpy isn't being used.
    value = b'\xde\xad\x00\xbe\xef'
    cnxn.execute("create table t1(a bytea)")
    cnxn.execute("insert into t1 values ($1)", value)
    result = cnxn.fetchval("select * from t1")
    assert value == result

# def test_bytea_wrongtype(cnxn):
#     # Add a NULL byte in the middle to ensure strcpy isn't being used.
#     value = (b'\x80\x03cmtech.cornerstone.sessions\nSession\nq\x00)\x81q\x01}q\x02(X\x07\x00\x00\x00user_idq\x03NX\t\x00\x00\x00user_nameq\x04NX\x0b\x00\x00\x00permissionsq\x05cbuiltins\nset\nq\x06]q\x07\x85q\x08Rq\tub.',)
#     cnxn.execute("create table t1(a bytea)")
#     cnxn.execute("insert into t1 values ($1)", value)
#     result = cnxn.fetchval("select * from t1")
#     assert value == result


#
# date / timestamp
#


def test_date(cnxn):
    _test_type(cnxn, 'date', date(2001, 2, 3))


def test_time(cnxn):
    value = time(12, 34, 56)
    cnxn.execute("create table t1(a time)")
    cnxn.execute("insert into t1 values ($1)", value)
    result = cnxn.fetchval("select a from t1")
    assert result == value


def test_timestamp(cnxn):
    cnxn.execute("create table t1(a timestamp)")
    value = datetime(2001, 2, 3, 4, 5, 6, 7)
    cnxn.execute("insert into t1 values ($1)", value)
    result = cnxn.fetchval("select a from t1")
    assert result == value


def test_timestamptz(cnxn):
    cnxn.execute("create table t1(a timestamptz)")
    value = datetime(2001, 2, 3, 4, 5, 6, 7)
    cnxn.execute("insert into t1 values ($1)", value)
    result = cnxn.fetchval("select a from t1")
    assert result == value


#  def test_timezone(cnxn):
#      """
#      Ensure we can pass a datetime that has UTC already.
#      """
#      cnxn.execute("create table t1(a timestamptz)")
#      value = datetime(2023, 11, 30, 21, 0, tzinfo=timezone.utc)
#      cnxn.execute("insert into t1 values ($1)", value)
#      result = cnxn.fetchval("select a from t1")
#      assert result == value


def test_timezone_toutc(cnxn):
    """
    Ensure we can pass a datetime as a parameter and convert it to UTC.
    """
    # 2020-04-14 17:00 Central -> 2020-04-14 22:00 UTC
    central = datetime(2020, 4, 14, 17, 0)

    utc = cnxn.fetchval(
        """
        select timezone('UTC', $1 at time zone 'America/Chicago')
        """, central)

    assert utc == datetime(2020, 4, 14, 22, 0)


def test_interval(cnxn):
    cnxn.execute("create table t1(a interval)")
    value = timedelta(days=3, hours=4, minutes=5, seconds=6)
    cnxn.execute("insert into t1 values ($1)", value)
    result = cnxn.fetchval("select a from t1")
    assert result == value


#
# Error Handling
#

# def test_error_param_count(cnxn):
#     """
#     Was seeing a segfault on OS/X when performing an update with 3 parameters
#     but supplying only 2 values.  There doesn't seem to be a way to determine this.
#     """
#     cnxn.execute("create table t1(a varchar(20), b varchar(20), c text)")
#     cnxn.execute("insert into t1(a) values ('1')")
#     with pytest.raises(pglib.Error):
#         cnxn.execute("update t1 set b=$1, c=$2 where a=$1",
#                           'xyz',
#                           # purposely leave out value for 'c'
#                           '1')

#
# array of parameters
#

def test_array_date(cnxn):
    cnxn.execute("create table t1(id int, v date[])")
    value = [None, date(2001, 1, 1), date(2002, 12, 13)]
    cnxn.execute("insert into t1 values (1, $1)", value)
    result = cnxn.fetchval("select v from t1")
    assert result == value


def test_array_int2(cnxn):
    cnxn.execute("create table t1(id int, v int[])")
    value = [None, -32768, -2, -1, 0, 1, 2, 32767]
    cnxn.execute("insert into t1 values (1, $1)", value)
    result = cnxn.fetchval("select v from t1")
    assert result == value


def test_array_int4(cnxn):
    # Test with a 4-byte value
    cnxn.execute("create table t1(id int, v int[])")
    value = [None, -2147483648, -32768, -2, -1, 0, 1, 2, 32767, 2147483647]
    cnxn.execute("insert into t1 values (1, $1)", value)
    result = cnxn.fetchval("select v from t1")
    assert result == value


def test_array_bigint(cnxn):
    # MAX_INTEGER = 2147483647
    cnxn.execute("create table t1(id int, v bigint[])")
    value = [None, -9223372036854775808, -2147483648, -32768, -2, -1, 0,
             1, 2, 32767, 2147483647, 9223372036854775807]
    cnxn.execute("insert into t1 values (1, $1)", value)
    result = cnxn.fetchval("select v from t1")
    assert result == value


def test_array_float(cnxn):
    cnxn.execute("create table t1(id int, v float[])")
    value = [None, -100000.0, -32768.0, -123.45, -1.0, 0.0,
             1.0, 123.45, 32767.0, 2147483647.0, 10101010.8989]
    cnxn.execute("insert into t1 values (1, $1)", value)
    result = cnxn.fetchval("select v from t1")
    assert result == value


def test_array_text(cnxn):
    cnxn.execute("create table t1(id int, v text[])")
    value = ['one', None, 'two']
    cnxn.execute("insert into t1 values (1, $1)", value)
    result = cnxn.fetchval("select v from t1")
    assert result == value


def test_array_int_empty(cnxn):
    cnxn.execute("create table t1(id int, v int[])")
    cnxn.execute("insert into t1(id, v) values (1, array[]::int[])")
    result = cnxn.fetchval("select v from t1")
    assert result == []


def test_array_bigint_empty(cnxn):
    cnxn.execute("create table t1(id bigint, v bigint[])")
    cnxn.execute("insert into t1(id, v) values (1, array[]::bigint[])")
    result = cnxn.fetchval("select v from t1")
    assert result == []


def test_array_text_empty(cnxn):
    cnxn.execute("create table t1(id int, v text[])")
    cnxn.execute("insert into t1(id, v) values (1, array[]::text[])")
    result = cnxn.fetchval("select v from t1")
    assert result == []


def test_array_int_in(cnxn):
    cnxn.execute("create table t1(id int)")
    for value in [1, 2, 3]:
        cnxn.execute("insert into t1 values ($1)", value)
    value = [1, 3]
    rset = cnxn.execute("select id from t1 where id = ANY($1)", value)
    assert len(rset) == 2


def test_array_int8_in(cnxn):
    MAX_INTEGER = 2147483647
    cnxn.execute("create table t1(id bigint)")
    for value in [1, MAX_INTEGER * 2, sys.maxsize]:
        cnxn.execute("insert into t1 values ($1)", value)
    value = [1, sys.maxsize]
    rset = cnxn.execute("select id from t1 where id = ANY($1)", value)
    assert len(rset) == 2


def test_array_text_in(cnxn):
    cnxn.execute("create table t1(id int, v text)")
    for value in ['one', 'two', 'three']:
        cnxn.execute("insert into t1 values (1, $1)", value)
    value = ['one', 'three']
    rset = cnxn.execute("select v from t1 where v = ANY($1)", value)
    assert len(rset) == 2


# I don't have a good solution for this yet.  If an array is empty or all NULLs, we don't
# know what type to choose when sending to the DB.  I've chosen text, but it doesn't
# convert as wells as I'd hoped - the backend won't accept it.  I've tried ANYARRAYOID and
# that doesn't work either.

# def test_array_none(cnxn):
#     # I've made the data type 'int[]' since we're going to try inserting as text[].  All we
#     # have is "None", so we don't know what type and will default to text.
#     cnxn.execute("create table t1(id int, v int[])")
#     value = [None, None, None]
#     cnxn.execute("insert into t1 values (1, $1)", value)
#     result = cnxn.fetchval("select v from t1")
#     assert result == value

# This looks weird, but each type must be tested like this.  Code in each type ensures the
# types are the same.  Perhaps we should fix that, but I didn't want to go through the loop
# so many times.


def test_array_int_bad(cnxn):
    cnxn.execute("create table t1(id int, v int[])")
    value = [1, 'two']
    with pytest.raises(pglib.Error):
        cnxn.execute("insert into t1 values (1, $1)", value)


#
# Miscellaneous
#

def test_fetchall(cnxn):
    # fetchall is simply an alias for execute.  It reads nicely in code that is also using
    # fetchval and fetchrow.
    cnxn.execute("create table t1(id int)")
    cnxn.execute("insert into t1 values (1), (2)")
    rset = cnxn.fetchall("select id from t1 order by id")
    assert len(rset) == 2
    assert [row.id for row in rset] == [1, 2]


def test_scope_close(cnxn):
    "Connection should close when it goes out of scope"

    # Each connection is allocated a process on the server to handle queries.  Each process has
    # a unique PID that we can get from the connection.  When a connection is closed, the PID
    # is no longer active.
    #
    # We can see what PIDs are active from the (virtual?) pg_stat_activity table, which
    # helpfully includes a PID column.  When a connection is open, the PID is in the table.
    # When it is closed, it is no longer in the table.  (I don't know how much time we have
    # before they get reused.)

    def _t():
        other = pglib.connect(CONNINFO)
        pid = other.pid
        val = other.fetchval("select pid from pg_stat_activity where pid=$1", pid)
        assert val is not None
        return pid

    pid = _t()
    val = cnxn.fetchval("select pid from pg_stat_activity where pid=$1", pid)
    assert val is None


def test_insert_result(cnxn):
    """
    Ensure that an insert returns the row count, not a result set.
    """
    cnxn.execute("create table t1(a varchar(20), b int)")
    result = cnxn.execute("insert into t1 values ('one', 1)")
    assert result == 1


def test_repr(cnxn):
    """
    For debugging purposes, printing a row should produce the same output as a tuple.
    """
    cnxn.execute("create table t1(a varchar(20), b int)")
    cnxn.execute("insert into t1 values ('one', 1)")
    row = cnxn.fetchrow("select a,b from t1")
    t = ('one', 1)
    assert str(row) == str(t)


def test_cnxn_status(cnxn):
    # I don't know how to make a bad status, so we'll just ensure the attribute exists
    # and is true.
    assert cnxn.status


def test_txn_status(cnxn):
    assert cnxn.transaction_status == pglib.PQTRANS_IDLE
    cnxn.execute("begin")
    assert cnxn.transaction_status == pglib.PQTRANS_INTRANS
    try:
        cnxn.execute("drop table bogus")
    except:                     # noqa
        pass
    assert cnxn.transaction_status == pglib.PQTRANS_INERROR

    cnxn.execute("rollback")
    assert cnxn.transaction_status == pglib.PQTRANS_IDLE


def test_uuid(cnxn):
    value = uuid.UUID('4bfe4344-e7f2-41c3-ab88-1aecd79abd12')
    cnxn.execute("create table t1(a uuid)")
    cnxn.execute("insert into t1 values ($1)", value)
    result = cnxn.fetchval("select a from t1")
    assert result == value


def test_rset_columns(cnxn):
    cnxn.execute("create table t1(a int, b int, c int)")
    cnxn.execute("insert into t1 values (1,1,1)")
    rset = cnxn.execute("select a,b,c from t1")
    assert rset.columns == ('a', 'b', 'c')


def test_rset_colinfos(cnxn):
    cnxn.execute(
        """
        create table t1(
          a int4,
          b text,
          c date,
          d timestamptz,
          e decimal(19, 2)
        )
        """)

    values = [1, 'one', '2001-01-01', '2001-01-01 12:34', '3.14']
    cnxn.execute("insert into t1 values ($1, $2, $3, $4, $5)", *values)
    rset = cnxn.fetchall("select * from t1")

    expected_infos = [
        ('a', 'int4'),
        ('b', 'text'),
        ('c', 'date'),
        ('d', 'timestamptz'),
        ('e', 'numeric'),
    ]

    for actual, expected in zip(rset.colinfos, expected_infos):
        # Convert the actual to an info_t.  There are some values we don't know
        # what the value should be like OIDs.

        assert actual.name == expected[0]

        typename = cnxn.fetchval(
            """
            select typname
              from pg_type
             where oid = $1
            """, actual.type)
        assert typename == expected[1]


def test_row_columns(cnxn):
    cnxn.execute("create table t1(a int, b int, c int)")
    cnxn.execute("insert into t1 values (1,1,1)")
    row = cnxn.fetchrow("select a,b,c from t1")
    assert row.columns == ('a', 'b', 'c')


def test_assignment(cnxn):
    """
    Ensure columns can be assigned to rows.
    """
    cnxn.execute("create table t1(a int)")
    cnxn.execute("insert into t1 values (1)")
    row = cnxn.fetchrow("select a from t1")
    assert row.a == 1
    row.a = 2
    assert row.a == 2


def test_row_failure(cnxn):
    """
    Calling cnxn.fetchrow() with invalid SQL used to return "SQL wasn't a
    query" because row was not detecting the error before trying to access
    results.
    """
    cnxn.execute("create table t1(a varchar(20))")
    try:
        cnxn.fetchrow("select bogus from t1")
    except pglib.Error as ex:
        msg = str(ex)
        assert '[42703]' in msg


def test_fetchval_failure(cnxn):
    """
    Calling cnxn.fetchval() with invalid SQL used to return "SQL wasn't a
    query" because row was not detecting the error before trying to access
    results.
    """
    cnxn.execute("create table t1(a varchar(20))")
    try:
        cnxn.fetchval("select bogus from t1")
    except pglib.Error as ex:
        msg = str(ex)
        assert '[42703]' in msg, "msg={!r}".format(msg)


def test_null_param(cnxn):
    # At one point, inserting a NULL parameter followed by a non-NULL parameter caused a segfault.
    #
    # A single parameter or two Nones did not crash.

    cnxn.execute("create table t1(a varchar(20), b integer)")
    cnxn.execute("insert into t1(a) values ($1)", 'testing')
    cnxn.execute("update t1 set a=$1, b=$2", None, 1)


def test_txn_commit(cnxn):
    cnxn.execute("create table t1(a int)")
    other = pglib.connect(CONNINFO)
    other.begin()
    other.execute("insert into t1 values (1)")
    other.commit()
    count = cnxn.fetchval("select count(*) from t1")
    assert count == 1


def test_txn_failure(cnxn):
    cnxn.execute("create table t1(a int)")
    other = pglib.connect(CONNINFO)
    other.begin()
    other.execute("insert into t1 values (1)")
    other = None  # should roll back
    count = cnxn.fetchval("select count(*) from t1")
    assert count == 0


def test_txn_rollback(cnxn):
    cnxn.execute("create table t1(a int)")
    other = pglib.connect(CONNINFO)
    other.begin()
    other.execute("insert into t1 values (1)")
    other.rollback()
    count = cnxn.fetchval("select count(*) from t1")
    assert count == 0


def test_txn_rollback_failure(cnxn):
    "Ensure rollback doesn't fail if the txn status is INERROR"
    try:
        cnxn.begin()
        cnxn.execute("select x from bogus")  # table does not exists
    except:                                  # noqa
        cnxn.rollback()


def test_txn_empty_commit(cnxn):
    "Ensure commit doesn't fail if the txn status is IDLE"
    cnxn.begin()
    cnxn.commit()


def test_tmp(cnxn):
    """
    A sync version of test_async.  We're getting the results in text format
    instead of binary even though I've requested binary.
    """
    cnxn.execute("create table t1(a varchar(20), b int)")
    cnxn.execute("insert into t1 values ($1, $2)", 'abc', 3)
    rset = cnxn.execute("select a, b from t1")
    for row in rset:
        assert row.a == 'abc'
        assert row[0] == 'abc'
        assert row.b == 3
        assert row[1] == 3


def test_notifies(cnxn):
    "Ensure synchronous notifications() works."

    # We want to test two cases: (1) a notification exists before the call and (2) a
    # notification exists after we're in the select loop.
    #
    # The first is easy.  The second requires we start a thread but have it sleep a bit to
    # give us time to get into the select loop.  I've chosen to sleep for 0.1 seconds.
    #
    # Remember that ther server can de-duplicate notifications.  I don't think it matters
    # here since we're using separate connections for the notifications, but I'll use
    # different channels anyway.

    def notify(conninfo):
        sleep(0.1)
        other = pglib.connect(conninfo)
        other.execute("notify test2, 'testing'")

    cnxn.execute("listen test1")
    cnxn.execute("listen test2")

    n = cnxn.notifications(timeout=0)
    assert n is None

    cnxn.notify('test1', 'testing')
    n = cnxn.notifications(timeout=1)
    assert n == ('test1', 'testing')

    threading.Thread(target=notify, args=(CONNINFO,)).start()
    n = cnxn.notifications(timeout=1)
    assert n == ('test2', 'testing')


def test_double_close(cnxn):
    "Make sure close is safe"
    cnxn.close()
    cnxn.close()


def test_closed_error(cnxn):
    "Make sure APIs raise an error if already closed instead of crashing"

    cnxn.close()
    with pytest.raises(pglib.Error):
        # All of the fetch methods use the same guard
        cnxn.execute("select 1")

    with pytest.raises(pglib.Error):
        cnxn.begin()

    with pytest.raises(pglib.Error):
        cnxn.rollback()


def test_connection_count():
    before = pglib.connection_count()
    cnxn = pglib.connect(CONNINFO)
    assert pglib.connection_count() == (before + 1)
    cnxn.close()
    assert pglib.connection_count() == before
    cnxn = None
    assert pglib.connection_count() == before


def test_count(cnxn):
    "Ensure delete statements return affected row count."
    cnxn.execute(
        """
        select generate_series(1, 3) as id
          into t1
        """)

    count = cnxn.execute("delete from t1 where id in (1, 2, 3)")
    assert count == 3


def test_hstore(cnxn):
    cnxn.execute("create extension if not exists hstore")
    row = cnxn.fetchrow("select oid, typname from pg_type where typname='hstore'")
    pglib.register_type(row.oid, row.typname)

    cnxn.execute("create table t1(id serial, fields hstore)")

    values = [
        {'key1': 'val1'},
        {'key1': None},
        {'key1': 'val1', 'key2': 'val2'},
        {'': 'val1'},
        {},
    ]

    for value in values:
        cnxn.execute("insert into t1(fields) values ($1)", pglib.hstore(value))

    rset = cnxn.execute("select fields from t1 order by id")

    assert len(rset) == len(values)

    for expected, row in zip(values, rset):
        assert expected == row.fields


def test_enums(cnxn):
    cnxn.execute("drop type if exists test_t")
    cnxn.execute("create type test_t as enum('one', 'two')")
    rset = cnxn.execute("select oid, typname from pg_type where typtype='e'")
    for row in rset:
        print('oid:', row.oid, 'type:', row.typname)
        pglib.register_enum(row.oid)

    cnxn.execute("create table t1(id serial, t test_t)")
    cnxn.execute("insert into t1(t) values ($1)", 'one')
    cnxn.execute("insert into t1(t) values ('two')")

    val = cnxn.fetchval("select t from t1 where id=1")
    assert val == 'one'

    val = cnxn.fetchval("select t from t1 where id=2")
    assert val == 'two'


def test_name(cnxn):
    # Ensure we can read the 'name' type.  I don't know why it isn't just a string.
    name = cnxn.fetchval(
        """
        select attname
          from pg_attribute
         limit 1
        """)
    assert isinstance(name, str)


def test_json(cnxn):

    value = {
        'one': 1,
        'a': [1, 2, 3],
        '2': 'two'
    }

    cnxn.execute("create table t1(j json)")
    cnxn.execute("insert into t1 values($1)", value)
    result = cnxn.fetchval("select j from t1")

    assert value == result


def test_empty_json(cnxn):
    value = {}
    cnxn.execute("create table t1(j json)")
    cnxn.execute("insert into t1 values($1)", value)
    result = cnxn.fetchval("select j from t1")
    assert value == result


def test_jsonb(cnxn):

    value = {
        'one': 1,
        'a': [1, 2, 3],
        '2': 'two'
    }

    cnxn.execute("create table t1(j jsonb)")
    cnxn.execute("insert into t1 values($1)", value)
    result = cnxn.fetchval("select j from t1")

    assert value == result


def test_jsonb_wrapper(cnxn):
    value = [1, 2, 3]
    wrapper = pglib.json(value)
    cnxn.execute("create table t1(j jsonb)")
    cnxn.execute("insert into t1 values($1)", wrapper)
    result = cnxn.fetchval("select j from t1")
    assert value == result


def test_empty_jsonb(cnxn):
    value = {}
    cnxn.execute("create table t1(j jsonb)")
    cnxn.execute("insert into t1 values($1)", value)
    result = cnxn.fetchval("select j from t1")
    assert value == result


def test_jsonb_array(cnxn):
    # REVIEW: We can only read these for now.
    value = [{"a": 1}, {"a": 22}]
    cnxn.execute("create table t1(j jsonb)")
    cnxn.execute("""insert into t1 values('{"a": 1}')""")
    cnxn.execute("""insert into t1 values('{"a": 22}')""")

    result = cnxn.fetchval("select array_agg(j) from t1")
    assert result == value

def test_info(cnxn):
    info = cnxn.info()
    assert info['dbname'] == 'test'

    defaults = pglib.defaults()
    assert isinstance(defaults, dict)
    assert not defaults.get('dbname')


def test_ltree(cnxn):
    cnxn.execute("create extension if not exists ltree")

    row = cnxn.fetchrow("select oid, typname from pg_type where typname='ltree'")
    pglib.register_type(row.oid, row.typname)

    cnxn.execute("create table t1(id int, path ltree)")
    cnxn.execute("insert into t1 values ($1, $2)", 1, "a.b.c")
    result = cnxn.fetchval("select path from t1")
    assert result == 'a.b.c'


def test_large_insert(cnxn):
    cnxn.execute("drop table if exists large_data")
    cnxn.execute("create table large_data(code text, description text)")
    query = (Path(__file__).parent / 'large-insert.sql').read_text(encoding='utf8')
    print('-' * 40)
    cnxn.execute(query)
