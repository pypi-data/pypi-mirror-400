""" Lazy man's easy conversion between date strings and date tuple/date objects.

It's actually very easy to code it directly, plus it's better to reduce
dependency.  This module provides very few additional functionality.  One being
able to detect if a list of strings/date tuples are given, and act accordingly.
Use these few lines of code instead if you are not too lazy:

from datetime import datetime
d = datetime.strptime(s, '%Y-%m-%d').date()

from datetime import date
s = str(date((1995,2,3)))
s = str(date(*tp))
# tp is your existing tuple, s will be string '1995-02-03'
"""
import unittest


def date_tuple_to_string(tp):
    """ Converts date integer tuple (y,m,d) into string 'yyyy-mm-dd'.  Input
    supports both a single date-tuple as well as a list of date-tuples. """
    from datetime import date
    single = False
    if len(tp) == 3:
        if all([isinstance(i, int) for i in tp]):
            single = True
    if single:
        return str(date(*tp))
    else:
        # assuming input is a list of date-tuples
        return [str(date(*d)) for d in tp]

def _s2d(s):
    """ Converts a date string of format 'yyyy-mm-dd' or 'dd/mm/yyyy' into a
    python datetime.date object. """
    from datetime import datetime
    if '/' in s:
        frmt = '%d/%m/%Y'
    elif '-' in s:
        frmt = '%Y-%m-%d'
    else:
        raise Exception("Date string format only support 'yyyy-mm-dd' or 'dd/mm/yyyy'")
    return datetime.strptime(s, frmt).date()

def date_string_to_tuple(s):
    """ Converts a date string of format 'yyyy-mm-dd' or 'dd/mm/yyyy' into a
    tuple of integers (y,m,d).  Input supports both a single string as well as a
    list of strings. """
    def d2t(d):
        return (d.year, d.month, d.day)
    if isinstance(s, list):
        return [d2t(_s2d(sd)) for sd in s]
    else:
        return d2t(_s2d(s))

def date_string_to_date(s):
    """ Converts a date string of format 'yyyy-mm-dd' or 'dd/mm/yyyy' into a
    python datetime.date object.  Input supports both a single string as well as
    a list of strings. """
    from datetime import date
    if isinstance(s, list):
        return [_s2d(sd) for sd in s]
    else:
        return _s2d(s)

def year_fraction_to_date(year_fraction):
    """ Converts a decimal/float year into a python datetime.date object.
    Input supports both a single float as well as a list of floats. """
    from datetime import date, timedelta
    def yf2d(yf):
        year = int(yf)
        fraction = yf - year
        # assuming 365.25 days per year
        day_of_year = int(fraction * 365.25)
        return date(year, 1, 1) + timedelta(days=day_of_year)
    if isinstance(year_fraction, list):
        return [yf2d(yf) for yf in year_fraction]
    else:
        return yf2d(year_fraction)

def year_fraction_to_date_str(year_fraction):
    """ Converts a decimal/float year into a string of format 'dd/mm/yyyy'.
    Input supports both a single float as well as a list of floats. """
    dd = year_fraction_to_date(year_fraction)
    if isinstance(dd, list):
        return [d.strftime("%d/%m/%Y") for d in dd]
    else:
        return dd.strftime("%d/%m/%Y")

def toYearFraction(date):
    """ converts python datetime objects into decimal/float years
    https://stackoverflow.com/a/6451892/2368167
    """
    from datetime import datetime as dt
    import time
    def sinceEpoch(date): # returns seconds since epoch
        return time.mktime(date.timetuple())
    s = sinceEpoch

    year = date.year
    startOfThisYear = dt(year=year, month=1, day=1)
    startOfNextYear = dt(year=year+1, month=1, day=1)

    yearElapsed = s(date) - s(startOfThisYear)
    yearDuration = s(startOfNextYear) - s(startOfThisYear)
    fraction = yearElapsed/yearDuration

    return date.year + fraction

def toYearFraction2(date):
    """ converts python datetime objects into decimal/float years
    https://stackoverflow.com/a/6451892/2368167

    fix Epoch issue?
    """
    from datetime import datetime as dt
    from datetime import date as dd
    import time
    def sinceEpoch(date): # returns seconds since epoch
        return date - dd(1970,1,1)
    s = sinceEpoch

    year = date.year
    startOfThisYear = dd(year=year, month=1, day=1)
    startOfNextYear = dd(year=year+1, month=1, day=1)

    yearElapsed = s(date) - s(startOfThisYear)
    yearDuration = s(startOfNextYear) - s(startOfThisYear)
    fraction = yearElapsed.total_seconds()/yearDuration.total_seconds()

    return date.year + fraction

def year_fraction(year, month, day):
    """ https://stackoverflow.com/a/36949905/2368167
    """
    import datetime
    date = datetime.date(year, month, day)
    start = datetime.date(date.year, 1, 1).toordinal()
    year_length = datetime.date(date.year+1, 1, 1).toordinal() - start
    return date.year + float(date.toordinal() - start) / year_length

class TestEasyDate(unittest.TestCase):
    """docstring for TestEasyDate"""
    def test_year_fraction(self):
        for d,f in [
            ((2023, 1, 1), 2023.0),
            ((2023, 6, 30), 2023.493),
            ((2023, 12, 31), 2023.997),
            ((2024, 1, 1), 2024.0),
        ]:
            result = year_fraction(*d)
            self.assertAlmostEqual(result, f, places=3)
                
    def test_year_fraction_mid_year(self):
        """Test year_fraction for middle of the year"""
        # Test July 1st (approximately mid-year)
        result = year_fraction(2023, 7, 1)
        self.assertGreater(result, 2023.4)
        self.assertLess(result, 2023.6)

    def test_year_fraction_to_date(self):
        """ test by starting with dd/mm/yyyy, convert to fraction, then back to dd/mm/yyyy, final one should be the same as the first one """
        ds = ['2011-03-05', '2011-3-6', '04/11/2011', '5/11/2011']
        for d in ds:
            dd = _s2d(d)
            f = toYearFraction2(dd)
            d2 = year_fraction_to_date(f)
            self.assertEqual(dd, d2)
        
        ds = ['04/11/2011', '05/01/2011']
        for d in ds:
            dd = _s2d(d)
            f = toYearFraction2(dd)
            d2 = year_fraction_to_date_str(f)
            self.assertEqual(d, d2)

    def test_tuple_to_string(self):
        s1 = (1995,10,2)
        s2 = [1995,10,2]
        ss = [s1, s2]
        for s in ss:
            self.assertEqual('1995-10-02', date_tuple_to_string(s))
        self.assertEqual(['1995-10-02']*2, date_tuple_to_string(ss))

    def test_string_to_tuple(self):
        d1 = '2011-03-05'
        d2 = '2011-3-5'
        d3 = '05/03/2011'
        d4 = '5/3/2011'
        ds = [d1,d2,d3,d4]
        for d in ds:
            self.assertEqual((2011,3,5), date_string_to_tuple(d))
        self.assertEqual([(2011,3,5)]*4, date_string_to_tuple(ds))

    def test_string_to_date(self):
        from datetime import date
        d1 = '2011-03-05'
        d2 = '2011-3-5'
        d3 = '05/03/2011'
        d4 = '5/3/2011'
        ds = [d1,d2,d3,d4]
        for d in ds:
            self.assertEqual(date(2011,3,5), date_string_to_date(d))
        self.assertEqual([date(2011,3,5)]*4, date_string_to_date(ds))



if __name__ == '__main__':
    unittest.main(verbosity=2)
