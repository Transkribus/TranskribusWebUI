from django.test import TestCase

from . import utils
from . import services


class TestUtilsMurl(TestCase):

    def test_equals_a(self):
        m = utils.mURL('a')

        self.assertNotEqual(str(m), 'b')
        self.assertEqual(str(m), 'a')

    def test_call_joins_path_segments(self):
        m = utils.mURL('a')

        self.assertEqual(str(m('a')), 'a/a', str(m('a')))

    def test_getitem_concatenates_strings(self):
        m = utils.mURL('a')

        self.assertEqual(str(m['a']), 'aa')

    def test_mixing_call_and_getitem(self):
        m = utils.mURL('a')

        self.assertEqual(str(m('b')['a']), 'a/ba')
        self.assertEqual(str(m['b']('a')['c']), 'ab/ac')
        self.assertEqual(str(m['b']('a')['c']('d')), 'ab/ac/d')

    def test_converts_int_to_string(self):
        m = utils.mURL('a')

        self.assertEqual(str(m['b']('3')['2'](1)), 'ab/32/1')

    def test_getattr_joins_path_segments(self):
        m = utils.mURL('a')

        self.assertEqual(str(m.a), 'a/a', str(m.a))
        self.assertEqual(str(m.a.a), 'a/a/a')
        self.assertEqual(str(m.a.a['a']), 'a/a/aa')


class TestTranskribusAPI(TestCase):

    def usage_example(self):

        api = services.TranskribusAPI()

        r = api.login(
            username='',
            password=''
        )

        # cookies = r.cookies.get_dict()
        cookies = api._session_cookies

        api = services.TranskribusAPI(cookies=cookies)

        self.fail(api.list_collections())
