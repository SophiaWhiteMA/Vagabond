#Checks out to the mater branch and then updates all NPM and Python dependencies.
#Make sure to commit your work before running this script!


#cd into root directory
cd ..

#Checkout to master branch and pull updates
git checkout master
git pull

# Update python depdencies
cd server
pip3 install -r requirements.txt
cd ..

#Update JS dependencies
cd client
npm install
cd ..

