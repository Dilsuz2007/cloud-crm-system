# TexStyle CRM Docker Deploy

## Local

```powershell
docker compose build
docker compose up -d
docker compose exec backend python -m backend.app.init_db
```

Open `http://127.0.0.1:3003/`.

## AWS EC2

```bash
scp -r ./TexStyleCRM ubuntu@YOUR_SERVER_IP:~/TexStyleCRM
ssh ubuntu@YOUR_SERVER_IP
cd ~/TexStyleCRM
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
export SECRET_KEY='replace-with-a-long-random-secret'
docker compose build
docker compose up -d
docker compose exec backend python -m backend.app.init_db
```

Open port `3003/tcp` in the EC2 security group, then visit:

```text
http://YOUR_SERVER_IP:3003/
```

`backend.app.init_db` resets the database. Run it only for first setup or when demo data should be recreated.
