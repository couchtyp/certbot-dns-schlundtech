"""Tests for certbot_dns_schlundtech.dns_schlundtech."""
import certbot.compat.os as os
import unittest

import mock
from certbot import errors
from certbot.plugins import dns_test_common
from certbot.plugins.dns_test_common import DOMAIN
from certbot.tests import util as test_util

patch_display_util = test_util.patch_display_util

USER = 'user'
PASSWORD = 'password'
CONTEXT = 10
TOKEN = 'token'
TTL = 10


class AuthenticatorTest(test_util.TempDirTestCase, dns_test_common.BaseAuthenticatorTest):

    def setUp(self):
        from certbot_dns_schlundtech.dns_schlundtech import Authenticator

        super(AuthenticatorTest, self).setUp()

        path = os.path.join(self.tempdir, 'file.ini')
        dns_test_common.write({
            "dns_schlundtech_user": USER,
            "dns_schlundtech_password": PASSWORD,
            "dns_schlundtech_context": CONTEXT,
            "dns_schlundtech_token": TOKEN,
        }, path)

        self.config = mock.MagicMock(dns_schlundtech_credentials=path, dns_schlundtech_propagation_seconds=0)
        self.auth = Authenticator(self.config, "dns-schlundtech")

        self.mock_client = mock.MagicMock()
        # _get_gateway_client | pylint: disable=protected-access
        self.auth._get_gateway_client = mock.MagicMock(return_value=self.mock_client)

    @patch_display_util()
    def test_perform(self, unused_mock_get_utility):
        self.auth.perform([self.achall])

        expected = [mock.call.add_txt_record(DOMAIN, '_acme-challenge.'+DOMAIN, mock.ANY)]
        self.assertEqual(expected, self.mock_client.mock_calls)

    @patch_display_util()
    def test_cleanup(self, unused_mock_get_utility):
        # _attempt_cleanup | pylint: disable=protected-access
        self.auth._attempt_cleanup = True
        self.auth.cleanup([self.achall])

        expected = [mock.call.del_txt_record(DOMAIN, '_acme-challenge.'+DOMAIN, mock.ANY)]
        self.assertEqual(expected, self.mock_client.mock_calls)


