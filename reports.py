#! /usr/bin/env python3.5
import pymysql
from app import app
from gardentrax import *
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import *
from matplotlib.dates import DateFormatter
import numpy as np
import seaborn as sns
import base64
import calendar
from datetime import date,datetime
from io import BytesIO
#from db_config import mysql
from flask import session, redirect

operation="Reports"

@app.route('/reports')
def show_reports():
    if not session.get('logged_in'):
        return redirect("/")
    try:
        option = get_settings()
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        comparison_chart = {}
        # Height Comparison
        sql = "select customer.name, customer.id, MAX(log.height) as measure, MAX(log.span) as span from log INNER JOIN customer on customer.id=log.customer_ID WHERE customer.current_stage NOT IN ('Archive','Dead') GROUP BY customer_ID ORDER BY measure,span"
        cursor.execute(sql)
        conn.commit()
        data = cursor.fetchall()

        if not all(data):
            chart = get_comparison_chart(data,"Height",option["length_units"])
            comparison_chart['height_comparison'] = chart.decode('utf8')
        else:
            comparison_chart['height_comparison'] = get_photo_base64('data_not_available.png')

        sql = "select customer.name, customer.id, MAX(log.nodes) as measure from log INNER JOIN customer on customer.id=log.customer_ID WHERE log.nodes > 0 AND customer.current_stage NOT IN ('Archive','Dead')GROUP BY customer_ID  ORDER BY measure"
        cursor.execute(sql)
        conn.commit()
        data = cursor.fetchall()

        if not all(data):
            chart = get_comparison_chart(data,"Nodes","Number of Nodes")
            comparison_chart['node_comparison'] = chart.decode('utf8')
        else:
            comparison_chart['node_comparison'] = get_photo_base64('data_not_available.png')

        sql = "select customer.name, customer.id, COUNT(log.transcustomer) as measure from log INNER JOIN customer on customer.id=log.customer_ID WHERE log.transcustomer > 0 AND customer.current_stage NOT IN ('Archive','Dead') GROUP BY customer_ID ORDER BY measure"
        cursor.execute(sql)
        conn.commit()
        data = cursor.fetchall()
        if not all(data):
            chart = get_comparison_chart(data,"Transcustomers","Number of Transcustomers")
            comparison_chart['transcustomers'] = chart.decode('utf8')
        else:
            comparison_chart['transcustomers'] = get_photo_base64('data_not_available.png')  
        return render_template("reports.html",comparison_chart=comparison_chart,icon=get_icons(),option=option,operation=operation,program_name=app.program_name,is_login=session.get('logged_in'))
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
