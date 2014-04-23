startenv:
	virtualenv .

createdb:
	mysql -u root -p < create.sql

reqs:
	pip install -r requirements.txt	
