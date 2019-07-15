import os, time, mysql.connector
from flask import Flask, Response, request, jsonify, abort, make_response
app = Flask(__name__)

OK = 200
CREATED = 201
BAD_REQUEST = 400
NOT_FOUND = 404
SERVER_ERROR = 500

MYSQL_HOST = os.environ['MYSQL_HOST']
MYSQL_USER = 'root'
MYSQL_PASS = os.environ['MYSQL_ROOT_PASSWORD']
MYSQL_DB = os.environ['MYSQL_DATABASE']
MYSQL_AUTH = 'mysql_native_password'

def db_connect():
    
    try:

        db = mysql.connector.connect(
            host = MYSQL_HOST,
            user = MYSQL_USER,
            password = MYSQL_PASS,
            database = MYSQL_DB,
            auth_plugin= MYSQL_AUTH
        )
        cursor = db.cursor(buffered=True)
        return cursor , db

    except: abort(SERVER_ERROR)

def in_database(cursor, db, device_id):

    try:
        cursor.execute((
            "SELECT * "
            "FROM devices " 
            "WHERE device_id = %s" 
        ) % str(device_id))

    except: 
        db.close()
        abort(501)
    
    return False if cursor.rowcount < 1 else True

def clear_database(cursor, db):

    try:
        cursor.execute("DELETE FROM devices")
        cursor.execute("DELETE FROM device_data")
        db.commit()
    except:
        db.rollback()
        db.close()
        abort(SERVER_ERROR)

def get_device_list(cursor, db):

    try:
        cursor.execute((
            "SELECT * "
            "FROM devices "
            "ORDER BY device_id"
        ))
        
        results = cursor.fetchall()
        devices = []
        for row in results: devices.append(row[0])

    except:
        db.close()
        abort(SERVER_ERROR)

    return devices

def get_device(cursor, db, device_id):

    try:
        
        cursor.execute((
            "SELECT * "
            "FROM devices "
            "WHERE device_id = %s"
        ) % str(device_id))

        results = cursor.fetchall()
        device_row = results[0]

    except:
        db.close
        abort(SERVER_ERROR)

    return device_row

def create_device(cursor, db, device_id, frequency, config):

    try:
        cursor.execute((
            "INSERT INTO devices (device_id, frequency, config) "
            "VALUES (%s, %s, '%s')"
        ) % (device_id, frequency, config))

        db.commit()

    except Exception as e:
        db.rollback()
        db.close()
        return str(e)
        abort(SERVER_ERROR)

def update_device(cursor, db, device_id, frequency, config):

    try:

        cursor.execute((
            "UPDATE devices "
            "SET frequency = %s, config = '%s' "
            "WHERE device_id = %s"
        ) % (str(frequency), str(config), str(device_id)))

        db.commit()

    except Exception as e:

        db.rollback()
        db.close()
        return str(e)
        abort(SERVER_ERROR)

def get_data(cursor, db, device_id): 

    try:
        cursor.execute((
            "SELECT * "
            "FROM device_data "
            "WHERE device_id = %s "
            "ORDER BY time_stamp" 
        ) % device_id)

        results = cursor.fetchall()
        data = []
        for row in results: data.append(row)

    except:
        db.close
        abort(SERVER_ERROR)

    return data

def create_data(cursor, db, device_id, ch0, ch1, ch2, ch3): 
    try:
        timestamp = int(time.time())

        cursor.execute((
            "INSERT INTO device_data "
            "(device_id, time_stamp, chan_0, chan_1, chan_2, chan_3) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        ), (str(device_id), timestamp, ch0, ch1, ch2, ch3))

        cursor.execute((
            "UPDATE devices "
            "SET time_stamp = %s, chan_0 = %s, chan_1 = %s, chan_2 = %s, chan_3 = %s "
            "WHERE device_id = %s"
        ), (timestamp, ch0, ch1, ch2, ch3, str(device_id)))

        db.commit()

    except:
        db.rollback()
        db.close()
        abort(BAD_REQUEST)

@app.route("/")
def test_connection(): return make_response("[Pynet] - Connection Successful", OK)

@app.route("/devices", methods=["GET", "POST"])
def devices():
    
    if request.method == "GET":

        cursor, db = db_connect()
        devices = get_device_list(cursor, db)
        return_message = {'response': devices}

        db.close()
        return make_response(jsonify(return_message),OK)

    elif request.method == "POST":

        cursor, db = db_connect()
        clear_database(cursor, db)

        db.close
        return make_response('',OK)

@app.route("/devices/<int:device_id>", methods=["GET", "POST"])
def devices_device(device_id):

    if request.method == "GET":

        cursor, db = db_connect()
        if not in_database(cursor, db, device_id): abort(NOT_FOUND)
        device_row = get_device(cursor, db, device_id)
        return_message = {'response': device_row}

        db.close
        return make_response(jsonify(return_message), OK)

    elif request.method == "POST":

        cursor, db = db_connect()
        default_frequency = 60
        default_config = ""

        if in_database(cursor, db, device_id): 

            if 'frequency' not in request.args or 'config' not in request.args:
                current_device = get_device(cursor, db, device_id)
                default_frequency = current_device[1]
                default_config = current_device[2] 
            
            frequency = request.args.get('frequency', default_frequency)
            config = request.args.get('config', default_config)
            update_device(cursor, db, device_id, frequency, config)

        else:
            frequency = request.args.get('frequency', default_frequency)
            config = request.args.get('config', default_config)
            create_device(cursor, db, device_id, frequency, config)

        db.close()
        return make_response('',CREATED)

@app.route("/devices/<int:device_id>/data", methods=["GET", "POST"])
def devices_device_data(device_id):

    if request.method == "GET":

        cursor, db = db_connect()
        if not in_database(cursor, db, device_id): abort(NOT_FOUND)
        data = get_data(cursor, db, device_id)
        return_message = {'response': data}
        db.close()
        return make_response(jsonify(return_message), OK)

    elif request.method == "POST":

        cursor, db = db_connect()
        if not in_database(cursor, db, device_id): abort(NOT_FOUND)

        try: ch0 = str(float(request.args['ch0']))
        except: ch0 = None
        try: ch1 = str(float(request.args['ch1']))
        except: ch1 = None
        try: ch2 = str(float(request.args['ch2']))
        except: ch2 = None
        try: ch3 = str(float(request.args['ch3']))
        except: ch3 = None

        create_data(cursor, db, device_id, ch0, ch1, ch2, ch3)
        return make_response('', CREATED)


