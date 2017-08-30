# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 02:24:05 2017

@author: take_
"""


import sys
import os

import db
db.initDB()

import datetime

from sqlalchemy import and_

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

def echo(arg):
    return arg
    
def insertAsset(name,username):
    result = db.assetDB.insert().execute(name = name, username = username)
    return result.inserted_primary_key[0] # idを返します
    
def formatResult(rs):
    if len(rs) == 0:
        return []
    
    result = []
    for row in rs:
        data = dict(zip([str(c) for c in row.keys()],row.values()))
        data['date'] = data['date'].strftime('%Y-%m-%d %H:%M:%S')
        result.append(data)
        
    return result

def fetchAllAsset():
    return formatResult(db.assetDB.select().execute().fetchall())


def searchAsset(condition):
    expressions = []
    if 'name' in condition:
        expressions.append(db.assetDB.c.name == condition['name'])
    
    if 'username' in condition:
        expressions.append(db.assetDB.c.username == condition['username'])
    
    if 'date' in condition:
        dateFrom = datetime.datetime.strptime(condition['date'][0],'%Y-%m-%d %H:%M:%S')
        dateTo   = datetime.datetime.strptime(condition['date'][1],'%Y-%m-%d %H:%M:%S')
        expressions.append(dateFrom <= db.assetDB.c.date)
        expressions.append(db.assetDB.c.date <= dateTo)
        
    if 'id' in condition:
        expressions.append(db.assetDB.c.id == condition['id'])
    
    s = db.assetDB.select().where(and_(*expressions))
    
    return formatResult(s.execute().fetchall())

def startServer(port = 15600):
    server = SimpleXMLRPCServer(("localhost",port))
    
    server.register_introspection_functions()
    server.register_function(echo)
    server.register_function(insertAsset)
    server.register_function(fetchAllAsset)
    server.register_function(searchAsset)
    
    return server

if __name__ == "__main__":
    server = startServer()
    server.serve_forever()
    
    
    
    


