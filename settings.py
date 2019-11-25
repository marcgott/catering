#! /usr/bin/env python3.5
import pymysql
import os
from app import app
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import *
from matplotlib.dates import DateFormatter
import numpy as np
import seaborn as sns
import base64
import calendar
import requests
from datetime import date,datetime,timedelta
from io import BytesIO
from flask import session, redirect, render_template
try:
    from db_config import mysql
except ImportError as e:
	pass

def check_login():
    if not session.get('logged_in'):
        return False
    return True

def get_icons(operation=None):
    icons = {'dashboard':'tachometer-alt','log':'clipboard-check','customers':'leaf','products':'spa','nutrients':'tint','repellents':'bug','strains':'dna','menus':'sun','reports':'file-contract','settings':'bars','germination':'egg','seedling':'seedling','vegetation':'leaf','pre-flowering':'spa','flowering':'pepper-hot','harvest':'tractor','archive':'eye-slash','dead':'skull-crossbones','gender':'venus-mars','source':'shipping-fast','unknown':'question','male':'mars','female':'venus','hermaphrodite':'venus-mars','grow_medium':'prescription-bottle','lux':'lightbulb','temp':'thermometer-three-quarters','humidity':'cloud-sun-rain','light':'sun','dark':'moon'}
    return icons

def get_strain_types():
    return [('Unknown','Unknown'),('Annuum','Annuum'),('Baccatum','Baccatum'),('Chinense','Chinense'),('Frutrescens','Frutrescens'),('Pubescens','Pubescens')]
def get_settings():
    global app
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM options")
        rows = cursor.fetchall()
        options={}
        for row in rows:
            key = row['option_key']
            value = row['option_value']
            if row['option_value'] == 'True':
                    value = True
            options[key]=value
        app.settings = options
        return options
    except Exception as e:
        print(e)

def get_daystats(dt=None):
    option=get_settings()

    daydate = date.today()
    req = 'https://api.sunrise-sunset.org/json?lat=%s&lng=%s&date=%s' % (option['latitude'],option['longitude'],daydate)
    res = requests.get(req)
    #print(res.json)
    return res.text

def get_measurement_plot(rows,customer_name,**kwargs):
    option=get_settings()

    labels = [0]
    heights= [0]
    spans = [0]
    trims = []
    last_span = 0
    last_height = 0
    mindate = rows[0]['mindate'] - timedelta(days=2)
    for row in rows:
        labels[0]  = mindate
        heights[0] = 0
        spans[0] = 0
        labels.append(row['logdate'])
        if row['height'] >0:
            heights.append(row['height'])
            last_height = row['height']
        else:
            heights.append(last_height)

        if row['span'] >0:
            spans.append(row['span'])
            last_span = row['span']
        else:
            spans.append(last_span)
        trims.append({'date':row['logdate'],'type':row['trim']})

    x = np.arange(len(labels))  # the label locations
    fig, ax = plt.subplots()

    ylimit = int(max(heights + spans) + 5)
    d1 = ax.plot_date(labels,heights,fmt='o', tz=None, xdate=True, ydate=False,linestyle='-',label="Height" )
    d2 = ax.plot_date(labels,spans,fmt='o', tz=None, xdate=True, ydate=False,linestyle='-',label="Span")


    for i,trim in enumerate(trims):
        if trim['type'] != '':
            color = "".join(['C',str(i)])
            plt.axvline(trim['date'],label=trim['type'],color=color)

    if 'stages' in kwargs:
        for i,stage in enumerate(kwargs['stages']):
            color = "".join(['C',str(i+5)])
            plt.axvline(stage['logdate'],label=stage['stage'],color=color,linestyle='--')
            if stage['logdate'] not in labels:
                labels.append(stage['logdate'])

    if date.today() not in labels:
        labels.append(date.today())
    ax.set_ylabel(option['length_units'])
    ax.set_xlim([min(labels),max(labels) + timedelta(days=2)])
    ax.set_xticks(labels)
    ax.set_xticklabels(labels)
    ax.grid(True, linestyle='-')
    ax.tick_params( width=3, grid_color='g', grid_alpha=0.5)
    ax.set_ylim([0,ylimit])
    ax.set_title('Growth Chart for '+customer_name)
    formatter = DateFormatter('%m/%d/%y')
    for tick in ax.xaxis.get_majorticklabels():
        tick.set_horizontalalignment("right")
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30, labelsize=7)
    ax.legend(loc='upper left')
    fig.tight_layout()

    figfile = BytesIO()
    fig.savefig(figfile, format='png')
    figfile.seek(0)  # rewind to beginning of file

    #figdata_png = base64.b64encode(figfile.read())
    figdata_png = base64.b64encode(figfile.getvalue())
    return figdata_png

