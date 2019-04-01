#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 15:31:56 2018

@author: cqj
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""



import json
import re
import math
import pandas as pd
from pandas import DataFrame
import numpy as py
from pandas import *
from matplotlib import pyplot as plt
from sklearn.cross_validation import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import collections
from sklearn.ensemble import RandomForestClassifier
from fuzzywuzzy import fuzz
from geopy.distance import vincenty

"""
This assignment can be done in groups of 3 students. Everyone must submit individually.

Write down the UNIs of your group (if applicable)

Name : Yijia Chen 
Uni  : yc3425

Name : Yiwen Zhang
Uni  : yz3310

Name : Haotian Zeng
Uni  : hz2494

"""

dir="/Users/cqj/Desktop/Columbia/2018Spring/COMS 4121 ComSys/HW3/"
with open(dir+'locu_train.json') as f:
    locu_train = json.loads(f.read())

with open(dir+'foursquare_train.json') as f:
    fs_train = json.loads(f.read())

matches_train = pd.read_csv(dir+'matches_train.csv')


def dataCleaning(datalist):
    for k in range(0,600):
        datalist[k]['phone'] = re.sub("[^0-9]", "", str(datalist[k]['phone']))
        datalist[k]['name'] = re.sub("[ ]", "", str(datalist[k]['name']))
        datalist[k]['website'] = re.sub("[http://www.com ]", "", str(datalist[k]['website']))
        datalist[k]['street_address'] = re.sub("[. ]", "", str(datalist[k]['street_address']))

    return datalist

locu_train = dataCleaning(locu_train)
fs_train = dataCleaning(fs_train)



def VectorGenerate(dataA, dataB): 
    a = len(dataA)
    b = len(dataB)
    vector = [[] for index in range(0,a*b)]
 
    for i in range(0,a):
        for j in range(0,b):
            vector[i*b+j].append(dataA[i]['id'])
            vector[i*b+j].append(dataB[j]['id'])


            
            name1 = dataA[i]['name'].lower()
            name2 = dataB[j]['name'].lower()
            if name1 == '' or name2 == '':
                vector[i*b+j].append(0)
            else:
                vector[i*b+j].append((fuzz.ratio(name1, name2)/10)-5)
                
            
            phone1 = dataA[i]['phone']
            phone2 = dataB[j]['phone']
            if phone1 == '' or phone2 == '':
                vector[i*b+j].append(1)
            else:
                vector[i*b+j].append((fuzz.ratio(phone1, phone2)/10)-5)
                
            
            lat1 = dataA[i]["latitude"]
            lat2 = dataB[j]["latitude"]
            long1= dataA[i]["longitude"]
            long2= dataB[j]["longitude"]
            if(lat1 is None or lat2 is None or long1 is None or long2 is None):
                vector[i*b+j].append(0)
            else:
                place1 = (lat1, long1)
                place2 = (lat2, long2)
                dist = vincenty(place1, place2).meters
                vector[i*b+j].append(5-dist*0.01)
                     
            
            post1 = dataA[i]['postal_code']
            post2 = dataB[j]['postal_code']
            if post1 == '' or post2 == '':
                vector[i*b+j].append(1)
            elif post1 == post2:
                vector[i*b+j].append(5)
            else:
                vector[i*b+j].append(0)
                
            
            addr1 = dataA[i]['street_address'].lower()
            addr2 = dataB[j]['street_address'].lower()
            if addr1 == '' or addr2 == '':
                vector[i*b+j].append(1) 
            else:
                vector[i*b+j].append((fuzz.ratio(addr1, addr2)/10) - 5)
            
                          
            
            web1 = dataA[i]['website'].lower()
            web2 = dataB[j]['website'].lower()    
            if web1 == '' or web2 == '':
                vector[i*b+j].append(1)
            else:
                vector[i*b+j].append((fuzz.ratio(web1, web2)/10) - 5)
            
    
    return vector
            

with open(dir+'locu_test.json') as f:
    locu_test = json.loads(f.read())

with open(dir+'foursquare_test.json') as f:
    fs_test = json.loads(f.read())



columns=['locu_id', 'fs_id', 'name', 'phone', 'lat_long', 'postcode', 'address', 'website']

def get_matches(locu_train, fs_train, matches_train, locu_test, fs_test):
    trainVector = VectorGenerate(locu_train,fs_train)
    length = len(columns)
    
    arr_train = []
    for k in range(0,len(trainVector)):
        arr_train.append(list(map(int,trainVector[k][2:length])))

    X_train = py.array(arr_train)
 
    
    matchTupleList = []
    for k in range(0,len(matches_train)):
        matchTupleList.append(tuple(matches_train.iloc[k]))


    y = []
    for k in range(0,len(trainVector)):
        if tuple(trainVector[k][0:2]) in matchTupleList:
            y.append(1)
        else:
            y.append(-1)
       
    ytrain = py.array(y)

    
    testVector = VectorGenerate(locu_test,fs_test)
    arr_test = []
    for k in range(0,len(testVector)):
        arr_test.append(list(map(int,testVector[k][2:length])))
    
    X_test = py.array(arr_test)
    
    X_train1,X_train2,ytrain1,ytrain2 = train_test_split(X_train,ytrain,test_size=0.3,random_state=0)
    

    clf = RandomForestClassifier(n_estimators= 150, max_depth=7)
    clf.fit(X_train1, ytrain1)

    
    ypredtrain2 = clf.predict(X_train2)
    print(classification_report(ytrain2, ypredtrain2))    
    
    
    ypredtest = clf.predict(X_test)
    print(collections.Counter(ypredtest))
    testFeature = pd.DataFrame(testVector, columns=columns)
    
    testFeature['matched'] = pd.Series(ypredtest, index=testFeature.index)
    
    matches = []
    for k in range(0, len(testFeature)):
        if(testFeature.loc[k,'matched'] == 1):
            matches.append((testFeature.loc[k,'locu_id'],testFeature.loc[k,'fs_id']))
    

    return matches

matches_test = get_matches(locu_train, fs_train, matches_train, locu_test, fs_test)

with open(dir+"nlpmatches_test.csv", 'w') as f:
    f.write("locu_id" + "," + "foursquare_id" + "\n")
    for m in matches_test:
        f.write(str(m[0]) + "," + str(m[1]) + "\n")



