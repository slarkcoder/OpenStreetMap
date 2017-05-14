from peewee import *

db = MySQLDatabase("osm", host='127.0.0.1', user="root", passwd="slarker.me", charset="utf8")

class Node(Model):
    id = PrimaryKeyField()
    node_id = BigIntegerField(unique=True, null=False)
    lat = DecimalField(null=False, decimal_places=7)
    lon = DecimalField(null=False, decimal_places=7)
    timestamp = TimestampField(null=False)
    changeset = IntegerField(null=False)
    uid = BigIntegerField(null=False)
    user = TextField(null=False)
    version = IntegerField(null=False)

    class Meta:
        database = db


class Way(Model):
    id = PrimaryKeyField()
    way_id = BigIntegerField(unique=True, null=False)
    timestamp = TimestampField(null=False)
    changeset = IntegerField(null=False)
    uid = BigIntegerField(null=False)
    user = TextField(null=False)
    version = IntegerField(null=False)

    class Meta:
        database = db

class Relation(Model):
    id = PrimaryKeyField()
    relation_id = BigIntegerField(unique=True, null=False)
    timestamp = TimestampField(null=False)
    changeset = IntegerField(null=False)
    uid = BigIntegerField(null=False)
    user = TextField(null=False)
    version = IntegerField(null=False)

    class Meta:
        database = db

class User(Model):
    id = PrimaryKeyField()
    user_id = BigIntegerField(unique=True, null=False)
    user = TextField(null=False)
    count = BigIntegerField(null=False)

    class Meta:
        database = db