#!/usr/bin/env python3
#
# Copyright (C) 2024 VyOS maintainers and contributors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 or later as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from base_vyostest_shim import VyOSUnitTestSHIM

from vyos.ifconfig import Section
from vyos.utils.process import process_named_running
from vyos.xml_ref import default_value

PROCESS_NAME = 'babeld'
base_path = ['protocols', 'babel']

class TestProtocolsBABEL(VyOSUnitTestSHIM.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._interfaces = Section.interfaces('ethernet', vlan=False)
        # call base-classes classmethod
        super(TestProtocolsBABEL, cls).setUpClass()
        # Retrieve FRR daemon PID - it is not allowed to crash, thus PID must remain the same
        cls.daemon_pid = process_named_running(PROCESS_NAME)
        # ensure we can also run this test on a live system - so lets clean
        # out the current configuration :)
        cls.cli_delete(cls, base_path)

    def tearDown(self):
        # always destroy the entire babel configuration to make the processes
        # life as hard as possible
        self.cli_delete(base_path)
        self.cli_commit()

        # check process health and continuity
        self.assertEqual(self.daemon_pid, process_named_running(PROCESS_NAME))

    def test_babel_interfaces(self):
        def_update_interval = default_value(base_path + ['interface', 'eth0', 'update-interval'])
        channel = '20'
        hello_interval = '1000'
        max_rtt_penalty = '100'
        rtt_decay = '23'
        rtt_max = '119'
        rtt_min = '11'
        rxcost = '40000'
        type = 'wired'

        for interface in self._interfaces:
            self.cli_set(base_path + ['interface', interface])
            self.cli_set(base_path + ['interface', interface, 'channel', channel])
            self.cli_set(base_path + ['interface', interface, 'enable-timestamps'])
            self.cli_set(base_path + ['interface', interface, 'hello-interval', hello_interval])
            self.cli_set(base_path + ['interface', interface, 'max-rtt-penalty', max_rtt_penalty])
            self.cli_set(base_path + ['interface', interface, 'rtt-decay', rtt_decay])
            self.cli_set(base_path + ['interface', interface, 'rtt-max', rtt_max])
            self.cli_set(base_path + ['interface', interface, 'rtt-min', rtt_min])
            self.cli_set(base_path + ['interface', interface, 'enable-timestamps'])
            self.cli_set(base_path + ['interface', interface, 'rxcost', rxcost])
            self.cli_set(base_path + ['interface', interface, 'split-horizon', 'disable'])
            self.cli_set(base_path + ['interface', interface, 'type', type])

        self.cli_commit()

        frrconfig = self.getFRRconfig('router babel', daemon=PROCESS_NAME)
        for interface in self._interfaces:
            self.assertIn(f' network {interface}', frrconfig)

            iface_config = self.getFRRconfig(f'interface {interface}', daemon=PROCESS_NAME)
            self.assertIn(f' babel channel {channel}', iface_config)
            self.assertIn(f' babel enable-timestamps', iface_config)
            self.assertIn(f' babel update-interval {def_update_interval}', iface_config)
            self.assertIn(f' babel hello-interval {hello_interval}', iface_config)
            self.assertIn(f' babel rtt-decay {rtt_decay}', iface_config)
            self.assertIn(f' babel rtt-max {rtt_max}', iface_config)
            self.assertIn(f' babel rtt-min {rtt_min}', iface_config)
            self.assertIn(f' babel rxcost {rxcost}', iface_config)
            self.assertIn(f' babel max-rtt-penalty {max_rtt_penalty}', iface_config)
            self.assertIn(f' no babel split-horizon', iface_config)
            self.assertIn(f' babel {type}', iface_config)

    def test_babel_redistribute(self):
        ipv4_protos = ['bgp', 'connected', 'isis', 'kernel', 'ospf', 'rip', 'static']
        ipv6_protos = ['bgp', 'connected', 'isis', 'kernel', 'ospfv3', 'ripng', 'static']

        for protocol in ipv4_protos:
            self.cli_set(base_path + ['redistribute', 'ipv4', protocol])
        for protocol in ipv6_protos:
            self.cli_set(base_path + ['redistribute', 'ipv6', protocol])

        self.cli_commit()

        frrconfig = self.getFRRconfig('router babel', daemon=PROCESS_NAME)
        for protocol in ipv4_protos:
            self.assertIn(f' redistribute ipv4 {protocol}', frrconfig)
        for protocol in ipv6_protos:
            if protocol == 'ospfv3':
                protocol = 'ospf6'
            self.assertIn(f' redistribute ipv6 {protocol}', frrconfig)

    def test_babel_basic(self):
        diversity_factor = '64'
        resend_delay = '100'
        smoothing_half_life = '400'

        self.cli_set(base_path + ['parameters', 'diversity'])
        self.cli_set(base_path + ['parameters', 'diversity-factor', diversity_factor])
        self.cli_set(base_path + ['parameters', 'resend-delay', resend_delay])
        self.cli_set(base_path + ['parameters', 'smoothing-half-life', smoothing_half_life])

        self.cli_commit()

        frrconfig = self.getFRRconfig('router babel', daemon=PROCESS_NAME)
        self.assertIn(f' babel diversity', frrconfig)
        self.assertIn(f' babel diversity-factor {diversity_factor}', frrconfig)
        self.assertIn(f' babel resend-delay {resend_delay}', frrconfig)
        self.assertIn(f' babel smoothing-half-life {smoothing_half_life}', frrconfig)

if __name__ == '__main__':
    unittest.main(verbosity=2)
