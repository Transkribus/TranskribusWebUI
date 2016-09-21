from unittest import mock

from django.test import TestCase

from . import utils
from . import services

from .models import User, UserInfo
from .auth_backends import TranskribusBackend


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


class TestTranskribusBackend(TestCase):

    @mock.patch('transkribus.services.login')
    def test_authenticate_fails(self, login):

        login.return_value = {}

        backend = TranskribusBackend()

        user = backend.authenticate(username='some', password='thing')

        self.assertIsNone(user)
        self.assertEqual(User.objects.count(), 0)

    @mock.patch('transkribus.services.login')
    def test_creates_user(self, login):

        login.return_value = {
            'username': 'some',
            'password': 'thing',
            'first_name': 'some',
            'last_name': 'thing',
            'is_superuser': False,
            'gender': 'unknown',
            'affiliation': 'unknown',
            'email': 'some@thing.org',
            'session_id': 'deadbeef',
        }

        backend = TranskribusBackend()

        user = backend.authenticate(username='some', password='thing')

        self.assertIsNotNone(user)
        expected = User.objects.all().first().pk
        self.assertEqual(expected, user.pk)

    @mock.patch('transkribus.services.login')
    def test_creates_user_info(self, login):

        expected = User.objects.create(username='some')

        login.return_value = {
            'username': 'some',
            'password': 'thing',
            'first_name': 'some',
            'last_name': 'thing',
            'is_superuser': False,
            'gender': 'neuter',
            'affiliation': 'nouns',
            'email': 'some@thing.org',
            'session_id': 'deadbeef',
        }

        backend = TranskribusBackend()

        user = backend.authenticate(username='some', password='thing')


        self.assertEqual(expected.pk, user.pk)

        self.assertIsInstance(expected.info, UserInfo)

        self.assertEqual(user.first_name, 'some')
        self.assertEqual(user.last_name, 'thing')

        self.assertEqual(user.info.affiliation, 'nouns')
        self.assertEqual(user.info.gender, 'neuter')

    @mock.patch('transkribus.services.login')
    def test_updates_user_data(self, login):

        data_1 = {
            'username': 'some',
            'password': 'thing',
            'first_name': 'some',
            'last_name': 'thing',
            'is_superuser': False,
            'email': 'some@thing.org',
        }

        data_2 = {
            'gender': 'neuter',
            'affiliation': 'nouns',
            'session_id': 'deadbeef',
        }

        user = User.objects.create(**data_1)
        info = UserInfo.objects.create(user=user, **data_2)

        user_pk = user.pk
        info_pk = info.pk

        data = {}

        data_1['last_name'] = 'how'
        data_2['affiliation'] = 'adverb'
        data_2['gender'] = 'n/a'

        data.update(data_1)
        data.update(data_2)

        login.return_value = data

        backend = TranskribusBackend()

        user = backend.authenticate(username='some', password='thing')

        self.assertEqual(user.pk, user_pk)
        self.assertEqual(info.pk, info_pk)
        self.assertIsInstance(user.info, UserInfo)

        self.assertEqual(user.first_name, 'some')
        self.assertEqual(user.last_name, 'how')

        self.assertEqual(user.info.affiliation, 'adverb')
        self.assertEqual(user.info.gender, 'n/a')


class TestServices(TestCase):

    data = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><trpUserLogin><userId>1</userId><userName>some@thing.org</userName><email>some@thing.org</email><affiliation>nouns</affiliation><firstname>some</firstname><lastname>thing</lastname><gender>neuter</gender><isActive>1</isActive><isAdmin>true</isAdmin><created><nanos>0</nanos></created><loginTime>1776-07-04T02:55:09.625+02:00</loginTime><sessionId>1AF785265C5FEA0F0B2ED78BEB0F6E0A</sessionId><userAgent>TranskribusWebUI</userAgent><ip>1.2.3.4</ip></trpUserLogin>'

    @mock.patch('requests.post')
    def test_login_succeeds(self, post):

        import io

        post.return_value = mock.Mock(
            status_code=200,
            headers={'Content-Type': 'application/xml;charset=utf-8'},
            content=self.data,
        )

        data = services.login(
            username='some',
            password='thing',
        )

        self.assertEqual(data['first_name'], 'some')
        self.assertEqual(data['last_name'], 'thing')
        self.assertEqual(data['is_superuser'], True)
        self.assertEqual(data['is_active'], True)

    @mock.patch('requests.post')
    def test_login_fails(self, post):

        import io

        post.return_value = mock.Mock(
            status_code=401,
            headers={},
            content=b'',
        )

        data = services.login(
            username='some',
            password='thing',
        )

        self.assertDictEqual(data, {})

    def test_serialize(self):
        self.fail("Implement _serialize test case")


class TestLoginRequired(TestCase):

    @mock.patch('transkribus.services.login')
    def test_retrieve_test_view_works_when_logged_in(self, login):

        test_url = '/transkribus/test/'

        user = User.objects.create_user(username='some', password='thing', email='some@thing.org')

        login.return_value = {
            'username': 'some',
            'password': 'thing',
            'first_name': 'some',
            'last_name': 'thing',
            'is_superuser': False,
            'gender': 'unknown',
            'affiliation': 'unknown',
            'email': 'some@thing.org',
            'session_id': 'deadbeef',
        }

        is_logged_in = self.client.login(username='some', password='thing')

        self.assertTrue(is_logged_in)

        r = self.client.get(test_url)

        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, b'OK')

    @mock.patch('transkribus.auth_backends.TranskribusBackend')
    def test_logged_in_fails(self, backend):
        import logging

        test_url = '/transkribus/test/'

        user = User.objects.create_user(username='some', password='thing', email='some@thing.org', is_active=True)

        backend.return_value = mock.Mock(authenticate=lambda **_: None)

        is_logged_in = self.client.login(username='some', password='thing', follow=True)

        self.assertFalse(is_logged_in)

    def test_redirect_if_no_login(self):

        test_url = '/transkribus/test/'
        expected_url = "{}/?next={}".format('/login', test_url)

        response = self.client.get(test_url, follow=True)

        self.assertRedirects(response, expected_url)
