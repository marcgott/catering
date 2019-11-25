#! /usr/bin/env python3.5

import pymysql
from app import app
from flask import flash, render_template, request, redirect, session
from wtforms import Form, TextField, SelectField, TextAreaField, validators, StringField, SubmitField
from tables import *
from forms import *

icon="clipboard-check"
operation="order"

@app.route('/order')
def show_order():
	if check_login() is not True:
		return redirect("/")
	try:
		offset = 0
		if request.args.get('offset') is not None:
			offset = 0 + int(request.args.get('offset'))
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		sql = "SELECT `order`.*, customer.name as customer_name, nutrient.name as nutrient_name, product.name as product_name, repellent.name as repellent_name FROM `order` LEFT JOIN customer ON customer.id = `order`.customer_ID LEFT JOIN nutrient ON nutrient.id = `order`.nutrient_ID LEFT JOIN product ON product.id = `order`.product_ID LEFT JOIN repellent ON repellent.id = `order`.repellent_ID ORDER BY `order`.orderdate DESC, ts DESC LIMIT %d,40" % int(offset)
		cursor.execute(sql)
		rows = cursor.fetchall()
		#get_settings()
		table = Orders(rows)
		table.border = True
		table.customer_name.show=True
		if isinstance( app.settings["allow_orders_edit"],(bool) ):
			table.edit.show=True
			table.delete.show=True
		else:
			table.edit.show=False
			table.delete.show=False

		cursor = conn.cursor(pymysql.cursors.DictCursor)
		sql = "SELECT COUNT(*) AS ordercount FROM `order`"
		cursor.execute(sql)
		rowcount = cursor.fetchone()
		returned_rows = len(rows)
		return render_template('orders.html', offset=int(offset), table=table, icon=icon, total_orders=rowcount['ordercount'],returned_rows=returned_rows,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

@app.route('/order/print', methods=['GET'])
def add_print_order_view():
	if check_login() is not True:
		return redirect("/")
	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT id as customer_ID,name FROM customer  WHERE current_stage <> 'Archive' AND current_stage <> 'Dead' ORDER BY CAST(name AS unsigned)")
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
			printrow['transcustomer']= ''
			printrow['lux']= ''
			printrow['soil_pH']= ''
			printrow['trim']= ''
			printrow['notes']= ''
			tablerows.append(printrow)
		table = Printorder(tablerows)
		table.border = True
	except Exception as e:
		print(e)
	title_verb = "Print"
	icon="clipboard-check"
	return render_template('print_order.html', title_verb=title_verb, table=table, icon=icon, rows=rows,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))

#
# Display and process new order
@app.route('/order/new', methods=['GET','POST'])
def add_new_order_view():
	if check_login() is not True:
		return redirect("/")
	icon=None
	if request.method == 'POST':
		try:
			_water = 1 if 'water' in request.form else 0
			_transcustomer = 1 if 'transcustomer' in request.form else 0
			_customer_ID = request.form['customer_ID']
			_height = request.form['height']
			_span = request.form['span']
			_nodes = request.form['nodes']
			_product_ID = request.form['product_ID']
			_nutrient_ID = request.form['nutrient_ID']
			_repellent_ID = request.form['repellent_ID']
			_stage = request.form['stage']
			_soil_pH = request.form['soil_pH']
			_orderdate = request.form['orderdate']
			_trim = request.form['trim']
			_notes = request.form['notes']

			sql = "INSERT INTO order(customer_ID, water, height, span, nodes, product_ID, nutrient_ID, repellent_ID, stage, trim, transcustomer, notes, orderdate,  soil_pH ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
			data = (_customer_ID, _water, _height, _span, _nodes, _product_ID, _nutrient_ID, _repellent_ID, _stage, _trim, _transcustomer, _notes, _orderdate, _soil_pH)
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute(sql, data)
			conn.commit()

			sql = "UPDATE customer set current_stage=%s , current_product=%s, current_nodes=%s WHERE id=%s"
			data = (_stage,_product_ID, _nodes, _customer_ID)
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute(sql, data)
			conn.commit()

			icon="clipboard-check"
			flash('New order Added!','info')
		except Exception as e:
			icon="remove"
			flash('New order Not Added','error')
			print(e)

	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT customer.id as customer_ID,customer.name AS name, product.light_hours as light_hours FROM customer LEFT JOIN product ON customer.current_product = product.id WHERE customer.current_stage <> 'Archive' AND customer.current_stage <> 'Dead' ORDER BY CAST(customer.name AS unsigned)")
		rows = cursor.fetchall()

		form = OrderForm(request.form)

	except Exception as e:
		print(e)
	title_verb = "Add"
	icon="clipboard-check"
	icons = get_icons()
	return render_template('operation_form.html', formpage='add_order.html', action=request.path, title_verb=title_verb, form=form, icon=icon, icons=icons, rows=rows,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))