class SchlundtechGatewayClientTest(unittest.TestCase):
    record_name = "_acme-challenge"
    record_fqdn = record_name + "." + DOMAIN
    record_content = "bar"
    system_ns = "ns1." + DOMAIN

    def setUp(self):
        from certbot_dns_schlundtech.dns_schlundtech import _SchlundtechGatewayClient
        self.gateway_client = _SchlundtechGatewayClient(USER, PASSWORD, CONTEXT, TOKEN, TTL)
        self._mock_call({})  # Safety mock

    def test_auth(self):
        self.assertDictEqual(
            {
                'user': USER,
                'password': PASSWORD,
                'context': CONTEXT,
                'token': TOKEN
            },
            self.gateway_client._auth()
        )

    def test_zone_info(self):
        self._mock_zone_info('success', {'name': DOMAIN})
        zone = self.gateway_client._zone_info(DOMAIN, self.record_fqdn)
        self.assertDictEqual(zone, {'name': DOMAIN})

    def test_zone_info_domain_missing(self):
        self._mock_zone_info('error')
        self.assertRaises(errors.PluginError, self.gateway_client._zone_info, DOMAIN, self.record_fqdn)

    def test_add_txt_record(self):
        self._mock_zone_info('success', {'name': DOMAIN, 'system_ns': self.system_ns, 'soa': {'level': '1'}}, False)
        self._mock_call({'status': {'type': 'success'}})
        self.gateway_client.add_txt_record(DOMAIN, self.record_name, self.record_content)
        self.gateway_client._call.assert_called_with({
            'code': '0202001',
            'zone': {
                'name': DOMAIN,
                'system_ns': self.system_ns
            },
            'default': {
                'rr_add': {
                    'name': self.record_name,
                    'type': 'TXT',
                    'value': self.record_content,
                    'ttl': TTL
                },
                'soa': {'level': '1'}
            }
        })

    def test_add_txt_record_domain_missing(self):
        self._mock_zone_info('error')
        self.assertRaises(errors.PluginError,
                          self.gateway_client.add_txt_record, DOMAIN, self.record_name, self.record_content)

    def test_add_txt_record_already_exists(self):
        self._mock_zone_info('success',
                             {
                                 'name': DOMAIN, 'system_ns': self.system_ns, 'soa': {'level': '1'},
                                 'rr': [{'name': self.record_name, 'value': self.record_name}]
                             },
                             False)
        self._mock_call({'status': {'type': 'success'}})
        self.gateway_client.add_txt_record(DOMAIN, self.record_name, self.record_content)
        self.gateway_client._call.assert_called_with({
            'code': '0202001',
            'zone': {
                'name': DOMAIN,
                'system_ns': self.system_ns
            },
            'default': {
                'rr_add': {
                    'name': self.record_name,
                    'type': 'TXT',
                    'value': self.record_content,
                    'ttl': TTL
                },
                'soa': {'level': '1'}
            }
        })

    def test_add_txt_record_error(self):
        self._mock_zone_info('success', {'name': DOMAIN, 'system_ns': self.system_ns, 'soa': {'level': '1'}}, False)
        self._mock_call({'status': {'type': 'error'}})
        self.assertRaises(errors.PluginError,
                          self.gateway_client.add_txt_record, DOMAIN, self.record_name, self.record_content)

    def test_del_txt_record(self):
        self._mock_zone_info('success', {'name': DOMAIN, 'system_ns': self.system_ns, 'soa': {'level': '1'}}, False)
        self._mock_call({'status': {'type': 'success'}})
        self.gateway_client.del_txt_record(DOMAIN, self.record_name, self.record_content)
        self.gateway_client._call.assert_called_with({
            'code': '0202001',
            'zone': {
                'name': DOMAIN,
                'system_ns': self.system_ns
            },
            'default': {
                'rr_rem': {
                    'name': self.record_name,
                    'type': 'TXT',
                    'value': self.record_content,
                    'ttl': TTL
                }
            }
        })

    def test_del_txt_record_domain_missing(self):
        self._mock_zone_info('error')
        self.assertRaises(errors.PluginError,
                          self.gateway_client.del_txt_record, DOMAIN, self.record_name, self.record_content)

    def test_del_txt_record_error(self):
        self._mock_zone_info('success', {'name': DOMAIN, 'system_ns': self.system_ns, 'soa': {'level': '1'}}, False)
        self._mock_call({'status': {'type': 'error'}})
        self.assertRaises(errors.PluginError,
                          self.gateway_client.del_txt_record, DOMAIN, self.record_name, self.record_content)

    def _mock_zone_info(self, status, zone=None, mock_call=True):
        if mock_call:
            self._mock_call({'status': {'type': status}, 'data': {'zone': zone}})
        else:
            # _zone_info | pylint: disable=protected-access
            self.gateway_client._zone_info = mock.MagicMock(return_value=zone)

    def _mock_call(self, return_value):
        # _call | pylint: disable=protected-access
        self.gateway_client._call = mock.MagicMock(return_value=return_value)


class XmlTest(unittest.TestCase):
    tag = 'test'
    data = '<' + tag + '><a>1</a><a>2</a><b>hello</b></' + tag + '>'
    obj = {'a': ['1', '2'], 'b': 'hello'}
    encoding = 'UTF-8'

    def setUp(self):
        from certbot_dns_schlundtech.dns_schlundtech import _XML
        self.xml = _XML()

    def test_fromstring(self):
        r = self.xml.fromstring(self.data)
        self.assertDictEqual(self.obj, r)

    def test_tostring(self):
        r = self.xml.tostring(self.tag, self.obj).decode(self.encoding)
        self.assertEqual(self.data, r)


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
