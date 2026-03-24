:layout: landing
:description: Kurigram — Elegant, modern and asynchronous Telegram MTProto API framework in Python.

Kurigram
========

.. rst-class:: lead

    Elegant, modern and asynchronous **Telegram MTProto API** framework for Python.
    Build user clients and bots with a clean, Pythonic interface.

.. container:: buttons

    `Get Started <intro/quickstart>`_
    `API Reference <api/methods/index>`_
    `GitHub <https://github.com/KurimuzonAkuma/pyrogram>`_

.. code-block:: python

    from pyrogram import Client, filters

    app = Client("my_account")


    @app.on_message(filters.private)
    async def hello(client, message):
        await message.reply("Hello from Kurigram!")


    app.run()

-----

.. grid:: 1 1 2 3
    :gutter: 2
    :padding: 0
    :class-row: surface

    .. grid-item-card:: :iconify:`mdi:server-network` MTProto API
        :link: topics/mtproto-vs-botapi
        :link-type: doc

        Direct access to Telegram's MTProto protocol.
        No middleman, no limitations — full API power.

    .. grid-item-card:: :iconify:`mdi:lightning-bolt` Async & Fast
        :link: topics/speedups
        :link-type: doc

        Built on top of ``asyncio`` for high-performance
        concurrent I/O. Optional TgCrypto & uvloop support.

    .. grid-item-card:: :iconify:`mdi:language-python` Pythonic API
        :link: start/invoking
        :link-type: doc

        Elegant, intuitive methods and types.
        Write less boilerplate, get more done.

    .. grid-item-card:: :iconify:`mdi:account-multiple` Users & Bots
        :link: start/auth
        :link-type: doc

        First-class support for both user accounts
        and bot identities. One framework, all use cases.

    .. grid-item-card:: :iconify:`mdi:filter-variant` Smart Filters
        :link: topics/use-filters
        :link-type: doc

        Powerful, composable update filters.
        Chain, combine and create custom ones with ease.

    .. grid-item-card:: :iconify:`mdi:puzzle` Plugin System
        :link: topics/smart-plugins
        :link-type: doc

        Modular smart plugin architecture.
        Organize handlers across files cleanly.

-----

First Steps
-----------

.. grid:: 1 1 2 2
    :gutter: 2
    :padding: 0

    .. grid-item-card:: :iconify:`mdi:rocket-launch` Quick Start
        :link: intro/quickstart
        :link-type: doc

        Overview to get you started quickly.

    .. grid-item-card:: :iconify:`mdi:function-variant` Invoking Methods
        :link: start/invoking
        :link-type: doc

        How to call Kurigram's methods.

    .. grid-item-card:: :iconify:`mdi:bell-ring` Handling Updates
        :link: start/updates
        :link-type: doc

        How to handle Telegram updates.

    .. grid-item-card:: :iconify:`mdi:alert-circle` Error Handling
        :link: start/errors
        :link-type: doc

        How to handle API errors correctly.

API Reference
-------------

.. grid:: 1 1 2 3
    :gutter: 2
    :padding: 0

    .. grid-item-card:: :iconify:`mdi:cube` Client
        :link: api/client
        :link-type: doc

        The Client class reference.

    .. grid-item-card:: :iconify:`mdi:format-list-bulleted` Methods
        :link: api/methods/index
        :link-type: doc

        All available high-level methods.

    .. grid-item-card:: :iconify:`mdi:shape` Types
        :link: api/types/index
        :link-type: doc

        All available high-level types.

    .. grid-item-card:: :iconify:`mdi:format-list-numbered` Enumerations
        :link: api/enums/index
        :link-type: doc

        Available enumerations.

    .. grid-item-card:: :iconify:`mdi:link-variant` Bound Methods
        :link: api/bound-methods/index
        :link-type: doc

        Convenient bound methods.

    .. grid-item-card:: :iconify:`mdi:funnel` Filters
        :link: api/filters
        :link-type: doc

        Update filter reference.

.. toctree::
    :hidden:
    :caption: Introduction

    intro/quickstart
    intro/install

.. toctree::
    :hidden:
    :caption: Getting Started

    start/setup
    start/auth
    start/invoking
    start/updates
    start/errors
    start/examples/index

.. toctree::
    :hidden:
    :caption: API Reference

    api/client
    api/methods/index
    api/types/index
    api/bound-methods/index
    api/enums/index
    api/handlers
    api/decorators
    api/errors/index
    api/filters

.. toctree::
    :hidden:
    :caption: Topic Guides

    topics/use-filters
    topics/create-filters
    topics/more-on-updates
    topics/client-settings
    topics/speedups
    topics/text-formatting
    topics/synchronous
    topics/smart-plugins
    topics/storage-engines
    topics/serializing
    topics/proxy
    topics/scheduling
    topics/mtproto-vs-botapi
    topics/debugging
    topics/test-servers
    topics/advanced-usage
    topics/voice-calls

.. toctree::
    :hidden:
    :caption: Meta

    faq/index
    support

.. toctree::
    :hidden:
    :caption: Telegram Raw API

    telegram/functions/index
    telegram/types/index
    telegram/base/index
