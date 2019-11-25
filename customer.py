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
operation="Customer"
icon="leaf"

#
# Show default customers page, general statistics
@app.route('/customers')
def show_customers():
	if check_login() is not True:
		return redirect("/")
	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT customer.id, customer.name as name, customer.gender, strain.name as strain_name, menu.name as menu_name,product.name as current_product, customer.source, customer.current_stage, customer.photo FROM customer LEFT JOIN strain on strain.id=customer.strain_ID LEFT JOIN menu ON menu.id=customer.menu_ID LEFT JOIN product ON product.id=customer.current_product ORDER BY customer.name ASC")
		rows = cursor.fetchall()
		total_customers = len(rows)

		sql = "SELECT current_stage as name,count(current_stage) as count FROM customer GROUP BY current_stage"
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute(sql)
		stagecount = cursor.fetchall()
		table = Customer(rows)
		table.border = True
		return render_template('main.html', table=table, total_count=total_customers, add_operation_url='.add_new_customer_view',icon=icon,stagecount=stagecount,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()


#
# Display and process new customer
@app.route('/customer/new', methods=['GET','POST'])
def add_new_customer_view():
	if check_login() is not True:
		return redirect("/")
	icon=None
	if request.method == 'POST':
		try:
			_name = request.form['name']
			_gender = request.form['gender']
			_strain_ID = request.form['strain']
			_menu_ID = request.form['menu']
			_source = request.form['source']
			_grow_medium = request.form['grow_medium']
			_photo = ''

			if request.files["photo"]:
				photo_data = request.files["photo"]
				photo_data.save(secure_filename(photo_data.filename))
				photo_data.seek(0)  # rewind to beginning of file
				photo = base64.b64encode(photo_data.getvalue()).decode('utf8')
				_photo = json.dumps({"mimetype":photo_data.mimetype, "data":photo})

			sql = "INSERT INTO customer(name,gender,strain_ID,menu_ID,source,grow_medium,photo) VALUES(%s, %s, %s, %s, %s, %s, %s)"
			data = (_name, _gender, _strain_ID, _menu_ID, _source, _grow_medium, _photo)
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute(sql, data)
			conn.commit()
			icon="leaf"
			flash('New Customer Added!','info')
		except Exception as e:
			icon="remove"
			flash('New Customer Not Added!','error')
			print(e)

	try:
		form = CustomerForm(request.form)
	except Exception as e:
		print(e)
	title_verb = "Add"
	return render_template('operation_form.html', formpage='add_customer.html', title_verb=title_verb, form=form, icon=icon, row=None, operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))

