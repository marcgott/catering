#! /usr/bin/env python3.5
import pymysql
from app import app
from flask import flash, jsonify,render_template, request, redirect,session, abort
from forms import *
from tables import *
from werkzeug import generate_password_hash

app.config['DO_INSTALL'] = True
operation="Install"
@app.route('/install')
def do_install():
    dbcredform = InstallForm(request.form)
    settingsform = SettingsForm(request.form)
    return render_template('install.html', is_install=True, settingsform=settingsform, dbcredform=dbcredform,program_name=app.program_name,operation=operation)

@app.route('/install/check_db', methods=['POST'])
def do_install_checkdb():
    try:
        dbcred = request.form
        connection = pymysql.connect(host=dbcred['dbhost'],user=dbcred['dbuname'],password=dbcred['dbpass'],db=dbcred['dbname'],cursorclass=pymysql.cursors.DictCursor)
        return jsonify({"success":connection.db.decode('utf-8')})
    except pymysql.err.OperationalError as e:
        return jsonify(e.args)
    except pymysql.err.InternalError as e:
        return jsonify(e.args)

@app.route('/install/settings', methods=['POST'])
def do_install_settings():
    try:
        settings = request.form
        connection = pymysql.connect(host=settings['dbhost'],user=settings['dbuname'],password=settings['dbpass'],db=settings['dbname'],cursorclass=pymysql.cursors.DictCursor)
        stmts = parse_sql('gardentrax.sql')
        with connection.cursor() as cursor:
            for stmt in stmts:
                cursor.execute(stmt)
            connection.commit()

        #install sql
        #INSERT INTO settings()
        _username = request.form['username']
        _password = request.form['password']
        _port = request.form['port']
        _date_format = request.form['date_format']
        _timezone = request.form['timezone']
        _temp_units = request.form['temp_units']
        _length_units = request.form['length_units']
        _volume_units = request.form['volume_units']
        _latitude = request.form['latitude']
        _longitude = request.form['longitude']
        _allow_orders_edit = "True" if 'allow_orders_edit' in request.form else ""
        _allow_envlog_edit = "True" if 'allow_envlog_edit' in request.form else ""
        settings_sql = "INSERT INTO `options` (`option_key`, `option_value`) VALUES('date_format', %s),('timezone', %s),('temp_units', %s),('length_units', %s),('volume_units', %s),('username', %s),('password', %s),('latitude', %s),('longitude', %s),('allow_orders_edit', %s),('allow_envlog_edit', %s);"
        data = (_date_format,_timezone,_temp_units,_length_units,_volume_units,_username,_password,_latitude, _longitude, _allow_envlog_edit, _allow_orders_edit)
        with connection.cursor() as cursor:
            cursor.execute(settings_sql,data)
            connection.commit()
        #with(open db_config.py)
        api_key = generate_password_hash("".join(_username+settings['dbhost']))
        with open('db_config.py','w') as dbc:
            dbc.write("from app import app\nfrom flaskext.mysql import MySQL\nmysql = MySQL()\napp.config['MYSQL_DATABASE_USER'] = '%s'\napp.config['MYSQL_DATABASE_PASSWORD'] = '%s'\napp.config['MYSQL_DATABASE_DB'] = '%s'\napp.config['MYSQL_DATABASE_HOST'] = '%s'\napp.config['API_KEY'] = '%s'\napp.config['APP_PORT'] = '%s'\nmysql.init_app(app)" % (settings['dbuname'], settings['dbpass'], settings['dbname'],settings['dbhost'],api_key[-32:-8:2],_port  ) )
        dbc.close()
        app.config['DO_INSTALL'] = False
        #return redirect("/reload")
        return jsonify({"success":connection.db.decode('utf-8')})
    except pymysql.err.OperationalError as e:
        return jsonify(e.args)

to_reload = False

@app.route('/reload')
def reload():
    global to_reload
    to_reload = True
    return app

class AppReloader(object):
    def __init__(self, create_app):
        self.create_app = create_app
        self.app = create_app()

    def get_application(self):
        global to_reload
        if to_reload:
            self.app = self.create_app()
            to_reload = False

        return self.app

    def __call__(self, environ, start_response):
        app = self.get_application()
        return app(environ, start_response)

###

def parse_sql(filename):
    data = open(filename, 'r').readlines()
    stmts = []
    DELIMITER = ';'
    stmt = ''

    for lineno, line in enumerate(data):
        if not line.strip():
            continue

        if line.startswith('--'):
            continue

        if 'DELIMITER' in line:
            DELIMITER = line.split()[1]
            continue

        if (DELIMITER not in line):
            stmt += line.replace(DELIMITER, ';')
            continue

        if stmt:
            stmt += line
            stmts.append(stmt.strip())
            stmt = ''
        else:
            stmts.append(line.strip())
    return stmts
