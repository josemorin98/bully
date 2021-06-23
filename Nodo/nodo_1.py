from flask import Flask, request
from flask import Response
from flask import jsonify
import json
import threading
import requests
import sys
import queue
import time


app = Flask(__name__)
app.debug = True

# Recibir los parametros
arg = sys.argv
# Estados del nodo
id_nodo = int(arg[1]) # ID posicion 1
election = False
puerto_nodo = arg[2] # Puerto del contenedor
puertos = arg[3].split(',') # Lista de puertos
# Datos del coordinador
puerto_cor = 0
id_cor = 0
without_coordina = False
puertos_kill = []
verificar = False

# Verifica si es el coordinador
if (arg[4] == '1'):
    coordina = True
    id_cor = id_nodo
else:
    coordina = False

pet =0
# Recibe los datos del nuevo coordinador
@app.route('/COORDINATOR', methods = ['POST'])
def fun_coordinator():
    global puerto_cor
    global pet
    global election
    message = request.get_json()
    puerto_cor = message['puerto']
    id_cor = message['id']
    app.logger.error('------ COORDINATOR '+str(id_cor)+' ------')
    election = False
    without_coordina = False
    pet =0
    # Comienza el proceso de verificacion
    monitor = threading.Thread(target=fun_verificar)
    monitor.start()
        
    return jsonify({'response':'RECIBIDO'})

# Hace el proceso de election
@app.route('/ELECTION',methods = ['POST'])
def fun_election():
    global election
    if (election==True):
        # Recibi el post
        message = request.get_json()
        # Id y puerto del nodo que hace peticion de election
        id_vecino = message['id']
        port_nodo = message['puerto']
        # app.logger.error('------ ELECTION CON EL NODO '+str(id_vecino) + ' ------')
        # Si el nodo actual es mayor
        if (id_nodo>id_vecino):
            # app.logger.error('------ SOY MAYOR ------')
            return jsonify({'response':'OK'})    
        # Si el vecino es mayor
    else:
            # app.logger.error('------ SOY MENOR ------')
        return jsonify({'response':'NO'})

# Funcion de verificacion del coordinator
def fun_verificar():
    global puerto_cor
    global pet
    global election
    global without_coordina
    
    while True:
        try:
            if (election == False):
                if (puerto_cor == puerto_nodo):
                    break
                time.sleep(5+(id_nodo))
                url = '192.168.0.4:'+str(puerto_cor)+'/PRUEBA'
                headers = {'PRIVATE-TOKEN': '<your_access_token>', 'Content-Type':'application/json'}
                req = requests.post('http://'+url, headers=headers)
                # app.logger.error('------ SOY EL NODO No.'+str(id_nodo)+' - '+str(puerto_nodo)+'------')
                pet += 1
                app.logger.error('------('+str(pet)+') ACTIVO '+str(puerto_cor)+' ------')
        except requests.exceptions.ConnectionError:
            # Proceso de election
            puertos_kill.append(puerto_cor)
            # Notifica a todos de election
            time.sleep(10)
            if(election == False and without_coordina == False):
                for puerto in puertos:
                    if (puerto not in puertos_kill):
                        # requests
                        # app.logger.error('------ ME DI CUENTA ------')
                        app.logger.error('------ ME DI CUENTA ('+str(puerto)+') ------')
                        url = '192.168.0.4:'+puerto+'/PRE'
                        # Enviar petricion de eleccion
                        headers = {'PRIVATE-TOKEN': '<your_access_token>', 'Content-Type':'application/json'}
                        req = requests.post('http://'+url, headers=headers)
                        response_json = req.json()
                        app.logger.error('------ '+response_json['response']+' ('+str(puerto)+') ------')
                # Inicio proceo de election
                app.logger.error('------ PROCESO ------')
                election = True
                init()
            break
    

# Verificacion de actividad
@app.route('/PRE',methods = ['POST'])
def pre():
    global election
    election = True
    without_coordina = True
    app.logger.error('------ ELECTION ------')
    return jsonify({'response':'ELECTION'})

# Verificacion de actividad
@app.route('/INICIO_ELECTION',methods = ['POST'])
def inicio_election():
    global election    
    # time.sleep(10)
    init()
    return jsonify({'response':'OK'})

