from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/snmp-server.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_snmp_server = resolve('snmp_server')
    l_0_default_vrfs = resolve('default_vrfs')
    l_0_no_default_vrfs = resolve('no_default_vrfs')
    try:
        t_1 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    try:
        t_2 = environment.filters['arista.avd.hide_passwords']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.hide_passwords' found.")
    try:
        t_3 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_4 = environment.filters['list']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'list' found.")
    try:
        t_5 = environment.filters['rejectattr']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'rejectattr' found.")
    try:
        t_6 = environment.filters['selectattr']
    except KeyError:
        @internalcode
        def t_6(*unused):
            raise TemplateRuntimeError("No filter named 'selectattr' found.")
    try:
        t_7 = environment.filters['sort']
    except KeyError:
        @internalcode
        def t_7(*unused):
            raise TemplateRuntimeError("No filter named 'sort' found.")
    try:
        t_8 = environment.filters['string']
    except KeyError:
        @internalcode
        def t_8(*unused):
            raise TemplateRuntimeError("No filter named 'string' found.")
    try:
        t_9 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_9(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_9((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server)):
        pass
        yield '!\n'
        if t_9(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'ipv4_acls')):
            pass
            for l_1_acl in environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'ipv4_acls'):
                l_1_acl_cli = missing
                _loop_vars = {}
                pass
                l_1_acl_cli = str_join(('snmp-server ipv4 access-list ', environment.getattr(l_1_acl, 'name'), ))
                _loop_vars['acl_cli'] = l_1_acl_cli
                if t_9(environment.getattr(l_1_acl, 'vrf')):
                    pass
                    l_1_acl_cli = str_join(((undefined(name='acl_cli') if l_1_acl_cli is missing else l_1_acl_cli), ' vrf ', environment.getattr(l_1_acl, 'vrf'), ))
                    _loop_vars['acl_cli'] = l_1_acl_cli
                yield str((undefined(name='acl_cli') if l_1_acl_cli is missing else l_1_acl_cli))
                yield '\n'
            l_1_acl = l_1_acl_cli = missing
        if t_9(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'ipv6_acls')):
            pass
            for l_1_acl in environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'ipv6_acls'):
                l_1_acl_cli = missing
                _loop_vars = {}
                pass
                l_1_acl_cli = str_join(('snmp-server ipv6 access-list ', environment.getattr(l_1_acl, 'name'), ))
                _loop_vars['acl_cli'] = l_1_acl_cli
                if t_9(environment.getattr(l_1_acl, 'vrf')):
                    pass
                    l_1_acl_cli = str_join(((undefined(name='acl_cli') if l_1_acl_cli is missing else l_1_acl_cli), ' vrf ', environment.getattr(l_1_acl, 'vrf'), ))
                    _loop_vars['acl_cli'] = l_1_acl_cli
                yield str((undefined(name='acl_cli') if l_1_acl_cli is missing else l_1_acl_cli))
                yield '\n'
            l_1_acl = l_1_acl_cli = missing
        if t_9(environment.getattr(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'engine_ids'), 'local')):
            pass
            yield 'snmp-server engineID local '
            yield str(environment.getattr(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'engine_ids'), 'local'))
            yield '\n'
        if t_9(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'contact')):
            pass
            yield 'snmp-server contact '
            yield str(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'contact'))
            yield '\n'
        if t_9(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'location')):
            pass
            yield 'snmp-server location '
            yield str(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'location'))
            yield '\n'
        if t_9(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'local_interfaces')):
            pass
            for l_1_local_interface in t_3(t_5(context, environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'local_interfaces'), 'vrf', 'arista.avd.defined'), 'name'):
                _loop_vars = {}
                pass
                yield 'snmp-server local-interface '
                yield str(environment.getattr(l_1_local_interface, 'name'))
                yield '\n'
            l_1_local_interface = missing
            for l_1_local_interface in t_3(t_6(context, environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'local_interfaces'), 'vrf', 'arista.avd.defined'), sort_key='vrf', ignore_case=False):
                _loop_vars = {}
                pass
                yield 'snmp-server vrf '
                yield str(environment.getattr(l_1_local_interface, 'vrf'))
                yield ' local-interface '
                yield str(environment.getattr(l_1_local_interface, 'name'))
                yield '\n'
            l_1_local_interface = missing
        if t_9(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'views')):
            pass
            for l_1_view in t_3(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'views'), 'name'):
                l_1_view_cli = resolve('view_cli')
                _loop_vars = {}
                pass
                if t_9(environment.getattr(l_1_view, 'name')):
                    pass
                    l_1_view_cli = str_join(('snmp-server view ', environment.getattr(l_1_view, 'name'), ))
                    _loop_vars['view_cli'] = l_1_view_cli
                if t_9(environment.getattr(l_1_view, 'mib_family_name')):
                    pass
                    l_1_view_cli = str_join(((undefined(name='view_cli') if l_1_view_cli is missing else l_1_view_cli), ' ', environment.getattr(l_1_view, 'mib_family_name'), ))
                    _loop_vars['view_cli'] = l_1_view_cli
                if t_9(environment.getattr(l_1_view, 'included'), True):
                    pass
                    l_1_view_cli = str_join(((undefined(name='view_cli') if l_1_view_cli is missing else l_1_view_cli), ' included', ))
                    _loop_vars['view_cli'] = l_1_view_cli
                elif t_9(environment.getattr(l_1_view, 'included'), False):
                    pass
                    l_1_view_cli = str_join(((undefined(name='view_cli') if l_1_view_cli is missing else l_1_view_cli), ' excluded', ))
                    _loop_vars['view_cli'] = l_1_view_cli
                yield str((undefined(name='view_cli') if l_1_view_cli is missing else l_1_view_cli))
                yield '\n'
            l_1_view = l_1_view_cli = missing
        if t_9(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'communities')):
            pass
            for l_1_community in t_3(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'communities'), 'name'):
                l_1_hide_passwords = resolve('hide_passwords')
                l_1_communities_cli = missing
                _loop_vars = {}
                pass
                l_1_communities_cli = str_join(('snmp-server community ', t_2(environment.getattr(l_1_community, 'name'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)), ))
                _loop_vars['communities_cli'] = l_1_communities_cli
                if t_9(environment.getattr(l_1_community, 'view')):
                    pass
                    l_1_communities_cli = str_join(((undefined(name='communities_cli') if l_1_communities_cli is missing else l_1_communities_cli), ' view ', environment.getattr(l_1_community, 'view'), ))
                    _loop_vars['communities_cli'] = l_1_communities_cli
                if t_9(environment.getattr(l_1_community, 'access')):
                    pass
                    l_1_communities_cli = str_join(((undefined(name='communities_cli') if l_1_communities_cli is missing else l_1_communities_cli), ' ', environment.getattr(l_1_community, 'access'), ))
                    _loop_vars['communities_cli'] = l_1_communities_cli
                else:
                    pass
                    l_1_communities_cli = str_join(((undefined(name='communities_cli') if l_1_communities_cli is missing else l_1_communities_cli), ' ro', ))
                    _loop_vars['communities_cli'] = l_1_communities_cli
                if t_9(environment.getattr(l_1_community, 'access_list_ipv6')):
                    pass
                    l_1_communities_cli = str_join(((undefined(name='communities_cli') if l_1_communities_cli is missing else l_1_communities_cli), ' ipv6 ', environment.getattr(environment.getattr(l_1_community, 'access_list_ipv6'), 'name'), ))
                    _loop_vars['communities_cli'] = l_1_communities_cli
                if t_9(environment.getattr(l_1_community, 'access_list_ipv4')):
                    pass
                    l_1_communities_cli = str_join(((undefined(name='communities_cli') if l_1_communities_cli is missing else l_1_communities_cli), ' ', environment.getattr(environment.getattr(l_1_community, 'access_list_ipv4'), 'name'), ))
                    _loop_vars['communities_cli'] = l_1_communities_cli
                yield str((undefined(name='communities_cli') if l_1_communities_cli is missing else l_1_communities_cli))
                yield '\n'
            l_1_community = l_1_hide_passwords = l_1_communities_cli = missing
        if t_9(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'groups')):
            pass
            for l_1_group in t_3(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'groups'), 'name'):
                l_1_group_cli = resolve('group_cli')
                _loop_vars = {}
                pass
                if t_9(environment.getattr(l_1_group, 'name')):
                    pass
                    l_1_group_cli = str_join(('snmp-server group ', environment.getattr(l_1_group, 'name'), ))
                    _loop_vars['group_cli'] = l_1_group_cli
                if t_9(environment.getattr(l_1_group, 'version')):
                    pass
                    l_1_group_cli = str_join(((undefined(name='group_cli') if l_1_group_cli is missing else l_1_group_cli), ' ', environment.getattr(l_1_group, 'version'), ))
                    _loop_vars['group_cli'] = l_1_group_cli
                if (t_9(environment.getattr(l_1_group, 'authentication')) and t_9(environment.getattr(l_1_group, 'version'), 'v3')):
                    pass
                    l_1_group_cli = str_join(((undefined(name='group_cli') if l_1_group_cli is missing else l_1_group_cli), ' ', environment.getattr(l_1_group, 'authentication'), ))
                    _loop_vars['group_cli'] = l_1_group_cli
                if t_9(environment.getattr(l_1_group, 'read')):
                    pass
                    l_1_group_cli = str_join(((undefined(name='group_cli') if l_1_group_cli is missing else l_1_group_cli), ' read ', environment.getattr(l_1_group, 'read'), ))
                    _loop_vars['group_cli'] = l_1_group_cli
                if t_9(environment.getattr(l_1_group, 'write')):
                    pass
                    l_1_group_cli = str_join(((undefined(name='group_cli') if l_1_group_cli is missing else l_1_group_cli), ' write ', environment.getattr(l_1_group, 'write'), ))
                    _loop_vars['group_cli'] = l_1_group_cli
                if t_9(environment.getattr(l_1_group, 'notify')):
                    pass
                    l_1_group_cli = str_join(((undefined(name='group_cli') if l_1_group_cli is missing else l_1_group_cli), ' notify ', environment.getattr(l_1_group, 'notify'), ))
                    _loop_vars['group_cli'] = l_1_group_cli
                yield str((undefined(name='group_cli') if l_1_group_cli is missing else l_1_group_cli))
                yield '\n'
            l_1_group = l_1_group_cli = missing
        for l_1_user in t_5(context, t_3(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'users'), 'name'), 'remote_address', 'arista.avd.defined'):
            l_1_user_cli = resolve('user_cli')
            l_1_hide_passwords = resolve('hide_passwords')
            _loop_vars = {}
            pass
            if t_9(environment.getattr(l_1_user, 'name')):
                pass
                l_1_user_cli = str_join(('snmp-server user ', environment.getattr(l_1_user, 'name'), ))
                _loop_vars['user_cli'] = l_1_user_cli
            if t_9(environment.getattr(l_1_user, 'group')):
                pass
                l_1_user_cli = str_join(((undefined(name='user_cli') if l_1_user_cli is missing else l_1_user_cli), ' ', environment.getattr(l_1_user, 'group'), ))
                _loop_vars['user_cli'] = l_1_user_cli
            if t_9(environment.getattr(l_1_user, 'version')):
                pass
                l_1_user_cli = str_join(((undefined(name='user_cli') if l_1_user_cli is missing else l_1_user_cli), ' ', environment.getattr(l_1_user, 'version'), ))
                _loop_vars['user_cli'] = l_1_user_cli
            if ((t_9(environment.getattr(l_1_user, 'auth')) and t_9(environment.getattr(l_1_user, 'version'), 'v3')) and t_9(environment.getattr(l_1_user, 'auth_passphrase'))):
                pass
                if t_9(environment.getattr(l_1_user, 'localized')):
                    pass
                    l_1_user_cli = str_join(((undefined(name='user_cli') if l_1_user_cli is missing else l_1_user_cli), ' localized ', environment.getattr(l_1_user, 'localized'), ))
                    _loop_vars['user_cli'] = l_1_user_cli
                l_1_user_cli = str_join(((undefined(name='user_cli') if l_1_user_cli is missing else l_1_user_cli), ' auth ', environment.getattr(l_1_user, 'auth'), ' ', t_2(environment.getattr(l_1_user, 'auth_passphrase'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)), ))
                _loop_vars['user_cli'] = l_1_user_cli
                if (t_9(environment.getattr(l_1_user, 'priv')) and t_9(environment.getattr(l_1_user, 'priv_passphrase'))):
                    pass
                    l_1_user_cli = str_join(((undefined(name='user_cli') if l_1_user_cli is missing else l_1_user_cli), ' priv ', environment.getattr(l_1_user, 'priv'), ' ', t_2(environment.getattr(l_1_user, 'priv_passphrase'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)), ))
                    _loop_vars['user_cli'] = l_1_user_cli
            yield str((undefined(name='user_cli') if l_1_user_cli is missing else l_1_user_cli))
            yield '\n'
        l_1_user = l_1_user_cli = l_1_hide_passwords = missing
        for l_1_engine_id in t_3(environment.getattr(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'engine_ids'), 'remotes'), 'address'):
            l_1_remote_engine_ids_cli = resolve('remote_engine_ids_cli')
            _loop_vars = {}
            pass
            if (t_9(environment.getattr(l_1_engine_id, 'id')) and t_9(environment.getattr(l_1_engine_id, 'address'))):
                pass
                l_1_remote_engine_ids_cli = str_join(('snmp-server engineID remote ', environment.getattr(l_1_engine_id, 'address'), ))
                _loop_vars['remote_engine_ids_cli'] = l_1_remote_engine_ids_cli
                if t_9(environment.getattr(l_1_engine_id, 'udp_port')):
                    pass
                    l_1_remote_engine_ids_cli = str_join(((undefined(name='remote_engine_ids_cli') if l_1_remote_engine_ids_cli is missing else l_1_remote_engine_ids_cli), ' udp-port ', environment.getattr(l_1_engine_id, 'udp_port'), ))
                    _loop_vars['remote_engine_ids_cli'] = l_1_remote_engine_ids_cli
                l_1_remote_engine_ids_cli = str_join(((undefined(name='remote_engine_ids_cli') if l_1_remote_engine_ids_cli is missing else l_1_remote_engine_ids_cli), ' ', environment.getattr(l_1_engine_id, 'id'), ))
                _loop_vars['remote_engine_ids_cli'] = l_1_remote_engine_ids_cli
                yield str((undefined(name='remote_engine_ids_cli') if l_1_remote_engine_ids_cli is missing else l_1_remote_engine_ids_cli))
                yield '\n'
        l_1_engine_id = l_1_remote_engine_ids_cli = missing
        for l_1_user in t_6(context, t_3(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'users'), 'name'), 'remote_address', 'arista.avd.defined'):
            l_1_user_cli = resolve('user_cli')
            l_1_hide_passwords = resolve('hide_passwords')
            _loop_vars = {}
            pass
            if t_9(environment.getattr(l_1_user, 'name')):
                pass
                l_1_user_cli = str_join(('snmp-server user ', environment.getattr(l_1_user, 'name'), ))
                _loop_vars['user_cli'] = l_1_user_cli
            if t_9(environment.getattr(l_1_user, 'group')):
                pass
                l_1_user_cli = str_join(((undefined(name='user_cli') if l_1_user_cli is missing else l_1_user_cli), ' ', environment.getattr(l_1_user, 'group'), ))
                _loop_vars['user_cli'] = l_1_user_cli
            if (t_9(environment.getattr(l_1_user, 'remote_address')) and t_9(environment.getattr(l_1_user, 'version'), 'v3')):
                pass
                l_1_user_cli = str_join(((undefined(name='user_cli') if l_1_user_cli is missing else l_1_user_cli), ' remote ', environment.getattr(l_1_user, 'remote_address'), ))
                _loop_vars['user_cli'] = l_1_user_cli
                if t_9(environment.getattr(l_1_user, 'udp_port')):
                    pass
                    l_1_user_cli = str_join(((undefined(name='user_cli') if l_1_user_cli is missing else l_1_user_cli), ' udp-port ', environment.getattr(l_1_user, 'udp_port'), ))
                    _loop_vars['user_cli'] = l_1_user_cli
            if t_9(environment.getattr(l_1_user, 'version')):
                pass
                l_1_user_cli = str_join(((undefined(name='user_cli') if l_1_user_cli is missing else l_1_user_cli), ' ', environment.getattr(l_1_user, 'version'), ))
                _loop_vars['user_cli'] = l_1_user_cli
            if ((t_9(environment.getattr(l_1_user, 'auth')) and t_9(environment.getattr(l_1_user, 'version'), 'v3')) and t_9(environment.getattr(l_1_user, 'auth_passphrase'))):
                pass
                if t_9(environment.getattr(l_1_user, 'localized')):
                    pass
                    l_1_user_cli = str_join(((undefined(name='user_cli') if l_1_user_cli is missing else l_1_user_cli), ' localized ', environment.getattr(l_1_user, 'localized'), ))
                    _loop_vars['user_cli'] = l_1_user_cli
                l_1_user_cli = str_join(((undefined(name='user_cli') if l_1_user_cli is missing else l_1_user_cli), ' auth ', environment.getattr(l_1_user, 'auth'), ' ', t_2(environment.getattr(l_1_user, 'auth_passphrase'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)), ))
                _loop_vars['user_cli'] = l_1_user_cli
                if (t_9(environment.getattr(l_1_user, 'priv')) and t_9(environment.getattr(l_1_user, 'priv_passphrase'))):
                    pass
                    l_1_user_cli = str_join(((undefined(name='user_cli') if l_1_user_cli is missing else l_1_user_cli), ' priv ', environment.getattr(l_1_user, 'priv'), ' ', t_2(environment.getattr(l_1_user, 'priv_passphrase'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)), ))
                    _loop_vars['user_cli'] = l_1_user_cli
            yield str((undefined(name='user_cli') if l_1_user_cli is missing else l_1_user_cli))
            yield '\n'
        l_1_user = l_1_user_cli = l_1_hide_passwords = missing
        for l_1_host in t_7(environment, t_1(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'hosts'), []), attribute='host'):
            l_1_host_cli = resolve('host_cli')
            l_1_hide_passwords = resolve('hide_passwords')
            _loop_vars = {}
            pass
            if t_9(environment.getattr(l_1_host, 'host')):
                pass
                l_1_host_cli = str_join(('snmp-server host ', environment.getattr(l_1_host, 'host'), ))
                _loop_vars['host_cli'] = l_1_host_cli
                if t_9(environment.getattr(l_1_host, 'vrf')):
                    pass
                    l_1_host_cli = str_join(((undefined(name='host_cli') if l_1_host_cli is missing else l_1_host_cli), ' vrf ', environment.getattr(l_1_host, 'vrf'), ))
                    _loop_vars['host_cli'] = l_1_host_cli
                if (t_9(environment.getattr(l_1_host, 'users')) and (t_8(t_1(environment.getattr(l_1_host, 'version'), '3')) == '3')):
                    pass
                    for l_2_user in environment.getattr(l_1_host, 'users'):
                        _loop_vars = {}
                        pass
                        if (t_9(environment.getattr(l_2_user, 'username')) and t_9(environment.getattr(l_2_user, 'authentication_level'))):
                            pass
                            yield str((undefined(name='host_cli') if l_1_host_cli is missing else l_1_host_cli))
                            yield ' version 3 '
                            yield str(environment.getattr(l_2_user, 'authentication_level'))
                            yield ' '
                            yield str(environment.getattr(l_2_user, 'username'))
                            yield '\n'
                    l_2_user = missing
                elif (t_9(environment.getattr(l_1_host, 'community')) and (t_8(t_1(environment.getattr(l_1_host, 'version'), '2c')) in ['1', '2c'])):
                    pass
                    yield str((undefined(name='host_cli') if l_1_host_cli is missing else l_1_host_cli))
                    yield ' version '
                    yield str(t_1(environment.getattr(l_1_host, 'version'), '2c'))
                    yield ' '
                    yield str(t_2(environment.getattr(l_1_host, 'community'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)))
                    yield '\n'
        l_1_host = l_1_host_cli = l_1_hide_passwords = missing
        if t_9(environment.getattr(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'traps'), 'enable'), True):
            pass
            yield 'snmp-server enable traps\n'
        elif t_9(environment.getattr(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'traps'), 'enable'), False):
            pass
            yield 'no snmp-server enable traps\n'
        for l_1_snmp_trap in t_3(environment.getattr(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'traps'), 'snmp_traps'), 'name'):
            _loop_vars = {}
            pass
            if t_9(environment.getattr(l_1_snmp_trap, 'enabled'), False):
                pass
                yield 'no snmp-server enable traps '
                yield str(environment.getattr(l_1_snmp_trap, 'name'))
                yield '\n'
            else:
                pass
                yield 'snmp-server enable traps '
                yield str(environment.getattr(l_1_snmp_trap, 'name'))
                yield '\n'
        l_1_snmp_trap = missing
        if t_9(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'vrfs')):
            pass
            l_0_default_vrfs = t_4(context.eval_ctx, t_6(context, environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'vrfs'), 'name', 'equalto', 'default'))
            context.vars['default_vrfs'] = l_0_default_vrfs
            context.exported_vars.add('default_vrfs')
            l_0_no_default_vrfs = t_3(t_5(context, environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'vrfs'), 'name', 'equalto', 'default'), 'name', ignore_case=False)
            context.vars['no_default_vrfs'] = l_0_no_default_vrfs
            context.exported_vars.add('no_default_vrfs')
            for l_1_vrf in ((undefined(name='default_vrfs') if l_0_default_vrfs is missing else l_0_default_vrfs) + (undefined(name='no_default_vrfs') if l_0_no_default_vrfs is missing else l_0_no_default_vrfs)):
                _loop_vars = {}
                pass
                if t_9(environment.getattr(l_1_vrf, 'enable'), True):
                    pass
                    yield 'snmp-server vrf '
                    yield str(environment.getattr(l_1_vrf, 'name'))
                    yield '\n'
                else:
                    pass
                    yield 'no snmp-server vrf '
                    yield str(environment.getattr(l_1_vrf, 'name'))
                    yield '\n'
            l_1_vrf = missing
        if t_9(environment.getattr((undefined(name='snmp_server') if l_0_snmp_server is missing else l_0_snmp_server), 'ifmib_ifspeed_shape_rate'), True):
            pass
            yield 'snmp-server ifmib ifspeed shape-rate\n'

