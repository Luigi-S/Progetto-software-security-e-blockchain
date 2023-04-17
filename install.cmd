wsl --set-default docker-desktop
wsl sed -i -e 's/H\"/?\"/' app/Dockerfile
docker compose build
wsl sed -i -e 's/\r$//' ganache/ganaches.sh