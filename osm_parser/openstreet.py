#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow
from osmModel import *
import osmModel
from peewee import *
from peewee import SelectQuery
import dateutil.parser
from decimal import *
from datetime import *
import re
from bs4 import BeautifulSoup

OSM_FILE = "shanghai.osm"  # Replace this with your osm file
SAMPLE_FILE = "sample.osm"

k = 100 # Parameter: take every k-th top level element

def get_element(osm_file, tags):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

# 插入 Node 到 MySQL
def insertNode():
    if Node.table_exists() == False:
        Node.create_table()

    start = datetime.now()
    print(start)

    with osmModel.db.atomic():
        for i, element in enumerate(get_element(OSM_FILE, ('node'))):
            dic = element.attrib
            stamp = dateutil.parser.parse(dic['timestamp'])

            lat = Decimal(dic['lat'])
            lon = Decimal(dic['lon'])

            try:
                Node.create(node_id=int(dic['id']),
                                   lat=lat,
                                   lon=lon,
                                   timestamp=stamp,
                                   changeset=int(dic['changeset']),
                                   uid=int(dic['uid']),
                                   user=dic['user'],
                                   version=int(dic['version']))
                print("save, id = ", dic['id'])
            except DatabaseError as e:
                print("error：", e)
                print('error id = ', dic['id'])

    end = datetime.now()

    print('运行了：',(end - start).seconds)

# 插入 Way 到 MySQL
def insertWay():

    if Way.table_exists() == False:
        Way.create_table()

    start = datetime.now()

    with osmModel.db.atomic():
        for i, element in enumerate(get_element(OSM_FILE, ('way'))):
            dic = element.attrib
            stamp = dateutil.parser.parse(dic['timestamp'])

            try:
                Way.create(way_id=int(dic['id']),
                                   timestamp=stamp,
                                   changeset=int(dic['changeset']),
                                   uid=int(dic['uid']),
                                   user=dic['user'],
                                   version=int(dic['version']))
                print("save, id = ", dic['id'])
            except DatabaseError as e:
                print("error：", e)
                print('error id = ', dic['id'])

    end = datetime.now()
    print('运行了：',(end - start).seconds)

# 插入 Relation 到 MySQL
def insertRelation():
    if Relation.table_exists() == False:
        Relation.create_table()

    start = datetime.now()

    with osmModel.db.atomic():
        for i, element in enumerate(get_element(OSM_FILE, ('relation'))):
            dic = element.attrib
            stamp = dateutil.parser.parse(dic['timestamp'])

            try:
                Relation.create(relation_id=int(dic['id']),
                                   timestamp=stamp,
                                   changeset=int(dic['changeset']),
                                   uid=int(dic['uid']),
                                   user=dic['user'],
                                   version=int(dic['version']))
                print("save, id = ", dic['id'])
            except DatabaseError as e:
                print("error：", e)
                print('error id = ', dic['id'])

    end = datetime.now()
    print('运行了：',(end - start).seconds)

# 获取样本 osm
def get_sample_osm():
    with open(SAMPLE_FILE, 'wb+') as output:
        output.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write(b'<osm>\n  ')

        # Write every kth top level element
        for i, element in enumerate(get_element(OSM_FILE, tags=('node', 'relation', 'way'))):
            if i % k == 0:
                output.write(ET.tostring(element, encoding='utf-8'))

        output.write(b'</osm>')

# 获取表行数
def get_row_count():
    nodes = SelectQuery(Node).select()
    ways = SelectQuery(Way).select()
    relations = SelectQuery(Relation).select()

    print("nodes count = ", nodes.count())
    print("ways count = ", ways.count())
    print("relations count = ", relations.count())

# 查询 User 数量
def get_user_count():
    query = Node.select(Node.user, fn.Count(Node.user).alias("user_count")).group_by(Node.user)
    query = query.order_by(SQL('user_count DESC'))

    num = 0
    for node in query[0:100]:
        print(node.user_count)
        print(node.user)
        num += node.user_count

    print('num = ', num)
    print('per = ', num/625646)

def get_fast_food_count():
    with open("shanghai.osm", 'rb') as f:
        soup = BeautifulSoup(f.read(), "lxml")
        fastfood = soup.find_all('tag', k='amenity', v='fast_food')

        sum = 0
        for food in fastfood:
            tags = food.find_next_siblings()
            for tag in tags:
                if tag['k'] == 'name:en':
                    sum +=1
                    print(tag['v'])

        print("Done!")
        print("sum = ",sum)

# User 数量排序
def sort_user_count():
    # query = Node.select(Node.user, fn.Count(Node.user).alias("user_count")).group_by(Node.user)
    # query = query.order_by(SQL('user_count DESC'))
    #
    # #User 数量
    # print("独立用户数：",query.count())
    #
    # # 排名前 10 的 User
    # print("排名前 10 的用户：")
    # for node in query[0:10]:
    #     print(node.user_count)
    #     print(node.user)

    if User.table_exists() == False:
        User.create_table()

    with osmModel.db.atomic():
        query = Node.select(Node.user, fn.Count(Node.user).alias("user_count")).group_by(Node.user).having(fn.Count(Node.user) < 100)
        print(query.count())
            # try:
            #     User.create(user_id=node.uid,
            #                 user=node.user,
            #                 count=node.user_count
            #                 )
            #     print("save, id = ", node.uid)
            # except DatabaseError as e:
            #     print("error：", e)
            #     print('error id = ', node.uid)

def verify_postcode():
    rex_postcode = re.compile(r'[1-9]\d{5}(?!\d)')
    with open("shanghai.osm", 'rb') as f:
        soup = BeautifulSoup(f.read(), "lxml")
        postcodes = soup.find_all('tag', k='addr:postcode')
        for post in postcodes:
            if rex_postcode.fullmatch(post['v']) == None:
                print(post['v'])

        print("Done!")

def verify_lat_lon():
    with open("shanghai.osm", 'rb') as f:
        soup = BeautifulSoup(f.read(), "lxml")
        nodes = soup.find_all('node')

        print("lat")
        for node in nodes:
            if len(node['lat']) < 6:
                print(node['lat'])

        print("lon")
        for node in nodes:
            if len(node['lon']) < 7:
                print(node['lon'])

        print("Done!")


if __name__ == '__main__':
    # get_sample_osm()
    # insertRelation()
    # insertNode()
    # insertWay()

    # get_row_count()
    # get_user_count()

    # verify_postcode()
    # verify_lat_lon()
    get_fast_food_count()