blocks = {}
debug_info = '7=68&10=71&11=73&12=77&13=79&14=81&16=83&19=86&20=88&21=92&22=94&23=96&25=98&28=101&29=104&31=106&32=109&34=111&35=114&37=116&38=118&39=122&41=125&42=129&45=134&46=136&47=140&48=142&50=144&51=146&53=148&54=150&55=152&56=154&58=156&61=159&62=161&63=166&64=168&65=170&67=172&68=174&70=178&72=180&73=182&75=184&76=186&78=188&81=191&82=193&83=197&84=199&86=201&87=203&89=205&90=207&92=209&93=211&95=213&96=215&98=217&99=219&101=221&105=224&106=229&107=231&109=233&110=235&112=237&113=239&115=241&118=243&119=245&121=247&122=249&124=251&127=253&129=256&130=260&131=262&132=264&133=266&135=268&136=270&140=273&141=278&142=280&144=282&145=284&147=286&148=288&149=290&150=292&153=294&154=296&156=298&159=300&160=302&162=304&163=306&165=308&168=310&170=313&171=318&172=320&173=322&174=324&176=326&178=328&179=331&181=333&184=340&186=342&190=349&192=352&195=355&196=358&197=361&199=366&202=369&203=371&204=374&205=377&206=380&207=383&209=388&213=391'