Description
-----------

Tyrs is a twitter and identi.ca client using curses that is easily configurable.

- [Home Site](http://tyrs.nicosphere.net)
- [Quick Start](http://tyrs.nicosphere.net/quick_start.html)
- [Screenshot](http://tyrs.nicosphere.net/screenshot.html)
- [Reference guide](http://tyrs.nicosphere.net/reference.html)
- [Pypi download page](http://pypi.python.org/pypi/tyrs)

Functionality
--------------

- Identi.ca and Twitter support
- Oauth authentication
- Proxy support
- utf-8 support, 256 Colors, transparency
- Mentions, Direct messages, Favorites, User and Search timelines
- Follow/Unfollow
- Display thread view of replies
- ur1.ca, bit.ly and goo.gl support
- Filter system
- Configuration file allows for lots of customization

Installation
------------

* Current release with `easy_install` (for python2.7, but other release coming soon):
    
    sudo easy_install http://pypi.python.org/packages/2.7/t/tyrs/tyrs-0.5.0-py2.7.egg

or with python-pip tools:

    sudo pip install tyrs

Dependecies that should be install automatically:
* python-twitter, python-oauth2, python-argparse
Requires: python-setuptools

    git clone git://github.com/Nic0/tyrs.git
    cd tyrs
    python setup.py build
    sudo python setup.py install

check the [installation guide](http://tyrs.nicosphere.net/reference.html#installation) for more information.

Licence
-------

GNU GENERAL PUBLIC LICENCE (GPL)
Check `doc/LICENCE` for the full licence text.

Author
------

Nicolas Paris
http://www.nicosphere.net
