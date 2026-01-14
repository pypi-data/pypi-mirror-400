Introduction into Textual and writing Tests for it
**************************************************

What's textual?
===============

`Textual <https://textual.textualize.io/>`_ is a rapid application development framework for Python that enables
developers to build sophisticated **text-based user interfaces (TUIs)** with a simple API. It allows creating
interactive applications that run in the terminal or a web browser, leveraging existing Python skills for efficient
development. The framework focuses on creating beautiful and functional UIs, making it suitable for modern terminal
applications.

What does this BalderHub package provide?
=========================================

This BalderHub project provides bindings to the
`Textual's Pilot feature <https://textual.textualize.io/guide/testing/>`_. Because Balder does not support Python's
async framework and the Textual test framework relies on it, this package converts all async calls to sync calls.

It also provides different components to write tests according to the Page Object Model. Have a look at the
``Examples`` section of this document to see how you can do that.