#! /usr/bin/env python3.5
import pymysql
from app import app
#from flask_table import Table
#from db_config import mysql
from flask import flash, render_template, request, redirect, session
from wtforms import Form, TextField, SelectField, TextAreaField, validators, StringField, SubmitField
from tables import *
from forms import *

operation="Environments"
icon="spa"
#
# Show default environments page, general statistics
@app.route('/environments')
def show_environments():
	if check_login() is not True:
		return redirect("/")
	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT * FROM environment ORDER BY name ASC")
		rows = cursor.fetchall()
		table = Environment(rows)
		table.border = True
		total_environments = len(rows)
		return render_template('main.html', table=table, total_count=total_environments, add_operation_url='.add_new_environment_view',icon=icon,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

#
# Display and process new environment
@app.route('/environment/new', methods=['GET','POST'])
def add_new_environment_view():
	if check_login() is not True:
		return redirect("/")
	icon=None
	if request.method == 'POST':
		try:
			_name = request.form['name']
			_location = request.form['location']
			_light_hours = request.form['light_hours']
			_temperature = request.form['temperature']
			_humidity = request.form['humidity']
			_light_source = request.form['light_source']
			_lumens = request.form['lumens']
			_wattage = request.form['wattage']
			_grow_area = request.form['grow_area']
			_containment = request.form['containment']
			_max_plants = request.form['max_plants']

			sql = "INSERT INTO environment(name,location,light_hours,temperature,humidity,light_source,lumens,wattage,grow_area,containment,max_plants) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
			data = (_name, _location, _light_hours,_temperature,_humidity,_light_source,_lumens,_wattage,_grow_area,_containment,_max_plants)
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute(sql, data)
			conn.commit()
			icon="spa"
			flash('New Environment Added','info')
		except Exception as e:
			icon="remove"
			flash('New environment Not Added!','error')
			print(e)

	try:
		form = EnvironmentForm(request.form)
	except Exception as e:
		print(e)
	title_verb = "Add"
	return render_template('operation_form.html', formpage='add_environment.html', title_verb=title_verb, form=form, icon=icon, row=None,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))

@app.route('/environment/log/new', methods=['POST','GET'])
def add_new_log_environment():
	if check_login() is not True:
		return redirect("/")
	icon=None
	if request.method == 'POST':
		try:
			_environment_ID = request.form['environment_ID']
			_logdate = request.form['logdate']
			_temperature = request.form['temperature']
			_humidity = request.form['humidity']
			_light = request.form['light']
			_dark = request.form['dark']
			_lux = request.form['lux']

			sql = "INSERT INTO envlog(environment_ID,logdate,temperature,humidity,light,dark,lux) VALUES(%s, %s, %s, %s, %s, %s, %s)"
			data = (_environment_ID,_logdate,_temperature,_humidity,_light,_dark,_lux)
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute(sql, data)
			conn.commit()
		except Exception as e:
			print(e)

@app.route('/environment/log/edit/<int:id>', methods=['POST','GET'])
def edit_log_environment(id):
	if check_login() is not True:
		return redirect("/")
	icon=None
	if request.method == 'POST':
		try:
			_is = request.form['id']
			_environment_ID = request.form['environment_ID']
			_logdate = request.form['logdate']
			_temperature = request.form['temperature']
			_humidity = request.form['humidity']
			_light = request.form['light']
			_dark = request.form['dark']
			_lux = request.form['lux']
		except Exception as e:
			print(e)

@app.route('/environment/edit/<int:id>', methods=['POST','GET'])
def edit_environment(id):
	if check_login() is not True:
		return redirect("/")
	icon=None
	if request.method == "POST":
		try:
			_name = request.form['name']
			_location = request.form['location']
			_light_hours = request.form['light_hours']
			_temperature = request.form['temperature']
			_humidity = request.form['humidity']
			_light_source = request.form['light_source']
			_lumens = request.form['lumens']
			_wattage = request.form['wattage']
			_grow_area = request.form['grow_area']
			_containment = request.form['containment']
			_max_plants = request.form['max_plants']
			_id = request.form['id']

			sql = "UPDATE environment SET name=%s, location=%s, light_hours=%s,temperature=%s,humidity=%s,light_source=%s,lumens=%s,wattage=%s,grow_area=%s,containment=%s,max_plants=%s WHERE id=%s"
			data = (_name, _location, _light_hours,_temperature,_humidity,_light_source,_lumens,_wattage,_grow_area,_containment,_max_plants, _id)
			print(sql)
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute(sql, data)
			conn.commit()
			icon="spa"
			flash('Environment updated successfully!','info')
		except Exception as e:
			print(e)
			flash('Error updating environment','error')

	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT * FROM environment WHERE id=%s", id)
		row = cursor.fetchone()

		if row:
			form = EnvironmentForm(request.form)
			form.name.default = row['name']
			form.location.default = row['location']
			form.light_hours.default = row['light_hours']
			form.temperature.default = row['temperature']
			form.humidity.default = row['humidity']
			form.light_source.default = row['light_source']
			form.lumens.default = row['lumens']
			form.wattage.default = row['wattage']
			form.grow_area.default = row['grow_area']
			form.containment.default = row['containment']
			form.max_plants.default = row['max_plants']
			form.process()
		else:
			return 'Error loading #{id}'.format(id=id)
		title_verb = "Edit"
		icon="spa"
		return render_template('operation_form.html', formpage='add_environment.html', title_verb=title_verb, icon=icon, form=form, row=row,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

@app.route('/environment/delete/<int:id>')
def delete_environment(id):
	try:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM environment WHERE id=%s", (id,))
		conn.commit()
		flash('Environment deleted successfully!','info')
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()
	return redirect("/environments")
