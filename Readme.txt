ScalyMUCK
Copyright (c) 2012 Liukcairo

This is just an experimental MUCK server I'm working on every once and a while. It should by no means
be used for anything practical at the moment as I cannot guarantee it's dependability (as a single person --me
can't throughly test the code like that alone).

Table of Contents--
I. Foreword
II. Installation
	
===============================
I. Foreword
===============================
	
As stated above, the current verison of this MUCK server is simply experimental and should
be considered altogether unstable unless you're fond of backing up data constantly and
griping about bugs.
	
===============================
II.	Installation
===============================
	
Windows Installation---

1. Download & Install Python 2.7 from http://www.python.org/
2. Download and install setup tools from http://pypi.python.org/pypi/setuptools
3. C:\PythonX\Lib\site-packages\ is set on your PATH, replacing the X with your specific version of Python.
4. Use easy_install to download and install the py-bcrypt and sqlalchemy binaries:
	easy_install py-bcrypt
	easy_install sqlalchemy
5. CD to the main directory of ScalyMUCK and run "Run.bat". Note there is no daemon for Windows.
I cannot guarantee this software will work on a Windows system at all, however.
		
Linux Installation---
Most Linux based operating systems, if not all should have a Python runtime built in as it is.

1. If you do not have a Python runtime for any reason, please download and install python:
	For Debian Systems: sudo apt-get install python
	** I do not know what it would be for other distributions.
2. Install setuptools:
	For Debian systems: sudo apt-get install python-setuptools
3. Install sqlalchemy:
	For Debian systems: sudo easy_install sqlalchemy
4. Install py-bcrypt
	For Debian systems: sudo easy_install py-bcrypt
5. To run, simply CD to the main application directory and run "Run.sh"

The server was programmed on a Python 2.7.3 runtime, so if you have issues running this on
any other version, try upgrading/downgrading to this version first.
	
Last changed: Thursday, October 25th, 2012