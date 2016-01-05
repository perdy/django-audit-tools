============
Installation
============

To install *Audit* you need to follow the next steps:

#. Add MongoDB repository.
#. Install MongoDB.
#. Configure authentication for MongoDB.
#. Install Django Audit Tools package.

Install MongoDB
===============

Add repository
--------------
Import the public key used by the package management system::

    sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10

Create a list file for MongoDB repository::

    echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list

Reload local package database::

    sudo apt-get update

Install MongoDB packages
------------------------
Install the MongoDB packages::

    sudo apt-get install mongodb-org=2.6.3 mongodb-org-server=2.6.3 mongodb-org-shell=2.6.3 mongodb-org-mongos=2.6.3 mongodb-org-tools=2.6.3

(OPTIONAL) Pin a specific version of MongoDB::

    echo "mongodb-org hold" | sudo dpkg --set-selections
    echo "mongodb-org-server hold" | sudo dpkg --set-selections
    echo "mongodb-org-shell hold" | sudo dpkg --set-selections
    echo "mongodb-org-mongos hold" | sudo dpkg --set-selections
    echo "mongodb-org-tools hold" | sudo dpkg --set-selections

Start MongoDB::

    sudo service mongod start

Configure authentication
------------------------
Connect to MongoDB using client terminal::

    mongo

Change to admin database::

    use admin

Create admin user (replace <USER_ADMIN> and <PASSWORD_ADMIN>)::

    db.createUser({
        user: "<USER_ADMIN>",
        pwd: "<PASSWORD_ADMIN>",
        roles:
            [
                { role: "userAdminAnyDatabase", db: "admin" }
            ]
        }
    )

Activate authentication login uncommenting the next line in /etc/mongod.conf::

    # auth = True

Restart MongoDB::

    sudo service mongod restart

Connect to MongoDB as admin::

    mongo admin -u <USER_ADMIN> -p <PASSWORD_ADMIN>

Change to audit database (replace <DATABASE>)::

    use <DATABASE>

Create audit user (replace <USER> and <PASSWORD>)::

    db.createUser({
        user: "<USER>",
        pwd: "<PASSWORD>",
        roles:
            [
                { role: "readWrite", db: "<DATABASE>" }
            ]
        }
    )

(OPTIONAL) Add environment variables appending next lines to virtualenv's activate file (replace <USER> and <PASSWORD>)::

    export DB_AUDIT_USER=<USER>
    export DB_AUDIT_PASSWORD=<PASSWORD>

Install Audit
=============

Use pip to install *Audit* from local file::

    pip install django-audit-tools.tar.gz

Or install from pip repository::

    pip install django-audit-tools

