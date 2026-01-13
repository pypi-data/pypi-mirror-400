from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/traffic-policies.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_traffic_policies = resolve('traffic_policies')
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_2 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    try:
        t_3 = environment.filters['lower']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'lower' found.")
    try:
        t_4 = environment.filters['unique']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'unique' found.")
    try:
        t_5 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    try:
        t_6 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_6(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    if t_5((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies)):
        pass
        yield '!\ntraffic-policies\n'
        for l_1_field_set_port in t_1(environment.getattr(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'field_sets'), 'ports'), sort_key='name', ignore_case=False):
            _loop_vars = {}
            pass
            yield '   field-set l4-port '
            yield str(environment.getattr(l_1_field_set_port, 'name'))
            yield '\n'
            if t_5(environment.getattr(l_1_field_set_port, 'port_range')):
                pass
                yield '      '
                yield str(environment.getattr(l_1_field_set_port, 'port_range'))
                yield '\n'
            yield '   !\n'
        l_1_field_set_port = missing
        l_1_loop = missing
        for l_1_field_set_ipv4, l_1_loop in LoopContext(t_1(environment.getattr(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'field_sets'), 'ipv4'), sort_key='name', ignore_case=False), undefined):
            _loop_vars = {}
            pass
            yield '   field-set ipv4 prefix '
            yield str(environment.getattr(l_1_field_set_ipv4, 'name'))
            yield '\n'
            if t_5(environment.getattr(l_1_field_set_ipv4, 'prefixes')):
                pass
                yield '      '
                yield str(t_2(context.eval_ctx, t_1(environment.getattr(l_1_field_set_ipv4, 'prefixes')), ' '))
                yield '\n'
            if t_5(environment.getattr(l_1_field_set_ipv4, 'except')):
                pass
                yield '      except '
                yield str(t_2(context.eval_ctx, t_1(environment.getattr(l_1_field_set_ipv4, 'except')), ' '))
                yield '\n'
            if (not environment.getattr(l_1_loop, 'last')):
                pass
                yield '   !\n'
        l_1_loop = l_1_field_set_ipv4 = missing
        l_1_loop = missing
        for l_1_field_set_ipv6, l_1_loop in LoopContext(t_1(environment.getattr(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'field_sets'), 'ipv6'), sort_key='name', ignore_case=False), undefined):
            _loop_vars = {}
            pass
            yield '   field-set ipv6 prefix '
            yield str(environment.getattr(l_1_field_set_ipv6, 'name'))
            yield '\n'
            if t_5(environment.getattr(l_1_field_set_ipv6, 'prefixes')):
                pass
                yield '      '
                yield str(t_2(context.eval_ctx, t_1(environment.getattr(l_1_field_set_ipv6, 'prefixes')), ' '))
                yield '\n'
            if t_5(environment.getattr(l_1_field_set_ipv6, 'except')):
                pass
                yield '      except '
                yield str(t_2(context.eval_ctx, t_1(environment.getattr(l_1_field_set_ipv6, 'except')), ' '))
                yield '\n'
            if (not environment.getattr(l_1_loop, 'last')):
                pass
                yield '   !\n'
        l_1_loop = l_1_field_set_ipv6 = missing
        if t_5(environment.getattr(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'options'), 'counter_per_interface'), True):
            pass
            yield '   counter interface per-interface ingress\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'options'), 'counter_interface_poll_interval')):
            pass
            yield '   counter interface poll interval '
            yield str(environment.getattr(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'options'), 'counter_interface_poll_interval'))
            yield ' seconds\n'
        for l_1_policy in t_1(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'policies'), sort_key='name', ignore_case=False):
            _loop_vars = {}
            pass
            yield '   !\n   traffic-policy '
            yield str(environment.getattr(l_1_policy, 'name'))
            yield '\n'
            if t_5(environment.getattr(l_1_policy, 'counters')):
                pass
                yield '      counter '
                yield str(t_2(context.eval_ctx, t_1(t_4(environment, environment.getattr(l_1_policy, 'counters'))), ' '))
                yield '\n      !\n'
            if t_5(environment.getattr(l_1_policy, 'matches')):
                pass
                for l_2_match in environment.getattr(l_1_policy, 'matches'):
                    l_2_bgp_flag = resolve('bgp_flag')
                    l_2_redirect_cli = resolve('redirect_cli')
                    l_2_next_hop_flag = resolve('next_hop_flag')
                    _loop_vars = {}
                    pass
                    yield '      match '
                    yield str(environment.getattr(l_2_match, 'name'))
                    yield ' '
                    yield str(t_3(environment.getattr(l_2_match, 'type')))
                    yield '\n'
                    if t_5(environment.getattr(environment.getattr(l_2_match, 'source'), 'prefixes')):
                        pass
                        yield '         source prefix '
                        yield str(t_2(context.eval_ctx, t_1(environment.getattr(environment.getattr(l_2_match, 'source'), 'prefixes')), ' '))
                        yield '\n'
                    elif t_5(environment.getattr(environment.getattr(l_2_match, 'source'), 'prefix_lists')):
                        pass
                        yield '         source prefix field-set '
                        yield str(t_2(context.eval_ctx, t_1(environment.getattr(environment.getattr(l_2_match, 'source'), 'prefix_lists')), ' '))
                        yield '\n'
                    if t_5(environment.getattr(environment.getattr(l_2_match, 'destination'), 'prefixes')):
                        pass
                        yield '         destination prefix '
                        yield str(t_2(context.eval_ctx, t_1(environment.getattr(environment.getattr(l_2_match, 'destination'), 'prefixes')), ' '))
                        yield '\n'
                    elif t_5(environment.getattr(environment.getattr(l_2_match, 'destination'), 'prefix_lists')):
                        pass
                        yield '         destination prefix field-set '
                        yield str(t_2(context.eval_ctx, t_1(environment.getattr(environment.getattr(l_2_match, 'destination'), 'prefix_lists')), ' '))
                        yield '\n'
                    if t_5(environment.getattr(l_2_match, 'protocols')):
                        pass
                        l_2_bgp_flag = True
                        _loop_vars['bgp_flag'] = l_2_bgp_flag
                        for l_3_protocol in environment.getattr(l_2_match, 'protocols'):
                            l_3_protocol_neighbors_cli = resolve('protocol_neighbors_cli')
                            l_3_bgp_flag = l_2_bgp_flag
                            l_3_protocol_cli = resolve('protocol_cli')
                            l_3_protocol_port_cli = resolve('protocol_port_cli')
                            l_3_protocol_field_cli = resolve('protocol_field_cli')
                            _loop_vars = {}
                            pass
                            if ((t_3(environment.getattr(l_3_protocol, 'protocol')) in ['neighbors', 'bgp']) and (undefined(name='bgp_flag') if l_3_bgp_flag is missing else l_3_bgp_flag)):
                                pass
                                if (t_3(environment.getattr(l_3_protocol, 'protocol')) == 'neighbors'):
                                    pass
                                    l_3_protocol_neighbors_cli = 'protocol neighbors bgp'
                                    _loop_vars['protocol_neighbors_cli'] = l_3_protocol_neighbors_cli
                                    if t_5(environment.getattr(l_3_protocol, 'enforce_gtsm'), True):
                                        pass
                                        l_3_protocol_neighbors_cli = str_join(((undefined(name='protocol_neighbors_cli') if l_3_protocol_neighbors_cli is missing else l_3_protocol_neighbors_cli), ' enforce ttl maximum-hops', ))
                                        _loop_vars['protocol_neighbors_cli'] = l_3_protocol_neighbors_cli
                                    yield '         '
                                    yield str((undefined(name='protocol_neighbors_cli') if l_3_protocol_neighbors_cli is missing else l_3_protocol_neighbors_cli))
                                    yield '\n'
                                else:
                                    pass
                                    yield '         protocol bgp\n'
                                break
                            else:
                                pass
                                l_3_bgp_flag = False
                                _loop_vars['bgp_flag'] = l_3_bgp_flag
                                l_3_protocol_cli = str_join(('protocol ', t_3(environment.getattr(l_3_protocol, 'protocol')), ))
                                _loop_vars['protocol_cli'] = l_3_protocol_cli
                                if (t_5(environment.getattr(l_3_protocol, 'flags')) and (t_3(environment.getattr(l_3_protocol, 'protocol')) == 'tcp')):
                                    pass
                                    for l_4_flag in environment.getattr(l_3_protocol, 'flags'):
                                        _loop_vars = {}
                                        pass
                                        yield '         '
                                        yield str((undefined(name='protocol_cli') if l_3_protocol_cli is missing else l_3_protocol_cli))
                                        yield ' flags '
                                        yield str(l_4_flag)
                                        yield '\n'
                                    l_4_flag = missing
                                if ((t_3(environment.getattr(l_3_protocol, 'protocol')) in ['tcp', 'udp']) and (((t_5(environment.getattr(l_3_protocol, 'src_port')) or t_5(environment.getattr(l_3_protocol, 'dst_port'))) or t_5(environment.getattr(l_3_protocol, 'src_field'))) or t_5(environment.getattr(l_3_protocol, 'dst_field')))):
                                    pass
                                    if (t_5(environment.getattr(l_3_protocol, 'src_port')) or t_5(environment.getattr(l_3_protocol, 'dst_port'))):
                                        pass
                                        l_3_protocol_port_cli = (undefined(name='protocol_cli') if l_3_protocol_cli is missing else l_3_protocol_cli)
                                        _loop_vars['protocol_port_cli'] = l_3_protocol_port_cli
                                        if t_5(environment.getattr(l_3_protocol, 'src_port')):
                                            pass
                                            l_3_protocol_port_cli = str_join(((undefined(name='protocol_port_cli') if l_3_protocol_port_cli is missing else l_3_protocol_port_cli), ' source port ', environment.getattr(l_3_protocol, 'src_port'), ))
                                            _loop_vars['protocol_port_cli'] = l_3_protocol_port_cli
                                        if t_5(environment.getattr(l_3_protocol, 'dst_port')):
                                            pass
                                            l_3_protocol_port_cli = str_join(((undefined(name='protocol_port_cli') if l_3_protocol_port_cli is missing else l_3_protocol_port_cli), ' destination port ', environment.getattr(l_3_protocol, 'dst_port'), ))
                                            _loop_vars['protocol_port_cli'] = l_3_protocol_port_cli
                                        yield '         '
                                        yield str((undefined(name='protocol_port_cli') if l_3_protocol_port_cli is missing else l_3_protocol_port_cli))
                                        yield '\n'
                                    if (t_5(environment.getattr(l_3_protocol, 'src_field')) or t_5(environment.getattr(l_3_protocol, 'dst_field'))):
                                        pass
                                        l_3_protocol_field_cli = (undefined(name='protocol_cli') if l_3_protocol_cli is missing else l_3_protocol_cli)
                                        _loop_vars['protocol_field_cli'] = l_3_protocol_field_cli
                                        if t_5(environment.getattr(l_3_protocol, 'src_field')):
                                            pass
                                            l_3_protocol_field_cli = str_join(((undefined(name='protocol_field_cli') if l_3_protocol_field_cli is missing else l_3_protocol_field_cli), ' source port field-set ', environment.getattr(l_3_protocol, 'src_field'), ))
                                            _loop_vars['protocol_field_cli'] = l_3_protocol_field_cli
                                        if t_5(environment.getattr(l_3_protocol, 'dst_field')):
                                            pass
                                            l_3_protocol_field_cli = str_join(((undefined(name='protocol_field_cli') if l_3_protocol_field_cli is missing else l_3_protocol_field_cli), ' destination port field-set ', environment.getattr(l_3_protocol, 'dst_field'), ))
                                            _loop_vars['protocol_field_cli'] = l_3_protocol_field_cli
                                        yield '         '
                                        yield str((undefined(name='protocol_field_cli') if l_3_protocol_field_cli is missing else l_3_protocol_field_cli))
                                        yield '\n'
                                elif (t_5(environment.getattr(l_3_protocol, 'icmp_type')) and ((t_3(environment.getattr(l_3_protocol, 'protocol')) == 'icmp') or (t_3(environment.getattr(l_3_protocol, 'protocol')) == 'icmpv6'))):
                                    pass
                                    yield '         '
                                    yield str((undefined(name='protocol_cli') if l_3_protocol_cli is missing else l_3_protocol_cli))
                                    yield ' type '
                                    yield str(t_2(context.eval_ctx, t_1(environment.getattr(l_3_protocol, 'icmp_type')), ' '))
                                    yield ' code all\n'
                                else:
                                    pass
                                    yield '         '
                                    yield str((undefined(name='protocol_cli') if l_3_protocol_cli is missing else l_3_protocol_cli))
                                    yield '\n'
                        l_3_protocol = l_3_protocol_neighbors_cli = l_3_bgp_flag = l_3_protocol_cli = l_3_protocol_port_cli = l_3_protocol_field_cli = missing
                    if t_5(environment.getattr(environment.getattr(l_2_match, 'fragment'), 'offset')):
                        pass
                        yield '         fragment offset '
                        yield str(environment.getattr(environment.getattr(l_2_match, 'fragment'), 'offset'))
                        yield '\n'
                    elif t_6(environment.getattr(l_2_match, 'fragment')):
                        pass
                        yield '         fragment\n'
                    if t_5(environment.getattr(l_2_match, 'ttl')):
                        pass
                        yield '         ttl '
                        yield str(environment.getattr(l_2_match, 'ttl'))
                        yield '\n'
                    if (t_5(environment.getattr(environment.getattr(l_2_match, 'packet_type'), 'vxlan')) or t_5(environment.getattr(environment.getattr(l_2_match, 'packet_type'), 'multicast'), True)):
                        pass
                        yield '         !\n         packet type\n'
                        if t_5(environment.getattr(environment.getattr(l_2_match, 'packet_type'), 'multicast'), True):
                            pass
                            yield '            multicast\n'
                        if t_5(environment.getattr(environment.getattr(l_2_match, 'packet_type'), 'vxlan')):
                            pass
                            yield '            vxlan '
                            yield str(environment.getattr(environment.getattr(l_2_match, 'packet_type'), 'vxlan'))
                            yield '\n'
                    if ((((t_5(environment.getattr(environment.getattr(l_2_match, 'actions'), 'count')) or t_5(environment.getattr(environment.getattr(l_2_match, 'actions'), 'traffic_class'))) or t_5(environment.getattr(environment.getattr(l_2_match, 'actions'), 'dscp'))) or t_5(environment.getattr(environment.getattr(l_2_match, 'actions'), 'drop'), True)) or t_5(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'))):
                        pass
                        yield '         !\n         actions\n'
                        if t_5(environment.getattr(environment.getattr(l_2_match, 'actions'), 'count')):
                            pass
                            yield '            count '
                            yield str(environment.getattr(environment.getattr(l_2_match, 'actions'), 'count'))
                            yield '\n'
                        if t_5(environment.getattr(environment.getattr(l_2_match, 'actions'), 'drop'), True):
                            pass
                            yield '            drop\n'
                            if t_5(environment.getattr(environment.getattr(l_2_match, 'actions'), 'log'), True):
                                pass
                                yield '            log\n'
                        if t_5(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'aggregation_groups')):
                            pass
                            yield '            redirect aggregation group '
                            yield str(t_2(context.eval_ctx, t_1(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'aggregation_groups')), ' '))
                            yield '\n'
                        if t_5(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'interface')):
                            pass
                            yield '            redirect interface '
                            yield str(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'interface'))
                            yield '\n'
                        if ((not (t_5(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'interface')) or t_5(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'aggregation_groups')))) and t_5(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'))):
                            pass
                            l_2_redirect_cli = 'redirect next-hop '
                            _loop_vars['redirect_cli'] = l_2_redirect_cli
                            l_2_next_hop_flag = False
                            _loop_vars['next_hop_flag'] = l_2_next_hop_flag
                            if t_5(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'ipv4_addresses')):
                                pass
                                l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), t_2(context.eval_ctx, t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'ipv4_addresses')), ' '), ))
                                _loop_vars['redirect_cli'] = l_2_redirect_cli
                                if t_5(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf')):
                                    pass
                                    l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), ' vrf ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf'), ))
                                    _loop_vars['redirect_cli'] = l_2_redirect_cli
                                l_2_next_hop_flag = True
                                _loop_vars['next_hop_flag'] = l_2_next_hop_flag
                            elif t_5(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'ipv6_addresses')):
                                pass
                                l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), t_2(context.eval_ctx, t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'ipv6_addresses')), ' '), ))
                                _loop_vars['redirect_cli'] = l_2_redirect_cli
                                if t_5(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf')):
                                    pass
                                    l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), ' vrf ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf'), ))
                                    _loop_vars['redirect_cli'] = l_2_redirect_cli
                                l_2_next_hop_flag = True
                                _loop_vars['next_hop_flag'] = l_2_next_hop_flag
                            elif t_5(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'groups')):
                                pass
                                l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), 'group ', t_2(context.eval_ctx, t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'groups')), ' '), ))
                                _loop_vars['redirect_cli'] = l_2_redirect_cli
                                l_2_next_hop_flag = True
                                _loop_vars['next_hop_flag'] = l_2_next_hop_flag
                            elif t_5(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'recursive_ipv4_addresses')):
                                pass
                                l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), 'recursive ', t_2(context.eval_ctx, t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'recursive_ipv4_addresses')), ' '), ))
                                _loop_vars['redirect_cli'] = l_2_redirect_cli
                                if t_5(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf')):
                                    pass
                                    l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), ' vrf ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf'), ))
                                    _loop_vars['redirect_cli'] = l_2_redirect_cli
                                l_2_next_hop_flag = True
                                _loop_vars['next_hop_flag'] = l_2_next_hop_flag
                            elif t_5(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'recursive_ipv6_addresses')):
                                pass
                                l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), 'recursive ', t_2(context.eval_ctx, t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'recursive_ipv6_addresses')), ' '), ))
                                _loop_vars['redirect_cli'] = l_2_redirect_cli
                                if t_5(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf')):
                                    pass
                                    l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), ' vrf ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf'), ))
                                    _loop_vars['redirect_cli'] = l_2_redirect_cli
                                l_2_next_hop_flag = True
                                _loop_vars['next_hop_flag'] = l_2_next_hop_flag
                            if (t_5(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'ttl')) and (undefined(name='next_hop_flag') if l_2_next_hop_flag is missing else l_2_next_hop_flag)):
                                pass
                                l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), ' ttl ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'ttl'), ))
                                _loop_vars['redirect_cli'] = l_2_redirect_cli
                            if ((undefined(name='next_hop_flag') if l_2_next_hop_flag is missing else l_2_next_hop_flag) == True):
                                pass
                                yield '            '
                                yield str((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli))
                                yield '\n'
                        if t_5(environment.getattr(environment.getattr(l_2_match, 'actions'), 'dscp')):
                            pass
                            yield '            set dscp '
                            yield str(environment.getattr(environment.getattr(l_2_match, 'actions'), 'dscp'))
                            yield '\n'
                        if t_5(environment.getattr(environment.getattr(l_2_match, 'actions'), 'traffic_class')):
                            pass
                            yield '            set traffic class '
                            yield str(environment.getattr(environment.getattr(l_2_match, 'actions'), 'traffic_class'))
                            yield '\n'
                    yield '      !\n'
                l_2_match = l_2_bgp_flag = l_2_redirect_cli = l_2_next_hop_flag = missing
            yield '      match ipv4-all-default ipv4\n'
            if t_5(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv4')):
                pass
                yield '         actions\n'
                if t_5(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv4'), 'count')):
                    pass
                    yield '            count '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv4'), 'count'))
                    yield '\n'
                if t_5(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv4'), 'drop'), True):
                    pass
                    yield '            drop\n'
                    if t_5(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv4'), 'log'), True):
                        pass
                        yield '            log\n'
                if t_5(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv4'), 'dscp')):
                    pass
                    yield '            set dscp '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv4'), 'dscp'))
                    yield '\n'
                if t_5(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv4'), 'traffic_class')):
                    pass
                    yield '            set traffic class '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv4'), 'traffic_class'))
                    yield '\n'
            yield '      !\n      match ipv6-all-default ipv6\n'
            if t_5(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv6')):
                pass
                yield '         actions\n'
                if t_5(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv6'), 'count')):
                    pass
                    yield '            count '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv6'), 'count'))
                    yield '\n'
                if t_5(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv6'), 'drop'), True):
                    pass
                    yield '            drop\n'
                    if t_5(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv6'), 'log'), True):
                        pass
                        yield '            log\n'
                if t_5(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv6'), 'dscp')):
                    pass
                    yield '            set dscp '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv6'), 'dscp'))
                    yield '\n'
                if t_5(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv6'), 'traffic_class')):
                    pass
                    yield '            set traffic class '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv6'), 'traffic_class'))
                    yield '\n'
        l_1_policy = missing

blocks = {}
debug_info = '7=48&12=51&13=55&14=57&15=60&20=65&21=69&22=71&23=74&25=76&26=79&28=81&33=86&34=90&35=92&36=95&38=97&39=100&41=102&46=106&49=109&50=112&53=114&55=118&57=120&58=123&61=125&63=127&64=134&66=138&67=141&68=143&69=146&72=148&73=151&74=153&75=156&78=158&79=160&80=162&81=170&82=172&83=174&84=176&85=178&87=181&91=186&93=189&94=191&95=193&96=195&97=199&100=204&106=206&107=208&108=210&109=212&111=214&112=216&114=219&117=221&118=223&119=225&120=227&122=229&123=231&125=234&127=236&128=239&130=246&136=249&137=252&138=254&142=257&143=260&145=262&148=265&151=268&152=271&156=273&160=276&161=279&164=281&167=284&171=287&172=290&174=292&175=295&177=297&178=299&179=301&180=303&181=305&182=307&183=309&185=311&186=313&187=315&188=317&189=319&191=321&192=323&193=325&194=327&195=329&196=331&197=333&198=335&200=337&201=339&202=341&203=343&204=345&206=347&208=349&209=351&211=353&212=356&216=358&217=361&220=363&221=366&230=371&233=374&234=377&237=379&240=382&245=385&246=388&249=390&250=393&255=396&258=399&259=402&262=404&265=407&270=410&271=413&274=415&275=418'