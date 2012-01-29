Hot generate Research Data
++++++++++++++++++++++++++

Create the research tables
$ mysql -u root -p childcount < research_tables.sql

Generate the research ids - should be done atleast once
$ ./generate_research_id.py

Generate the research data
$ mysql -u root -p childcount < request-formA.sql
$ mysql -u root -p childcount < request-formB.sql
$ mysql -u root -p childcount < request-formC.sql

Copy the files from /tmp folder

$ mv /tmp/formA.csv ~/backup
$ mv /tmp/formB.csv ~/backup
$ mv /tmp/formC.csv ~/backup

Remove null values i.e \N from *.csv
$ find  *.csv -type f -exec sed -i "s/\\\N//g" {} \;
