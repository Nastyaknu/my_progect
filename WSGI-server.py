import wsgiref.simple_server
import traceback
from app_logic import application

#--------------------------------------------------------------------
# Блок 2
HOST = ''                 # Комп'ютер для з'єднання
PORT = 5556              # Порт для з'єднання

wsgiref.simple_server.WSGIServer.allow_reuse_address = True
wsgiref.simple_server.WSGIServer.allow_reuse_port = True
srv = wsgiref.simple_server.WSGIServer((HOST, PORT), wsgiref.simple_server.WSGIRequestHandler)
srv.set_app(application)


# Блок 3
try:
    srv.serve_forever()
except:
    print('Exception occurred')
    print(traceback.format_exc())
#
srv.server_close()