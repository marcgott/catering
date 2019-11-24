#! /usr/bin/env python3.5
from app import app
from flask import Markup
from flask_table import Table, Col, LinkCol, ButtonCol, BoolCol, BoolNaCol, DateCol, DatetimeCol
from gardentrax import *

class AddIconCol(Col):
    def td_format(self, content):
        if content != '':
            icon = get_icons()
            return '<i class="fas fa-%s"></i>  %s' % (icon[content.lower()],content)
        return ''

class PlantLog(Table):
    table_id = 'daily_log'
    classes = ['main','chart','log']
    id = Col('id', show=False)
    plant_name = LinkCol('Plant Name', 'view_plant', url_kwargs=dict(id='plant_ID'),attr='plant_name')
    orderdate = DateCol('Order Date', date_format='short')
    stage = AddIconCol('Stage')
    water = BoolCol('Water',  yes_display='Yes', no_display='No')
    height = Col('Height')
    span = Col('Span')
    nodes = Col('Nodes')
    nutrient_name = Col('Nutrient')
    repellent_name = Col('Repellent')
    environment_name = Col('Environment')
    lux = Col('Lux',td_html_attrs={'class':'luxlevel'}, show=False)
    soil_pH = Col('Soil pH')
    trim = Col('Trim')
    transplant = BoolCol('Transplant',  yes_display='Yes', no_display='No')
    notes = Col('Notes')
    edit = LinkCol('Edit', 'edit_order', url_kwargs=dict(id='id'), show=False)
    delete = LinkCol('Delete', 'delete_order', url_kwargs=dict(id='id'), show=False)

class PrintLog(Table):
    table_id = 'print_log'
    name = Col('Plant Name',td_html_attrs={'class':'printname'})
    picture = Col('Photo', show=False)
    water = Col('H2O',td_html_attrs={'class':'printblank'})
    nutrient = Col('Nutr.')
    height = Col('Height',td_html_attrs={'class':'printblank'})
    span = Col('Span',td_html_attrs={'class':'printblank'})
    nodes = Col('Nodes',td_html_attrs={'class':'printblank'})
    transplant = Col('Repot')
    lux = Col('Lux', show=False)
    soil_pH = Col('pH')
    trim = Col('Trim')
    notes = Col('Notes',column_html_attrs={'class':'printnotes'})

class Plant(Table):
    classes = ['main','chart','plant']
    id = Col('id', show=False)
    name = Col('Name')
    gender = AddIconCol('Gender')
    strain_name = Col('Strain')
    cycle_name = Col('Cycle')
    photo = Col('Photo' ,show=False)
    current_stage = AddIconCol('Current Stage')
    current_environment = Col('Current Environment')
    source = Col('Source', show=False)
    grow_medium = Col('Grow Medium', show=False)
    log = LinkCol('Log', 'show_plant_log', url_kwargs=dict(id='id'))
    details = LinkCol('Details', 'view_plant', url_kwargs=dict(id='id'))
    edit = LinkCol('Edit', 'edit_plant', url_kwargs=dict(id='id'))
    delete = LinkCol('Delete', 'delete_plant', url_kwargs=dict(id='id'))

    def get_tr_attrs(self, item):
        if item['current_stage'] == 'Dead':
            return {'class': 'dead'}
        else:
            return {}

class Cycle(Table):
    classes = ['main','chart','cycle']
    id = Col('id', show=False)
    name = Col('Name')
    start = Col('Start')
    end = Col('End')
    location = Col('Location')
    light_hours = Col('Light Hours')
    edit = LinkCol('Edit', 'edit_cycle', url_kwargs=dict(id='id'))
    delete = LinkCol('Delete', 'delete_cycle', url_kwargs=dict(id='id'))

class Strain(Table):
    classes = ['main','chart','strain']
    id = Col('id', show=False)
    name = Col('Name')
    type = Col('Type')
    notes = Col('Notes')
    edit = LinkCol('Edit', 'edit_strain', url_kwargs=dict(id='id'))
    delete = LinkCol('Delete', 'delete_strain', url_kwargs=dict(id='id'))

class Environment(Table):
    classes = ['main','chart','environment']
    id = Col('id', show=False)
    name = Col('Name')
    location = Col('Location')
    light_hours = Col('Light Hours')
    temperature = Col('Temperature')
    humidity = Col('Humidity')
    light_source = Col('Light Source')
    lumens = Col('Lumens')
    wattage = Col('Wattage')
    grow_area = Col('Grow area')
    containment = Col('Containment')
    max_plants = Col('Maximum Number of Plants')
    edit = LinkCol('Edit', 'edit_environment', url_kwargs=dict(id='id'))
    delete = LinkCol('Delete', 'delete_environment', url_kwargs=dict(id='id'))

class Nutrient(Table):
    classes = ['main','chart','nutrient']
    id = Col('id', show=False)
    name = Col('Name')
    organic = Col('Organic')
    nitrogen = Col('Nitrogen')
    phosphorus = Col('Phosphorus')
    potassium = Col('Potassium')
    trace = Col('Trace')
    edit = LinkCol('Edit', 'edit_nutrient', url_kwargs=dict(id='id'))
    delete = LinkCol('Delete', 'delete_nutrient', url_kwargs=dict(id='id'))

class Repellent(Table):
    classes = ['main','chart','repellent']
    id = Col('id', show=False)
    name = Col('Name')
    type = Col('Type')
    target = Col('Target')
    price = Col('Price')
    purchase_location = Col('Purchase Location')
    notes = Col('Notes')
    edit = LinkCol('Edit', 'edit_repellent', url_kwargs=dict(id='id'))
    delete = LinkCol('Delete', 'delete_repellent', url_kwargs=dict(id='id'))

class Statistics(Table):
    settings = get_settings()
    table_id = ['statistics']
    classes = ['statistics']
    pc = Col('Plant Count')
    ec = Col('Environment Count')
    sc = Col('Strain Count')
    ac = Col('Cycle Count')
    rc = Col('Repellent Count')
    nc = Col('Nutrient Count')
    lastlog = DatetimeCol('Last Log')

class Settings(Table):
    table_id = ['settings']
    classes = ['statistics']
    username = Col('Username')
    password = Col('Password', show=False)
    timezone = Col('Timezone')
    latitude = Col('Latitude')
    longitude = Col('Longitude')
    temp_units = Col('Temperature Units')
    volume_units = Col('Volume Units')
    length_units = Col('Length_Units')
    date_format = Col('Date Format')
    allow_plantlog_edit = Col('Allow Plant Log Edit/Delete')
    allow_envlog_edit = Col('Allow Environment Log Edit/Delete')
