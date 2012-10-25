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
	
Note: miniboa is a requirement but does not appear to have an entry inside of pip
It is included with the ScalyMUCK application for convenience and may be located
here: http://code.google.com/p/miniboa/

Windows Installation---

1. Download & Install Python 2.7 from http://www.python.org/
2. Download and install setup tools from http://pypi.python.org/pypi/setuptools
3. Make sure C:\PythonX\Lib\site-packages\ is set on your PATH, replacing the X with your specific version of Python.
4. Use easy_install to download and install pip:
	easy_install pip
5. Create a virtual environment in a directory of your choosing:
	virtualenv myEnv --no-site-packages
6. Activate the virtual environment (run from the virtualenv main directory):
	. bin/activate
7. Install the required libraries (run from scalyMUCK's main directory):
	pip install -r ./requirements.txt
8. Edit the following files to suit your needs:
	application/data/exit_message.txt
	application/data/settings_gameplay.cfg
	application/data/settings_server.cfg
	application/data/welcome_message.txt
	application/data/database_password.txt
9. CD to the main directory of ScalyMUCK and run "run.bat". Note there is no daemon mode for Windows.
I cannot guarantee this software will work on a Windows sjujauystem at all, however.
		
Linux Installation---
Most Linux based operating systems, if not all should have a Python runtime built in as it is.
If you already know what you're doing, then you probably shouldn't need to have to read
over this.

1. If you do not have a Python runtime for any reason, please download and install python:
	For Debian Systems: sudo apt-get install python
	** I do not know what it would be for other distributions.
2. Install python headers (used for compilation of the packages installed with pip):
	For Debian Systems: sudo apt-get install python-dev
3. Install setuptools:
	For Debian systems: sudo apt-get install python-setuptools
4. Install pip:
	For Debian systems: sudo easy_install pip
5. Create a virtual environment in a directory of your choosing:
	virtualenv myEnv --no-site-packages
6. Activate the virtual environment (run from the virtualenv main directory):
	.  bin/activate
7. Install the required libraries (run from scalyMUCK's main directory):
	pip install -r ./requirements.txt
8. Edit the following files to suit your needs:
	application/data/exit_message.txt
	application/data/settings_gameplay.cfg
	application/data/settings_server.cfg
	application/data/welcome_message.txt
	application/data/database_password.txt
9. Run "run.sh" from scalyMUCK's main directory and everything should work. If failure happens to occur, 
check your log files for any misconfigurations or useful errors for me to look at.

The server was programmed on a Python 2.7.3 runtime, so if you have issues running this on
any other version, try upgrading/downgrading to this version first.
	
Last changed: Thursday, October 25th, 2012