# -*- coding: utf-8 -*-
# Copyright (C) 2023-2025 TU-Dresden (ZIH)
# ralf.klammer@tu-dresden.de
# moritz.wilhelm@tu-dresden.de

import logging

from datetime import datetime

from flask import (  # type: ignore
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    current_app,
)
from flask_login import (  # type: ignore
    login_user,
    logout_user,
    login_required,
)

log = logging.getLogger(__name__)

# Create Blueprint for authentication routes
auth_routes = Blueprint("auth", __name__)


@auth_routes.route("/login", methods=["GET", "POST"])
def login():
    # Redirect if user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for("views.overview"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Check if "remember me" option is selected
        remember = True if request.form.get("remember") else False

        user_manager = current_app.user_manager
        user = user_manager.get_user(username)

        # Validate user credentials
        if not user or not user.check_password(password):
            flash(
                "Bitte überprüfe deine Anmeldedaten und versuche es erneut.",
                "danger",
            )
            return render_template("auth/login.html")

        # Login successful
        user.last_login = datetime.now().isoformat()
        user_manager.save_users()
        login_user(user, remember=remember)

        # Redirect to requested page or default to overview
        next_page = request.args.get("next")
        return redirect(next_page or url_for("views.overview"))

    return render_template("auth/login.html")


@auth_routes.route("/logout")
@login_required
def logout():
    # Log out the current user
    logout_user()
    return redirect(url_for("auth.login"))
