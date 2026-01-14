import click
import sys
import json

from .sign import sign_pplg
from .timestamp import timestamp_pplg

CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help']
)
__version__ = '1.0.37'
@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__)
@click.pass_context
def cli(ctx):
    pass

@cli.command()
@click.option('-i', '--input_file', type=str, help='File input', required=True)
@click.option('-o', '--output_file', type=str, help='File output', required=True)
@click.option('-tk', '--api_token', type=str, help='API Token', required=True)
@click.option('-t', '--tenant_id', type=int, help='TenantID', required=True)
@click.option('-pki', '--pki', type=int, required=True, default=0, 
    help='''
        Certificate type to sign \n
        0: Paperlogic certificate \n
        1: JCAN certificate \n
        2: Company seal certificate \n
        3: NRA-PKI certificate \n
        4: E-Seal HSM	 \n
    '''
)
@click.option('-uid', '--user_id', type=int, help='UserID')
@click.option('-e', '--email', type=str, help='Email')
@click.option('-pwd', '--pdf_password', type=str, help='PDF File Password')
@click.option(
    '-env', '--environment',
    type=click.Choice(['dev', 'stg', 'prod'], case_sensitive=False),
    default='stg',
    help='Environment to run the SDK (dev/stg/prod)'
)
@click.option(
    '-pos', '--position', 
    type=str, 
    help='''Signature imprint position as JSON: 
    '{"page": 0, "left": 200, "bottom": 200, "height": 60, "width": 60, "custom_imprint": "/path/to/image.png"}'
    '''
)
def sign(input_file, output_file, api_token, tenant_id, pki, user_id=None, email=None, environment='stg', pdf_password=None, position=None):
    """Sign document"""
    if environment == 'dev':
        click.echo("Development mode activated")
    elif environment == 'stg':
        click.echo("Staging mode activated")
    elif environment == 'prod':
        click.echo("Production mode activated")

    click.echo("Start Signing")

    kwargs = {'pdf_password': pdf_password} if pdf_password else {}
    
    if position:
        try:
            kwargs['position'] = json.loads(position)
        except json.JSONDecodeError:
            click.echo("Status: failure \nError: error.invalid_position \nErrorMessage: position must be valid JSON.", err=True)
            sys.exit(1)

    res, msg = sign_pplg(input_file, output_file, api_token, tenant_id, pki, user_id, email, environment, **kwargs)

    if res:
        click.echo(f"Status: success")
        sys.exit(0)
    else:
        if msg == 'error.password.required':
            click.echo(f'''Status: failure \nError: error.password.incorrect \nErrorMessage: PDF file's password is not correct. Please provide correct password.''', 
                err=True
            )
        elif msg == 'error.pki.user_id.required':
            click.echo(f'''Status: failure \nError: error.pki.user_id.required \nErrorMessage: Sign by company seal requires user_id (group_id).''', 
                err=True
            )
        elif msg == 'error.wrong_tenant':
            click.echo(f'''Status: failure \nError: error.wrong_tenant \nErrorMessage: You don't have permission on this tenant.''', 
                err=True
            )
        elif msg == 'error.sdk_permission':
            click.echo(f'''Status: failure \nError: error.sdk_permission\nErrorMessage: Your tenant does not have permission on this sdk function.''', 
                err=True
            )
        elif msg == 'message.errors.certificate.not-exists':
            click.echo(f'''Status: failure \nError: error.certificate.not-exists \nErrorMessage: Certificate file is not exists.''', 
                err=True
            )
        elif msg == 'message.errors.users.not-permission':
            click.echo(f'''Status: failure \nError: error.users.not-permission \nErrorMessage: User does not have permission.''', 
                err=True
            )
        elif msg == 'error.position.invalid':
            click.echo(f'''Status: failure \nError: error.position.invalid \nErrorMessage: Signature position is outside the page boundaries.''', 
                err=True
            )
        elif msg == 'error.file.not_found':
            click.echo(f'''Status: failure \nError: error.file.not_found \nErrorMessage: Input PDF file does not exist.''', 
                err=True
            )
        elif msg == 'error.image.not_found':
            click.echo(f'''Status: failure \nError: error.image.not_found \nErrorMessage: Custom imprint image file not found.''', 
                err=True
            )
        elif msg == 'error.image.unsupported_format':
            click.echo(f'''Status: failure \nError: error.image.unsupported_format \nErrorMessage: Image format not supported. Use PNG, JPG, GIF, BMP, WEBP or TIFF.''', 
                err=True
            )
        elif msg == 'error.image.cannot_read':
            click.echo(f'''Status: failure \nError: error.image.cannot_read \nErrorMessage: Image file is corrupted or cannot be read.''', 
                err=True
            )
        else:
            click.echo(f'''Status: failure \nError: error.other \nErrorMessage: {msg}''', 
                err=True
            )
        sys.exit(1)

@cli.command()
@click.option('-i', '--input_file', type=str, help='File input', required=True)
@click.option('-o', '--output_file', type=str, help='File output', required=True)
@click.option('-tk', '--api_token', type=str, help='API Token', required=True)
@click.option('-t', '--tenant_id', type=int, help='TenantID', required=True)
@click.option('-pwd', '--pdf_password', type=str, help='PDF File Password')
@click.option(
    '-env', '--environment',
    type=click.Choice(['dev', 'stg', 'prod'], case_sensitive=False),
    default='stg',
    help='Environment to run the SDK (dev/stg/prod)'
)
def timestamp(input_file, output_file, api_token, tenant_id, environment='stg', pdf_password=None):
    """Timestamp document"""
    if environment == 'dev':
        click.echo("Development mode activated")
    elif environment == 'stg':
        click.echo("Staging mode activated")
    elif environment == 'prod':
        click.echo("Production mode activated")

    click.echo(f"Start Timestamp")

    kwargs = {'pdf_password': pdf_password} if pdf_password else {}
    res, msg = timestamp_pplg(input_file, output_file, api_token, tenant_id, environment, **kwargs)

    if res:
        click.echo(f"Status: success")
        sys.exit(0)
    else:
        if msg == 'error.password.required':
            click.echo(f'''Status: failure \nError: error.password.incorrect \nErrorMessage: PDF file's password is not correct. Please provide correct password.''', 
                err=True
            )
        elif msg == 'error.wrong_tenant':
            click.echo(f'''Status: failure \nError: error.wrong_tenant \nErrorMessage: You don't have permission on this tenant.''', 
                err=True
            )
        elif msg == 'error.sdk_permission':
            click.echo(f'''Status: failure \nError: error.sdk_permission\nErrorMessage: Your tenant does not have permission on this sdk function.''', 
                err=True
            )
        else:
            click.echo(f'''Status: failure \nError: error.other \nErrorMessage: {msg}''', 
            err=True)
        sys.exit(1)
