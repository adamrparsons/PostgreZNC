# PostgreZNC
Adam Parsons (me@adamparsons.id.au)

## Installing
* Requires systemd-journal for debugging 

I chose this because any sort of debugging or stdout with modpython is absolutely impossible, this should have taken me an hour to write, but took almost two days because of how awful znc's modpython is, and its awesome, descriptive error messages such as "Module Aborted"

If you don't have or don't want systemd, just remove any line beginning with 'journal.send' and 
replace it with "pass" if its the sole statement after an except

### Requirements

    apt-get install python3-pip znc-dev znc-python build-essential postgresql
    pip3 install contextlib2 psycopg2

After that, edit the database connection details in this file "postgresConnectString()" to reflect yours

### Setting up the database

open a shell and create your database "pznc" 

    sudo su postgres
    createdb pznc

Or something like that, however you would create your databases normally.
Afterwards, drop into the psql shell and create the database with this schema

    CREATE TABLE chanlog (
      id SERIAL,
      code varchar(10) DEFAULT NULL,
      network varchar(64) DEFAULT NULL,
      channel varchar(64) DEFAULT NULL,
      host varchar(128) DEFAULT NULL,
      zuser varchar(32) DEFAULT NULL,
      user_mode char(1) DEFAULT NULL,
      target_user varchar(32) DEFAULT NULL,
      message text,
      date timestamp DEFAULT NULL,
      PRIMARY KEY (id)
    );


Note: You will not be able to run this script directly, its a python class, not an executable script, so don't bother trying, instead it should be placed inside your znc modules directory

    sudo cp pznc.py /usr/lib/znc/

And load it inside your IRC client with 

    /msg *status loadmod pznc

Check your syslog or journalctl for errors in configuration

## Copying
Some of this is directly copied and pasted from a similar module but for mysql, and without any exceptions. I really wanted this to be done as quickly as possible, so I needed to cheat a little.

You can compare theirs here: https://github.com/buxxi/znc-mysql/blob/master/sql.py

## Known Issues: 
Duplicate lines often occur, easily sovable though if anyone cares, I didn't write this because
I planned on using it, I wrote it to learn how to make a znc modpython module, I don't actually use this.
