#! /usr/bin/env python3.5

import pymysql
from app import app
#from flask_table import Table
#from db_config import mysql
from flask import flash, render_template, request, redirect, session
from wtforms import Form, TextField, SelectField, TextAreaField, validators, StringField, SubmitField
from tables import *
from forms import *

icon="clipboard-check"
operation="Log"

@app.route('/logs')
def show_logs():
	if check_login() is not True:
		return redirect("/")
	try:
		offset = 0
		if request.args.get('offset') is not None:
			offset = 0 + int(request.args.get('offset'))
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		sql = "SELECT log.*, plant.name as plant_name, nutrient.name as nutrient_name, environment.name as environment_name, repellent.name as repellent_name FROM log LEFT JOIN plant ON plant.id = log.plant_ID LEFT JOIN nutrient ON nutrient.id = log.nutrient_ID LEFT JOIN environment ON environment.id = log.environment_ID LEFT JOIN repellent ON repellent.id = log.repellent_ID ORDER BY logdate DESC, ts DESC LIMIT %d,40" % int(offset)
		cursor.execute(sql)
		rows = cursor.fetchall()
		#get_settings()
		table = PlantLog(rows)
		table.border = True
		table.plant_name.show=True
		if isinstance( app.settings["allow_plantlog_edit"],(bool) ):
			table.edit.show=True
			table.delete.show=True
		else:
			table.edit.show=False
			table.delete.show=False

		cursor = conn.cursor(pymysql.cursors.DictCursor)
		sql = "SELECT COUNT(*) AS logcount FROM log "
		cursor.execute(sql)
		rowcount = cursor.fetchone()
		returned_rows = len(rows)
		return render_template('logs.html', offset=int(offset), table=table, icon=icon, total_logs=rowcount['logcount'],returned_rows=returned_rows,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

@app.route('/log/print', methods=['GET'])
def add_print_log_view():
	if check_login() is not True:
		return redirect("/")
	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT id as plant_ID,name FROM plant  WHERE current_stage <> 'Archive' AND current_stage <> 'Dead' ORDER BY CAST(name AS unsigned)")
		rows = cursor.fetchall()
		tablerows = []
		option = get_settings()
		for row in rows:
			printrow = {}
			printrow['name'] = row['name']
			printrow['picture']= ''
			printrow['water']= ''+option['volume_units']
			printrow['nutrient']= ''
			printrow['height']= ''+option['length_units']
			printrow['span']= ''+option['length_units']
			printrow['nodes']= ''
			printrow['transplant']= ''
			printrow['lux']= ''
			printrow['soil_pH']= ''
			printrow['trim']= ''
			printrow['notes']= ''
			tablerows.append(printrow)
		table = PrintLog(tablerows)
		table.border = True
	except Exception as e:
		print(e)
	title_verb = "Print"
	icon="clipboard-check"
	return render_template('print_log.html', title_verb=title_verb, table=table, icon=icon, rows=rows,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))

#
# Display and process new log
@app.route('/log/new', methods=['GET','POST'])
def add_new_log_view():
	if check_login() is not True:
		return redirect("/")
	icon=None
	if request.method == 'POST':
		try:
			_water = 1 if 'water' in request.form else 0
			_transplant = 1 if 'transplant' in request.form else 0
			_plant_ID = request.form['plant_ID']
			_height = request.form['height']
			_span = request.form['span']
			_nodes = request.form['nodes']
			_environment_ID = request.form['environment_ID']
			_nutrient_ID = request.form['nutrient_ID']
			_repellent_ID = request.form['repellent_ID']
			_stage = request.form['stage']
			_soil_pH = request.form['soil_pH']
			_logdate = request.form['logdate']
			_trim = request.form['trim']
			_notes = request.form['notes']

			sql = "INSERT INTO log(plant_ID, water, height, span, nodes, environment_ID, nutrient_ID, repellent_ID, stage, trim, transplant, notes, logdate,  soil_pH ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
			data = (_plant_ID, _water, _height, _span, _nodes, _environment_ID, _nutrient_ID, _repellent_ID, _stage, _trim, _transplant, _notes, _logdate, _soil_pH)
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute(sql, data)
			conn.commit()

			sql = "UPDATE plant set current_stage=%s , current_environment=%s, current_nodes=%s WHERE id=%s"
			data = (_stage,_environment_ID, _nodes, _plant_ID)
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute(sql, data)
			conn.commit()

			icon="clipboard-check"
			flash('New Log Added!','info')
		except Exception as e:
			icon="remove"
			flash('New Log Not Added','error')
			print(e)

	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT plant.id as plant_ID,plant.name AS name, environment.light_hours as light_hours FROM plant LEFT JOIN environment ON plant.current_environment = environment.id WHERE plant.current_stage <> 'Archive' AND plant.current_stage <> 'Dead' ORDER BY CAST(plant.name AS unsigned)")
		rows = cursor.fetchall()

		form = LogForm(request.form)
		envform = EnvironmentLogForm(request.form)
		envform.light.default = session['daylight'] if session['daylight'] != 'unknown' else 0
		envform.light.default = rows[0]['light_hours'] if rows[0]['light_hours'] != 'unknown' else 0
		envform.dark.default = session['darkness'] if session['darkness'] != 'unknown' else 0
		envform.process()
	except Exception as e:
		print(e)
	title_verb = "Add"
	icon="clipboard-check"
	icons = get_icons()
	return render_template('operation_form.html', formpage='add_plantlog.html', action=request.path, title_verb=title_verb, form=form,envform=envform, icon=icon, icons=icons, rows=rows,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))

