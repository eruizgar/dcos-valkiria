from __future__ import absolute_import
import unittest
from dcos_valkiria import cli


class TestCli(unittest.TestCase):

    def test_get_ips_list(self):
        self.assertEquals(cli._get_ips_list(None), 1)
        self.assertEquals(cli._get_ips_list('10.200.1.21'), ['10.200.1.21'])
        self.assertEquals(cli._get_ips_list('10.200.1.21,13.12.12.123'), ['10.200.1.21', '13.12.12.123'])
        self.assertEquals(cli._get_ips_list('123.123.123.123 123.123.123.124'), ['123.123.123.123', '123.123.123.124'])
        self.assertEquals(cli._get_ips_list('123.123.123.123 123.123.123.124 , 152.245.112.152'), ['123.123.123.123', '123.123.123.124', '152.245.112.152'])
        self.assertEquals(cli._get_ips_list('333.200.1.21'), ['333.200.1.21'])
        self.assertEquals(cli._get_ips_list('200.1.21'), [])
        self.assertEquals(cli._get_ips_list('1233.200.1.21'), [])
        self.assertEquals(cli._get_ips_list('1233.200.1.21 23.23.23.23'), ['23.23.23.23'])


if __name__ == "__main__":
    unittest.main()
