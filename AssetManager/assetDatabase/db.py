# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 07:22:34 2017

@author: take_
"""

from sqlalchemy import *

import datetime

engine = create_engine('sqlite:///asset_cedec2017.db', echo=True)
metadata = MetaData(bind = engine)

assetDB = Table("assetDB",metadata,
                Column('id', Integer, primary_key=True),
                Column('name', String),
                Column('username',String),
                Column('date', DATETIME, default = datetime.datetime.now, nullable = False))

def initDB():
    metadata.create_all()
    
