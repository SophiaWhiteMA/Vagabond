#This script should be run after downloading the Vagabond repository.
#It will set up your python virtual environment and install all missing
# Python and NodeJS dependencies.


#CD into root directory
cd ..

#Create and activate virtual environment
cd server/vagabond
python3 -m venv env
source env/bin/activate #UNIX
source env/Scripts/activate #Windows

#Install python dependencies
pip3 install -r requirements.txt

#CD back to root directory
cd ../..

#Install node dependencies
cd client
npm install
cd ..

