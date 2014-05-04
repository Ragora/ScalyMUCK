===========================================================================================
	ScalyMUCK	Version 3.5.0
	MUCK server application written for Python 2.7.
	Copyright (c) 2013 Robert MacGregor

	This software is licensed under the MIT license. Please refer to LICENSE.txt for
	more information.
===========================================================================================

ScalyMUCK BitBucket Wiki: https://github.com/Ragora/ScalyMUCK/wiki

Table of Contents:
	I. Foreword
	II. Installation on Ubuntu x86 and x64
		A. Download/Verify Prerequisites
		B. Configuring a Virtual Environment
		C. Configuring with MySQL
		D. Wrapping it up

I. FOREWORD

ScalyMUCK was originally designed to attempt to take the place of older, out of date MUCK server software and to attempt to ease 
the process of switching as much as possible with the soon to come conversion tool.

II. INSTALLATION ON UBUNTU x86 AND x64
	Seeing that ScalyMUCK is written in Python, it is very easy to get up and running in pretty much any Linux distribution 
	but this quickstart guide covers Ubuntu based systems (should also work for Debian as well).

	A. DOWNLOAD/VERIFY PREREQUISITES
		There are several tools used to download and install a working ScalyMUCK server, which can all be acquired using 
		the following commands:

		sudo apt-get install python python-dev python-setuptools git && sudo easy_install pip && sudo pip install virtualenv

		GIT is helpful for keeping your server up-to-date in the event that there are changes pushed to the source code.

	B. CONFIGURING A VIRTUAL ENVIRONMENT
		Configuring a working virtual environment to separate your dependencies isn't that hard of a task as well. 
		To create a fresh virtualenv you would run:

		virtualenv --no-site-packages ScalyMUCK

		Of course you can change 'ScalyMUCK' to whatever else you feel like, but note you should NOT move the virtual 
		environment once it was created as this will cause the virtual environment to quit working.

		Once the virtualenv is created, I usually just move whatever application I am trying to run in it to the root 
		directory of the virtualenv but this is not required. You still, however, need to activate your virtual environment
		by navigating to the bin/ directory and running:

		. activate

		Your terminal should now look something along the lines of: ”(ScalyMUCK)user@host$”. This means the virtual environment is 
		activated and is ready for modification or execution of an application within the virtual environment's context. You now 
		need to install the ScalyMUCK dependencies by first CD'ing to the root directory of your ScalyMUCK install and running 
		(it'll only take a minute or two):

		pip install -r ./requirements.txt

		ScalyMUCK is now configured and ready to go and you may move on to sub section D. If you wish to configure ScalyMUCK to
		work with a remote database server, then please refer to the appropriate sub section below.

	C. CONFIGURING WITH MYSQL

		By default ScalyMUCK uses SQLite which creates the database on your local file system – this probably actually will be fine 
		for most MUCK's anymore as I would imagine it's very hard to get that amount of activity to make this type of storage slow. 
		However, if you would like to to use MySQL there's a few more steps to do so.

		First you need to make sure you have libmysqlclient-dev installed:

		sudo apt-get install libmysqlclient-dev python-mysqldb

		And you need to install mysql-python into your virtual environment:

		pip install MySQL-python

		After that, you must edit the appropriate fields in application/config/settings_server.cfg to correspond to your MySQL server
		information.

	D. WRAPPING IT UP

		You now have several files to edit, all of which being entirely self-explanatory once you see them:
			* application/config/server_config.cfg
			* application/config/welcome_message.txt
			* application/config/exit_message.txt
			* application/config/permissions.cfg

		Once you have the desired configuration, you can test ScalyMUCK as long as your virtualenv is still active by running the 
		following code from the application/ directory:

		python ./main.py

		ScalyMUCK should run as expected, however, theabove code will run ScalyMUCK as a non-daemon. If you wish to have a daemon you 
		would run it with: 

		python ./main.py start

		ScalyMUCK is built on a fully modular architecture, therefore the base ScalyMUCK isn't all that capable of much. However there
		is only a small handful of mods I have been attempting to furnish, which you can find information on at ScalyMUCK's BitBucket
		Wiki as linked at the top of this file.
