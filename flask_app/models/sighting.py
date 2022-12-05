from flask_app.config.mysqlconnection import MySQLConnection, connectToMySQL

from flask import flash
from flask_app import app
from flask_app.models.user import User
from flask_bcrypt import Bcrypt 
bcrypt = Bcrypt(app) 
import re	
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

db='bird_sightings_schema'

class Sighting:
    def __init__(self,data):
        self.id = data['id']
        self.location = data['location']
        self.date_of_sighting = data['date_of_sighting']
        self.number_of_birds = data['number_of_birds']
        self.description = data['description']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.reported_by = data['reported_by']

    @staticmethod
    def sighting_is_valid(sighting):
        is_valid = True
        if sighting['number_of_birds'] == 0:
            flash('number_of_birds must be greater than 0.')
            is_valid = False
        if sighting['location'] == "":
            flash('Give sighting location information')
            is_valid = False
        if sighting['date_of_sighting'] == 0:
            flash('select sighting date_of_sighting')
            is_valid = False
        if sighting['description'] == "":
            flash('please add a discription of sighting')
        return is_valid
        


    @classmethod
    def get_sightings_by_reporter_id(cls, data):
        query = 'SELECT * FROM sightings WHERE reporter_id=%(reporter_id)s;'
        results = connectToMySQL(db).query_db(query,data)
        sightings = []
        for sighting in results:
            sightings.append(cls(sighting))
        return sightings

    @classmethod
    def save_sighting(cls,data):
        query = "INSERT INTO sightings (location, date_of_sighting, number_of_birds, reported_by, description, reporter_id) VALUES (%(location)s, %(date_of_sighting)s,%(number_of_birds)s, %(reported_by)s, %(description)s,  %(reporter_id)s);"
        connectToMySQL(db).query_db(query, data)
        return

    @classmethod
    def get_sighting_by_id(cls,data):
        query = 'SELECT * FROM sightings WHERE id = %(id)s'

        results = connectToMySQL(db).query_db(query, data)
        
        return cls(results[0])

    @classmethod
    def get_sightings_and_users(cls):
        query = 'SELECT * FROM sightings JOIN users ON reporter_id = users.id;'
        results =  connectToMySQL(db).query_db(query)
        list_sightings = []
        for row in results:
            current_sighting = cls(row)
            user_data = {
                'id' : row['users.id'],
                'first_name' : row['first_name'],
                'last_name' : row['last_name'],
                'email' : row['email'],
                'password' : row ['password'],
                'created_at' : row['users.created_at'],
                'updated_at' : row['users.updated_at']
            }
            current_user = User(user_data)
            current_sighting.reported_by = current_user
            list_sightings.append(current_sighting)
        return list_sightings

    @classmethod
    def update_one(cls,data):
        query = 'UPDATE sightings SET location = %(location)s, date_of_sighting = %(date_of_sighting)s, number_of_birds = %(number_of_birds)s, description = %(description)s, reporter_id = %(reporter_id)s WHERE id = %(id)s;'
        return connectToMySQL(db).query_db(query,data)

    classmethod
    def delete_one(data):
        query = 'DELETE FROM sightings WHERE id = %(id)s;'
        return connectToMySQL(db).query_db(query,data)