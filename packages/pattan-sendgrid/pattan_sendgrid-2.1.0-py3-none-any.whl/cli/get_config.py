import click
import json
import re

@click.command()
@click.option('--default-sender', help='Sender label as defined in sendgrid. If left unset the first one found will be set as the default ')
@click.option('--default-ip-pool', help='Sendgird -> settings -> ip addresses . If left unset the first one found will be set as the default ')
@click.option('--default-unsubscribe_group', help='Sendgrid -> marketing -> unsubscribe group . If left unset the first one found will be set as the default ')
@click.option('--default-dynamic-template', help='Sendgrid -> email api -> dynamic template . If left unset the first one found will be set as the default ')
@click.pass_context
def gc(ctx, default_sender, default_ip_pool, default_unsubscribe_group, default_dynamic_template):
    """ get and format configuration information so its suitable for consumption by the patten_email class"""
    senders = ctx.invoke(gs, dump_std=False)
    ip_pools = ctx.invoke(gi, dump_std=False)
    asm = ctx.invoke(ga, dump_std=False)
    templates = ctx.invoke(gt, dump_std=False)

    auto_generated_config_dict = {}
    auto_generated_config_dict['api_key'] = ctx.obj.get('api_key')


    sender_config = {}
    for sender in senders:
        del sender['updated_at']
        del sender['created_at']
        del sender['locked']
        del sender['id']
        del sender['verified']
        del sender['country']
        sender_config[sender['nickname']] = sender
        sender_config[sender['nickname']]['from_address'] = sender.pop('from')

    sender_keys = list(sender_config.keys())
    if default_sender in sender_keys:
        sender_config['DEFAULT'] = sender_config[default_sender]
    else:
        if len(sender_config) > 0:
            sender_config['DEFAULT'] = sender_config[sender_keys[0]]

    auto_generated_config_dict['senders'] = sender_config


    ip_pool_config = {}
    for ip_pool in ip_pools:
        ip_pool_config[ip_pool['name']] = ip_pool

    ip_pool_keys = list(ip_pool_config.keys())
    if default_ip_pool in ip_pool_keys:
        ip_pool_config['DEFAULT'] = ip_pool_config[default_ip_pool]
    else:
        if len(ip_pool_config) > 0:
            ip_pool_config['DEFAULT'] = ip_pool_config[ip_pool_keys[0]]

    auto_generated_config_dict['ip_pools'] = ip_pool_config


    unsubscribe_groups_config = {}
    for unsubscribe_group in asm:
        unsubscribe_groups_config[unsubscribe_group['name']] = {}
        unsubscribe_groups_config[unsubscribe_group['name']]['id'] = unsubscribe_group['id']

    unsubscribe_group_keys = list(unsubscribe_groups_config.keys())
    if default_unsubscribe_group in unsubscribe_group_keys:
        unsubscribe_groups_config['DEFAULT'] = unsubscribe_groups_config[default_unsubscribe_group]
    else:
        if len(unsubscribe_groups_config) > 0:
            unsubscribe_groups_config['DEFAULT'] = unsubscribe_groups_config[unsubscribe_group_keys[0]]

    auto_generated_config_dict['unsubscribe_groups'] = unsubscribe_groups_config

    templates_config = {}
    for template in templates:
        templates_config[template['name']]= {}
        templates_config[template['name']]['id'] = template['id']
        templates_config[template['name']]['name'] = template['name']
        isolated_template_variables = ctx.invoke(gtv, template_id = template['id'], dump_std=False)
        templates_config[template['name']]['variables'] = isolated_template_variables


    template_keys = list(templates_config.keys())
    if default_dynamic_template in template_keys:
        templates_config['DEFAULT'] = templates_config[default_dynamic_template]
    else:
        if len(templates_config) > 0:
            templates_config['DEFAULT'] = templates_config[template_keys[0]]

    auto_generated_config_dict['email_templates'] = templates_config

    click.echo(json.dumps(auto_generated_config_dict))




@click.command()
@click.option('--dump-std', default=True )
@click.pass_context
def gs(ctx, dump_std):
    """ get sendgird senders """
    response = ctx.obj['sg_client'].senders.get()
    body = response.body.decode('utf-8')
    if dump_std:
        click.echo(body)
    return json.loads(body)


@click.command()
@click.option('--dump-std', default=True )
@click.pass_context
def ga(ctx, dump_std):
    """ get sendgird asms (unsubscribe groups)"""
    params = {}
    response = ctx.obj['sg_client'].asm.groups.get(query_params=params)
    body = response.body.decode('utf-8')
    if dump_std:
        click.echo(body)
    return json.loads(body)

@click.command()
@click.option('--dump-std', default=True )
@click.pass_context
def gt(ctx, dump_std):
    """ get sendgird dynamic templates """
    params = {'generations': 'dynamic'}
    response = ctx.obj['sg_client'].templates.get(query_params=params)
    body = response.body.decode('utf-8')
    if dump_std:
        click.echo(body)
    return json.loads(body)['templates']
    # return json.loads(response.body.decode('utf-8'))['templates']


@click.command()
@click.option('--dump-std', default=True )
@click.pass_context
def gi(ctx, dump_std):
    """ get sendgird ip pools """
    response = ctx.obj['sg_client'].ips.pools.get()
    body = response.body.decode('utf-8')
    if dump_std:
        click.echo(body)
    return json.loads(body)

@click.command()
@click.argument('template_id')
@click.option('--dump-std', default=True )
@click.pass_context
def gtd(ctx, template_id, dump_std):
    """ get details for a specific template """
    response = ctx.obj['sg_client'].templates._(template_id).get()
    body = json.loads(response.body.decode('utf-8'))
    # get the active version of the template
    template = None
    for version in body['versions']:
        if version['active'] == 1:
            template = version
            break
    if not template:
        # @todo convert logger
        pass
    del(body['versions'])
    body['template'] = template

    if dump_std:
        click.echo(body)
    return body

@click.command()
@click.argument('template_id')
@click.option('--dump-std', default=True )
@click.pass_context
def gtv(ctx, template_id, dump_std):
    """ get the variables defined in a specific template. """

    body = ctx.invoke(gtd, template_id = template_id, dump_std=False)
    if not body['template']:
        return []
    # Regular expression to find all Mustache variables
    # @todo the parsing could be better also variables in the subject line are not detected.
    content_variables = re.findall(r'{{\s*([^}]+)\s*}}', body['template']['plain_content'])
    subject_variables = []
    if 'subject' in body['template'].keys():
        subject_variables = re.findall(r'{{\s*([^}]+)\s*}}', body['template']['subject'])

    try:
        # these are defined with the asm config, @todo find a better mustache pattern the extra '{' is weird
        content_variables.remove('{unsubscribe')
        content_variables.remove('{unsubscribe_preferences')
    except:
        pass

    if dump_std:
        click.echo(f"content variables {content_variables}")
        click.echo(f"subject variables {subject_variables}")
    return content_variables + subject_variables