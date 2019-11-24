#! /usr/bin/env python3.5
import pymysql
from app import app
#from db_config import mysql
from flask import jsonify, flash, request, session, abort
from pytz import all_timezones
from forms import *
from tables import *
from plants import *
from cycles import *
from strains import *
from environments import *
from nutrients import *
from repellents import *
from log import *

program_name="PepperTrax"

@app.route('/api/login', methods=['POST'])
def do_api_login():
	option = get_settings();

	print("API LOGIN CALLED")
	datastr = request.data.decode('utf-8')
	_json = json.loads(datastr)
	api_key = _json['api_key']
	if _json['api_key'] == app.config['API_KEY']:
		resp = jsonify({"api_authentcation":"success"})
		session['logged_in'] = True
		resp.status_code = 200
		return resp
	else:
		resp = jsonify({"message":"bad_api_key"})
		resp.status_code = 500
		print(resp)
		return resp


@app.route('/api/plants', methods=['GET'])
def do_api_get_log():
	option = get_settings();
	print("API LOG CALLED")
	if True:
		try:
			conn = mysql.connect()
			cursor = conn.cursor(pymysql.cursors.DictCursor)
			cursor.execute("SELECT id,name FROM plant")
			rows = cursor.fetchall()
			#print(rows)
			resp = jsonify(rows)
			resp.status_code = 200
			#print(resp)
			return resp
		except Exception as e:
			print(e)
		finally:
			cursor.close()
			conn.close()

	else:
		resp = jsonify({"message":"get log error"})
		resp.status_code = 500
		print(resp)
		return resp

@app.route('/api/plantlog/new/<int:id>', methods=['POST'])
def do_api_post_plant_log(id):
	try:
		option = get_settings();
		print("API PLANT NEW ",id," CALLED")
		print(request.json)
		#print(request.args)
		#print(request.form)
		keys = []
		values = []


		for k,v in request.json:
			keys.append(str("`%s`") % k)
			values.append(str('"%s"') % v)
		sql = "INSERT INTO log(%s) VALUES(%s)" % (','.join(keys),','.join(values) )
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute(sql)
		conn.commit()
		resp = jsonify({"message":"success"})
		resp.status_code = 200
		return resp
	except Exception as e:
		print(e)


@app.route('/api/plant/view/<int:id>', methods=['GET'])
def do_api_get_plant_view(id):
	option = get_settings();
	print("API PLANT VIEW ",id," CALLED")
	if True:
		try:
			conn = mysql.connect()
			cursor = conn.cursor(pymysql.cursors.DictCursor)
			cursor.execute("SELECT * FROM plant WHERE id=%s",(id))
			row = cursor.fetchone()
			resp = jsonify(row)
			resp.status_code = 200
			return resp
		except Exception as e:
			print(e)
		finally:
			cursor.close()
			conn.close()

	else:
		resp = jsonify({"message":"get log error"})
		resp.status_code = 500
		print(resp)
		return resp

@app.route('/api/list/<string:listname>', methods=['GET'])
def do_api_get_list(listname):
	print("API LIST %s CALLED" % listname)
	list = get_db_list(table = listname,idval = True,idtxt = "None",format='json')
	return list
