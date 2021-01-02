import datetime
from functools import wraps
import jwt
from jwt import ExpiredSignatureError
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from dataBase import DataBase,load
import email_sender
app = Flask(__name__)

app.config['SECRET_KEY'] = b'_5#y2L"F4Q8z\n\xec]/'
app.config['Access-Control-Allow-Origin'] = '*'
CORS(app)
def monthToNum(shortMonth):

    return {
            'Jan' : "01",
            'Feb' : "02",
            'Mar' : "03",
            'Apr' : "04",
            'May' : "05",
            'Jun' : "06",
            'Jul' : "07",
            'Aug' : "08",
            'Sep' : "09",
            'Oct' : "10",
            'Nov' : "11",
            'Dec' : "12"
    }[shortMonth]

def convertDate(date):
    parts=date.split(" ")
    year=parts[3]
    day=parts[2]
    month=parts[1]
    month=monthToNum(month)
    date_conv=year+'-'+month+'-'+day
    return date_conv
def get_list_of_spec(l):
    l_spec=[]
    try:
        l_phone=l[0][2]
    except IndexError:
        l_phone=''
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
        staff_list=[]
        for i in rez:
            specialization=dataBase.doctor_specializations(i[2])
            l_spec,l_phone=get_list_of_spec(specialization)
            doctor={'firstName':i[0],'lastName':i[1],'cnp':i[2],'email':i[4],'specializations':l_spec,'phone':l_phone}
            staff_list.append(doctor)
        return jsonify({personal:staff_list})
@app.route('/get-spec',methods=['POST'])
def get_spec_of_a_doctor():
    if 'cnp' in request.headers:
        dataBase=DataBase()
        cnp=request.headers['cnp']
        result=dataBase.get_spec(cnp)
        return jsonify({"spec":result})
    return jsonify({"spec":" "})
@app.route('/get-doctors-secretary',methods=['POST'])
def get_doctors():
    dataBase=DataBase()
    names=dataBase.get_dotors_for_secretary()
    if(len(names)>0):
        return jsonify({"all_doctor_names": names})
    else:
        return jsonify({"all_doctor_names": []})


@app.route('/contact', methods=['POST'])
def contact():
    if "firstname" and "lastname" and "email"  and "subject" in request.headers:
        return jsonify({"message": "Thank you for you message"})
    return jsonify({"message": "Invalid request"})

@app.route('/forgot-password', methods=['POST'])
def resetPass():
    if "email" in request.headers and request.headers['email'] != '':
        email=request.headers['email']
        dataBase=DataBase()
        result=dataBase.get_personal_details(email)
        print(result)
        if(len(result)>0):
            email=result[0][4]
            passwd=result[0][5]
            try:
                email_sender.recoverPassword(email,passwd)
            except Exception:
                print("can not send email :(")
            return jsonify({'message': 'You will receive a email with instructions'})
    return jsonify({'message': "Invalid request"})

@app.route('/create-doctor',methods=['POST'])
def register_doctor():
    if "first_name" and "last_name" and "email"  and "cnp" and "spec" and "cellphone" and "password" in request.headers:
        first_name = request.headers['first_name']
        last_name=request.headers['last_name']
        email = request.headers['email']
        password = request.headers['password']
        cnp = request.headers['cnp']
        phone=request.headers['cellphone']
        spec=request.headers['spec']
        dataBase=DataBase()
        dataBase.insertDoctor(last_name,first_name,email,password,cnp)
        dataBase.addSpecialization(cnp,spec,phone)
        if dataBase.checkUser(email, password):
            return jsonify({"message":"account created succesfully!"})
        return jsonify({'message':'something went wrong.. :('})
@app.route('/get-doctor-spec',methods=['POST'])
def get_doc_spec():
    if "spec" in request.headers:
        dataBase = DataBase()
        spec=request.headers['spec']
        names = dataBase.get_doc_spec(spec)
        if (len(names) > 0):
            return jsonify({"all_doctor_names": names})
        else:
            return jsonify({"all_doctor_names": []})
