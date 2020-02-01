docker build -t zinc .

docker tag zinc infrarift/zinc
docker tag zinc infrarift/zinc:latest

docker push infrarift/zinc
docker push infrarift/zinc:latest