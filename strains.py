#! /usr/bin/env python3.5
import pymysql
from app import app
#from flask_table import Table
#from db_config import mysql
from flask import flash, render_template, request, redirect, session
from wtforms import Form, TextField, SelectField, TextAreaField, validators, StringField, SubmitField
from tables import *
from forms import *

operation="Strains"
icon="dna"
#
# Show default strains page, general statistics
@app.route('/strains')
def show_strains():
	if check_login() is not True:
		return redirect("/")
	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT * FROM strain ORDER BY name ASC")
		rows = cursor.fetchall()
		table = Strain(rows)
		table.border = True
		total_strains = len(rows)
		return render_template('main.html', table=table, total_count=total_strains, add_operation_url='.add_new_strain_view',icon=icon,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

#
# Display and process new strain
@app.route('/strain/new', methods=['GET','POST'])
def add_new_strain_view():
	icon=None
	if request.method == 'POST':
		try:
			_name = request.form['name']
			_type = request.form['type']
			_notes = request.form['notes']

			sql = "INSERT INTO strain(name,type,notes) VALUES(%s, %s, %s)"
			data = (_name, _type, _notes)
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute(sql, data)
			conn.commit()
			icon="dna"
			flash('New Strain Added!','info')
		except Exception as e:
			icon="remove"
			flash('New strain Not Added!','error')
			print(e)

	try:
		form = StrainForm(request.form)
	except Exception as e:
		print(e)
	title_verb = "Add"
	return render_template('operation_form.html', formpage='add_strain.html', title_verb=title_verb, form=form, icon=icon, row=None,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))

@app.route('/strain/edit/<int:id>', methods=['POST','GET'])
def edit_strain(id):
	icon=None
	if request.method == "POST":
		_name = request.form['name']
		_type = request.form['type']
		_notes = request.form['notes']
		_id = request.form['id']

		sql = "UPDATE strain SET name=%s, type=%s, notes=%s WHERE id=%s"
		data = (_name, _type, _notes, _id)
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute(sql, data)
		conn.commit()
		icon="dna"
		flash('Strain updated successfully!','info')

	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT * FROM strain WHERE id=%s", id)
		row = cursor.fetchone()

		if row:
			form = StrainForm(request.form)
			form.name.default=row['name']
			form.type.default=row['type']
			form.notes.default=row['notes']
			form.process()
		else:
			return 'Error loading #{id}'.format(id=id)
		title_verb = "Edit"

		return render_template('operation_form.html', formpage='add_strain.html', title_verb=title_verb, icon=icon, form=form, row=row,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

@app.route('/strain/delete/<int:id>')
def delete_strain(id):
	try:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM strain WHERE id=%s", (id,))
		conn.commit()
		icon="dna"
		flash('Strain deleted successfully!','info')
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()
	return redirect('/strains')
