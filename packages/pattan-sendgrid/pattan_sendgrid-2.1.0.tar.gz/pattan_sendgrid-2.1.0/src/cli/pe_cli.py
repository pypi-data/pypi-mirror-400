import os
import click
from sendgrid import SendGridAPIClient
from cli.get_config import gc, gs, ga, gt, gtd, gi, gtv


@click.group()
@click.pass_context
def pe_cli(ctx):
    """CLI interface into the sendgrid backend to run export SENDGRID_API_KEY environment variable"""
    api_key = os.getenv('SENDGRID_API_KEY', None)
    if not api_key:
        # @todo the key should be able to be supplied as an optional argument
        click.echo("missing SENDGRID_API_KEY environment variable")
        exit(1)
    sg = SendGridAPIClient(api_key=api_key)
    ctx.obj = {'sg_client': sg.client, 'api_key': api_key}


pe_cli.add_command(gc)
pe_cli.add_command(gs)
pe_cli.add_command(ga)
pe_cli.add_command(gt)
pe_cli.add_command(gi)
pe_cli.add_command(gtd)
pe_cli.add_command(gtv)

if __name__ == '__main__':
    pe_cli()
