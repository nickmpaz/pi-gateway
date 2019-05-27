# ============================================================================================================================================================= 
#
# METHOD & ENDPOINT                 DESCRIPTION                         FORM        MODULE
#
# GET   /                           test connection                     NA          test_connection()
#        
# POST  /purge                      clear entire db                     devices     purge()
#    
# GET   /devices                    get list of devices                 NA          list_devices()
#
# GET   /devices/{dev_id}           get device last data point          NA          device_status()
# POST  /devices/{dev_id}           create a device                     config      create_device()
#
# GET   /devices/{dev_id}/config    get device config                   NA          get_config()
# POST  /devices/{dev_id}/config    update device config                config      set_config
#
# GET   /devices/{dev_id}/data      get data for device                 NA          get_data()
# POST  /devices/{dev_id}/data      create data point                   channels    set_data()
#
# ============================================================================================================================================================= 

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

CONNECTION_SUCCESSFUL = "[Pynet] - Connection Successful"
SELECT_DEVICE = "SELECT * FROM devices WHERE device_id = %s"
SELECT_DEVICES = "SELECT * FROM devices ORDER BY device_id"
SELECT_DATA = "SELECT * FROM device_data WHERE device_id = %s ORDER BY time_stamp"
INSERT_DEVICE = "INSERT INTO devices (device_id, frequency) VALUES (%s, %s)"
INSERT_DATA = "INSERT INTO device_data \
               (device_id, time_stamp, chan_0, chan_1, chan_2, chan_3) \
               VALUES (%s, %s, %s, %s, %s, %s)" 
DELETE_ALL_DEVICES = "DELETE FROM devices"
DELETE_ALL_DATA = "DELETE FROM device_data"
DELETE_DEVICE = "DELETE FROM devices WHERE device_id = %s"
DELETE_DATA = "DELETE FROM device_data WHERE device_id = %s"
UPDATE_CONFIG = "UPDATE devices SET frequency = %s WHERE device_id = %s"
UPDATE_STATUS = "UPDATE devices SET \
                 time_stamp = %s, chan_0 = %s, chan_1 = %s, chan_2 = %s, chan_3 = %s \
                 WHERE device_id = %s"

# ============================================================================================================================================================= 

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
    except:
        abort(SERVER_ERROR)

def in_database(device_id, cursor):
    cursor.execute(SELECT_DEVICE % str(device_id))
    if cursor.rowcount < 1: return False
    return True

@app.route("/")
def test_connection():
    return make_response(CONNECTION_SUCCESSFUL, OK)

@app.route("/purge", methods=["POST"])
def purge_database():
    # clear database
    if request.method == "POST":
        if 'device' in request.form.keys():
            cursor, db = db_connect()
            try:
                device = str(int(request.form['device']))
                cursor.execute(DELETE_DEVICE % device)
                db.commit()
                cursor.execute(DELETE_DATA % device)
                db.commit()
                db.close()
            except Exception as e:
                db.rollback()
                db.close()
                return str(e)
                #abort(SERVER_ERROR)

            return make_response('',OK)
        else:
            cursor, db = db_connect()
            try:
                cursor.execute(DELETE_ALL_DEVICES)
                db.commit()
                cursor.execute(DELETE_ALL_DATA)
                db.commit()
                db.close()
            except:
                db.rollback()
                db.close()
                abort(SERVER_ERROR)

            return make_response('',OK)

@app.route("/devices", methods=["GET"])
def index():
    # return list of devcices
    if request.method == "GET":
        cursor, db = db_connect()
        try:
            cursor.execute(SELECT_DEVICES)
            results = cursor.fetchall()
            return_message = {'response': []}
            for row in results:
                return_message['response'].append(row[0])
            db.close()
        except:
            db.close()
            abort(SERVER_ERROR)

        return make_response(jsonify(return_message),OK)

