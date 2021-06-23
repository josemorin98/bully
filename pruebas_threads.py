import threading
# import queue
import requests
import json
import sched
import time

# o=False
# def enviar_datos(dato_1,dato_2,q):
#     if(o == True):
#         print('hola')
#     q.put({
#                 'id':2,
#                 'puerto':222
#             })

# q = queue.Queue()
# aux = threading.Thread(target=enviar_datos,args=(5,5,q))
# aux.start()
            
# # Recibir
# responde_json = q.get()
# print(responde_json['id'])

datas = {
        'id':'3',
        'puerto':'503'
        }
url = '192.168.0.4:503/PRUEBA'
headers = {'PRIVATE-TOKEN': '<your_access_token>', 'Content-Type':'application/json'}
req = requests.post('http://'+url, headers=headers)


# def pruebaa(a,b):
#     while True:
#         print(a,b)

# s = sched.scheduler(time.time, time.sleep)
# s.enter(5, 1, pruebaa, argument=('positional',3))
# s.run()
# time.sleep(4)
# s.cancel()