def get_water_calendar(dates,customer_name):
    sns.set_style("whitegrid")
    plt.figure(figsize=(9, 3))
    # non days are grayed
    ax = plt.gca().axes
    ax.add_patch(Rectangle((29, 2), width=.8, height=.8,
                           color='gray', alpha=.3))
    ax.add_patch(Rectangle((30, 2), width=.8, height=.8,
                           color='gray', alpha=.5))
    ax.add_patch(Rectangle((31, 2), width=.8, height=.8,
                           color='gray', alpha=.5))
    ax.add_patch(Rectangle((31, 4), width=.8, height=.8,
                           color='gray', alpha=.5))
    ax.add_patch(Rectangle((31, 6), width=.8, height=.8,
                           color='gray', alpha=.5))
    ax.add_patch(Rectangle((31, 9), width=.8, height=.8,
                           color='gray', alpha=.5))
    ax.add_patch(Rectangle((31, 11), width=.8, height=.8,
                           color='gray', alpha=.5))

    waterdays = []
    watermonths = []
    for dt in dates:
        waterdays.append(dt['d'])
        watermonths.append(dt['m'])
    for d, m in zip(waterdays,watermonths):
        ax.add_patch(Rectangle((d, m),
                               width=.8, height=.8, color='C0'))
    plt.yticks(np.arange(1, 13)+.5, list(calendar.month_abbr)[1:])
    plt.xticks(np.arange(1,32)+.5, np.arange(1,32))
    plt.xlim(1, 32)
    plt.ylim(1, 13)
    ax.set_title('Water Chart for '+customer_name)
    plt.gca().invert_yaxis()
    # remove borders and ticks
    for spine in plt.gca().spines.values():
        spine.set_visible(False)
    plt.tick_params(top=False, bottom=False, left=False, right=False)
    #plt.show()
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)  # rewind to beginning of file

    #figdata_png = base64.b64encode(figfile.read())
    figdata_png = base64.b64encode(figfile.getvalue())
    return figdata_png

def get_comparison_chart(data,chartname,yaxis_label):
    option=get_settings()
    labels = []
    measures= []

    for row in data:
        labels.append(row['name'])
        measures.append(float(row['measure']))

    fig, ax = plt.subplots()
    ylimit = max(measures) + 5

    d1 = ax.bar(labels,measures,label=chartname)
    plt.axhline(np.average(measures),label="Average",color="r")

    ax.set_ylabel(yaxis_label)
    ax.set_xticks(labels)
    ax.set_xticklabels(labels)
    ax.tick_params(width=3)
    ax.set_ylim([0,ylimit])
    ax.set_title('Customer '+chartname)
    for tick in ax.xaxis.get_majorticklabels():
        tick.set_horizontalalignment("right")

    ax.xaxis.set_tick_params(rotation=30, labelsize=8)
    ax.legend(loc='upper left')

    plt.tight_layout()
    figfile = BytesIO()
    fig.savefig(figfile, format='png')
    figfile.seek(0)  # rewind to beginning of file

    #figdata_png = base64.b64encode(figfile.read())
    figdata_png = base64.b64encode(figfile.getvalue())
    return figdata_png


def get_rank(customer_ID,measure):

    sql = "SELECT customer_ID, @prev := @curr as prev, @curr := height as height, @rank := IF(@prev > @curr, @rank+@ties, @rank) AS rank, (1-@rank/@total) as percentrank FROM  log, (SELECT @curr := null, @prev := null, @rank := 0, @ties := 1, @total := count(*) from log where %s is not null) b WHERE %s is not null ORDER BY %s DESC" % (measure,measure,measure)
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql)
    rows = cursor.fetchall()
    if len(rows) > 0:
        for row in rows:
            if row['customer_ID'] == customer_ID:
                return row
    else:
        return {'rank':0}

def get_photo_base64(photo):
    APP_PATH = os.path.dirname(__file__)
    photopath = 'static/images/%s' % photo
    with open(os.path.join(APP_PATH,photopath), 'rb') as photo_data:
        photostream = base64.b64encode(photo_data.read())
        return photostream.decode('utf8')
