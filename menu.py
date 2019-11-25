#! /usr/bin/env python3.5
import pymysql
from app import app
#from flask_table import Table
#from db_config import mysql
from flask import flash, render_template, request, redirect, session
from wtforms import Form, TextField, SelectField, TextAreaField, validators, StringField, SubmitField
from tables import *
from forms import *

operation="Menus"
icon="sun"
#
# Show default menus page, general statistics
@app.route('/menus')
def show_menus():
	if check_login() is not True:
		return redirect("/")
	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT * FROM menu ORDER BY name ASC")
		rows = cursor.fetchall()
		table = Menu(rows)
		table.border = True
		total_menus = len(rows)
		return render_template('main.html', table=table, total_count=total_menus, add_operation_url='.add_new_menu_view',icon=icon,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

#
# Display and process new menu
@app.route('/menu/new', methods=['GET','POST'])
def add_new_menu_view():
	icon=None
	if request.method == 'POST':
		try:
			_name = request.form['name']
			_location = request.form['location']
			_start = request.form['start']
			_end = request.form['end']
			_light_hours = request.form['light_hours']

			sql = "INSERT INTO menu(name,location,start,end,light_hours) VALUES(%s, %s, %s, %s, %s)"
			data = (_name, _location, _start, _end, _light_hours)
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute(sql, data)
			conn.commit()
			icon="sun"
			flash('New Menu Added!','info')
		except Exception as e:
			icon="remove"
			flash('New Menu Not Added!','error')
			print(e)

	try:
		form = MenuForm(request.form)
	except Exception as e:
		print(e)
	title_verb = "Add"
	return render_template('operation_form.html', formpage='add_menu.html', title_verb=title_verb, form=form, icon=icon, row=None,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))

@app.route('/menu/edit/<int:id>', methods=['POST','GET'])
def edit_menu(id):
	icon=None
	if request.method == "POST":
		_name = request.form['name']
		_location = request.form['location']
		_start = request.form['start']
		_end = request.form['end']
		_light_hours = request.form['light_hours']
		_id = request.form['id']

		sql = "UPDATE menu SET name=%s, location=%s, start=%s, end=%s, light_hours=%s WHERE id=%s"
		data = (_name, _location, _start, _end, _light_hours, _id)
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute(sql, data)
		conn.commit()
		icon="sun"
		flash('menu updated successfully!','info')

	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT * FROM menu WHERE id=%s", id)
		row = cursor.fetchone()

		if row:
			form = MenuForm(request.form)
			form.name.default=row['name']
			form.location.default=row['location']
			form.start.default=row['start']
			form.end.default=row['end']
			form.light_hours.default=row['light_hours']
			form.process()
		else:
			return 'Error loading #{id}'.format(id=id)
		title_verb = "Edit"

		return render_template('operation_form.html', formpage='add_menu.html', title_verb=title_verb, icon=icon, form=form, row=row,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

@app.route('/menu/delete/<int:id>')
def delete_menu(id):
	try:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM menu WHERE id=%s", (id,))
		conn.commit()
		flash('Menu deleted successfully!','info')
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()
	return redirect("/menus")