@app.route('/write-schedule',methods=['POST'])
def register_schedule():
    if "pacient_cnp" and "doctor_fullname" and "doctor_spec" and "date_for_consult" and "time_for_consult" and "details" and 'cerere' in request.headers:

        pacient_cnp=request.headers['pacient_cnp']
        print(request.headers)
        doctor_fullname=request.headers['doctor_fullname']
        full_name=doctor_fullname.split(" ")
        doc_firstname=full_name[0]
        doc_lastname=full_name[1]
        doc_spec=request.headers['doctor_spec']
        print(doc_spec)
        details=request.headers['details']
        time=request.headers['time_for_consult']
        ziua_raw=request.headers['date_for_consult']
        tip=request.headers['cerere']
        if(len(ziua_raw)>10):
            ziua=convertDate(request.headers['date_for_consult'])
        else:
            ziua=ziua_raw
        dataBase=DataBase()
        success=dataBase.write_schedule(pacient_cnp,doc_lastname,doc_firstname,doc_spec,time,ziua,details,tip)
        dataBase.remove_from_personal_schedule(pacient_cnp,doc_spec,time,ziua,details)
        if success:
            return jsonify({"message":"Programarea a fost cu succes, va asteptam!","color":"green"})
        return jsonify({'message':'Timpul sau data a fost deja rezervata, Va rugam sa alegiti o alta perioada/data!',"color":"red"})
@app.route('/get-schedule',methods=['POST'])
def get_scheduled():
    dataBase=DataBase()
    result=dataBase.get_schedule()
    if(len(result)>0):
        return jsonify({"scheduled":result})
    else:
        return jsonify({"scheduled":[]})
@app.route('/get-services',methods=['POST'])
def get_services():
    dataBase=DataBase()
    service=dataBase.get_services()
    if(len(service)>0):
        return jsonify({"services":service})
    else:
        return jsonify({"services":[]})


@app.route('/add-services',methods=['POST'])
def add_service():
    if "service_name" and "price" in request.headers:
        service=request.headers["service_name"]
        price=request.headers['price']
        dataBase=DataBase()
        succes=dataBase.add_services(service,price)
        if succes:
            return jsonify({"message":"Serviciul a fost adaugat cu succes!"})
        return jsonify({"message":"Database error!"})
@app.route('/modify-scheduled',methods=['POST'])
def modify_scheduled():
    if "cnp" and "spec" and "ora" and "data"  in request.headers:
        cnp=request.headers['cnp']
        spec=request.headers['spec']
        ora=request.headers['ora']
        data=request.headers['data']
        database=DataBase()
        suc=database.update_schedule(cnp,spec,ora,data)
        if suc:
            return jsonify({"message":"programarea a fost anulata cu succes!"})
        return jsonify({"message":"Database error!"})
@app.route('/remove-scheduled',methods=['POST'])
def remove_scheduled():
    if "cnp" and "spec" and "ora" and "data"  in request.headers:
        cnp=request.headers['cnp']
        spec=request.headers['spec']
        ora=request.headers['ora']
        data=request.headers['data']
        database=DataBase()
        print("Se apeleaza!!!!!")
        suc=database.remove_from_scheduled(cnp,spec,ora,data)
        if suc:
            return jsonify({"message":"programarea a fost anulata cu succes!"})
        return jsonify({"message":"Database error!"})
@app.route('/remove-services',methods=['POST'])
def remove_service():
    if 'service_name' in request.headers:
        service=request.headers['service_name']
        dataBase=DataBase()
        succes=dataBase.remove_service(service)
        if succes:
            return jsonify({"message":"Serviciu anulat cu succes!"})
        else:
            return jsonify({"message":"Database error!"})
@app.route('/ajust-services',methods=['POST'])
def modify_service():
    if 'servicii' in request.headers:
        all_services=request.headers['servicii']
        print(all_services)
        service_name = ""
        price = ""
        l_service = []
        l_price = []
        all_services = all_services.split(',')
        for i in range(len(all_services)):
            if i % 2 == 0:
                l_service.append(all_services[i])
            else:
                l_price.append(all_services[i])

        for i in range(len(l_service)):
            database=DataBase()
            succes=database.modify_service(l_service[i],l_price[i])
        if succes:
            return jsonify({"message":"Serviciul a fost modificat cu succes!"})
        else:
            return jsonify({"message":"Database error!"})

