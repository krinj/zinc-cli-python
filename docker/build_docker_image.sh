docker build -t zinc:latest .
VERSION=$(git rev-parse HEAD)
echo "Using Version: ${VERSION}"

docker tag zinc:latest infrarift/zinc
docker tag zinc:latest infrarift/zinc:latest
docker tag zinc:latest infrarift/zinc:"${VERSION}"

docker push infrarift/zinc
docker push infrarift/zinc:latest
docker push infrarift/zinc:"${VERSION}"