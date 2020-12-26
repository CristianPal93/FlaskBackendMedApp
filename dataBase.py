import sqlite3
import sqlalchemy
from sqlalchemy import create_engine
from datetime import datetime
import os.path
from os import path


class DataBase:
    def __init__(self):
        self.connection = None
        try:
            self.__create_dataBase()
        except sqlalchemy.exc.OperationalError:
            print("Table exists in the database return a connection to the schema instead!")
            self.connection=self.__create_connection()

    def __get_curent_time(self):
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        return dt_string

    def __create_dataBase(self):
        engine = create_engine('sqlite:///schema.db', echo=True)
        self.connection=engine.connect()
        sql_statement='CREATE TABLE Person(LastName varchar(255) NOT NULL ,FirstName varchar(255) NOT NULL,Cnp varchar(13) primary key ,Job varchar(20),Email varchar(255) not NULL ,Password VARCHAR (20) not NULL );'
        self.connection.execute(sql_statement)
        sql_statement='CREATE TABLE Specialization(Cnp varchar(13),Specialization varchar(255),phoneNumber varchar(12) , FOREIGN KEY (Cnp) REFERENCES Person(Cnp));'
        self.connection.execute(sql_statement)
        sql_statement = 'CREATE TABLE Schedule(Cnp varchar(13),FirstName varchar(255), LastName varchar(255),FirstNameDoctor varchar(255), LastNameDoctor varchar(255),Specialization varchar(255),ScheduleTime TIMESTAMP UNIQUE , FOREIGN KEY (Cnp) REFERENCES Person(Cnp));'
        self.connection.execute(sql_statement)

    def __create_connection(self):
        engine = create_engine('sqlite:///schema.db', echo=True)
        conn=engine.connect()
        return conn

    def wirite_to_db(self, query):
        if path.exists('schema.db'):
            print('Schema is present!')
            try:
                if self.connection is not None:
                    self.connection.execute(query)
                else:
                    self.connection=self.__create_connection()
                    self.connection.execute(query)
            except sqlalchemy.exc.IntegrityError or sqlite3.IntegrityError:
                   print("This record exists in the table!")
        else:
            print('Schema is missing!')
            self.__create_dataBase()
            self.wirite_to_db(query)

    def write_schedule(self, pacient_cnp, doctor_first_name, doctor_last_name, doctor_specialization,time_for_consult):
        if (path.exists('schema.db')):
            print('Schema is present!')
            pacient = self.get_from_db('Select * from person where cnp='+pacient_cnp+';')
            doctor = self.get_from_db('Select * from person where LastName="'+doctor_last_name+'" and FirstName="' + doctor_first_name+'";')
            spec = self.get_from_db('Select * from Specialization where cnp="'+doctor[0][3]+'" and Specialization="' + doctor_specialization+'";')
            sql = 'Insert into Schedule(Cnp,FirstName,LastName,FirstNameDoctor,LastNameDoctor,Specialization,ScheduleTime) VALUES ("'+pacient[0][3]+'","'+pacient[0][0]+'","'+pacient[0][1]+'","'+doctor[0][0]+'","'+doctor[0][1]+'","'+spec[0][1]+'","'+time_for_consult+'");'
            self.connection.connect()
            self.connection.execute(sql)
            return True
        else:
            print('Schema is missing!')
            self.__create_dataBase()
            self.write_schedule(self, pacient_cnp, doctor_first_name, doctor_last_name, doctor_specialization)
    def insertDoctor(self,last_name,first_name,email,password,cnp=None):
        if(cnp is not None):
            sql = "Insert INTO Person(LastName,FirstName,Cnp,Job,Email,Password) VALUES ("+first_name+","+last_name+","+cnp+",doctor,"+email+","+password+");"
        else:
            sql = "Insert INTO Person(LastName,FirstName,Job,Email,Password) VALUES ("+first_name+","+last_name+","+"doctor,"+email+","+password+");"
        if(sql):
            self.wirite_to_db(sql)
        else:
            print("No sql query!")

    def get_from_db(self, query):
        if self.connection is not None:
            self.connection.connect()
            result = self.connection.execute(query)
            result = result.fetchall()
        else:
            self.connetion = self.__create_connection()
            result = self.connection.execute(query)
            result = result.fetchall()
        return result

    def close_connetion(self):
        self.connection.close()

    def open_connetion(self):
        self.connection.connect()

    def checkUser(self,username,password):
        sqlQuery="SELECT * FROM PERSON WHERE email='"+username+"' and Password='"+password+"';"
        result=self.get_from_db(sqlQuery)
        if len(result)>0:
            return True
        else:
            return False
    def checkJob(self,username,password):
        sqlQuery = "SELECT * FROM PERSON WHERE email='" + username + "' and Password='" + password + "';"
        result = self.get_from_db(sqlQuery)
        if len(result)>0:
            return result[0][3]
        return None
    def deleteRecordFromPerson(self,cnp):
        sql="Delete from Person where cnp="+cnp+";"
        self.wirite_to_db(sql)
    def addSpecialization(self,cnp,spec,cellphone):
        sql = "Insert INTO Specialization(Cnp,Specialization,phoneNumber) VALUES ("+cnp+","+spec+","+cellphone+");"
        self.wirite_to_db(sql)
    def insertPacient(self,lastName,firstName,cnp,job,email,password):
        sql = "Insert INTO Person(LastName,FirstName,Cnp,Job,Email,Password) VALUES ('"+firstName+"','"+lastName+"','"+cnp+"','"+job+"','"+email+"','"+password+"');"
        self.wirite_to_db(sql)
    def get_staff(self,job):
        sql = "Select * from Person where job='"+job+"';"
        return self.get_from_db(sql)
    def doctor_specializations(self,cnp):
        sql = "Select * from Specialization where cnp='"+cnp+"';"
        return self.get_from_db(sql)