@app.route('/log/edit/<int:id>', methods=['POST','GET'])
def edit_log(id):
	icon=None
	if request.method == "POST":
		_water = 1 if 'water' in request.form else 0
		_transplant = 1 if 'transplant' in request.form else 0
		_plant_ID = request.form['plant_ID']
		_height = request.form['height']
		_span = request.form['span']
		_nodes = request.form['nodes']
		_environment_ID = request.form['environment_ID']
		_nutrient_ID = request.form['nutrient_ID']
		_repellent_ID = request.form['repellent_ID']
		_stage = request.form['stage']
		_soil_pH = request.form['soil_pH']
		_logdate = request.form['logdate']
		_trim = request.form['trim']
		_notes = request.form['notes']
		_id = request.form['id']

		sql = "UPDATE log SET plant_ID=%s, water=%s, height=%s, span=%s, nodes=%s, environment_ID=%s, nutrient_ID=%s, repellent_ID=%s, stage=%s, trim=%s, transplant=%s, notes=%s, logdate=%s, soil_pH=%s WHERE id=%s"
		data = (_plant_ID, _water, _height, _span, _nodes, _environment_ID, _nutrient_ID, _repellent_ID, _stage, _trim, _transplant, _notes, _logdate, _soil_pH, _id)
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute(sql, data)
		conn.commit()

		sql = "UPDATE plant set current_stage=%s , current_environment=%s, current_nodes=%s WHERE id=%s"
		data = (_stage,_environment_ID, _nodes, _plant_ID)
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute(sql, data)
		conn.commit()

		icon="clipboard-check"
		flash('Log updated successfully!','info')

	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT log.*, plant.name as name FROM log LEFT JOIN plant ON plant.id=log.plant_ID WHERE log.id=%s LIMIT 1", id)
		row = cursor.fetchone()

		if row:
			form = LogForm(request.form)
			form.id.default = row['id']
			form.logdate.default = row['logdate'] if row['logdate']!='' else ''
			form.water.default = True if row['water'] > 0 else 0
			form.transplant.default = True if row['transplant'] > 0 else 0
			form.span.default = row['span'] if row['span'] > 0 else ''
			form.nodes.default = row['nodes'] if row['nodes'] > 0 else ''
			form.height.default = row['height'] if row['height'] > 0 else ''
			form.stage.default = row['stage'] if row['stage'] != '' else ''
			form.soil_pH.default = row['soil_pH'] if row['soil_pH'] > 0 else ''
			form.environment_ID.default = row['environment_ID'] if row['environment_ID'] != '' else ''
			form.repellent_ID.default = row['repellent_ID'] if row['repellent_ID'] != '' else ''
			form.nutrient_ID.default = row['nutrient_ID'] if row['nutrient_ID'] != '' else ''
			form.notes.default = row['notes'] if row['notes'] !='' else ''
			form.process()
		else:
			return 'Error loading #{id}'.format(id=id)
		title_verb = "Edit"
		icon="clipboard-check"
		icons = get_icons()
		return render_template('operation_form.html', formpage='add_plantlog.html', action=request.path, title_verb=title_verb, icon=icon, icons=icons, form=form, rows=[row], rowid=row['id'],operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

@app.route('/log/delete/<int:id>')
def delete_log(id):
	try:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM log WHERE id=%s", (id,))
		conn.commit()
		flash('Log deleted successfully!','info')
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()
	return redirect("/logs")
