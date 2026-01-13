from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/static-routes.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_static_routes = resolve('static_routes')
    l_0_default_routes = resolve('default_routes')
    l_0_vrf_routes = resolve('vrf_routes')
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_2 = environment.filters['capitalize']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'capitalize' found.")
    try:
        t_3 = environment.filters['list']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'list' found.")
    try:
        t_4 = environment.filters['rejectattr']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'rejectattr' found.")
    try:
        t_5 = environment.filters['selectattr']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'selectattr' found.")
    try:
        t_6 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_6(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_6((undefined(name='static_routes') if l_0_static_routes is missing else l_0_static_routes)):
        pass
        yield '!\n'
        l_0_default_routes = (t_3(context.eval_ctx, t_4(context, (undefined(name='static_routes') if l_0_static_routes is missing else l_0_static_routes), 'vrf', 'arista.avd.defined')) + t_3(context.eval_ctx, t_5(context, t_5(context, (undefined(name='static_routes') if l_0_static_routes is missing else l_0_static_routes), 'vrf', 'arista.avd.defined'), 'vrf', 'equalto', 'default')))
        context.vars['default_routes'] = l_0_default_routes
        context.exported_vars.add('default_routes')
        l_0_vrf_routes = t_3(context.eval_ctx, t_4(context, t_5(context, (undefined(name='static_routes') if l_0_static_routes is missing else l_0_static_routes), 'vrf', 'arista.avd.defined'), 'vrf', 'equalto', 'default'))
        context.vars['vrf_routes'] = l_0_vrf_routes
        context.exported_vars.add('vrf_routes')
        for l_1_static_route in (t_1(t_1((undefined(name='default_routes') if l_0_default_routes is missing else l_0_default_routes), 'next_hop', default_value=''), 'prefix') + t_1(t_1(t_1((undefined(name='vrf_routes') if l_0_vrf_routes is missing else l_0_vrf_routes), 'next_hop', default_value=''), 'prefix'), 'vrf', ignore_case=False)):
            l_1_static_route_cli = missing
            _loop_vars = {}
            pass
            l_1_static_route_cli = 'ip route'
            _loop_vars['static_route_cli'] = l_1_static_route_cli
            if (t_6(environment.getattr(l_1_static_route, 'vrf')) and (environment.getattr(l_1_static_route, 'vrf') != 'default')):
                pass
                l_1_static_route_cli = str_join(((undefined(name='static_route_cli') if l_1_static_route_cli is missing else l_1_static_route_cli), ' vrf ', environment.getattr(l_1_static_route, 'vrf'), ))
                _loop_vars['static_route_cli'] = l_1_static_route_cli
            l_1_static_route_cli = str_join(((undefined(name='static_route_cli') if l_1_static_route_cli is missing else l_1_static_route_cli), ' ', environment.getattr(l_1_static_route, 'prefix'), ))
            _loop_vars['static_route_cli'] = l_1_static_route_cli
            if t_6(environment.getattr(l_1_static_route, 'interface')):
                pass
                l_1_static_route_cli = str_join(((undefined(name='static_route_cli') if l_1_static_route_cli is missing else l_1_static_route_cli), ' ', t_2(environment.getattr(l_1_static_route, 'interface')), ))
                _loop_vars['static_route_cli'] = l_1_static_route_cli
            if t_6(environment.getattr(l_1_static_route, 'next_hop')):
                pass
                l_1_static_route_cli = str_join(((undefined(name='static_route_cli') if l_1_static_route_cli is missing else l_1_static_route_cli), ' ', environment.getattr(l_1_static_route, 'next_hop'), ))
                _loop_vars['static_route_cli'] = l_1_static_route_cli
                if t_6(environment.getattr(l_1_static_route, 'track_bfd'), True):
                    pass
                    l_1_static_route_cli = str_join(((undefined(name='static_route_cli') if l_1_static_route_cli is missing else l_1_static_route_cli), ' track bfd', ))
                    _loop_vars['static_route_cli'] = l_1_static_route_cli
            if t_6(environment.getattr(l_1_static_route, 'distance')):
                pass
                l_1_static_route_cli = str_join(((undefined(name='static_route_cli') if l_1_static_route_cli is missing else l_1_static_route_cli), ' ', environment.getattr(l_1_static_route, 'distance'), ))
                _loop_vars['static_route_cli'] = l_1_static_route_cli
            if t_6(environment.getattr(l_1_static_route, 'tag')):
                pass
                l_1_static_route_cli = str_join(((undefined(name='static_route_cli') if l_1_static_route_cli is missing else l_1_static_route_cli), ' tag ', environment.getattr(l_1_static_route, 'tag'), ))
                _loop_vars['static_route_cli'] = l_1_static_route_cli
            if t_6(environment.getattr(l_1_static_route, 'name')):
                pass
                l_1_static_route_cli = str_join(((undefined(name='static_route_cli') if l_1_static_route_cli is missing else l_1_static_route_cli), ' name ', environment.getattr(l_1_static_route, 'name'), ))
                _loop_vars['static_route_cli'] = l_1_static_route_cli
            if t_6(environment.getattr(l_1_static_route, 'metric')):
                pass
                l_1_static_route_cli = str_join(((undefined(name='static_route_cli') if l_1_static_route_cli is missing else l_1_static_route_cli), ' metric ', environment.getattr(l_1_static_route, 'metric'), ))
                _loop_vars['static_route_cli'] = l_1_static_route_cli
            yield str((undefined(name='static_route_cli') if l_1_static_route_cli is missing else l_1_static_route_cli))
            yield '\n'
        l_1_static_route = l_1_static_route_cli = missing

blocks = {}
debug_info = '7=50&9=53&10=56&11=59&15=63&16=65&17=67&19=69&20=71&21=73&23=75&24=77&25=79&26=81&29=83&30=85&32=87&33=89&35=91&36=93&38=95&39=97&41=99'