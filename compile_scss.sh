cd ..
cd vagabond-bootstrap/
npm run-script css
cd ..
cd vagabond/
cp ~/vagabond-bootstrap/dist/css/bootstrap.min.css ~/vagabond/client/public/css/
cp ~/vagabond-bootstrap/dist/css/vagabond/vagabond.css ~/vagabond/client/src/css/App.css
