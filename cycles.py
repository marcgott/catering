#! /usr/bin/env python3.5
import pymysql
from app import app
#from flask_table import Table
#from db_config import mysql
from flask import flash, render_template, request, redirect, session
from wtforms import Form, TextField, SelectField, TextAreaField, validators, StringField, SubmitField
from tables import *
from forms import *

operation="Cycles"
icon="sun"
#
# Show default cycles page, general statistics
@app.route('/cycles')
def show_cycles():
	if check_login() is not True:
		return redirect("/")
	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT * FROM cycle ORDER BY name ASC")
		rows = cursor.fetchall()
		table = Cycle(rows)
		table.border = True
		total_cycles = len(rows)
		return render_template('main.html', table=table, total_count=total_cycles, add_operation_url='.add_new_cycle_view',icon=icon,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

#
# Display and process new cycle
@app.route('/cycle/new', methods=['GET','POST'])
def add_new_cycle_view():
	icon=None
	if request.method == 'POST':
		try:
			_name = request.form['name']
			_location = request.form['location']
			_start = request.form['start']
			_end = request.form['end']
			_light_hours = request.form['light_hours']

			sql = "INSERT INTO cycle(name,location,start,end,light_hours) VALUES(%s, %s, %s, %s, %s)"
			data = (_name, _location, _start, _end, _light_hours)
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute(sql, data)
			conn.commit()
			icon="sun"
			flash('New Cycle Added!','info')
		except Exception as e:
			icon="remove"
			flash('New Cycle Not Added!','error')
			print(e)

	try:
		form = CycleForm(request.form)
	except Exception as e:
		print(e)
	title_verb = "Add"
	return render_template('operation_form.html', formpage='add_cycle.html', title_verb=title_verb, form=form, icon=icon, row=None,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))

@app.route('/cycle/edit/<int:id>', methods=['POST','GET'])
def edit_cycle(id):
	icon=None
	if request.method == "POST":
		_name = request.form['name']
		_location = request.form['location']
		_start = request.form['start']
		_end = request.form['end']
		_light_hours = request.form['light_hours']
		_id = request.form['id']

		sql = "UPDATE cycle SET name=%s, location=%s, start=%s, end=%s, light_hours=%s WHERE id=%s"
		data = (_name, _location, _start, _end, _light_hours, _id)
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute(sql, data)
		conn.commit()
		icon="sun"
		flash('cycle updated successfully!','info')

	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT * FROM cycle WHERE id=%s", id)
		row = cursor.fetchone()

		if row:
			form = CycleForm(request.form)
			form.name.default=row['name']
			form.location.default=row['location']
			form.start.default=row['start']
			form.end.default=row['end']
			form.light_hours.default=row['light_hours']
			form.process()
		else:
			return 'Error loading #{id}'.format(id=id)
		title_verb = "Edit"

		return render_template('operation_form.html', formpage='add_cycle.html', title_verb=title_verb, icon=icon, form=form, row=row,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

@app.route('/cycle/delete/<int:id>')
def delete_cycle(id):
	try:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM cycle WHERE id=%s", (id,))
		conn.commit()
		flash('Cycle deleted successfully!','info')
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()
	return redirect("/cycles")
