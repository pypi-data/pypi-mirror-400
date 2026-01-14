# -*- coding: utf-8 -*-
# Copyright (C) 2023-2024 TU-Dresden (ZIH)
# ralf.klammer@tu-dresden.de
# moritz.wilhelm@tu-dresden.de

import logging

import click
from .util import cli_startup
from .user import UserManager

log = logging.getLogger(__name__)


@click.group()
@click.option("--debug/--no-debug", "-d", is_flag=True, default=False)
@click.option("--login", default="rk")
@click.pass_context
def main(ctx, debug, login):
    cli_startup(log_level=debug and logging.DEBUG or logging.INFO)
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug
    ctx.obj["login"] = login


@main.group()
def user():
    """Benutzerverwaltung"""
    pass


@user.command()
@click.argument("username")
@click.argument("password")
@click.option("--email", default=None)
@click.option("--role", default="user", type=click.Choice(["user", "admin"]))
def create(username, password, email, role):
    """Erstelle einen neuen Benutzer"""
    user_manager = UserManager()

    success, message = user_manager.create_user(
        username, password, email, role
    )

    if success:
        click.echo(
            click.style(
                f"Benutzer '{username}' erfolgreich erstellt.", fg="green"
            )
        )
    else:
        click.echo(click.style(f"Fehler: {message}", fg="red"))


@user.command()
def list():
    """Liste alle Benutzer auf"""
    user_manager = UserManager()

    users = user_manager.users

    if not users:
        click.echo("Keine Benutzer gefunden.")
        return

    click.echo(f"{'Benutzername':<20} {'E-Mail':<30} {'Rolle':<10}")
    click.echo("-" * 60)

    for username, user in users.items():
        email = user.email or "-"
        click.echo(f"{username:<20} {email:<30} {user.role:<10}")


@user.command()
@click.argument("username")
def delete(username):
    """Lösche einen Benutzer"""
    user_manager = UserManager()

    if username not in user_manager.users:
        click.echo(
            click.style(
                f"Fehler: Benutzer '{username}' existiert nicht.", fg="red"
            )
        )
        return

    if click.confirm(f"Benutzer '{username}' wirklich löschen?"):
        del user_manager.users[username]
        user_manager.save_users()
        click.echo(
            click.style(
                f"Benutzer '{username}' erfolgreich gelöscht.", fg="green"
            )
        )
