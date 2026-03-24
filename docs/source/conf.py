#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

from pyrogram import __version__

project = "Kurigram"
copyright = "2017-present, Dan & KurimuzonAkuma"
author = "KurimuzonAkuma"

version = ".".join(__version__.split(".")[:-1])

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_iconify",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None)
}

master_doc = "index"
source_suffix = ".rst"
autodoc_member_order = "bysource"

templates_path = ["_templates"]
html_copy_source = False

napoleon_use_rtype = False
napoleon_use_param = False

pygments_style = "friendly"
pygments_dark_style = "monokai"

copybutton_prompt_text = "$ "

suppress_warnings = ["image.not_readable"]

html_title = "Kurigram"
html_theme = "shibuya"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_show_sourcelink = True
html_show_copyright = False
html_theme_options = {
    "accent_color": "violet",
    "dark_code": True,
    "globaltoc_expand_depth": 1,
    "github_url": "https://github.com/KurimuzonAkuma/pyrogram",
    "nav_links": [
        {
            "title": "Quick Start",
            "url": "intro/quickstart",
        },
        {
            "title": "API Reference",
            "url": "api/methods/index",
        },
        {
            "title": "Community",
            "url": "https://t.me/kurigram_chat",
            "external": True,
        },
    ],
}

latex_engine = "xelatex"

latex_elements = {
    "pointsize": "12pt",
    "fontpkg": r"""
        \setmainfont{Open Sans}
        \setsansfont{Bitter}
        \setmonofont{Ubuntu Mono}
        """
}
