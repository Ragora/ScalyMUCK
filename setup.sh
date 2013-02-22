echo "ScalyMUCK auto setup script for Ubuntu"
echo "DO NOT RUN AS ROOT"

sudo apt-get install python
sudo apt-get install python-pip
sudo apt-get install python-virtualenv
sudo apt-get install python-dev

virtualenv --no-site-packages ~/MUCK
cd ../
mv ./ScalyMUCK ~/MUCK/ScalyMUCK
cd ~/MUCK/bin
. ./activate
cd ~/MUCK/ScalyMUCK
pip install -r ./requirements.txt

rm run.sh
echo "cd ../bin/" >> run.sh
echo  ". activate" >> run.sh
echo "cd ../ScalyMUCK/application/" >> run.sh
echo "python ./muck.py" >> run.sh

rm daemon.sh
echo "cd ../bin/" >> daemon.sh
echo  ". activate" >> daemon.sh
echo "cd ../ScalyMUCK/application/" >> daemon.sh
echo "python ./muck.py start" >> daemon.sh

sudo chmod +x ./run.sh
sudo chmod +x ./daemon.sh

echo "Your install as located at: " ~/MUCK/ScalyMUCK/
echo "Now configure your file system then use run.sh or daemon.sh."
