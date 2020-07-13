#!/var/www/pyvenv/bin/python

import logging
import sys
from flask import Flask
import datetime
import sys
import flask_table as ft
import mysql.connector as sql
import os

# Add directory of this file to path (used for sql credentials file)
sys.path.append(os.path.dirname(__file__))

# Get sql database credentials
from sql_cred import * 

logging.basicConfig(stream=sys.stderr)

# Columns to show and their order. Dict values will be used as column names
cols = {'name': 'Name', 'description': 'Description', 'stockLevel': 'Stock', 'storageLocation_id': 'Location'}

# Connect to database
db = sql.connect(
    host     = sql_host,
    user     = sql_user,
    passwd   = sql_passwd,
    database = sql_database
)
crsr = db.cursor()

# Get part data
crsr.execute(f"SELECT category_id,{','.join(cols)} FROM Part")
tblRaw = crsr.fetchall()

# Get categories
crsr.execute("SELECT categoryPath,id FROM PartCategory")
tblCat = crsr.fetchall()

# Get storage locations
crsr.execute("SELECT id,name FROM StorageLocation")
tblLoc = crsr.fetchall()
# Transform list into dictionary
tblLoc = {r[0]:r[1] for r in tblLoc}
#print(tblRaw)



# html attributes
htmlAttr = {
 'border': '1',
 'cellspacing': '0'
}

colAttr = {
 'width': '400'
}

# Declare tables
TableCls = ft.create_table('TableCls', options={'html_attrs': htmlAttr})
for col, colName in cols.items():
  TableCls.add_column(col, ft.Col(colName))

# Sort categories and items
tblRaw.sort()
tblCat.sort()

html = ''
for cat in tblCat:
    # Extract parts of the current category and create dicts
    items = []
    for row in tblRaw:
        if cat[1] == row[0]:
            items += [{list(cols)[i]:row[len(row)-len(cols):][i] for i in range(len(cols))}]
    # Populate the table if any items existed in the category
    if items:
        # Add name of category
        toReplace = "Root Category \u27a4"
        html += f'<h1>{cat[0].replace(toReplace,"")}</h1>\n'
        # Populate table
        table = TableCls(items)
        html += table.__html__()

application = Flask(__name__)
@application.route("/")
def hello():
    return html

if __name__ == "__main__":
    application.run()
