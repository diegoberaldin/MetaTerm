MetaTerm is a not-so-pretentious terminology management application written in
the Python programming language.

It is designed as a totally open source, cross-platform application and it
is built upon standard technologies such as the SQLite DBMS. This makes it
possible to have the internal representation of the termbase stored as a simple
file on your local disk, leaving the possession of your terminological
information *entirely in your hands*.

Apart from the **Python** runtime environment and the language standard library
which should be provided by any Python distribution (version 3.x), the program
relies on the Qt graphical toolkit, via the **PyQt** (version 4.10) language
bindings. In order to achieve data persistence, the **SQLAlchemy** library
(version 0.8) is also needed as a dependency.

MetaTerm supports the creation of **term-oriented** and **concept-oriented**
terminological databases (a.k.a. *termbases*) with a user-defined structure,
allowing you to record terminological information at the concept level, at the
language level or term level, as described in the TMF metamodel (in accordance
to the ISO 30042 2008 standard).

MetaTerm is free software, released under the GPLv3 license. See LICENCE for
further information about what you can (and can't) do with the software.
