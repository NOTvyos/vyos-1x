#!/usr/bin/env python3
#
# Copyright (C) 2018-2024 VyOS maintainers and contributors
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

import os

from sys import exit
from syslog import syslog
from syslog import LOG_INFO

from vyos.config import Config
from vyos.configdict import is_node_changed
from vyos.configverify import verify_vrf
from vyos.utils.process import call
from vyos.template import render
from vyos import ConfigError
from vyos import airbag
<<<<<<< HEAD
=======
from vyos.pki import find_chain
from vyos.pki import encode_certificate
from vyos.pki import load_certificate
from vyos.utils.dict import dict_search_recursive
from vyos.utils.file import write_file

>>>>>>> 81dfb64eb (ssh: T6013: move principal name to "system login user <name> authentication")
airbag.enable()

config_file = r'/run/sshd/sshd_config'

sshguard_config_file = '/etc/sshguard/sshguard.conf'
sshguard_whitelist = '/etc/sshguard/whitelist'

key_rsa = '/etc/ssh/ssh_host_rsa_key'
key_dsa = '/etc/ssh/ssh_host_dsa_key'
key_ed25519 = '/etc/ssh/ssh_host_ed25519_key'

<<<<<<< HEAD
=======
trusted_user_ca_key = '/etc/ssh/trusted_user_ca_key'

>>>>>>> 6c3b1ef2f (ssh: T6013: support SSH AuthorizedPrincipalsFile in use with trusted-user-ca-key)
def get_config(config=None):
    if config:
        conf = config
    else:
        conf = Config()
    base = ['service', 'ssh']
    if not conf.exists(base):
        return None
    ssh = conf.get_config_dict(base, key_mangling=('-', '_'),
                               get_first_key=True, with_pki=True)

<<<<<<< HEAD
<<<<<<< HEAD
    ssh = conf.get_config_dict(base, key_mangling=('-', '_'), get_first_key=True)
=======
    ssh = conf.get_config_dict(
        base, key_mangling=('-', '_'), get_first_key=True, with_pki=True
    )
    login_users_base = ['system', 'login', 'user']
    login_users = conf.get_config_dict(
        login_users_base,
        key_mangling=('-', '_'),
        no_tag_node_value_mangle=True,
        get_first_key=True,
    )
>>>>>>> 6c3b1ef2f (ssh: T6013: support SSH AuthorizedPrincipalsFile in use with trusted-user-ca-key)

    # create a list of all users, cli and users
=======
>>>>>>> 81dfb64eb (ssh: T6013: move principal name to "system login user <name> authentication")
    tmp = is_node_changed(conf, base + ['vrf'])
    if tmp: ssh.update({'restart_required': {}})

    # We have gathered the dict representation of the CLI, but there are default
    # options which we need to update into the dictionary retrived.
    ssh = conf.merge_defaults(ssh, recursive=True)

    # Ignore default XML values if config doesn't exists
    # Delete key from dict
    if not conf.exists(base + ['dynamic-protection']):
         del ssh['dynamic_protection']

    # See if any user has specified a list of principal names that are accepted
    # for certificate authentication.
    tmp = conf.get_config_dict(['system', 'login', 'user'],
                                key_mangling=('-', '_'),
                                no_tag_node_value_mangle=True,
                                get_first_key=True)

    for value, _ in dict_search_recursive(tmp, 'principal'):
        # Only enable principal handling if SSH trusted-user-ca-key is set
        if 'trusted_user_ca_key' in ssh:
            ssh['trusted_user_ca_key'].update({'has_principals': {}})
        # We do only need to execute this code path once as we need to know
        # if any one of the local users has a principal set or not - this
        # accounts for the entire system.
        break

    return ssh

def verify(ssh):
    if not ssh:
        return None

    if 'rekey' in ssh and 'data' not in ssh['rekey']:
<<<<<<< HEAD
        raise ConfigError(f'Rekey data is required!')
