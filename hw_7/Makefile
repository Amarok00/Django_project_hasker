VENV = env

setup-deps:
	dnf install python3-pip python3 libpq curl nginx -y

setup-db:
	dnf install postgresql-server postgresql-contrib -y
	postgresql-setup initdb
	systemctl start postgresql
	sudo -u postgres psql <<"__END__"
	CREATE DATABASE hasker_db;
	CREATE USER django WITH ENCRYPTED PASSWORD 'qaz123';
	GRANT ALL PRIVILEGES ON DATABASE hasker_db TO django;
	__END__

migrations: setup-db
	python manage.py makemigrations
	python manage.py migrate
	python manage.py collectstatic

$(VENV)/bin/activate: setup-deps
	python3 -m venv env

prod: $(VENV)/bin/activate migrations
	export DJANGO_DEBUG=False
	pip install -r requirements-prod.txt
	gunicorn hasker.wsgi:application -c config/gunicorn/dev.py
