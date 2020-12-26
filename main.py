import datetime
from functools import wraps
import jwt
from jwt import ExpiredSignatureError
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

from dataBase import DataBase

app = Flask(__name__)

app.config['SECRET_KEY'] = b'_5#y2L"F4Q8z\n\xec]/'
app.config['Access-Control-Allow-Origin'] = '*'
CORS(app)

def get_list_of_spec(l):
    l_spec=[]
    l_phone=l[0][2]
    for i in l:
        l_spec.append(i[1])
    return l_spec,l_phone
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = data['USER_KEY']
        except ExpiredSignatureError:
            return make_response({'message': 'Expired token, please login again'}), 401
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/get-all-staff',methods=['POST'])
def get_staff():
    if "staff" in request.headers:
        personal=request.headers['staff']
        dataBase=DataBase()
        rez=dataBase.get_staff(personal)
        counter=0
        doctor_list=[]
        doctor={}
        for i in rez:
            specialization=dataBase.doctor_specializations(i[2])
            l_spec,l_phone=get_list_of_spec(specialization)
            doctor[personal+str(counter)]={'firstName':i[0],'lastName':i[1],'cnp':i[2],'email':i[4],'specializations':l_spec,'phone':l_phone}
            counter+=1
            doctor_list.append(doctor)
            doctor={}
        print(doctor_list)
        return jsonify({personal:doctor_list})

@app.route('/contact', methods=['POST'])
def contact():
    if "firstname" and "lastname" and "email"  and "subject" in request.headers:
        return jsonify({"message": "Thank you for you message"})
    return jsonify({"message": "Invalid request"})


@app.route('/create-doctor',methods=['POST'])
def register_client():
    if "fullname" and "email" and "password" and "cnp" and "spec" and "cellphone" in request.headers:
        fullname = request.headers['fullname']
        email = request.headers['email']
        password = request.headers['password']
        cnp = request.headers['cnp']
        phone=request.headers['cellphone']
        spec=request.headers['spec']
        dataBase=DataBase()
        if dataBase.checkJob(email,password):
            return jsonify({'message':"email already exists"})
        firstName,lastName=fullname.split(" ")
        job='doctor'
        dataBase.insertDoctor(lastName,firstName,cnp,job,email,password)
        dataBase.addSpecialization(cnp,spec,phone)
        if dataBase.checkUser(email, password):
            return jsonify({"message":"account created succesfully!"})
        return jsonify({'message':'something went wrong.. :('})
    # def write_schedule(self, pacient_cnp, doctor_first_name, doctor_last_name, doctor_specialization):


@app.route('/write_schedule',methods=['POST'])
def register_client():
    if "pacient_cnp" and "doctor_firstname" and "doctor_lastname" and "doctor_spec" in request.headers:
        pacient_cnp=request.headers['pacient_cnp']
        doc_firstname=request.headers['doctor_firstname']
        doc_lastname=request.headers['doctor_lastname']
        doc_spec=request.headers['doctor_spec']
        dataBase=DataBase()
        success=dataBase.write_schedule(pacient_cnp,doc_firstname,doc_lastname,doc_spec)
        if success:
            return jsonify({"message":"account created succesfully!"})
        return jsonify({'message':'something went wrong.. :('})

@app.route('/register-secretary',methods=['POST'])
def register_client():
    if "fullname" and "email" and "password" and "cnp" in request.headers:
        fullname = request.headers['fullname']
        email = request.headers['email']
        password = request.headers['password']
        cnp = request.headers['cnp']
        dataBase=DataBase()
        if dataBase.checkJob(email,password):
            return jsonify({'message':"email already exists"})
        firstName,lastName=fullname.split(" ")
        job='secretary'
        dataBase.insertPacient(lastName,firstName,cnp,job,email,password)
        if dataBase.checkUser(email, password):
            return jsonify({"message":"account created succesfully!"})
        return jsonify({'message':'something went wrong.. :('})

@app.route('/register-client',methods=['POST'])
def register_client():
    if "fullname" and "email" and "password" and "cnp" in request.headers:
        fullname = request.headers['fullname']
        email = request.headers['email']
        password = request.headers['password']
        cnp = request.headers['cnp']
        dataBase=DataBase()
        if dataBase.checkJob(email,password):
            return jsonify({'message':"email already exists"})
        firstName,lastName=fullname.split(" ")
        job='pacient'
        dataBase.insertPacient(lastName,firstName,cnp,job,email,password)
        if dataBase.checkUser(email, password):
            return jsonify({"message":"account created succesfully!"})
        return jsonify({'message':'something went wrong.. :('})

@app.route('/login', methods=['POST'])
def login():
    if "username" and "password" in request.headers:
        username = request.headers['username']
        password = request.headers['password']
        print(username,password)
        dataBase = DataBase()
        tokenValability = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        """
        check for user in database
        """
        if not dataBase.checkUser(username, password):
            print('no user')
            return make_response({'message': 'Invalid username or password'}, 401)
        """
        check for user rights in datebase
        """
        user_rights=dataBase.checkJob(username, password)
        """
        if everything is true
        then
        """
        first_name_last_name=username.split("@")[0].split(".")
        first_name=first_name_last_name[0]
        last_name=first_name_last_name[1]
        full_Name=first_name+" "+last_name
        token = jwt.encode({'USER_KEY': username, 'exp': tokenValability},
                           app.config['SECRET_KEY'])
        return jsonify({'accessToken': token.decode('UTF-8'), 'USER_KEY': full_Name})
    return make_response({'message': 'Invalid credentials'}, 401)


if __name__ == "__main__":
  app.run(debug=True)