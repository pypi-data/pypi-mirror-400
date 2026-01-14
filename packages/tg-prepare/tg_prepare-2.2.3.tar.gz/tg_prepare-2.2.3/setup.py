# -*- coding: utf-8 -*-
# Copyright (C) 2023-2024 TU-Dresden (ZIH)
# ralf.klammer@tu-dresden.de
# moritz.wilhelm@tu-dresden.de

from setuptools import setup, find_packages

setup(
    name="tg_prepare",
    version="2.2.3",
    description="Simple UI to handle TextGrid imports visually.",
    author="Ralf Klammer, Moritz Wilhelm",
    author_email="ralf.klammer@tu-dresden.de, moritz.wilhelm@tu-dresden.de",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "flask",
        "flask_json",
        "flask_login",
        "tg_model>=3.11.0",
        "tgclients",
        "tgadmin",
        "nextcloud-api-wrapper",
    ],
    package_data={
        "tgp_ui": [
            "static/js/*.js",
            "static/css/*.css",
            "static/svg/*.svg",
            "templates/*.html",
        ],
    },
    entry_points={
        "console_scripts": [
            "tgp_cli = tgp_backend.cli:main",
            "tgp_user = tgp_backend.cli:user",
            "tgp_app = tgp_ui.app:startup",
        ]
    },
)
