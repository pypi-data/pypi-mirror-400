import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from aiogram_part.commands import init
from aiogram_part.commands import handler as handler_mod
from aiogram_part.commands import model as model_mod
from aiogram_part.commands import keyboard as keyboard_mod
from aiogram_part.commands import filter as filter_mod
from aiogram_part.commands import middleware as middleware_mod
from aiogram_part.commands import i18n as i18n_mod
from aiogram_part.commands import database as database_mod
from aiogram_part.commands import service as service_mod
from aiogram_part.commands import state as state_mod
from aiogram_part.commands import validator as validator_mod
from aiogram_part.commands import enum as enum_mod
from aiogram_part.commands import test as test_mod
from aiogram_part.commands import check as check_mod
from aiogram_part.commands import stats as stats_mod
from aiogram_part.commands import webhook as webhook_mod
from aiogram_part.commands import deploy as deploy_mod

console = Console()

@click.group()
@click.version_option(
    version="1.0.1",
    prog_name="aiogram-part",
    message="%(prog)s %(version)s\nCopyright (C) 2026 Sattorbek\nLicense: MIT"
)
def main():
    """Professional CLI scaffolding tool for aiogram 3.x Telegram bots"""
    pass

@main.command()
@click.option("--with-db", is_flag=True, help="Initialize with database structure")
@click.option("--type", "db_type", type=click.Choice(["sqlite", "postgresql", "mysql"]), default="sqlite", help="Database type (default: sqlite)")
def init_project(with_db, db_type):
    init.execute(with_db, db_type)

@main.command()
def multiple_language():
    i18n_mod.execute()

@main.command()
@click.argument("scope", type=click.Choice(["user", "admin"]))
@click.argument("handler_type", type=click.Choice(["command", "message", "callback"]))
@click.argument("name")
def handler(scope, handler_type, name):
    handler_mod.execute(scope, handler_type, name)

@main.command()
@click.argument("name")
@click.option("--with-crud", is_flag=True, help="Generate CRUD operations")
def model(name, with_crud):
    model_mod.execute(name, with_crud)

@main.command()
@click.option("--scope", type=click.Choice(["user", "admin", "common"]), required=True)
@click.option("--build-keyboard", "keyboard_type", type=click.Choice(["inline", "reply"]), required=True)
@click.argument("name")
@click.option("--str-params", multiple=True, help="String parameters")
@click.option("--int-params", multiple=True, help="Integer parameters")
def keyboard(scope, keyboard_type, name, str_params, int_params):
    keyboard_mod.execute(scope, name, keyboard_type, str_params, int_params)

@main.command(name="filter")
@click.option("--scope", type=click.Choice(["user", "admin", "common"]), required=True)
@click.option("--type", "filter_type", type=click.Choice(["common", "callback"]), required=True)
@click.argument("name")
@click.option("--str-params", multiple=True, help="String parameters")
@click.option("--int-params", multiple=True, help="Integer parameters")
def filter_command(scope, filter_type, name, str_params, int_params):
    filter_mod.execute(scope, filter_type, name, str_params, int_params)

@main.command()
@click.option("--scope", type=click.Choice(["user", "admin", "common"]), required=True)
@click.argument("name")
@click.option("--types", multiple=True, type=click.Choice([
    "all", "message", "edited_message", "channel_post", "edited_channel_post",
    "callback_query", "inline_query", "chosen_inline_result",
    "shipping_query", "pre_checkout_query", "poll", "poll_answer",
    "my_chat_member", "chat_member", "chat_join_request"
]), help="Middleware types (default: all)")
def middleware(scope, name, types):
    if not types:
        types = ("all",)
    middleware_mod.execute(scope, name, types)

@main.group()
def database():
    """Database management commands (Aerich migrations)"""
    pass

@database.command(name="migrate")
@click.option("--force", is_flag=True, help="Force reinitialize")
def db_migrate(force):
    """Initialize database and create first migration"""
    database_mod.migrate(force)

@database.command(name="update")
@click.option("--name", default="auto_update", help="Migration name")
def db_update(name):
    """Create new migration and apply it (like Prisma migrate dev)"""
    database_mod.update(name)

@database.command(name="upgrade")
def db_upgrade():
    """Apply pending migrations"""
    database_mod.upgrade()

@database.command(name="downgrade")
@click.option("--version", default=-1, help="Number of migrations to rollback")
def db_downgrade(version):
    """Rollback migrations"""
    database_mod.downgrade(version)

@database.command(name="history")
def db_history():
    """Show migration history"""
    database_mod.history()

@database.command(name="heads")
def db_heads():
    """Show current migration heads"""
    database_mod.heads()

@database.command(name="reset")
def db_reset():
    """Drop all tables and reinitialize (DANGEROUS!)"""
    database_mod.reset()

@database.command(name="generate")
@click.argument("name")
def db_generate(name):
    """Generate migration without applying"""
    database_mod.generate_migration(name)

@database.command(name="inspect")
def db_inspect():
    """Show current database schema"""
    database_mod.inspect()

@main.command()
@click.option("--scope", type=click.Choice(["user", "admin", "common"]), required=True)
@click.argument("name")
def service(scope, name):
    """Generate service class for business logic"""
    service_mod.execute(scope, name)

@main.command()
@click.argument("name")
def state(name):
    """Generate FSM state class"""
    state_mod.execute(name)

@main.command()
@click.argument("name")
@click.option("--type", "validator_type", type=click.Choice(["regex", "custom"]), default="custom")
def validator(name, validator_type):
    """Generate validator function"""
    validator_mod.execute(name, validator_type)

@main.command()
@click.argument("name")
@click.option("--values", multiple=True, required=True, help="Enum values")
def enum(name, values):
    """Generate database enum"""
    enum_mod.execute(name, values)

@main.command()
@click.option("--type", "test_type", type=click.Choice(["handler", "service", "generic"]), default="generic")
@click.argument("name")
def test(test_type, name):
    """Generate test file"""
    test_mod.execute(test_type, name)

@main.command()
@click.option("--fix", is_flag=True, help="Auto-fix issues")
def check(fix):
    """Check project environment and configuration"""
    check_mod.execute(fix)

@main.command()
def stats():
    """Show project statistics"""
    stats_mod.execute()

@main.group()
def webhook():
    """Webhook management commands"""
    pass

@webhook.command(name="setup")
@click.argument("domain")
def webhook_setup(domain):
    """Setup webhook configuration"""
    webhook_mod.setup(domain)

@webhook.command(name="status")
def webhook_status():
    """Show webhook status"""
    webhook_mod.status()

@main.command()
@click.option("--user", default="botuser", help="System user to run the service")
def deploy(user):
    """Generate systemd service file"""
    deploy_mod.execute(user)

if __name__ == "__main__":
    main()