@app.route('/order/edit/<int:id>', methods=['POST','GET'])
def edit_order(id):
	icon=None
	if request.method == "POST":
		_water = 1 if 'water' in request.form else 0
		_transcustomer = 1 if 'transcustomer' in request.form else 0
		_customer_ID = request.form['customer_ID']
		_height = request.form['height']
		_span = request.form['span']
		_nodes = request.form['nodes']
		_product_ID = request.form['product_ID']
		_nutrient_ID = request.form['nutrient_ID']
		_repellent_ID = request.form['repellent_ID']
		_stage = request.form['stage']
		_soil_pH = request.form['soil_pH']
		_orderdate = request.form['orderdate']
		_trim = request.form['trim']
		_notes = request.form['notes']
		_id = request.form['id']

		sql = "UPDATE `order` SET customer_ID=%s, water=%s, height=%s, span=%s, nodes=%s, product_ID=%s, nutrient_ID=%s, repellent_ID=%s, stage=%s, trim=%s, transcustomer=%s, notes=%s, orderdate=%s, soil_pH=%s WHERE id=%s"
		data = (_customer_ID, _water, _height, _span, _nodes, _product_ID, _nutrient_ID, _repellent_ID, _stage, _trim, _transcustomer, _notes, _orderdate, _soil_pH, _id)
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute(sql, data)
		conn.commit()

		sql = "UPDATE customer set current_stage=%s , current_product=%s, current_nodes=%s WHERE id=%s"
		data = (_stage,_product_ID, _nodes, _customer_ID)
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute(sql, data)
		conn.commit()

		icon="clipboard-check"
		flash('order updated successfully!','info')

	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT `order`.*, customer.name as name FROM `order` LEFT JOIN customer ON customer.id=`order`.customer_ID WHERE `order`.id=%s LIMIT 1", id)
		row = cursor.fetchone()

		if row:
			form = orderForm(request.form)
			form.id.default = row['id']
			form.orderdate.default = row['orderdate'] if row['orderdate']!='' else ''
			form.water.default = True if row['water'] > 0 else 0
			form.transcustomer.default = True if row['transcustomer'] > 0 else 0
			form.span.default = row['span'] if row['span'] > 0 else ''
			form.nodes.default = row['nodes'] if row['nodes'] > 0 else ''
			form.height.default = row['height'] if row['height'] > 0 else ''
			form.stage.default = row['stage'] if row['stage'] != '' else ''
			form.soil_pH.default = row['soil_pH'] if row['soil_pH'] > 0 else ''
			form.product_ID.default = row['product_ID'] if row['product_ID'] != '' else ''
			form.repellent_ID.default = row['repellent_ID'] if row['repellent_ID'] != '' else ''
			form.nutrient_ID.default = row['nutrient_ID'] if row['nutrient_ID'] != '' else ''
			form.notes.default = row['notes'] if row['notes'] !='' else ''
			form.process()
		else:
			return 'Error loading #{id}'.format(id=id)
		title_verb = "Edit"
		icon="clipboard-check"
		icons = get_icons()
		return render_template('operation_form.html', formpage='add_customerorder.html', action=request.path, title_verb=title_verb, icon=icon, icons=icons, form=form, rows=[row], rowid=row['id'],operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

@app.route('/order/delete/<int:id>')
def delete_order(id):
	try:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM `order` WHERE id=%s", (id,))
		conn.commit()
		flash('order deleted successfully!','info')

	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()
		return redirect("/order")
