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
        dt_string = now.strftime("%Y-%m-%d")
        return dt_string

    def __create_dataBase(self):
        engine = create_engine('sqlite:///schema.db', echo=True,connect_args={"check_same_thread": False})
        self.connection=engine.connect()
        sql_statement='CREATE TABLE Person(LastName varchar(255) NOT NULL ,FirstName varchar(255) NOT NULL,Cnp varchar(13) primary key ,Job varchar(20),Email varchar(255) not NULL ,Password VARCHAR (20) not NULL );'
        self.connection.execute(sql_statement)
        sql_statement='CREATE TABLE Specialization(Cnp varchar(13) primary key ,Specialization varchar(255),phoneNumber varchar(12));'
        self.connection.execute(sql_statement)
        sql_statement = 'CREATE TABLE Schedule(Cnp varchar(13),FirstName varchar(255), LastName varchar(255),FirstNameDoctor varchar(255), LastNameDoctor varchar(255),Specialization varchar(255),ScheduleTime TIMESTAMP  ,ScheduleDate TIMESTAMP ,Details varchar(255),tipCerere varchar(255));'
        self.connection.execute(sql_statement)
        sql_statement = 'CREATE TABLE Tarif(Service varchar(13) primary key,Price varchar(255));'
        self.connection.execute(sql_statement)
        sql_statement = 'CREATE TABLE PersonalDetails(Cnp varchar(13) primary key,Address varchar(255),phoneNumber varchar(12));'
        self.connection.execute(sql_statement)
        sql_statement = 'CREATE TABLE PersonalSchedule(LastName varchar(255) NOT NULL ,FirstName varchar(255) NOT NULL,Specialization varchar(255),ScheduleTime TIMESTAMP  ,ScheduleDate TIMESTAMP ,Details varchar(255));'
        self.connection.execute(sql_statement)
        sql_statement = 'CREATE TABLE Trimitere(cnp varchar(13),LastName varchar(255),FirstName varchar(255), Service varchar(255) primary key,totalprice varchar(255),ScheduleTime TIMESTAMP  ,ScheduleDate TIMESTAMP);'
        self.connection.execute(sql_statement)
        sql_statement = 'CREATE TABLE EliberareaScrisoare(cnp_p varchar(13),LastName varchar(255) NOT NULL ,FirstName varchar(255) NOT NULL,Adresa_p varchar(255) NOT NULL,medicamente varchar(255) NOT NULL,diagnostic varchar(255) NOT NULL,FirstNameDoctor varchar(255), LastNameDoctor varchar(255),pret varchar(10),servicii varchar (255),ScheduleTime TIMESTAMP  ,ScheduleDate TIMESTAMP);'
        self.connection.execute(sql_statement)
        sql_statement = 'CREATE TABLE MaterialChirulgical(Material varchar(255));'
        self.connection.execute(sql_statement)


    def eliberare_scrisoare(self,cnp_p,l_n,f_n,add_p,s_p,di_p,f_doc,l_doc,pret,serv,ora,data):
        sql="Insert into EliberareaScrisoare(cnp_p,LastName,FirstName,Adresa_p,medicamente,diagnostic,FirstNameDoctor,LastNameDoctor,pret,servicii,ScheduleTime,ScheduleDate) VALUES ('"+cnp_p+"','"+l_n+"','"+f_n+"','"+add_p+"','"+s_p+"','"+di_p+"','"+f_doc+"','"+l_doc+"','"+pret+"','"+serv+"','"+ora+"','"+data+"');"
        succ=self.write_to_db(sql)
        return succ
    def inserare_material(self,material):
        sql="Insert into MaterialChirulgical(Material) values ('"+material+"');"
        self.write_to_db(sql)
    def get_all_trimiteri(self):
       sql="Select * from  Trimitere;"
       result=self.get_from_db(sql)
       if(len(result)>0):
            reg=[]
            full=[]
            for consults in result:
                for consult in consults:
                    reg.append(consult)
                full.append(reg)
                reg=[]
            return full
       else:
           return [[]]

    def get_all_scrisori(self):
       sql="Select * from  EliberareaScrisoare;"
       result=self.get_from_db(sql)
       if(len(result)>0):
            reg=[]
            full=[]
            for consults in result:
                for consult in consults:
                    reg.append(consult)
                full.append(reg)
                reg=[]
            return full
       else:
           return [[]]
    def get_all_trimiteri2(self,cnp):
       sql="Select * from  Trimitere where cnp='"+cnp+"';"
       result=self.get_from_db(sql)
       if(len(result)>0):
            reg=[]
            full=[]
            for consults in result:
                for consult in consults:
                    reg.append(consult)
                full.append(reg)
                reg=[]
            return full
       else:
           return [[]]

    def get_all_scrisori2(self,cnp):
       sql="Select * from  EliberareaScrisoare where cnp_p='"+cnp+"';"
       result=self.get_from_db(sql)
       if(len(result)>0):
            reg=[]
            full=[]
            for consults in result:
                for consult in consults:
                    reg.append(consult)
                full.append(reg)
                reg=[]
            return full
       else:
           return [[]]
    def get_all_pacients(self,doctor_cnp):
        sql="Select FirstName,LastName from Person where cnp='"+doctor_cnp+"';"
        result=self.get_from_db(sql)
        doc_first_name=result[0][1]
        doc_last_name=result[0][0]
        sql="Select cnp,specialization from Specialization where cnp='"+doctor_cnp+"';"
        result=self.get_from_db(sql)
        doc_spec=result[0][1]
        sql="Select cnp,FirstName,LastName,ScheduleTime,ScheduleDate,Details from Schedule where FirstNameDoctor='"+doc_first_name+"' and LastNameDoctor='"+doc_last_name+"' and Specialization='"+doc_spec+"' and tipCerere='trimitere';"
        result=self.get_from_db(sql)

        time = self.__get_curent_time()
        a_schedule=[]
        scheduled_list=[]
        for schedules in result:
            for schedule in schedules:
                a_schedule.append(schedule)
            cnp=a_schedule[0]
            full_name=a_schedule[1]+" "+a_schedule[2]
            time_for_consult=a_schedule[3]
            date_for_consult=a_schedule[4]
            details=a_schedule[5]
            sql = "Select  Service,totalprice from Trimitere where cnp='"+cnp+"' and ScheduleTime='"+a_schedule[3]+"' and ScheduleDate='"+a_schedule[4]+"';"
            result_t = self.get_from_db(sql)
            try:
                servicii = result_t[0][0]
                pret = result_t[0][1]
            except IndexError:
                servicii = ''
                pret = '50'
            full_list=[]
            if(time==date_for_consult):
                full_list.append(full_name)
                full_list.append(time_for_consult)
                full_list.append(date_for_consult)
                full_list.append(details)
                full_list.append(cnp)
                full_list.append(servicii)
                full_list.append(pret)
                scheduled_list.append(full_list)

            a_schedule=[]

        return scheduled_list
    def get_all_pacients_2(self,doctor_cnp):
        sql="Select FirstName,LastName from Person where cnp='"+doctor_cnp+"';"
        result=self.get_from_db(sql)
        doc_first_name=result[0][1]
        doc_last_name=result[0][0]
        sql="Select cnp,specialization from Specialization where cnp='"+doctor_cnp+"';"
        result=self.get_from_db(sql)
        doc_spec=result[0][1]
        sql="Select cnp,FirstName,LastName,ScheduleTime,ScheduleDate,Details from Schedule where FirstNameDoctor='"+doc_first_name+"' and LastNameDoctor='"+doc_last_name+"' and Specialization='"+doc_spec+"' and tipCerere='consult';"
        result=self.get_from_db(sql)

        time = self.__get_curent_time()
        a_schedule=[]
        scheduled_list=[]
        for schedules in result:
            for schedule in schedules:
                a_schedule.append(schedule)
            cnp=a_schedule[0]
            full_name=a_schedule[1]+" "+a_schedule[2]
            time_for_consult=a_schedule[3]
            date_for_consult=a_schedule[4]
            details=a_schedule[5]
            sql = "Select  Service,totalprice from Trimitere where cnp='"+cnp+"' and ScheduleTime='"+a_schedule[3]+"' and ScheduleDate='"+a_schedule[4]+"';"
            result_t = self.get_from_db(sql)
            try:
                servicii = result_t[0][0]
                pret = result_t[0][1]
            except IndexError:
                servicii = ''
                pret = '50'
            full_list=[]
            if(time==date_for_consult):
                full_list.append(full_name)
                full_list.append(time_for_consult)
                full_list.append(date_for_consult)
                full_list.append(details)
                full_list.append(cnp)
                full_list.append(servicii)
                full_list.append(pret)
                scheduled_list.append(full_list)

            a_schedule=[]

        return scheduled_list
    def final_price(self,cnp,service,total_price,time,date):
        sql="Select FirstName,LastName from Person where cnp='"+cnp+"';"
        results=self.get_from_db(sql)
        first=results[0][0]
        last=results[0][1]
        sql="Insert into Trimitere(cnp,FirstName,LastName,service,totalprice,ScheduleTime,ScheduleDate) VALUES ('"+cnp+"','"+first+"','"+last+"','"+service+"','"+total_price+"','"+time+"','"+date+"');"
        succes=self.write_to_db(sql)
        return succes
    def add_services(self,service,price):
        sql="INSERT INTO Tarif(Service,Price) VALUES ('"+service+"','"+price+"');"
        succes=self.write_to_db(sql)
        return succes
    def update_schedule(self,cnp,spec,ora,data):
        # sqlQuery = "Update PersonalDetails Set Address='" + address + "',phoneNumber='" + phone + "' where Cnp='" + cnp + "';"
        sql="Update Schedule Set ScheduleTime='"+ora+"',ScheduleDate='"+data+"' where cnp='"+cnp+"' and Specialization='"+spec+"';"
        succes=self.write_to_db(sql)
        return succes
    def remove_from_scheduled(self,cnp,spec,ora,data):
        sql="Delete from Schedule where cnp='"+cnp+"' and Specialization='"+spec+"' and ScheduleTime='"+ora+"' and ScheduleDate='"+data+"';"
        succes=self.write_to_db(sql)
        return succes
    def remove_from_personal_schedule(self,pacient_cnp,doc_spec,time,ziua,details):
        sql="Select FirstName,LastName from Person where cnp='"+pacient_cnp+"';"
        result=self.get_from_db(sql)
        sql="Delete from PersonalSchedule where LastName='"+result[0][1]+"' and FirstName='"+result[0][0]+"' and Specialization='"+doc_spec+"' and ScheduleTime='"+time+"' and ScheduleDate='"+ziua+"' and Details='"+details+"'"
        self.write_to_db(sql)
    def remove_service(self,serviceName):
        sql = "DELETE FROM Tarif where Service='"+serviceName+"';"
        self.write_to_db(sql)
    def get_price(self,service):
        sql="Select price from Tarif where service='"+service+"';"
        resutl=self.get_from_db(sql)
        return resutl[0][0]
    def modify_service(self,service,price):
        sql="UPDATE Tarif SET Price='"+price+"' where Service='"+service+"';"
        succes=self.write_to_db(sql)
        return succes
    def get_services(self):
        sql="Select * from Tarif;"
        result=self.get_from_db(sql)
        l_serv=[]
        full_list=[]
        for servis in result:
            l_serv.append(servis[0])
            l_serv.append(servis[1])
            full_list.append(l_serv)
            l_serv=[]
        return full_list

    def __create_connection(self):
        engine = create_engine('sqlite:///schema.db', echo=True,connect_args={"check_same_thread": False})
        conn=engine.connect()
        return conn

    def write_to_db(self, query):
        if path.exists('schema.db'):
            print('Schema is present!')
            try:
                if self.connection is not None:
                    self.connection.execute(query)
                    return True
                else:
                    self.connection=self.__create_connection()
                    self.connection.execute(query)
                    return True
            except sqlalchemy.exc.IntegrityError or sqlite3.IntegrityError:
                   print("This record exists in the table!")
                   return False
        else:
            print('Schema is missing!')
            self.__create_dataBase()
            self.write_to_db(query)

    def is_good_time(self,result,doctor_first_name,doctor_last_name,doctor_sepc,time_for_consult,date_for_consult):
        if(len(result)>0):
            ok=None
            for records in result:
                if(records[4]==doctor_first_name and records[3]==doctor_last_name and records[5]==doctor_sepc):
                    if(records[7]==date_for_consult  and records[6]==time_for_consult ):
                        ok=False

            if ok is not None:
                print("intra pe false")
                return False
            else:
                print("intra pe true")
                return True
        else:
            return True
    def write_schedule(self, pacient_cnp, doctor_first_name, doctor_last_name, doctor_specialization,time_for_consult,date_for_consult,details,tip):
        if (path.exists('schema.db')):
            print(doctor_first_name,doctor_last_name,doctor_specialization)
            sql="Select * from Schedule where Specialization='"+doctor_specialization+"' and FirstNameDoctor='"+doctor_last_name+"' and LastNameDoctor='"+doctor_first_name+"';"
            result=self.get_from_db(sql)
            print(pacient_cnp, doctor_first_name, doctor_last_name, doctor_specialization,time_for_consult,date_for_consult,details)
            is_ok=self.is_good_time(result,doctor_first_name,doctor_last_name,doctor_specialization,time_for_consult,date_for_consult)
            if(is_ok==True):
                pacient = self.get_from_db("Select * from person where cnp='"+pacient_cnp+"';")
                doctor = self.get_from_db('Select * from person where LastName="'+doctor_last_name+'" and FirstName="' + doctor_first_name+'";')
                spec = self.get_from_db("Select * from Specialization where cnp='"+doctor[0][2]+"' and Specialization='" + doctor_specialization+"';")
                print(pacient,doctor,spec)
                sql = "Insert into Schedule(Cnp,FirstName,LastName,FirstNameDoctor,LastNameDoctor,Specialization,ScheduleTime,ScheduleDate,Details,tipCerere) VALUES ('"+pacient[0][2]+"','"+pacient[0][0]+"','"+pacient[0][1]+"','"+doctor[0][0]+"','"+doctor[0][1]+"','"+spec[0][1]+"','"+time_for_consult+"','"+date_for_consult+"','"+details+"','"+tip+"');"
                self.connection.connect()
                self.connection.execute(sql)
                return True
            else:
                return False
        else:
            print('Schema is missing!')
            self.__create_dataBase()
            self.write_schedule(self, pacient_cnp, doctor_first_name, doctor_last_name, doctor_specialization)

    def get_schedule(self):
        sql="Select * from Schedule"
        result=self.get_from_db(sql)
        schduled_list=[]
        a_schedule=[]
        print(result)
        for schedules in result:
            for schedule in schedules:
                a_schedule.append(schedule)
            full_name=a_schedule[1]+" "+a_schedule[2]
            cnp=a_schedule[0]
            full_name_doc=a_schedule[3]+" "+a_schedule[4]
            spec=a_schedule[5]
            time=a_schedule[6]
            date=a_schedule[7]
            details=a_schedule[8]
            full_list=[]
            full_list.append(cnp)
            full_list.append(full_name)
            full_list.append(full_name_doc)
            full_list.append(spec)
            full_list.append(time)
            full_list.append(date)
            full_list.append(details)
            a_schedule=[]
            schduled_list.append(full_list)
        return schduled_list

    def insertDoctor(self,last_name,first_name,email,password,cnp):
        sql = "Insert INTO Person(LastName,FirstName,Cnp,Job,Email,Password) VALUES ('" + first_name + "','" + last_name + "','" + cnp + "','doctor','" + email + "','" + password + "');"
        self.write_to_db(sql)
    def insertSecretara(self,last_name,first_name,email,password,cnp):
        sql = "Insert INTO Person(LastName,FirstName,Cnp,Job,Email,Password) VALUES ('" + first_name + "','" + last_name + "','" + cnp + "','secretara','" + email + "','" + password + "');"
        self.write_to_db(sql)

    def insertAdmin(self,last_name,first_name,email,password,cnp=None):
        sql = "Insert INTO Person(LastName,FirstName,Cnp,Job,Email,Password) VALUES ('" + first_name + "','" + last_name + "','" + cnp + "','administrator','" + email + "','" + password + "');"
        self.write_to_db(sql)
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
        print(result)
        if len(result)>0:
            return result[0][3]
        return None
    def getCnp(self,username):
        sqlQuery = "SELECT * FROM PERSON WHERE email='" + username + "';"
        result = self.get_from_db(sqlQuery)
        print(result)
        if len(result)>0:
            return result[0][2]
        return None
    def get_personal_details(self,email):
        cnp=self.getCnp(email)
        if cnp:
            sql="Select * from Person where cnp='"+cnp+"';"
            resutPerson=self.get_from_db(sql)
            sql="Select * from PersonalDetails where cnp='"+cnp+"';"
            resutlPersonalDet=self.get_from_db(sql)
            if(len(resutPerson)>0 and len(resutlPersonalDet)==0):
                return resutPerson[0],resutlPersonalDet
            if(len(resutPerson)>0 and len(resutlPersonalDet)>0):
                return resutPerson[0],resutlPersonalDet[0]
        else:
            print("Record does not exist!")
    def save_changes(self):
        engine = create_engine('sqlite:///schema.db', echo=True,connect_args={"check_same_thread": False})
        self.connection = engine.connect()
        self.connection._commit_impl(autocommit=True)
        self.connection.close()
    def get_all_spec(self):
        sql="Select * from Specialization"
        resutl=self.get_from_db(sql)
        spec=[]
        if len(resutl)>0:
            for i in resutl:
                spec.append(i[1])
        spec=list(set(spec))
        return spec

    def get_person(self,cnp):
        sql="Select FirstName,LastName From Person where cnp='"+cnp+"';"
        result=self.get_from_db(sql)
        l=[]
        full=[]
        for persons in result:
            for person in persons:
                l.append(person)
            full.append(l)
        if(len(full)>0):
            return full

        return []

    def is_good_time_personal_schedule(self,result,doctor_sepc,time_for_consult,date_for_consult):
        if(len(result)>0):
            ok=None
            for records in result:
                if(records[2]==doctor_sepc):
                    if(records[4]==date_for_consult  and records[3]==time_for_consult ):
                        ok=False;
            if(ok is not None):
                return False
            else:
                return True
        else:
            return True

    def personal_schedule(self,first_name,last_name,spec,time,date,details):
        sql="Select * from PersonalSchedule;"
        result=self.get_from_db(sql)
        if(len(result)==0):
            sql = "Insert into PersonalSchedule(LastName,FirstName,Specialization,ScheduleTime,ScheduleDate,Details) VALUES('" + first_name + "','" + last_name + "','" + spec + "','" + time + "','" + date + "','" + details + "');"
            self.write_to_db(sql)
            return True
        is_ok=self.is_good_time_personal_schedule(result,spec,time,date)
        if(is_ok==True):
            sql="Insert into PersonalSchedule(LastName,FirstName,Specialization,ScheduleTime,ScheduleDate,Details) VALUES('"+first_name+"','"+last_name+"','"+spec+"','"+time+"','"+date+"','"+details+"');"
            self.write_to_db(sql)
            return True
        else:
            return False

    def get_personal_schedule(self):
        sql = "Select * from PersonalSchedule;"
        result = self.get_from_db(sql)
        schduled_list = []
        a_schedule = []
        print(result)
        for schedules in result:
            for schedule in schedules:
                a_schedule.append(schedule)
            first_name=a_schedule[1]
            last_name=a_schedule[0]
            sql="Select cnp from Person where FirstName='"+first_name+"' and LastName='"+last_name+"';"
            result=self.get_from_db(sql)
            cnp=result[0][0]
            full_name = a_schedule[0] + " " + a_schedule[1]
            spec = a_schedule[2]
            time = a_schedule[3]
            date = a_schedule[4]
            details = a_schedule[5]
            full_list = []
            full_list.append(cnp)
            full_list.append(full_name)
            full_list.append(spec)
            full_list.append(time)
            full_list.append(date)
            full_list.append(details)
            a_schedule = []
            schduled_list.append(full_list)
        return schduled_list
    def personal_details(self,cnp,first_name,last_name,email,address,phone):
        sqlQuery="Update Person Set FirstName='"+first_name+"',LastName='"+last_name+"',Email='"+email+"' Where Cnp='"+cnp+"';"
        self.write_to_db(sqlQuery)
        sqlQuery="Insert into PersonalDetails(Cnp,Address,phoneNumber) VALUES('"+cnp+"','"+address+"','"+phone+"');"
        if path.exists('schema.db'):
            print('Schema is present!')
            try:
                if self.connection is not None:
                    self.connection.execute(sqlQuery)
                else:
                    self.connection=self.__create_connection()
                    self.connection.execute(sqlQuery)
            except sqlalchemy.exc.IntegrityError or sqlite3.IntegrityError:
                   print("This record exists in the table attempt to update it!")
                   sqlQuery = "Update PersonalDetails set Address='"+address+"',phoneNumber='"+phone+"' where cnp='"+cnp+"'"

                   self.connection.execute(sqlQuery)
        else:
            print('Schema is missing!')
            self.__create_dataBase()
            self.write_to_db(sqlQuery)
    def get_doc_spec(self,spec):
        sql="Select cnp from Specialization where specialization='"+spec+"';"
        cnp=self.get_from_db(sql)[0][0]
        sql = "SELECT * FROM person where cnp='"+cnp+"';"
        result = self.get_from_db(sql)
        name_list = []
        for i in result:
            full_name = i[0] + " " + i[1]
            name_list.append(full_name)
        return name_list
    def get_dotors_for_secretary(self):
        sql='SELECT * FROM person where job="doctor";'
        result=self.get_from_db(sql)
        name_list=[]
        for i in result:
            full_name=i[0]+" "+i[1]
            name_list.append(full_name)
        return name_list

    def get_rights(self,email):
        sqlQuery = "SELECT * FROM PERSON WHERE email='" + email + "';"
        result = self.get_from_db(sqlQuery)
        job=result[0][3]
        return job
    def getUserName(self,username):
        sqlQuery="SELECT * FROM PERSON WHERE email='"+username+"';"
        result=self.get_from_db(sqlQuery)
        first_name=result[0][0]
        last_name=result[0][1]
        return first_name,last_name
    def deleteRecordFromPerson(self,cnp):
        sql="Delete from Person where cnp="+cnp+";"
        self.write_to_db(sql)
    def addSpecialization(self,cnp,spec,cellphone):
        sql = "Insert INTO Specialization(Cnp,Specialization,phoneNumber) VALUES ('"+cnp+"','"+spec+"','"+cellphone+"');"
        self.write_to_db(sql)
    def insertPacient(self,last_name,first_name,email,password,cnp):
        sql = "Insert INTO Person(LastName,FirstName,Cnp,Job,Email,Password) VALUES ('" + first_name + "','" + last_name + "','" + cnp + "','pacient','" + email + "','" + password + "');"
        self.write_to_db(sql)
    def get_staff(self,job):
        sql = "Select * from Person where job='"+job+"';"
        return self.get_from_db(sql)
    def doctor_specializations(self,cnp):
        sql = "Select * from Specialization where cnp='"+cnp+"';"
        return self.get_from_db(sql)
    def get_spec(self,cnp):
        sql = "Select Specialization from Specialization where cnp='" + cnp + "';"
        result=self.get_from_db(sql)
        return result[0][0]


def load():
    if path.exists('schema.db'):
        return
    else:
        d = DataBase()

        d.insertSecretara("Anca", "Hoinar", "anca.hoinar@gmail.com", "Admin123", "1900925303932")
        d.insertAdmin("Boros", "Larisa", "boros.larisa@gmail.com", "Admin123", "1890925303932")
        d.insertPacient("Cristian", "Pal", "cristian.pal@gmail.com", "Admin123", "1930925303932")
        d.insertDoctor("Laurentiu", "Girleanu", "laurentiu.girleanu@gmail.com", "Admin123", "1910925303932")
        d.insertDoctor("Ion", "Popescu", "ion.popescu@gmail.com", "Admin123", "1910924403932")
        d.addSpecialization("1910924403932", "Psiholog", "+40742451132")
        d.addSpecialization("1910925303932", "Neurolog", "+40742451132")
        d.add_services("ORL", "100")
        d.add_services("RMN", "400")
        d.add_services("Test Covid", "250")
        d.add_services("Spital", "10")
        d.add_services("Laborator", "100")
        d.add_services("Radiologie", "50")
        return
if __name__ == "__main__":

    load()

