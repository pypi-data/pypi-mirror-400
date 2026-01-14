"""Secrets management commands."""

import click
from rich.console import Console

from wowsql_cli.utils.formatters import format_output

console = Console()


@click.group()
def secrets_group():
    """Secrets management commands."""
    pass


@secrets_group.command('list')
@click.option('--project', help='Project slug (overrides default)')
@click.option('--format', type=click.Choice(['table', 'json', 'yaml']))
@click.pass_context
def list_secrets(ctx, project, format):
    """List all secrets."""
    try:
        api = ctx.obj['api']
        config = ctx.obj['config']
        project_slug = project or config.get_default_project()
        
        if not project_slug:
            console.print("[red]Error:[/red] No project specified. Use --project or set default project.")
            raise click.Abort()
        
        secrets = api.list_secrets(project_slug)
        output_format = format or ctx.obj['output']
        format_output(secrets, output_format, console)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@secrets_group.command('set')
@click.argument('key')
@click.argument('value')
@click.option('--public', is_flag=True, help='Mark secret as public (can be exposed to client)')
@click.option('--project', help='Project slug (overrides default)')
@click.pass_context
def set_secret(ctx, key, value, project, public):
    """Set a secret value."""
    try:
        api = ctx.obj['api']
        config = ctx.obj['config']
        project_slug = project or config.get_default_project()
        
        if not project_slug:
            console.print("[red]Error:[/red] No project specified. Use --project or set default project.")
            raise click.Abort()
        
        api.set_secret(project_slug, key, value, is_public=public)
        console.print(f"[green]✓[/green] Secret '{key}' set")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@secrets_group.command('get')
@click.argument('key')
@click.option('--project', help='Project slug (overrides default)')
@click.pass_context
def get_secret(ctx, key, project):
    """Get a secret value."""
    try:
        api = ctx.obj['api']
        config = ctx.obj['config']
        project_slug = project or config.get_default_project()
        
        if not project_slug:
            console.print("[red]Error:[/red] No project specified. Use --project or set default project.")
            raise click.Abort()
        
        value = api.get_secret(project_slug, key)
        console.print(value)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@secrets_group.command('unset')
@click.argument('key')
@click.option('--project', help='Project slug (overrides default)')
@click.pass_context
def unset_secret(ctx, key, project):
    """Delete a secret."""
    try:
        api = ctx.obj['api']
        config = ctx.obj['config']
        project_slug = project or config.get_default_project()
        
        if not project_slug:
            console.print("[red]Error:[/red] No project specified. Use --project or set default project.")
            raise click.Abort()
        
        api.delete_secret(project_slug, key)
        console.print(f"[green]✓[/green] Secret '{key}' deleted")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()