@app.route('/tax-services',methods=['POST'])
def taxt_service():
    if "cnp" and "servicii" and "time" and "data" in request.headers:
        cnp=request.headers['cnp']
        servicii=request.headers['servicii']
        time=request.headers['time']
        date=request.headers['data']
        pret=0
        service=''
        dataBase=DataBase()
        servicii = servicii.split(',')
        for i in servicii:
            pret+=int(dataBase.get_price(i))
            service+=i+','
        service=service[:-1]
        print("ASTEA se insereaza",cnp,servicii,pret,time,date)
        succes=dataBase.final_price(cnp,service,str(pret),time,date)
        if succes:
            return jsonify({"message":"facturare cu succes!"})
        else:
            return jsonify({"message":"database error!"})


@app.route('/get-schedule-per-doctor',methods=['POST'])
def get_schedule_per_doctor():
    if "cnp" in request.headers:
        doctor_cnp=request.headers['cnp']
        dataBase=DataBase()
        list_pacients=dataBase.get_all_pacients(doctor_cnp)
        if(len(list_pacients)>0):
            return jsonify({"pacients":list_pacients})
        else:
            return jsonify({"pacients":[]})

@app.route('/get-schedule-per-doctor-2',methods=['POST'])
def get_schedule_per_doctor_2():
    if "cnp" in request.headers:
        doctor_cnp=request.headers['cnp']
        dataBase=DataBase()
        list_pacients=dataBase.get_all_pacients_2(doctor_cnp)
        if(len(list_pacients)>0):
            return jsonify({"pacients":list_pacients})
        else:
            return jsonify({"pacients":[]})



@app.route('/get-personal-schedule',methods=['POST'])
def get_personal_scheduled():
    dataBase=DataBase()
    result=dataBase.get_personal_schedule()
    if(len(result)>0):
        return jsonify({"scheduled":result})
    else:
        return jsonify({"scheduled":[]})

@app.route('/get-person',methods=['POST'])
def get_person():
    if 'cnp' in request.headers:
        cnp=request.headers['cnp']
        dataBase=DataBase()
        result=dataBase.get_person(cnp)
        if(len(result)>0):
            return jsonify({"person":result})
        else:
            return jsonify({"person":[]})

@app.route('/register-secretary',methods=['POST'])
def register_secretary():
    if "first_name" and "last_name" and "email" and "cnp" and "cellphone" and "password"  in request.headers:
        first_name = request.headers['first_name']
        last_name = request.headers['last_name']
        email = request.headers['email']
        password = request.headers['password']
        cnp = request.headers['cnp']
        phone = request.headers['cellphone']
        address=""
        dataBase=DataBase()
        dataBase.insertSecretara(last_name, first_name, email, password, cnp)
        dataBase.personal_details(cnp, first_name, last_name, email, address, phone)
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
        dataBase.insertPacient(lastName,firstName,email,password,cnp)
        if dataBase.checkUser(email, password):
            return jsonify({"message":"account created succesfully!"})
        return jsonify({'message':'something went wrong.. :('})

@app.route('/add-foaie-consult',methods=['POST'])
def add_foaie_consult():
    if 'cnp' and 'nume' and 'addp' and 'sp' and 'dp' and 'fdoc' and 'ldoc' and 'p' and 'service' and 'ora' and 'data' in request.headers:
        cnp=request.headers['cnp']
        nume=request.headers['nume']
        fn,ln=nume.split(" ")
        addp=request.headers['addp']
        sp=request.headers['sp']
        dp=request.headers['dp']
        fdoc=request.headers['fdoc']
        ldoc=request.headers['ldoc']
        serv=request.headers['service']
        p=request.headers['p']
        ora=request.headers['ora']
        data=request.headers['data']
        dataBase=DataBase()
        s=dataBase.eliberare_scrisoare(cnp,ln,fn,addp,sp,dp,fdoc,ldoc,p,serv,ora,data)
        if s:
            return jsonify({"message":"Consultul a fost finalizat cu succes!"})
        return jsonify({'message':'something went wrong.. :('})



# (self,cnp_p,l_n,f_n,add_p,s_p,di_p,f_doc,l_doc,pret)
@app.route('/get-all-consults',methods=['POST'])
def get_all_consults():
    dataBase=DataBase()
    result=dataBase.get_all_scrisori()
    return jsonify({"consults":result})

@app.route('/get-all-trimiteri',methods=['POST'])
def get_all_trimiteri():
    dataBase=DataBase()
    result=dataBase.get_all_trimiteri()
    return jsonify({"consults":result})

