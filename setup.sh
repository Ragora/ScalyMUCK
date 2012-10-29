echo "ScalyMUCK (c) 2012 Liukcairo"
echo "ScalyMUCK Initial configuration Script"
echo " "
mkdir ~/.scalyMUCK
cd ~/.scalyMUCK
echo "# Configuration file for ScalyMUCK Server\nServerPort=8000\nServerAddress=0.0.0.0\nWorkFactor=10"  >> settings_server.cfg
echo "# Configuration file for ScalyMUCK Gameplay\n# There are none as of now."  >> settings_gameplay.cfg
echo "\nYou fall asleep in the current area." >> exit_message.txt
echo "============================================================\nWelcome! You're on a MUCK server running ScalyMUCK\nCopyright (c) 2012 Liukcairo\nYou may connect using the 'connect' command:\nconnect <username> <password>\n============================================================" >> welcome_message.txt
echo "Your data has been created at: " ~/.scalyMUCK