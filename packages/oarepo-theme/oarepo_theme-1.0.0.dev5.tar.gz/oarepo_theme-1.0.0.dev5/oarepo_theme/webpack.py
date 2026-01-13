#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-theme (see https://github.com/oarepo/oarepo-theme).
#
# oarepo-theme is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""OARepo theme webpack integration module.

This module provides webpack bundle project integration for OARepo SemanticUI theme.
"""

from __future__ import annotations

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": {
            "entry": {},
            "dependencies": {},
            "devDependencies": {},
            "aliases": {
                "../../theme.config$": "less/theme.config",
                "../../less/site": "less/site",
                "../../less": "less",
                "@less": "less",
                "themes/oarepo": "less/oarepo",
            },
        }
    },
)
