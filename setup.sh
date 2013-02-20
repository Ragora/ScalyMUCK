echo "ScalyMUCK (c) 2012 Liukcairo"
echo "ScalyMUCK Initial configuration Script"
echo " "

cd ~/
if [ -d ".scalyMUCK" ]
then
	echo ~/.scalyMUCK/ "already exists."
else
	mkdir .scalyMUCK
fi
cd .scalyMUCK

if [ -e "settings_server.cfg" ]
then	
	echo ~/.scalyMUCK/"settings_server.cfg already exists."
else
	echo "# Configuration file for ScalyMUCK Server" >> settings_server.cfg
	echo "ServerPort=8000" >> settings_server.cfg
	echo "ServerAddress=0.0.0.0" >> settings_server.cfg
	echo "WorkFactor=10"  >> settings_server.cfg
fi

if [ -e "settings_gameplay.cfg" ]
then
	echo ~/.scalyMUCK/"settings_server.cfg already exists."
else
	echo "# Configuration file for ScalyMUCK Gameplay" >> settings_gameplay.cfg
	echo "# There are none as of now."  >> settings_gameplay.cfg
fi

if [ -e "exit_message.txt" ]
then
	echo ~/.scalyMUCK/"exit_message.txt already exists."
else
	echo " " >> exit_message.txt
	echo "You fall asleep in the current area." >> exit_message.txt
fi

if [ -e "welcome_message.txt" ]
then
	echo ~/.scalyMUCK/"welcome_message.txt already exists."
else
	echo "============================================================" >> welcome_message.txt
	echo "Welcome! You're on a MUCK server running ScalyMUCK\nCopyright (c) 2012 Liukcairo" >> welcome_message.txt
	echo "You may connect using the 'connect' command:" >> welcome_message.txt
	echo "connect <username> <password>" >> welcome_message.txt
	echo "============================================================" >> welcome_message.txt
fi

echo " "
echo "Your data is located at:" ~/.scalyMUCK