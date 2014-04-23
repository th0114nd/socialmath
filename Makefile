startenv:
	virtualenv .

createdb:
	mysql -u root -p < create.sql
