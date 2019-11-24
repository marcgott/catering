#! /usr/bin/env python3.5
import os
import pymysql
from app import app
from io import BytesIO
import base64
import json
#from db_config import mysql
from werkzeug import secure_filename
from flask import flash, render_template, request, redirect, session,url_for
from wtforms import Form, TextField, SelectField, TextAreaField, validators, StringField, SubmitField
from tables import *
from forms import *
from gardentrax import get_measurement_plot,get_photo_base64
operation="Plants"
icon="leaf"

#
# Show default plants page, general statistics
@app.route('/plants')
def show_plants():
	if check_login() is not True:
		return redirect("/")
	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT plant.id, plant.name as name, plant.gender, strain.name as strain_name, cycle.name as cycle_name,environment.name as current_environment, plant.source, plant.current_stage, plant.photo FROM plant LEFT JOIN strain on strain.id=plant.strain_ID LEFT JOIN cycle ON cycle.id=plant.cycle_ID LEFT JOIN environment ON environment.id=plant.current_environment ORDER BY plant.name ASC")
		rows = cursor.fetchall()
		total_plants = len(rows)

		sql = "SELECT current_stage as name,count(current_stage) as count FROM plant GROUP BY current_stage"
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute(sql)
		stagecount = cursor.fetchall()
		table = Plant(rows)
		table.border = True
		return render_template('main.html', table=table, total_count=total_plants, add_operation_url='.add_new_plant_view',icon=icon,stagecount=stagecount,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()


#
# Display and process new plant
@app.route('/plant/new', methods=['GET','POST'])
def add_new_plant_view():
	if check_login() is not True:
		return redirect("/")
	icon=None
	if request.method == 'POST':
		try:
			_name = request.form['name']
			_gender = request.form['gender']
			_strain_ID = request.form['strain']
			_cycle_ID = request.form['cycle']
			_source = request.form['source']
			_grow_medium = request.form['grow_medium']
			_photo = ''

			if request.files["photo"]:
				photo_data = request.files["photo"]
				photo_data.save(secure_filename(photo_data.filename))
				photo_data.seek(0)  # rewind to beginning of file
				photo = base64.b64encode(photo_data.getvalue()).decode('utf8')
				_photo = json.dumps({"mimetype":photo_data.mimetype, "data":photo})

			sql = "INSERT INTO plant(name,gender,strain_ID,cycle_ID,source,grow_medium,photo) VALUES(%s, %s, %s, %s, %s, %s, %s)"
			data = (_name, _gender, _strain_ID, _cycle_ID, _source, _grow_medium, _photo)
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute(sql, data)
			conn.commit()
			icon="leaf"
			flash('New Plant Added!','info')
		except Exception as e:
			icon="remove"
			flash('New Plant Not Added!','error')
			print(e)

	try:
		form = PlantForm(request.form)
	except Exception as e:
		print(e)
	title_verb = "Add"
	return render_template('operation_form.html', formpage='add_plant.html', title_verb=title_verb, form=form, icon=icon, row=None, operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))

