from flask import Flask, render_template, request 
from datetime import date
import json
from web3 import Web3, HTTPProvider
import os


app = Flask(__name__)

UPLOAD_FOLDER = 'static/report'
global userid, hospital, pnameValue, pdateValue

def readDetails(contract_type):
    global details
    details = ""
    print(contract_type+"======================")
    blockchain_address = 'http://127.0.0.1:8545' #Blokchain connection IP
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'Report.json' 
    deployed_contract_address = '0x607ba269A1d3b2ea5EA552BAF8554faB0C2f66a9' #hash address to access EHR contract
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi) #now calling contract to access data
    if contract_type == 'hospital':
        details = contract.functions.getHospital().call() #call getHospital function to access all hospital details
    if contract_type == 'patient':
        details = contract.functions.getPatient().call()
    if contract_type == 'prescription':
        details = contract.functions.getPrescription().call()    
    print(details)    

def saveDataBlockChain(currentData, contract_type):
    global details
    global contract
    details = ""
    blockchain_address = 'http://127.0.0.1:8545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'Report.json' 
    deployed_contract_address = '0x607ba269A1d3b2ea5EA552BAF8554faB0C2f66a9' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    readDetails(contract_type)
    if contract_type == 'hospital':
        details+=currentData
        msg = contract.functions.setHospital(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'patient':
        details+=currentData
        msg = contract.functions.setPatient(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'prescription':
        details+=currentData
        msg = contract.functions.setPrescription(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)

def getPrescription(pname, pdate):
    global details
    readDetails("prescription")
    rows = details.split("\n")
    output = "Pending"
    doctor = "Pending"
    for i in range(len(rows)-1):
        arr = rows[i].split("#")
        if arr[0] == "prescription":
            if arr[1] == pname and arr[2] == pdate:
                output = arr[3]
                doctor = arr[4]
    return output, doctor

@app.route('/Prescription', methods=['GET','POST'])
def Prescription():
    if request.method == 'GET':
        global pnameValue, pdateValue
        pnameValue = request.args.get('pname')
        pdateValue = request.args.get('pdate')
        print(pnameValue+" "+pdateValue)
        context= "Patient Name: "+pnameValue
        return render_template('Prescription.html', data=context)


@app.route('/PrescriptionAction', methods=['POST'])
def PrescriptionAction():
    global pnameValue, pdateValue, userid
    prescription = request.form['t1']
    today = date.today()
    data = "prescription#"+pnameValue+"#"+pdateValue+"#"+prescription+"#"+userid+"#"+str(today)+"\n"
    saveDataBlockChain(data,"prescription")
    context= 'Prescription details added'
    return render_template('DoctorScreen.html', data=context) 

@app.route('/ViewPatientReport', methods=['GET','POST'])
def ViewPatientReport():
    if request.method == 'GET':
        global hospital
        readDetails("patient")
        rows = details.split("\n")
        output = ""
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "patient":
                temp = arr[4].split(",")
                flag = 0
                for k in range(len(temp)):
                    if temp[k] == hospital:
                        flag = 1
                        break
                if flag == 1:
                    prescription, doctor = getPrescription(arr[1],arr[6])
                    output+='<tr><td><font size="" color="black">'+str(arr[1])+'</td>'
                    output+='<td><font size="" color="black">'+str(arr[2])+'</td>'
                    output+='<td><font size="" color="black">'+str(arr[3])+'</td>'
                    output+='<td><font size="" color="black">'+str(arr[4])+'</td>'
                    output+='<td><font size="" color="black">'+str(arr[5])+'</td>'
                    output+='<td><font size="" color="black">'+str(arr[6])+'</td>'
                    output+='<td><img src="/static/reports/'+arr[5]+'" width="200" height="200"></img></td>'
                    output+='<td><font size="" color="black">'+prescription+'</td>'
                    output+='<td><font size="" color="black">'+doctor+'</td>'
                    if prescription == "Pending":
                        output+='<td><a href=\'Prescription?pname='+arr[1]+'&pdate='+arr[6]+'\'><font size=3 color=black>Click Here</font></a></td></tr>'
                    else:
                        output+='<td><font size="" color="black">Prescription Already Generated</td></tr>'
        
        return render_template('ViewPatientReport.html', data=output)  


    
@app.route('/ViewHealth', methods=['GET','POST'])
def ViewHealth():
    if request.method == 'GET':
        global userid
        readDetails("patient")
        rows = details.split("\n")
        output = ""
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "patient" and arr[1] == userid:
                prescription, doctor = getPrescription(arr[1],arr[6])
                output+='<tr><td><font size="" color="black">'+str(arr[1])+'</td>'
                output+='<td><font size="" color="black">'+str(arr[2])+'</td>'
                output+='<td><font size="" color="black">'+str(arr[3])+'</td>'
                output+='<td><font size="" color="black">'+str(arr[4])+'</td>'
                output+='<td><font size="" color="black">'+str(arr[5])+'</td>'
                output+='<td><font size="" color="black">'+str(arr[6])+'</td>'
                output+='<td><img src="/static/reports/'+arr[5]+'" width="200" height="200"></img></td>'
                output+='<td><font size="" color="black">'+prescription+'</td>'
                output+='<td><font size="" color="black">'+doctor+'</td>'
        
        return render_template('ViewHealth.html', data=output) 


@app.route('/ViewPatientHospital', methods=['GET', 'POST'])
def ViewPatientHospital():
    if request.method == 'GET':
        readDetails("hospital")
        rows = details.split("\n")
        output = ""
        for i in range(len(rows)-1):
            row = rows[i].split("#")
            if row[0] == "hospital":
                output+='<tr><td><font size="" color="black">'+str(row[1])+'</td>'
                output+='<td><font size="" color="black">'+str(row[2])+'</td>'
                output+='<td><font size="" color="black">'+str(row[3])+'</td>'
                output+='<td><font size="" color="black">'+str(row[4])+'</td>'
                output+='<td><font size="" color="black">'+str(row[5])+'</td>'
                output+='<td><font size="" color="black">'+str(row[6])+'</td>'
                output+='<td><font size="" color="black">'+str(row[7])+'</td>'
                output+='<td><font size="" color="black">'+str(row[8])+'</td>'
               
                
        
        return render_template('ViewPatientHospital.html', data=output)


@app.route('/AddHealthAction', methods=['POST'])
def AddHealthAction():
    if request.method == 'POST':
        age = request.form.get('t1', False)
        symptoms = request.form.get('t2', False)
        file = request.files['t3']
        filename = file.filename
        print("@@ Input posted = ", filename)
        file_path = os.path.join('static/reports/', filename)
        file.save(file_path)
        hospitals = request.form.getlist('t4')
        hospitals = ','.join(hospitals)
        today = date.today()

                
        data = "patient#"+userid+"#"+age+"#"+symptoms+"#"+hospitals+"#"+filename+"#"+str(today)+"\n"
        saveDataBlockChain(data, "patient")
                
        context = 'Your report shared with ' + hospitals
        return render_template('PatientScreen.html', data=context)
    



@app.route('/AddHealth', methods=['GET'])
def AddHealth():
    if request.method == 'GET':
        output = ""
        names = []
        readDetails("hospital")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "hospital":
                if arr[8] not in names:
                    names.append(arr[8])
                    output += '<option value="'+arr[8]+'">'+arr[8]+'</option>'
                    
        return render_template('AddHealth.html', data1=output)



@app.route('/ViewHospitalDetails', methods=['GET'])
def ViewHospitalDetails():
    if request.method == 'GET':
        readDetails("hospital")
        rows = details.split("\n")
        output = ""
        for i in range(len(rows)-1):
            row = rows[i].split("#")
            if row[0] == "hospital":
                output+='<tr><td><font size="" color="black">'+str(row[1])+'</td>'
                output+='<td><font size="" color="black">'+str(row[2])+'</td>'
                output+='<td><font size="" color="black">'+str(row[3])+'</td>'
                output+='<td><font size="" color="black">'+str(row[4])+'</td>'
                output+='<td><font size="" color="black">'+str(row[5])+'</td>'
                output+='<td><font size="" color="black">'+str(row[6])+'</td>'
                output+='<td><font size="" color="black">'+str(row[7])+'</td>'
                output+='<td><font size="" color="black">'+str(row[8])+'</td>'
                                
        
        return render_template('ViewHospitalDetails.html', data=output)



@app.route('/AdminLoginAction', methods=['GET','POST'])
def AdminLoginAction():
    if request.method == 'POST':
        global userid
        user = request.form['t1']
        password = request.form['t2']
        if user == "admin" and password == "admin":
            context= 'Welcome '+user
            return render_template('AdminScreen.html', data=context)
        else:
            context= 'Invalid Login'
            return render_template('AdminLogin.html', data=context)

        


@app.route('/PatientSignupAction', methods=['GET', 'POST'])
def PatientSignupAction():
    if request.method == 'POST':
        user = request.form['t1']
        password = request.form['t2']
        email = request.form['t3']
        contact = request.form['t4']
        address = request.form['t5']
        record = 'none'
        readDetails("patient")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "signup":
                if arr[1] == user:
                    record = "exists"
                    break
        if record == 'none':
            data = "signup#"+user+"#"+password+"#"+contact+"#"+email+"#"+address+"\n"
            saveDataBlockChain(data,"patient")
            context= 'Signup process completd and record saved in Blockchain'
            return render_template('PatientSignup.html', data=context)
        else:
            context= user+' Username already exists'
            return render_template('PatientSignup.html', data=context) 



@app.route('/PatientLoginAction', methods=['GET', 'POST'])
def PatientLoginAction():
    if request.method == 'POST':
        global userid
        user = request.form['t1']
        password = request.form['t2']
        status = 'none'
        readDetails("patient")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "signup":
                if arr[1] == user and arr[2] == password:
                    status = 'success'
                    userid = user
                    break
        if status == 'success':
            file = open('session.txt','w')
            file.write(user)
            file.close()
            context= "Welcome "+user
            return render_template('PatientScreen.html', data=context)
        else:
            context= 'Invalid login details'
            return render_template('PatientLogin.html', data=context) 


@app.route('/AddDoctorAction', methods=['GET', 'POST'])
def AddDoctorAction():
    if request.method == 'POST':
        user = request.form['t1']
        password = request.form['t2']
        email = request.form['t3']
        contact = request.form['t4']
        qualification = request.form['t5']
        experience = request.form['t6']
        hospital = request.form['t7']
        address = request.form['t8']
        record = 'none'
        readDetails("hospital")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "hospital":
                if arr[1] == user:
                    record = "exists"
                    break
        if record == 'none':
            data = "hospital#"+user+"#"+password+"#"+contact+"#"+email+"#"+address+"#"+qualification+"#"+experience+"#"+hospital+"\n"
            saveDataBlockChain(data,"hospital")
            context= 'New Doctor & Hospital details saved in Blockchain'
            return render_template('AddDoctor.html', data=context)
        else:
            context= username+' Username already exists'
            return render_template('AddDoctor.html', data=context)
        
@app.route('/DoctorLoginAction', methods=['GET', 'POST'])
def DoctorLoginAction():
    if request.method == 'POST':
        global userid, hospital
        user = request.form['t1']
        password = request.form['t2']
        status = 'none'
        readDetails("hospital")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "hospital":
                if arr[1] == user and arr[2] == password:
                    status = 'success'
                    userid = user
                    hospital = arr[8]
                    break
        if status == 'success':
            file = open('session.txt','w')
            file.write(user)
            file.close()
            context= "Welcome "+user
            return render_template('DoctorScreen.html', data=context)
        else:
            context= 'Invalid login details'
            return render_template('DoctorLogin.html', data=context)




@app.route('/AddDoctor', methods=['GET', 'POST'])
def AddDoctor():
    if request.method == 'GET':
       return render_template('AddDoctor.html', msg='')


@app.route('/AddHealth', methods=['GET', 'POST'])
def AddHealths():
    if request.method == 'GET':
       return render_template('AddHealth.html', msg='')

@app.route('/AdminLogin', methods=['GET', 'POST'])
def AdminLogin():
    if request.method == 'GET':
       return render_template('AdminLogin.html', msg='')

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
       return render_template('index.html', msg='')

@app.route('/AdminScreen', methods=['GET', 'POST'])
def AdminScreen():
    if request.method == 'GET':
       return render_template('AdminScreen.html', msg='')

@app.route('/DoctorLogin', methods=['GET', 'POST'])
def DoctorLogin():
    if request.method == 'GET':
       return render_template('DoctorLogin.html', msg='')

@app.route('/DoctorScreen', methods=['GET', 'POST'])
def DoctorScreen():
    if request.method == 'GET':
       return render_template('DoctorScreen.html', msg='')

@app.route('/PatientLogin', methods=['GET', 'POST'])
def PatientLogin():
    if request.method == 'GET':
       return render_template('PatientLogin.html', msg='')

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
       return render_template('index.html', msg='')

@app.route('/PatientScreen', methods=['GET', 'POST'])
def PatientScreen():
    if request.method == 'GET':
       return render_template('PatientScreen.html', msg='')
    
@app.route('/PatientSignup', methods=['GET', 'POST'])
def PatientSignup():
    if request.method == 'GET':
       return render_template('PatientSignup.html', msg='')

@app.route('/Prescription', methods=['GET', 'POST'])
def Prescriptions():
    if request.method == 'GET':
       return render_template('Prescription.html', msg='')

@app.route('/ViewHealth', methods=['GET', 'POST'])
def ViewHealths():
    if request.method == 'GET':
       return render_template('ViewHealth.html', msg='')

@app.route('/ViewHospitalDetails', methods=['GET', 'POST'])
def ViewHospitalDetailss():
    if request.method == 'GET':
       return render_template('ViewHospitalDetails.html', msg='')

@app.route('/ViewPatientHospital', methods=['GET', 'POST'])
def ViewPatientHospitals():
    if request.method == 'GET':
       return render_template('ViewPatientHospital.html', msg='')

@app.route('/ViewPatientReport', methods=['GET', 'POST'])
def ViewPatientReports():
    if request.method == 'GET':
       return render_template('ViewPatientReport.html', msg='')





            
        
if __name__ == '__main__':
    app.run()       