# Verificacion de actividad
@app.route('/PRUEBA',methods = ['POST'])
def prueba():
    app.logger.error('------ Verificacion '+str(puerto_cor)+' ------')
    return jsonify({'response':'SI'})
       
# Envio de daots por request
def enviar_datos(url,datas,q):
    headers = {'PRIVATE-TOKEN': '<your_access_token>', 'Content-Type':'application/json'}
    req = requests.post('http://'+url, data=json.dumps(datas), headers=headers)
    q.put(req.json())


def init():
    global coordina
    global puerto_cor
    # Inicia la election
    cont=0
    for puerto in puertos:
        if (puerto_nodo<puerto):
            if (puerto not in puertos_kill):
                # requests
                url = '192.168.0.4:'+puerto+'/ELECTION'
                datas = {
                        'id':id_nodo,
                        'puerto':puerto_nodo
                    }
                try:
                    headers = {'PRIVATE-TOKEN': '<your_access_token>', 'Content-Type':'application/json'}
                    req_i = requests.post('http://'+url, data=json.dumps(datas), headers=headers)
                    # Recibir
                    responde_json_ = req_i.json()
                    # Existe uno mayor
                    if (responde_json_['response'] == 'OK'):
                        app.logger.error('------ ('+str(puerto)+') OK ------')
                        # Se manda notifiacion al primer mayor
                        if(cont==0):
                            mayor_puerto = puerto
                            cont = 1
                except requests.exceptions.ConnectionError:
                    print('')
    # Envia la notificion al siguiente puerto mayor a que haga la election
    if (cont == 1):
        url = '192.168.0.4:'+mayor_puerto+'/INICIO_ELECTION'
        try:
            headers = {'PRIVATE-TOKEN': '<your_access_token>', 'Content-Type':'application/json'}
            req = requests.post('http://'+url, data=json.dumps(datas), headers=headers)
            # Recibir
            responde_json = req.json()
            # Existe uno mayor
            if (responde_json['response'] == 'OK'):
                app.logger.info('------ NODO NUEVO PARA ELECTION '+str(mayor_puerto)+' ------')
                # # Se manda notifiacion al primer mayor
                # if(cont==0):
                #     mayor_puerto = puerto
                #     cont = 1
        except requests.exceptions.ConnectionError:
            print('')   
    else:
        # Soy el nuevo coordinador
        coordina = True
        app.logger.info('------ SOY EL NUEVO COORDINATOR No.'+str(id_nodo)+'------')
        # Notificar a todos
        id_cor = id_nodo
        puerto_cor = puerto_nodo
        nada = 0
        for puerto in puertos:
            if (puerto not in puertos_kill and nada==0):
                # requests
                url = '192.168.0.4:'+puerto+'/COORDINATOR'
                datas = {
                        'id':id_nodo,
                        'puerto':puerto_nodo
                    }
                headers = {'PRIVATE-TOKEN': '<your_access_token>', 'Content-Type':'application/json'}
                req = requests.post('http://'+url, data=json.dumps(datas), headers=headers)
                # Recibir
                responde_json = req.json()
                app.logger.info('------ SE NOTIFICO AL NODO '+str(puerto) + ' - ' + responde_json['response']+' ------')
        nada = 1

# Coordinador
nada = 0
if (coordina==True and nada==0):
    # Notifico que es el coordinador
    app.logger.info('------ SOY EL COORDINADOR - No.'+str(id_nodo) + ' ------')
    time.sleep(10)
    app.logger.error(str(len(puertos))+' lista ------- ')
    for puerto in puertos:
        if (puerto not in puertos_kill):            
            # requests
            url = '192.168.0.4:'+puerto+'/COORDINATOR'
            datas = {
                'id':id_nodo,
                'puerto':puerto_nodo
            }
            headers = {'PRIVATE-TOKEN': '<your_access_token>', 'Content-Type':'application/json'}
            req = requests.post('http://'+url, data=json.dumps(datas), headers=headers)
            # Recibir
            responde_json = req.json()
            app.logger.info('------ SE NOTIFICO AL NODO '+str(puerto) + ' - ' + responde_json['response']+' ------')
    nada=1
        
    
    
if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)