if __name__ == "__main__":
    d = DataBase()
    # print(d.doctor_specializations('1910924403932'))
    # name="John"
    # first_name="Popescu"
    # passwd="Admin123"
    # email="pojohn@gmail.com"
    # cnp="1932509393032"
    # d.insertDoctor(name,first_name,email,passwd,cnp)


    # rez=d.checkUser("cristian.pal@gmail.com","Admin123")
    # print(rez)
    # print(d.checkJob("cristian.pal@gmail.com","Admin123"))

    # sql = 'Insert INTO Person(LastName,FirstName,Cnp,Job,Email,Password) VALUES ("Cristian","Pal","1930925303932","pacient","cristian.pal@gmail.com","Admin123");'
    # d.wirite_to_db(sql)
    # # sql = 'SELECT * FROM person where email="cristian.pal@gmail.com" and password="Admin123"';
    # # print(d.get_from_db(sql))
    # sql = 'Insert INTO Person(LastName,FirstName,Cnp,Job,Email,password) VALUES ("Laurentiu","Girleanu","1910925303932","doctor","laurentiu.girleanu@gmail.com","Admin1234");'
    # d.wirite_to_db(sql)
    # sql = 'Insert INTO Person(LastName,FirstName,Cnp,Job,Email,password) VALUES ("Ion","Popescu","1910924403932","doctor","ion.popescu@gmail.com","Admin12345");'
    # d.wirite_to_db(sql)
    sql = 'SELECT * FROM person';
    print(d.get_from_db(sql))
    # sql='Insert INTO Specialization(Cnp,Specialization,phoneNumber) VALUES ("1910925303932","Psiholog","+40742451132");'
    # d.wirite_to_db(sql)
    # sql = 'Insert INTO Specialization(Cnp,Specialization,phoneNumber) VALUES ("1910924403932","Neurolog","+40742451123");'
    # d.wirite_to_db(sql)
    # sql = 'Delete FROM specialization where cnp="1910924403932";'
    # d.wirite_to_db(sql)
    # d.write_schedule('1930925303932', "Girleanu", "Laurentiu", "Chirurg")
    # sql = 'Select * from Schedule;'
    # print(d.get_from_db(sql))



