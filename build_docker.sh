cd frontend
./manage build
rm -rf ../backend/static
cp -rf build ../backend/static
cd ../backend
docker build -t openpacs .
