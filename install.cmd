docker compose build
wsl --set-default docker-desktop
wsl sed -i -e 's/\r$//' ganache/ganaches.sh