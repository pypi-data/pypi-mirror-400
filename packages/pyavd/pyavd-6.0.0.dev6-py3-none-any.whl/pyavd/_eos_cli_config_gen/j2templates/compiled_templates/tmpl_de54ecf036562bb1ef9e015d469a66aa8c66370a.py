from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/static-routes.j2'

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
        t_1 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    try:
        t_2 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
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
        l_0_default_routes = (t_3(context.eval_ctx, t_4(context, (undefined(name='static_routes') if l_0_static_routes is missing else l_0_static_routes), 'vrf', 'arista.avd.defined')) + t_3(context.eval_ctx, t_5(context, t_5(context, (undefined(name='static_routes') if l_0_static_routes is missing else l_0_static_routes), 'vrf', 'arista.avd.defined'), 'vrf', 'equalto', 'default')))
        context.vars['default_routes'] = l_0_default_routes
        context.exported_vars.add('default_routes')
        l_0_vrf_routes = t_3(context.eval_ctx, t_4(context, t_5(context, (undefined(name='static_routes') if l_0_static_routes is missing else l_0_static_routes), 'vrf', 'arista.avd.defined'), 'vrf', 'equalto', 'default'))
        context.vars['vrf_routes'] = l_0_vrf_routes
        context.exported_vars.add('vrf_routes')
        yield '\n### Static Routes\n\n#### Static Routes Summary\n\n| VRF | Destination Prefix | Next Hop IP | Exit interface | Administrative Distance | Tag | Route Name | Metric |\n| --- | ------------------ | ----------- | -------------- | ----------------------- | --- | ---------- | ------ |\n'
        for l_1_static_route in (t_2(t_2((undefined(name='default_routes') if l_0_default_routes is missing else l_0_default_routes), 'next_hop', default_value=''), 'prefix') + t_2(t_2(t_2((undefined(name='vrf_routes') if l_0_vrf_routes is missing else l_0_vrf_routes), 'next_hop', default_value=''), 'prefix'), 'vrf', ignore_case=False)):
            l_1_next_hop = resolve('next_hop')
            l_1_vrf = l_1_interface = l_1_distance = l_1_tag = l_1_name = l_1_metric = l_1_prefix = missing
            _loop_vars = {}
            pass
            l_1_vrf = t_1(environment.getattr(l_1_static_route, 'vrf'), 'default')
            _loop_vars['vrf'] = l_1_vrf
            if t_6(environment.getattr(l_1_static_route, 'next_hop')):
                pass
                l_1_next_hop = environment.getattr(l_1_static_route, 'next_hop')
                _loop_vars['next_hop'] = l_1_next_hop
                if t_6(environment.getattr(l_1_static_route, 'track_bfd'), True):
                    pass
                    l_1_next_hop = str_join(((undefined(name='next_hop') if l_1_next_hop is missing else l_1_next_hop), ' (tracked with BFD)', ))
                    _loop_vars['next_hop'] = l_1_next_hop
            else:
                pass
                l_1_next_hop = '-'
                _loop_vars['next_hop'] = l_1_next_hop
            l_1_interface = t_1(environment.getattr(l_1_static_route, 'interface'), '-')
            _loop_vars['interface'] = l_1_interface
            l_1_distance = t_1(environment.getattr(l_1_static_route, 'distance'), '1')
            _loop_vars['distance'] = l_1_distance
            l_1_tag = t_1(environment.getattr(l_1_static_route, 'tag'), '-')
            _loop_vars['tag'] = l_1_tag
            l_1_name = t_1(environment.getattr(l_1_static_route, 'name'), '-')
            _loop_vars['name'] = l_1_name
            l_1_metric = t_1(environment.getattr(l_1_static_route, 'metric'), '-')
            _loop_vars['metric'] = l_1_metric
            l_1_prefix = environment.getattr(l_1_static_route, 'prefix')
            _loop_vars['prefix'] = l_1_prefix
            yield '| '
            yield str((undefined(name='vrf') if l_1_vrf is missing else l_1_vrf))
            yield ' | '
            yield str((undefined(name='prefix') if l_1_prefix is missing else l_1_prefix))
            yield ' | '
            yield str((undefined(name='next_hop') if l_1_next_hop is missing else l_1_next_hop))
            yield ' | '
            yield str((undefined(name='interface') if l_1_interface is missing else l_1_interface))
            yield ' | '
            yield str((undefined(name='distance') if l_1_distance is missing else l_1_distance))
            yield ' | '
            yield str((undefined(name='tag') if l_1_tag is missing else l_1_tag))
            yield ' | '
            yield str((undefined(name='name') if l_1_name is missing else l_1_name))
            yield ' | '
            yield str((undefined(name='metric') if l_1_metric is missing else l_1_metric))
            yield ' |\n'
        l_1_static_route = l_1_vrf = l_1_next_hop = l_1_interface = l_1_distance = l_1_tag = l_1_name = l_1_metric = l_1_prefix = missing
        yield '\n#### Static Routes Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/static-routes.j2', 'documentation/static-routes.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'default_routes': l_0_default_routes, 'vrf_routes': l_0_vrf_routes}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=50&8=52&9=55&17=59&21=64&22=66&23=68&24=70&25=72&28=76&30=78&31=80&32=82&33=84&34=86&35=88&36=91&42=109'