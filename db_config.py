#! /usr/bin/env python3.5
from app import app
from flaskext.mysql import MySQL

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'cateringpos'
app.config['MYSQL_DATABASE_PASSWORD'] = 'cateringpos'
app.config['MYSQL_DATABASE_DB'] = 'cateringpos'
app.config['MYSQL_DATABASE_HOST'] = '10.100.102.100'
app.config['API_KEY'] = '835e94d006b2'
app.config['APP_PORT'] = '8600'
mysql.init_app(app)
