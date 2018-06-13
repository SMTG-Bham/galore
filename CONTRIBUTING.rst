Contributing
============

Galore is managed by the Scanlon Materials Theory group at University
College London, and is open to contributions from third parties. If
you have an idea to make Galore better, please open an Issue outlining
your idea on the `Github issue tracker
<https://github.com/SMTG-UCL/galore/issues>`__.  This will allow a
public discussion of how well this fits the project design and goals,
and how it might be implemented.

Making changes
--------------

All contributions from third parties are managed using "Pull requests" on Github,
as are major changes by the core developers.
Create a copy of the project on your own Github account using the
"Fork" button near the top-right of the web interface and make your changes
on a new branch based on ``master``.
When you are ready to share these changes, create a pull request;
this will open a public discussion
`here <https://github.com/SMTG-UCL/galore/pulls>`__.

Before making substantial changes, *please begin discussion in an
Issue* so you have some idea if your proposal is likely to be
accepted!  For minor corrections it may be easier to move straight to
a pull request.

Galore is licensed under GPLv3 (see LICENSE file), including any
third-party contributions.

Further reading
~~~~~~~~~~~~~~~

- `A helpful unofficial guide to forking and pull requests on GitHub <https://gist.github.com/Chaser324/ce0505fbed06b947d962>`__
- `Another unofficial tutorial <https://www.thinkful.com/learn/github-pull-request-tutorial/>`__

Coding guidelines
-----------------

- Please follow `PEP8 <https://www.python.org/dev/peps/pep-0008/>`__
  including the 79-character line width limit. You can run a style
  checker on your code when you are done; a decent one called ``pep8``
  can be obtained with ``pip install pep8``.
- It is helpful to start commit messages with a short code indicating
  the type of change made; this makes it easier to scan the list of
  commits looking for e.g. documentation changes. The codes are loosely
  borrowed from
  `this scheme <https://wiki.fysik.dtu.dk/ase/development/contribute.html#writing-the-commit-message>`__
  used by the ASE project, but no strict scheme is enforced.
- Please ensure your changes pass the test suite (``python3 setup.py
  test``) and consider adding tests for any new behaviour. It can be
  helpful to write the test before you finish implementing the
  feature.
