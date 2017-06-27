"""`main` is the top level module for your Flask application."""
# Import the Flask Framework
import os
import MySQLdb

from flask import Flask
from flask import request, redirect, url_for, render_template, flash, json

# These environment variables are configured in app.yaml.
CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')

app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
data=''

def connect_to_cloudsql():
    # When deployed to App Engine, the `SERVER_SOFTWARE` environment variable
    # will be set to 'Google App Engine/version'.
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        # Connect using the unix socket located at
        # /cloudsql/cloudsql-connection-name.
        cloudsql_unix_socket = os.path.join(
            '/cloudsql', CLOUDSQL_CONNECTION_NAME)

        db = MySQLdb.connect(
            unix_socket=cloudsql_unix_socket,
            user=CLOUDSQL_USER,
            passwd=CLOUDSQL_PASSWORD)

    # If the unix socket is unavailable, then try to connect using TCP. This
    # will work if you're running a local MySQL server or using the Cloud SQL
    # proxy, for example:
    #
    #   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
    #
    else:
        db = MySQLdb.connect(
            host='127.0.0.1', user=CLOUDSQL_USER, passwd=CLOUDSQL_PASSWORD)

    return db

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    print 'asdfasdf'
    global data
    return 'Hello GCP!'+'\n'+data

@app.route('/poles', methods=['GET'])
def get_poles():
    """Return a friendly HTTP greeting."""
    ids = request.args.get('pole_ids', '')
    ids = ids.replace('[', '')
    ids = ids.replace(']', '')
    print ids
    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute('USE drone')
    sql = 'SELECT pole_id, longitude, latitude, created_at FROM poles p1 WHERE pole_id IN (' + ids + ') AND created_at=(SELECT MAX(created_at) FROM poles p2 WHERE p1.pole_id = p2.pole_id)'
    cursor.execute(sql)
    data = {}
    for r in cursor.fetchall():
        data[r[0]]={'longitude': r[1], 'latitude': r[2], 'created_at': r[3]}
    return json.dumps({ "status": "OK", "poles": data})

@app.route('/api/test', methods=['POST'])
def insert_pole():
    if request.headers['Content-Type'] != 'application/json':
        data='Content-Type is not application/json'
        print request.headers['Content-Type']
        return json.dumps({ "status": "error"}), 400
    requestJson = request.json
    sql = 'INSERT INTO drone.poles (pole_id, longitude, latitude) VALUE (3,12.341,56.785)'
    # sql = 'INSERT INTO drone.poles (pole_id, longitude, latitude) VALUE (' + str(requestJson['pole_id']) + ',' + requestJson['longitude'] + ',' + requestJson['latitude'] + ')'
    print sql
    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute('USE drone')
    cursor.execute(sql)
    return json.dumps({ "status": "OK"})

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
