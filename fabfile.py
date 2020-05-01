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


# REMOTE_PATH_SITE = '/home/{}/vteme'.format(REMOTE_USER)
# REMOTE_PATH_BACKUPS = '/home/{}/backups'.format(REMOTE_USER)

# for apply
# psql -f db_2019-09-04_15\:48.sql postgres


@task(hosts=(REMOTE_HOST, ))
def clean(c):
    with c.cd(REMOTE_PATH_SITE):
        c.run('docker system prune -a')


@task(hosts=(REMOTE_HOST, ))
def backup(c):
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
    c.sudo(
        'zip -r server_media_{date}.zip /var/lib/docker/volumes/vteme_media_data/'.format(  # noqa
            date=date
        ),
        shell=False
    )
    c.run(
        'mv server_media_{date}.zip {path}/'.format(
            date=date,
            path=REMOTE_PATH_BACKUPS
        )
    )
    with c.cd(REMOTE_PATH_SITE):
        c.run('COMPOSE_INTERACTIVE_NO_CLI=1 docker-compose exec postgres pg_dumpall -c -U postgresuser > db_{date}.sql'.format(  # noqa
            date=date))
        c.run('zip db_{date}.zip db_{date}.sql'.format(
            date=date))
        c.run('rm -f db_{date}.sql'.format(
            date=date))
        c.run('mv db_{date}.zip {path}/'.format(
            date=date, path=REMOTE_PATH_BACKUPS))


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
def deploy(connection, prod=None):
    remote_path = os.path.join(REMOTE_PROJECT_PATH, 'production' if prod else 'staging')
    with connection.cd(remote_path):
        _run(connection, 'docker-compose build --build-arg NGINX_MODE={}'.format('production' if prod else 'staging',))
        _run(connection, 'docker-compose stop')
        _run(connection, 'docker-compose up -d')


@task(hosts=(REMOTE_HOST, ))
def deploydevops(connection, prod=None):
    remote_path = os.path.join(REMOTE_PROJECT_PATH, 'production' if prod else 'staging')
    rsync(
        connection,
        os.path.join(LOCAL_DEVOPS_PATH, 'envs', 'server.env'),
        os.path.join(remote_path, 'server', '.docker.env'),
    )
    rsync(
        connection,
        os.path.join(LOCAL_DEVOPS_PATH, 'envs', 'sockjs.env'),
        os.path.join(remote_path, 'sockjs', '.docker.env'),
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
    rsync(
        connection,
        os.path.join(LOCAL_DEVOPS_PATH, 'docker-compose.yml'),
        os.path.join(remote_path, 'docker-compose.yml'),
    )


@task(hosts=(REMOTE_HOST, ))
def deployclient(connection, prod=None):
    os.system("cd {} && make build".format(LOCAL_CLIENT_PATH))
    remote_path = os.path.join(REMOTE_PROJECT_PATH, 'production' if prod else 'staging', 'client')
    rsync(
        connection,
        os.path.join(LOCAL_CLIENT_PATH, 'build'),
        remote_path,
    )


@task(hosts=(REMOTE_HOST, ))
def deployserver(connection, prod=None):
    rsync(
        connection,
        LOCAL_SERVER_PATH,
        os.path.join(REMOTE_PROJECT_PATH, 'production' if prod else 'staging'),
        **SERVER_RSYNC_OPTS,
    )


@task(hosts=(REMOTE_HOST, ))
def deploysockjs(connection, prod=None):
    rsync(
        connection,
        LOCAL_SOCKJS_PATH,
        os.path.join(REMOTE_PROJECT_PATH, 'production' if prod else 'staging'),
        **SERVER_RSYNC_OPTS,
    )