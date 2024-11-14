import http.server
import socketserver
import os

PORT = 8080
DIRECTORY = "templates"  # Atualize para o diretório correto

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

# Cria o servidor usando a porta definida e o manipulador com o diretório especificado
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Servindo arquivos no diretório {DIRECTORY} na porta {PORT}")
    httpd.serve_forever()
