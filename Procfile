
#web: gunicorn magic_mirror_docker.magic_mirror.wsgi --log-file -

web: waitress-serve --port=$PORT magic_mirror.wsgi:application