@app.route('/get-all-personal-consults',methods=['POST'])
def get_all_consults2():
    if 'cnp' in request.headers:
        cnp=request.headers['cnp']
        dataBase=DataBase()
        result=dataBase.get_all_scrisori2(cnp)
        return jsonify({"consults":result})
    return jsonify({'consults':[]})

@app.route('/get-all-personal-trimiteri',methods=['POST'])
def get_all_trimiteri2():
    if 'cnp' in request.headers:
        cnp=request.headers['cnp']
        dataBase=DataBase()
        result=dataBase.get_all_trimiteri2(cnp)
        return jsonify({"consults":result})
    return jsonify({'consults': []})

@app.route('/load-personal-details',methods=['POST'])
def getPersonalDetails():
    if "email" in request.headers:
        email=request.headers['email']
        database=DataBase()
        person, personal = database.get_personal_details(email)
        if len(person)>0 and len(personal)==0:
            return jsonify({"first_name":person[0],"last_name":person[1],"cnp":person[2],"email":person[4],"address":'',"phone":''})
        if len(person)>0 and len(personal)>0:
            return jsonify({"first_name":person[0],"last_name":person[1],"cnp":person[2],"email":person[4],"address":personal[1],"phone":personal[2]})

    return make_response({'message': 'Something went wrong'}, 401)

@app.route('/get-specializations',methods=['POST'])
def get_spec():
    database=DataBase()
    l_spec=database.get_all_spec()
    if len(l_spec)>0:
        return jsonify({"spectializations": l_spec})
    else:
        return make_response({'message': 'No specialization present in the database'}, 401)


@app.route('/change-personal-details',methods=['POST'])
def change_personal_details():
    if "first_name" and "last_name" and "email" and "address" and "phone" in request.headers:
        database=DataBase()
        first_name=request.headers['first_name']
        last_name=request.headers['last_name']
        email=request.headers['email']
        address=request.headers['address']
        phone=request.headers['phone']
        cnp=database.getCnp(email)
        database.personal_details(cnp,first_name,last_name,email,address,phone)
        if first_name and last_name and email:
            return jsonify({"first_name": first_name, "last_name": last_name, "email": email, "address": address,
                                "phone": phone})


    return make_response({'message': 'Something went wrong'}, 401)

@app.route('/personal-schedule',methods=['POST'])
def personal_schedule():
    if "first_name" and "last_name" and "spec" and "ziua" and "time" and "details" in request.headers:
        f_name=request.headers['first_name']
        l_name=request.headers['last_name']
        spec=request.headers['spec']
        date=convertDate(request.headers['ziua'])
        time=request.headers['time']
        details=request.headers['details']
        database=DataBase()
        success=database.personal_schedule(f_name,l_name,spec,time,date,details)
        if success:
            return jsonify({"message": "Programarea a fost cu succes!", "color": "green"})
        return jsonify({'message': 'Timpul sau data a fost deja rezervata, Va rugam sa alegiti o alta perioada/data!',
                        "color": "red"})
    return make_response({'message': 'Something went wrong'}, 401)

@app.route('/check-rights',methods=['POST'])
def check():
    if "email" in request.headers:
        email=request.headers['email']
        print(email)
        database=DataBase()
        rights=database.get_rights(email)
        if rights is not None:
            return jsonify({"rights":rights})
    return make_response({'message': 'Invalid user role check!'}, 401)


@app.route('/login', methods=['POST'])
def login():
    if "username" and "password" in request.headers:
        username = request.headers['username']
        password = request.headers['password']
        dataBase = DataBase()
        tokenValability = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        if not dataBase.checkUser(username, password):
            return make_response({'message': 'Invalid username or password'}, 401)
        user_rights=dataBase.checkJob(username, password)
        first_name,last_name=dataBase.getUserName(username)
        # full_Name=first_name+" "+last_name

        token = jwt.encode({'USER_KEY': username, 'exp': tokenValability},
                           app.config['SECRET_KEY'])
        return jsonify({'accessToken': token.decode('UTF-8'), 'USER_KEY': username, 'USER_ROLE':user_rights})
    return make_response({'message': 'Invalid credentials'}, 401)


if __name__ == "__main__":
  app.run(debug=True)
  notload=True
  if notload:
      load()
      notload=False
