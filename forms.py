#! /usr/bin/env python3.5
from app import app
from wtforms import Form, HiddenField, TextField, PasswordField, SelectField, TextAreaField, DateField, BooleanField, FloatField, IntegerField, validators, StringField, SubmitField, FileField
from pytz import all_timezones
from flask import jsonify
import pymysql
from gardentrax import get_strain_types
try:
    from db_config import mysql
except ImportError as e:
	pass

def get_db_list(**kwargs):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id,name FROM %s" % kwargs['table'])
        rows = cursor.fetchall()
        if kwargs['format'] == 'json':
                return jsonify(rows)
        else:
            optval = 0 if kwargs['idval'] == True else "Unknown"
            opttxt = kwargs['idtxt'] if kwargs['idtxt'] is not None else "Unknown"
            results = [(optval,opttxt)]
            for row in rows:
            	optval = row['id'] if kwargs['idval'] == True else row['name']
            	results.append((str(optval),row['name']))
        return results
    except Exception as e:
        print(e)

class InstallForm(Form):
    dbhost = TextField("Database Host")
    dbuname = TextField("Database Username")
    dbpass = TextField("Database Password")
    dbname = TextField("Database Name")

class LoginForm(Form):
    username = TextField("Username")
    password = PasswordField("Password")


class SettingsForm(Form):
    timezone_choices = []
    for tz in all_timezones:
        timezone_choices.append((tz,tz))
    username = TextField('Username')
    password = TextField('Password')
    port = IntegerField("Port Number")
    timezone = SelectField('Timezone',choices=timezone_choices)
    latitude = TextField('Latitude')
    longitude = TextField('Longitude')
    temp_units = SelectField('Temperature', choices=[('C','Celsius'),('F','Farenheit'),('K','Kelvin')])
    length_units = SelectField('Length',choices=[('cm','Centimeters'),('in','Inches')])
    volume_units = SelectField('Volume',choices=[('ml','Mililiters'),('oz','Ounces')])
    date_format = SelectField('Date Format', choices=[('yyyy-mm-dd','yyyy-mm-dd'),('mm/dd/yyyy','mm/dd/yyyy')])
    allow_plantlog_edit = BooleanField("Allow Plant Log Edits?")
    allow_envlog_edit = BooleanField("Allow Environment Log Edits?")

class PlantForm(Form):
    strains = get_db_list(table='strain',idval = True,idtxt = "Unknown",format=False)
    cycles = get_db_list(table='cycle',idval = True,idtxt = "Unknown",format=False)
    name = TextField('Name', validators=[validators.required()])
    gender = SelectField('Gender',choices=[('Unknown','Unknown'),('Male','Male'),('Female','Female'),('Hermaphrodite','Hermaphrodite')])
    strain = SelectField('Strain',choices=strains)
    cycle = SelectField('Cycle',choices=cycles)
    grow_medium = TextField('Grow Medium')
    source = SelectField('Source',choices=[('seed','Seed'),('clone','Clone'),('other','Other')])
    photo = FileField('Photo')

class CycleForm(Form):
    name = TextField('Name', validators=[validators.required()])
    start = DateField('Start', validators=[validators.required()])
    end = DateField('End')
    location = TextField('Location')
    light_hours = TextField('Light Hours')

class StrainForm(Form):
    name = TextField('Name', validators=[validators.required()])
    type = SelectField('Type',choices=get_strain_types())
    notes = TextAreaField('Notes')

class EnvironmentForm(Form):
    name = TextField('Name', validators=[validators.required()])
    location = SelectField('Location',choices=[('indoor','Indoor'),('outdoor','Outdoor')])
    light_hours = TextField('Light Hours')
    temperature = TextField('Temperature')
    humidity = TextField('Humidity')
    light_source = TextField('Light Source')
    lumens = TextField('Lumens')
    wattage = TextField('Wattage')
    grow_area = TextField('Grow area')
    containment = TextField('Containment')
    max_plants = TextField('Maximum Number of Plants')

class NutrientForm(Form):
    name = TextField('Name', validators=[validators.required()])
    organic = SelectField('Organic',choices=[('yes','Yes'),('no','No')])
    nitrogen = TextField('Nitrogen')
    phosphorus = TextField('Phosphorus')
    potassium = TextField('Potassium')
    trace = TextField('Trace')

class RepellentForm(Form):
    name = TextField('Name', validators=[validators.required()])
    type = SelectField('Type',choices=[('organic','Organic'),('chemical','Chemical'),('other','Other')])
    target = TextField('Target')
    price = TextField('Price')
    purchase_location = TextField('Purchase Location')
    notes = TextAreaField('Notes')

class LogForm(Form):
    environment = get_db_list(table = 'environment',idval = True,idtxt = "None",format=False)
    nutrient = get_db_list(table = 'nutrient',idval = True,idtxt = "None",format=False)
    repellent = get_db_list(table = 'repellent',idval = True,idtxt = "None",format=False)
    id = HiddenField()
    logdate = DateField('Date')
    plant_ID = HiddenField()
    water = BooleanField('Water')
    height = IntegerField('Height')
    span = IntegerField('Span')
    nodes = IntegerField('Nodes')
    trim = SelectField('Trim',choices=[('','None'),('Topping','Topping'),('Fimming','Fimming'),('ICE','ICE'),('Lollipop','Lollipop'),('Clone','Clone')])
    #lux = IntegerField('Lux')
    #temperature = IntegerField('Temperature')
    soil_pH = IntegerField('pH')
    transplant = BooleanField('Transplant')
    stage = SelectField('Stage',choices=[('None','None'),('Germination','Germination'),('Seedling','Seedling'),('Vegetation','Vegetation'),('Pre-Flowering','Pre-Flowering'),('Flowering','Flowering'),('Harvest','Harvest'),('Archive','Archive'),('Dead','Dead')])
    environment_ID = SelectField('Environment',choices=environment, coerce=int)
    nutrient_ID = SelectField('Nutrient',choices=nutrient, coerce=int)
    repellent_ID = SelectField('Repellent',choices=repellent, coerce=int)
    notes = TextAreaField('Notes')

class EnvironmentLogForm(Form):
    environment_ID = HiddenField()
    logdate = DateField('Date')
    temperature = IntegerField('Temperature')
    humidity = IntegerField('Humidity')
    light = IntegerField('Light')
    dark = IntegerField('Dark')
    lux = IntegerField('Lux')

class ApiForm(Form):
    api_key = TextField('API KEY')