=======
        raise ConfigError('Rekey data is required!')

    if 'trusted_user_ca_key' in ssh:
        if 'ca_certificate' not in ssh['trusted_user_ca_key']:
            raise ConfigError('CA certificate is mandatory when using ' \
                              'trusted-user-ca-key')

        ca_key_name = ssh['trusted_user_ca_key']['ca_certificate']
        verify_pki_ca_certificate(ssh, ca_key_name)
        pki_ca_cert = ssh['pki']['ca'][ca_key_name]
        if 'certificate' not in pki_ca_cert or not pki_ca_cert['certificate']:
            raise ConfigError(f"CA certificate '{ca_key_name}' is not valid or missing")
>>>>>>> 81dfb64eb (ssh: T6013: move principal name to "system login user <name> authentication")

    verify_vrf(ssh)
    return None

def generate(ssh):
    if not ssh:
        if os.path.isfile(config_file):
            os.unlink(config_file)

        return None

    # This usually happens only once on a fresh system, SSH keys need to be
    # freshly generted, one per every system!
    if not os.path.isfile(key_rsa):
        syslog(LOG_INFO, 'SSH RSA host key not found, generating new key!')
        call(f'ssh-keygen -q -N "" -t rsa -f {key_rsa}')
    if not os.path.isfile(key_dsa):
        syslog(LOG_INFO, 'SSH DSA host key not found, generating new key!')
        call(f'ssh-keygen -q -N "" -t dsa -f {key_dsa}')
    if not os.path.isfile(key_ed25519):
        syslog(LOG_INFO, 'SSH ed25519 host key not found, generating new key!')
        call(f'ssh-keygen -q -N "" -t ed25519 -f {key_ed25519}')

<<<<<<< HEAD
<<<<<<< HEAD
=======
    handle_trusted_user_ca_key(ssh)
=======
    if 'trusted_user_ca_key' in ssh:
        ca_key_name = ssh['trusted_user_ca_key']['ca_certificate']
        pki_ca_cert = ssh['pki']['ca'][ca_key_name]

        loaded_ca_cert = load_certificate(pki_ca_cert['certificate'])
        loaded_ca_certs = {
            load_certificate(c['certificate'])
            for c in ssh['pki']['ca'].values()
            if 'certificate' in c
        }

        ca_full_chain = find_chain(loaded_ca_cert, loaded_ca_certs)
        write_file(trusted_user_ca_key,
                   '\n'.join(encode_certificate(c) for c in ca_full_chain))
    else:
        if os.path.exists(trusted_user_ca_key):
            os.unlink(trusted_user_ca_key)
>>>>>>> 81dfb64eb (ssh: T6013: move principal name to "system login user <name> authentication")

>>>>>>> 6c3b1ef2f (ssh: T6013: support SSH AuthorizedPrincipalsFile in use with trusted-user-ca-key)
    render(config_file, 'ssh/sshd_config.j2', ssh)

    if 'dynamic_protection' in ssh:
        render(sshguard_config_file, 'ssh/sshguard_config.j2', ssh)
        render(sshguard_whitelist, 'ssh/sshguard_whitelist.j2', ssh)

    return None

def apply(ssh):
    systemd_service_ssh = 'ssh.service'
    systemd_service_sshguard = 'sshguard.service'
    if not ssh:
        # SSH access is removed in the commit
        call(f'systemctl stop ssh@*.service')
        call(f'systemctl stop {systemd_service_sshguard}')
        return None

    if 'dynamic_protection' not in ssh:
        call(f'systemctl stop {systemd_service_sshguard}')
    else:
        call(f'systemctl reload-or-restart {systemd_service_sshguard}')

    # we need to restart the service if e.g. the VRF name changed
    systemd_action = 'reload-or-restart'
    if 'restart_required' in ssh:
        # this is only true if something for the VRFs changed, thus we
        # stop all VRF services and only restart then new ones
        call(f'systemctl stop ssh@*.service')
        systemd_action = 'restart'

    for vrf in ssh['vrf']:
        call(f'systemctl {systemd_action} ssh@{vrf}.service')
    return None

if __name__ == '__main__':
    try:
        c = get_config()
        verify(c)
        generate(c)
        apply(c)
    except ConfigError as e:
        print(e)
        exit(1)
