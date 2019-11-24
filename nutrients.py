#! /usr/bin/env python3.5
import pymysql
from app import app
#from flask_table import Table
#from db_config import mysql
from flask import flash, render_template, request, redirect, session
from wtforms import Form, TextField, SelectField, TextAreaField, validators, StringField, SubmitField
from tables import *
from forms import *

operation="Nutrients"
icon="tint"
#
# Show default nutrients page, general statistics
@app.route('/nutrients')
def show_nutrients():
	if check_login() is not True:
		return redirect("/")
	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT * FROM nutrient ORDER BY name ASC")
		rows = cursor.fetchall()
		table = Nutrient(rows)
		table.border = True
		total_nutrients = len(rows)
		return render_template('main.html', table=table, total_count=total_nutrients, add_operation_url='.add_new_nutrient_view',icon=icon,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

#
# Display and process new nutrient
@app.route('/nutrient/new', methods=['GET','POST'])
def add_new_nutrient_view():
	icon=None
	if request.method == 'POST':
		try:
			_name = request.form['name']
			_organic = request.form['organic']
			_nitrogen = request.form['nitrogen']
			_phosphorus = request.form['phosphorus']
			_potassium = request.form['potassium']
			_trace = request.form['trace']

			sql = "INSERT INTO nutrient(name,organic,nitrogen,phosphorus,potassium,trace) VALUES(%s, %s, %s,%s, %s, %s)"
			data = (_name, _organic, _nitrogen, _phosphorus, _potassium, _trace)
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute(sql, data)
			conn.commit()
			icon="tint"
			flash('New nutrient Added!','info')
		except Exception as e:
			icon="remove"
			flash('New nutrient Not Added!','error')
			print(e)

	try:
		form = NutrientForm(request.form)
	except Exception as e:
		print(e)
	title_verb = "Add"
	return render_template('operation_form.html', formpage='add_nutrient.html',title_verb=title_verb, form=form, icon=icon, row=None, operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))

@app.route('/nutrient/edit/<int:id>', methods=['POST','GET'])
def edit_nutrient(id):
	icon=None
	if request.method == "POST":
		_name = request.form['name']
		_organic = request.form['organic']
		_nitrogen = request.form['nitrogen']
		_phosphorus = request.form['phosphorus']
		_potassium = request.form['potassium']
		_trace = request.form['trace']
		_id = request.form['id']

		sql = "UPDATE nutrient SET name=%s, organic=%s, nitrogen=%s, phosphorus=%s, potassium=%s, trace=%s WHERE id=%s"
		data = (_name, _organic, _nitrogen, _phosphorus, _potassium, _trace, _id)
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute(sql, data)
		conn.commit()
		icon="tint"
		flash('nutrient updated successfully!','info')

	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT * FROM nutrient WHERE id=%s", id)
		row = cursor.fetchone()

		if row:
			form = NutrientForm(request.form)
			form.name.default=row['name']
			form.organic.default=row['organic']
			form.nitrogen.default=row['nitrogen']
			form.phosphorus.default=row['phosphorus']
			form.potassium.default=row['potassium']
			form.trace.default=row['trace']
			form.process()
		else:
			return 'Error loading #{id}'.format(id=id)
		title_verb = "Edit"

		return render_template('operation_form.html', formpage='add_nutrient.html', title_verb=title_verb, icon=icon, form=form, row=row, operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

@app.route('/nutrient/delete/<int:id>')
def delete_nutrient(id):
	try:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM nutrient WHERE id=%s", (id,))
		conn.commit()
		icon="tint"
		flash('nutrient deleted successfully!','info')
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()
	return redirect('/nutrients')