#
# Edit
############################
@app.route('/customer/edit/<int:id>', methods=['POST','GET'])
def edit_customer(id):
	if check_login() is not True:
		return redirect("/")
	icon=None
	if request.method == "POST":
		#form = CustomerForm(request.form)
		_name = request.form['name']
		_gender = request.form['gender']
		_strain = request.form['strain']
		_menu = request.form['menu']
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

		sql = "UPDATE customer SET name=%s, gender=%s, strain_ID=%s, menu_ID=%s, source=%s, grow_medium=%s, photo=%s WHERE id=%s"
		data = (_name, _gender, _strain, _menu, _source, _grow_medium, _photo, _id)
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute(sql, data)
		conn.commit()
		icon="leaf"
		flash('Customer updated successfully!','info')

	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT * FROM customer WHERE id=%s", id)
		row = cursor.fetchone()
		if row:
			form = CustomerForm(request.form)
			form.name.default=row['name']
			form.gender.default=row['gender']
			form.source.default=row['source']
			form.grow_medium.default=row['grow_medium']
			form.strain.default=row['strain_ID']
			form.menu.default=row['menu_ID']
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
		return render_template('operation_form.html', formpage='add_customer.html', title_verb=title_verb, icon=icon, form=form, row=row, operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

#
# delete
###################################
@app.route('/customer/delete/<int:id>')
def delete_customer(id):
	try:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM customer WHERE id=%s", (id,))
		conn.commit()
		flash('Customer deleted successfully!','info')
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()
	return redirect("/customers")

#
# View
###################################
@app.route('/customer/view/<int:id>')
def view_customer(id):
	if check_login() is not True:
		return redirect("/")
	title_verb="View"
	try:
		option = get_settings()
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT customer.id, customer.name as name, customer.gender, strain.name as strain_name, menu.name as menu_name, customer.source, customer.grow_medium, product.name as current_product, customer.current_stage as current_stage, max(`order`.height) as current_height, max(`order`.span) as current_span FROM customer LEFT JOIN strain on strain.id=customer.strain_ID LEFT JOIN menu ON menu.id=customer.menu_ID LEFT JOIN product ON product.id=customer.current_product LEFT JOIN `order` ON customer.id=`order`.customer_ID WHERE customer.id=%s", (id,))
		conn.commit()
		row = cursor.fetchone()
		row['current_span'] = 0 if row['current_span'] is None else row['current_span']
		row['current_height'] = 0 if row['current_height'] is None else row['current_height']

		cursor.execute("SELECT MIN( orderdate ) as logdate, stage	FROM `order` WHERE customer_ID =%s	GROUP BY stage ORDER BY orderdate", (id,))
		conn.commit()
		stages = cursor.fetchall()

		cursor.execute("SELECT l.orderdate,l.span,l.height,l.trim, min(md.orderdate) as mindate FROM `order` l LEFT JOIN `order` md ON l.customer_ID=md.customer_ID WHERE (l.height<>0 OR l.span<>0 OR l.trim<>'') AND l.customer_ID=%s GROUP BY l.orderdate ORDER BY l.orderdate ASC", (id,))
		conn.commit()
		chart_rows = cursor.fetchall()

		cursor.execute("SELECT DAY(orderdate) as d, MONTH(orderdate) as m FROM `order` WHERE Water=1 AND customer_ID=%s ORDER BY orderdate ASC", (id,))
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
				nextdate = stages[i+1]['orderdate']

			stagetotal = nextdate - stage['orderdate']
			stage['stagetotal'] = stagetotal.days

	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

	return render_template("customers.html",water_chart=water_chart,growth_chart=growth_chart,icon=get_icons(),option=option,row=row,rows=stages,operation=operation,title_verb=title_verb,height_rank=height_rank['rank']+1,span_rank=span_rank['rank']+1,is_login=session.get('logged_in'))

@app.route('/customer/logs/<int:id>')
def show_customer_log(id):
	if check_login() is not True:
		return redirect("/")
	try:
		offset = 0
		if request.args.get('offset') is not None:
			offset = 0 + int(request.args.get('offset'))
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		sql = "SELECT `order`.*, customer.name as customer_name, nutrient.name as nutrient_name, product.name as product_name, repellent.name as repellent_name FROM `order` LEFT JOIN customer ON customer.id = `order`.customer_ID LEFT JOIN nutrient ON nutrient.id = `order`.nutrient_ID LEFT JOIN product ON product.id = `order`.product_ID LEFT JOIN repellent ON repellent.id = `order`.repellent_ID WHERE customer_ID=%d ORDER BY orderdate DESC, ts DESC LIMIT %d,50" % (id,int(offset))
		cursor.execute(sql)
		rows = cursor.fetchall()
		table = CustomerLog(rows)
		table.border = True
		table.customer_name.show=False
		if isinstance( app.settings["allow_customerlog_edit"],(bool) ):
			table.edit.show=True
			table.delete.show=True
		else:
			table.edit.show=False
			table.delete.show=False
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		sql = "SELECT COUNT(*)as ordercount from `order` where customer_ID=%d" % id
		cursor.execute(sql)
		rowcount = cursor.fetchone()
		returned_rows = len(rows)
		return render_template('orders.html', offset=offset,table=table, icon=icon, customer_name=rows[0]['customer_name'], total_logs=rowcount['ordercount'],returned_rows=returned_rows,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()
