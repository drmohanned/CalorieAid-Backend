
Calorie Development setup

Install required system packages:

    sudo apt-get install python3-pip
    sudo apt-get install python3-dev python3-setuptools
    sudo apt-get install libpq-dev
    sudo apt-get install postgresql postgresql-contrib

Create www directory where project sites and environment dir

    mkdir /var/www && mkdir /var/envs && mkdir /var/envs/bin

Install virtualenvwrapper

    sudo pip3 install virtualenvwrapper
    sudo pip3 install --upgrade virtualenv

Add these to your bashrc virutualenvwrapper work

    export WORKON_HOME=/var/envs
    export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
    export PROJECT_HOME=/var/www
    export VIRTUALENVWRAPPER_HOOK_DIR=/var/envs/bin
    source /usr/local/bin/virtualenvwrapper.sh

Create virtualenv

    cd /var/envs && mkvirtualenv --python=python3 calorie

Install requirements for a project.

    cd /var/www/calorie && pip install -r requirements/local.txt

##Database creation
###For psql

    sudo su - postgres
    psql
    DROP DATABASE IF EXISTS calorie;
    CREATE DATABASE calorie;
    CREATE USER calorie_user WITH password 'root';
    GRANT ALL privileges ON DATABASE calorie TO calorie_user;


####Configure rabbitmq-server to run workers.
    $ sudo apt-get update
    $ sudo apt-get upgrade
    $ cd ~
    $ wget http://packages.erlang-solutions.com/site/esl/esl-erlang/FLAVOUR_1_general/esl-erlang_20.1-1~ubuntu~xenial_amd64.deb
    $ sudo dpkg -i esl-erlang_20.1-1\~ubuntu\~xenial_amd64.deb
    $ echo "deb https://dl.bintray.com/rabbitmq/debian xenial main" | sudo tee /etc/apt/sources.list.d/bintray.rabbitmq.list
    $ wget -O- https://www.rabbitmq.com/rabbitmq-release-signing-key.asc | sudo apt-key add -
    $ sudo apt-get update
    $ sudo apt-get install rabbitmq-server
    $ sudo systemctl start rabbitmq-server.service
    $ sudo systemctl enable rabbitmq-server.service


####Add virtual host, and set permissions.

    $ sudo rabbitmqctl add_vhost calorie
    $ sudo rabbitmqctl add_user calorie_user root
    $ sudo rabbitmqctl set_permissions -p calorie calorie_user ".*" ".*" ".*"
    
  
###Set up supervisor (pm2)

    $ sudo apt-get install python-software-properties
    $ cd /var/www/calorie
    $ pm2 startup ubuntu14
    $ pm2 start scripts/manage_codebnb_init_default_consumer.sh --name calorie_init_default_consumer
    $ pm2 start scripts/manage_local_init_default_consumer.sh --name calorie_init_default_consumer
    $ pm2 save

####More about pm2 is here https://github.com/Unitech/pm2
