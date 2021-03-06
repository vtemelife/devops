import datetime
import os
from fabric import task
from patchwork.transfers import rsync


LOCAL_PROJECT_PATH = os.environ['LOCAL_PROJECT_PATH']
LOCAL_CLIENT_PATH = os.path.join(LOCAL_PROJECT_PATH, 'client')
LOCAL_SERVER_PATH = os.path.join(LOCAL_PROJECT_PATH, 'server')
LOCAL_SOCKJS_PATH = os.path.join(LOCAL_PROJECT_PATH, 'sockjs')
LOCAL_DEVOPS_PATH = os.path.join(LOCAL_PROJECT_PATH, 'devops')

REMOTE_HOST = os.environ['REMOTE_HOST']
REMOTE_PROJECT_PATH = os.environ['REMOTE_PROJECT_PATH']

SERVER_RSYNC_OPTS = dict(
    rsync_opts='--filter=":- .gitignore"',
    exclude=[
        '.git',
        '.github',
        '.vscode',
        '.gitignore',
        'CODEOWNERS',
        'LICENSE',
        'README.md',
        '.pre-commit-config.yaml',
        '.secrets.baseline',
        'pyproject.toml',
        'setup.cfg',
        '.isort.cfg',
        'compose',
        'docker-compose.yml',
    ]
)


def _run(connection, command):
    if connection.host in ('127.0.0.1', 'localhost'):
        connection.local(command)
    else:
        connection.run(command)


@task(hosts=(REMOTE_HOST, ))
def cleandocker(connection, instance=None):
    instance = instance or 'staging'
    remote_path = os.path.join(REMOTE_PROJECT_PATH, instance)
    with connection.cd(remote_path):
        _run(connection, 'docker system prune -a')


@task(hosts=(REMOTE_HOST, ))
def backup(connection, instance=None):
    instance = instance or 'staging'
    remote_path = os.path.join(REMOTE_PROJECT_PATH, instance)
    with connection.cd(remote_path):
        _run(connection, 'docker-compose build backup')
        _run(connection, 'docker-compose run backup')


@task(hosts=(REMOTE_HOST, ))
def cleanbackup(connection, instance=None):
    instance = instance or 'staging'
    remote_path = os.path.join(REMOTE_PROJECT_PATH, instance, 'backups')
    with connection.cd(remote_path):
        _run(connection, 'rm *.zip')


@task(hosts=(REMOTE_HOST, ))
def deployclient(connection, instance=None):
    instance = instance or 'staging'
    os.system("cd {} && make build".format(LOCAL_CLIENT_PATH))
    remote_path = os.path.join(REMOTE_PROJECT_PATH, instance, 'client')
    _run(connection, 'mkdir -p {}'.format(remote_path))
    rsync(
        connection,
        os.path.join(LOCAL_CLIENT_PATH, 'build'),
        remote_path,
    )


@task(hosts=(REMOTE_HOST, ))
def deployserver(connection, instance=None):
    instance = instance or 'staging'
    remote_path = os.path.join(REMOTE_PROJECT_PATH, instance)
    _run(connection, 'mkdir -p {}'.format(remote_path))
    rsync(
        connection,
        LOCAL_SERVER_PATH,
        remote_path,
        **SERVER_RSYNC_OPTS,
    )


@task(hosts=(REMOTE_HOST, ))
def deploysockjs(connection, instance=None):
    instance = instance or 'staging'
    remote_path = os.path.join(REMOTE_PROJECT_PATH, instance)
    _run(connection, 'mkdir -p {}'.format(remote_path))
    rsync(
        connection,
        LOCAL_SOCKJS_PATH,
        remote_path,
        **SERVER_RSYNC_OPTS,
    )


@task(hosts=(REMOTE_HOST, ))
def deploydevops(connection, instance=None):
    instance = instance or 'staging'
    remote_path = os.path.join(REMOTE_PROJECT_PATH, instance)
    rsync(
        connection,
        os.path.join(LOCAL_DEVOPS_PATH, 'envs'),
        os.path.join(remote_path, 'envs'),
    )
    rsync(
        connection,
        os.path.join(LOCAL_DEVOPS_PATH, 'envs', 'server_{}.env'.format(instance)),
        os.path.join(remote_path, 'server', '.env'),
    )
    rsync(
        connection,
        os.path.join(LOCAL_DEVOPS_PATH, 'envs', 'sockjs_{}.env'.format(instance)),
        os.path.join(remote_path, 'sockjs', '.env'),
    )
    rsync(
        connection,
        os.path.join(LOCAL_DEVOPS_PATH, 'envs', 'client_{}.env'.format(instance)),
        os.path.join(remote_path, 'client', '.env'),
    )
    rsync(
        connection,
        os.path.join(LOCAL_DEVOPS_PATH, 'envs', 'ssl'),
        os.path.join(remote_path, 'client'),
    )
    rsync(
        connection,
        os.path.join(LOCAL_DEVOPS_PATH, 'composes', 'server', 'compose'),
        os.path.join(remote_path, 'server'),
    )
    rsync(
        connection,
        os.path.join(LOCAL_DEVOPS_PATH, 'composes', 'sockjs', 'compose'),
        os.path.join(remote_path, 'sockjs'),
    )
    rsync(
        connection,
        os.path.join(LOCAL_DEVOPS_PATH, 'composes', 'client', 'compose'),
        os.path.join(remote_path, 'client'),
    )
    _run(connection, 'mkdir -p {}'.format(os.path.join(remote_path, 'backups')))
    rsync(
        connection,
        os.path.join(LOCAL_DEVOPS_PATH, 'composes', 'backups', 'compose'),
        os.path.join(remote_path, 'backups'),
    )
    rsync(
        connection,
        os.path.join(LOCAL_DEVOPS_PATH, 'docker-compose-{}.yml'.format(instance)),
        os.path.join(remote_path, 'docker-compose.yml'),
    )


@task(hosts=(REMOTE_HOST, ))
def deploy(connection, instance=None):
    deployclient(connection, instance=instance)
    deployserver(connection, instance=instance)
    deploysockjs(connection, instance=instance)
    deploydevops(connection, instance=instance)
    instance = instance or 'staging'
    remote_path = os.path.join(REMOTE_PROJECT_PATH, instance)
    with connection.cd(remote_path):
        _run(connection, 'docker-compose build')
        # _run(connection, 'docker-compose stop')
        _run(connection, 'docker-compose up -d react')