@app.route("/devices/<int:device_id>", methods=["GET", "POST"])
def devices(device_id):
    # return device status
    if request.method == "GET":
        cursor, db = db_connect()
        # ensure device exists in database and handle values
        try:
            device_id = str(device_id)
            if not in_database(device_id, cursor):
                raise Exception
        except:
            abort(NOT_FOUND)

        try:
            cursor.execute(SELECT_DEVICE % device_id)
            results = cursor.fetchall()
            data_point = results[0][2:]
            return_message = {'response': data_point}
            db.close()

        except:
            db.close
            abort(SERVER_ERROR)

        return make_response(jsonify(return_message), OK)
    # create a device
    elif request.method == "POST":
        cursor, db = db_connect()
        # verify request and handle values
        try:
            device_id = str(device_id)
            frequency = str(int(request.form['frequency']))
            if in_database(device_id, cursor):
                raise Exception
        except:
            abort(BAD_REQUEST)
        # execute insertion
        try:
            val = (device_id, frequency)
            cursor.execute(INSERT_DEVICE, val)
            db.commit()
            db.close()
        except:
            db.rollback()
            db.close()
            abort(SERVER_ERROR)

        return make_response('',CREATED)


@app.route("/devices/<int:device_id>/config", methods=["GET", "POST"])
def config(device_id):
    # return device config
    if request.method == "GET":
        cursor, db = db_connect()
        # ensure device exists in database and handle values
        try:
            device_id = str(device_id)
            if not in_database(device_id, cursor):
                raise Exception
        except:
            abort(NOT_FOUND)

        try:
            cursor.execute(SELECT_DEVICE % device_id)
            results = cursor.fetchall()
            data_point = results[0][:2]
            return_message = {'response': data_point}
            db.close()

        except:
            db.close
            abort(SERVER_ERROR)

        return make_response(jsonify(return_message), OK)
    # set device config
    elif request.method == "POST":
        cursor, db = db_connect()
        try:
            device_id = str(device_id)
            frequency = str(int(request.form['frequency']))
            if not in_database(device_id, cursor):
                raise Exception
        except:
            abort(BAD_REQUEST)
        try:
            val = (frequency, device_id)
            cursor.execute( UPDATE_CONFIG, val)
            db.commit()
            db.close()

        except:
            db.rollback()
            db.close
            abort(SERVER_ERROR)

        return make_response('',OK)


@app.route("/devices/<int:device_id>/data", methods=["GET", "POST"])
def data(device_id):
    # get all rows of data for device
    if request.method == "GET":
        cursor, db = db_connect()
        # ensure device exists in database and handle values
        try:
            device_id = str(device_id)
            if not in_database(device_id, cursor):
                raise Exception
        except:
            abort(NOT_FOUND)

        try:
            cursor.execute(SELECT_DATA % device_id)
            results = cursor.fetchall()
            return_message = {'response': []}
            for row in results:
                return_message['response'].append(row)
            db.close()

        except:
            db.close
            abort(SERVER_ERROR)

        return make_response(jsonify(return_message), OK)
    # insert a data row and update device status
    elif request.method == "POST":
        cursor, db = db_connect()
        # ensure device exists in database and handle values
        try:
            device_id = str(device_id)
            timestamp = str(int(time.time()))
            if not in_database(device_id, cursor):
                raise Exception
        except:
            abort(NOT_FOUND)

        try: ch0 = str(float(request.form['ch0']))
        except: ch0 = None
        try: ch1 = str(float(request.form['ch1']))
        except: ch1 = None
        try: ch2 = str(float(request.form['ch2']))
        except: ch2 = None
        try: ch3 = str(float(request.form['ch3']))
        except: ch3 = None

        try:
            val = (device_id, timestamp, ch0, ch1, ch2, ch3)
            cursor.execute(INSERT_DATA, val)
            db.commit()
            val = (timestamp, ch0, ch1, ch2, ch3, device_id)
            cursor.execute(UPDATE_STATUS, val)
            db.commit()
            db.close()
        except:
            db.rollback()
            db.close()
            abort(BAD_REQUEST)

        return make_response('', CREATED)

