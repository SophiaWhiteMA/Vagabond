#Don't run this script manually -- it is used by the
#deploy script.

#cd into root directory
cd ..

# build client
cd client
npm install
npm run build
cd ..

# Copy compiled client into static folder of server
cp -dr ./client/build/* ./server/vagabond/static/

# cd back into scripts folder
cd scripts

echo "Build process complete."
