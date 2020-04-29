import datetime
import os
from fabric import task
from patchwork.transfers import rsync


LOCAL_PATH_SITE = os.environ.get('LOCAL_PATH_SITE', default='/Users/seva/Projects/vteme/vteme/')
REMOTE_USER = 'vteme'
REMOTE_HOST = '{}@91.239.27.71'.format(REMOTE_USER)
REMOTE_PATH_SITE = '/home/{}/vteme'.format(REMOTE_USER)
REMOTE_PATH_BACKUPS = '/home/{}/backups'.format(REMOTE_USER)

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


@task(hosts=(REMOTE_HOST, ))
def deploy(
    c,
    withclean=False,
    withbackup=False,
):
    if withclean:
        clean(c)

    if withbackup:
        backup(c)


    os.system("cd {}client && make build-prod".format(LOCAL_PATH_SITE))
    rsync(
        c,
        LOCAL_PATH_SITE,
        REMOTE_PATH_SITE,
        exclude=[
            '*.pyc',
            '__pycache__',
            '.DS_Store',
            '.env',
            'env',
            '.vscode',
            '.git',
            'node_modules',
            'server_media',
            'server_static',
            'htmlcov',
            '.coverage',
            '.expo',
            'web-build',
            'web-report',
        ]
    )

    with c.cd(REMOTE_PATH_SITE):
        c.run('docker-compose build')
        c.run('docker-compose stop')
        c.run('docker-compose up -d')
