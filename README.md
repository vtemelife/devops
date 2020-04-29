# Vteme django server

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
cp envsets/env.dev .env
source .env
```

### Install project requirements:

```
make install
```

## Deploy env:

```
make deploy
```

## Backup static and DB:

```
make backup
```