#
# Edit
############################
@app.route('/plant/edit/<int:id>', methods=['POST','GET'])
def edit_plant(id):
	if check_login() is not True:
		return redirect("/")
	icon=None
	if request.method == "POST":
		#form = PlantForm(request.form)
		_name = request.form['name']
		_gender = request.form['gender']
		_strain = request.form['strain']
		_cycle = request.form['cycle']
		_source = request.form['source']
		_grow_medium = request.form['grow_medium']
		_id = request.form['id']
		_photo = ''

		if request.files["photo"]:
			photo_data = request.files["photo"]
			photo_data.save(secure_filename(photo_data.filename))
			photo_data.seek(0)  # rewind to beginning of file
			photo = base64.b64encode(photo_data.getvalue()).decode('utf8')
			_photo = json.dumps({"mimetype":photo_data.mimetype, "data":photo})

		sql = "UPDATE plant SET name=%s, gender=%s, strain_ID=%s, cycle_ID=%s, source=%s, grow_medium=%s, photo=%s WHERE id=%s"
		data = (_name, _gender, _strain, _cycle, _source, _grow_medium, _photo, _id)
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute(sql, data)
		conn.commit()
		icon="leaf"
		flash('Plant updated successfully!','info')

	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT * FROM plant WHERE id=%s", id)
		row = cursor.fetchone()
		if row:
			form = PlantForm(request.form)
			form.name.default=row['name']
			form.gender.default=row['gender']
			form.source.default=row['source']
			form.grow_medium.default=row['grow_medium']
			form.strain.default=row['strain_ID']
			form.cycle.default=row['cycle_ID']
			form.photo.default=row['photo']
			form.process()
			#photodata = json.loads(row['photo'])
			try:
				row['photo'] = json.loads(row['photo'])
			except Exception as e:
				#APP_PATH = os.path.dirname(__file__)
				#with open(os.path.join(APP_PATH,'static/images/photo_default.png'), 'rb') as photo_data:
					#photo = base64.b64encode(photo_data.read())
					photo = get_photo_base64('photo_default.png')
					#photo = photo.decode('utf8')
					row['photo'] = {'mimetype':'image/png','data':photo}

		else:
			return 'Error loading #{id}'.format(id=id)

		title_verb = "Edit"
		return render_template('operation_form.html', formpage='add_plant.html', title_verb=title_verb, icon=icon, form=form, row=row, operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

#
# delete
###################################
@app.route('/plant/delete/<int:id>')
def delete_plant(id):
	try:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM plant WHERE id=%s", (id,))
		conn.commit()
		flash('Plant deleted successfully!','info')
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()
	return redirect("/plants")

#
# View
###################################
@app.route('/plant/view/<int:id>')
def view_plant(id):
	if check_login() is not True:
		return redirect("/")
	title_verb="View"
	try:
		option = get_settings()
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT plant.id, plant.name as name, plant.gender, strain.name as strain_name, cycle.name as cycle_name, plant.source, plant.grow_medium, environment.name as current_environment, plant.current_stage as current_stage, max(log.height) as current_height, max(log.span) as current_span FROM plant LEFT JOIN strain on strain.id=plant.strain_ID LEFT JOIN cycle ON cycle.id=plant.cycle_ID LEFT JOIN environment ON environment.id=plant.current_environment LEFT JOIN log ON plant.id=log.plant_ID WHERE plant.id=%s", (id,))
		conn.commit()
		row = cursor.fetchone()
		row['current_span'] = 0 if row['current_span'] is None else row['current_span']
		row['current_height'] = 0 if row['current_height'] is None else row['current_height']

		cursor.execute("SELECT MIN( logdate ) as logdate, stage	FROM log WHERE plant_ID =%s	GROUP BY stage ORDER BY logdate", (id,))
		conn.commit()
		stages = cursor.fetchall()

		cursor.execute("SELECT l.logdate,l.span,l.height,l.trim, min(md.logdate) as mindate FROM log l LEFT JOIN log md ON l.plant_ID=md.plant_ID WHERE (l.height<>0 OR l.span<>0 OR l.trim<>'') AND l.plant_ID=%s GROUP BY l.logdate ORDER BY l.logdate ASC", (id,))
		conn.commit()
		chart_rows = cursor.fetchall()

		cursor.execute("SELECT DAY(logdate) as d, MONTH(logdate) as m FROM log WHERE Water=1 AND plant_ID=%s ORDER BY logdate ASC", (id,))
		conn.commit()
		water_dates = cursor.fetchall()

		water_chart=None
		growth_chart=None

		print( len(chart_rows))
		if len(chart_rows) > 0:
			growth_chart = get_measurement_plot(chart_rows,row['name'],stages=stages)
			growth_chart = growth_chart.decode('utf8')

		if len(water_dates) > 0:
			water_chart = get_water_calendar(water_dates,row['name'])
			water_chart = water_chart.decode('utf8')

		height_rank = get_rank(row['id'],'height')
		span_rank = get_rank(row['id'],'span')

		for i,stage in enumerate(stages):
			if i+1 >= len(stages):
				nextdate = date.today()
			else:
				nextdate = stages[i+1]['logdate']

			stagetotal = nextdate - stage['logdate']
			stage['stagetotal'] = stagetotal.days

	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

	return render_template("plants.html",water_chart=water_chart,growth_chart=growth_chart,icon=get_icons(),option=option,row=row,rows=stages,operation=operation,title_verb=title_verb,height_rank=height_rank['rank']+1,span_rank=span_rank['rank']+1,is_login=session.get('logged_in'))

@app.route('/plant/logs/<int:id>')
def show_plant_log(id):
	if check_login() is not True:
		return redirect("/")
	try:
		offset = 0
		if request.args.get('offset') is not None:
			offset = 0 + int(request.args.get('offset'))
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		sql = "SELECT log.*, plant.name as plant_name, nutrient.name as nutrient_name, environment.name as environment_name, repellent.name as repellent_name FROM log LEFT JOIN plant ON plant.id = log.plant_ID LEFT JOIN nutrient ON nutrient.id = log.nutrient_ID LEFT JOIN environment ON environment.id = log.environment_ID LEFT JOIN repellent ON repellent.id = log.repellent_ID WHERE plant_ID=%d ORDER BY logdate DESC, ts DESC LIMIT %d,50" % (id,int(offset))
		cursor.execute(sql)
		rows = cursor.fetchall()
		table = PlantLog(rows)
		table.border = True
		table.plant_name.show=False
		if isinstance( app.settings["allow_plantlog_edit"],(bool) ):
			table.edit.show=True
			table.delete.show=True
		else:
			table.edit.show=False
			table.delete.show=False
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		sql = "SELECT COUNT(*)as logcount from log where plant_ID=%d" % id
		cursor.execute(sql)
		rowcount = cursor.fetchone()
		returned_rows = len(rows)
		return render_template('logs.html', offset=offset,table=table, icon=icon, plant_name=rows[0]['plant_name'], total_logs=rowcount['logcount'],returned_rows=returned_rows,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()
