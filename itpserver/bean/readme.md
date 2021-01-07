# coding:utf-8
#
#
# ITM web server demo 1.0 (project_name: bean, app_name: itm)

# admin if use:
# admin url : http://ip:port/admin
# username/password: admin/admin123

# User info
# API use password is passwordHash (in dbtable UserProfile)

# test
# uwsgi_test.py is the test script of uwsgi server
# test_v1.py and test_v2.py is the API test script with python-requests

# packages
# from top to bottom import system packages, frame packages and custom packages
# the wrapped package is used for extension and testing

# server
# redis-server
# start : uwsgi --ini itmapi_uwsgi.ini
# reload: uwsgi --reload /tmp/bean-master.pid
# stop  : uwsgi --stop /tmp/bean-master.pid

# use for debug
# uwsgi --http :8000  --ini itmapi_uwsgi.ini
# uwsgi --master --https 0.0.0.0:443,foobar.crt,foobar.key,HIGH --chdir /home/share/bean/ --module bean.wsgi

# add user
# in /bean/itm_user
# python itm_user.py username password

# celery
# redis-server
# celery -A proj.tasks worker -E -l INFO -n worker_ars -Q ars_task
# python manage.py celery worker -E -l INFO -n worker_ars -Q ars_task
# python manage.py celery worker -E -l INFO -n worker_ers -Q ers_task
# python manage.py celery flower
# http://172.22.118.99:5555


# api data
#
# check_in
# {"username": "itm-admin", "timestamp": 1524625223, "passwordHash": "MjdjNjNkMqqq", "deviceType":1, "connectionType":0}
#
# register
# {"deviceID": "lian-test-deviceID", "deviceName": "lian-test-ucss", "logSources": ["1.1.1.1", "2.2.2.2", "3.3.3.3"]}
#
# itm-configs
# {}


# restful change
# response.py
# set status=0 if not status, set data={} if data is None

# views.py
# settings.py
# ...
