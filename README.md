# Vteme devops

## Install system dependencies (Ubuntu / OSX)

### Install required services (OSX)

```
brew install pyenv
```

### Install required services (Ubuntu)

```
apt...
```

### Setup pyenv

Please, execute these commands to activate your pyenv (for bash just replace .zshrc with .bashrc)

```
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
eval "$(pyenv init -)"
```

## Setup environment and run project

### Clone repository and install dependencies

```
git clone git@github.com:vtemelife/devops.git
cd devops
```

### Install and activate virtual environment

```
pyenv install 3.7.4
pyenv shell 3.7.4

python -mvenv env
source env/bin/activate
```

### Activate environment:

```
cp envsets/local_dev.env .local.env
source .local.env
```

### Install project requirements:

```
pip install -r requirements.txt
```

## Ask administrator to get envs folder with env configs and put it in root

```
devops % ls envs
client_production.env   server_production.env   sockjs_production.env   ssl
client_staging.env      server_staging.env      sockjs_staging.env
```

## Deploy env:

```
make deploy
```

### Deploy only staging

```
make deployst
```

### Deploy only production

```
make deploypr
```

## Backup static and DB:

```
make backup
```

### Backup only staging

```
make backupst
```

### Backup only production

```
make backuppr
```

## Clean images on staging

```
ssh to server
cd vtemelife/staging
```

### Remove images

```
docker-compose run backup bash
cd ../server_media
find . \! -name 'default.png' -delete
exit
```

### Update storage table

```
docker-compose run django bash
python manage.py shell
```

In shell:

```
from apps.storage.models import Image
Image.objects.all().update(image='default.png')
Ctrl-D
```

```
python manage.py generate_thumbnails
exit
```