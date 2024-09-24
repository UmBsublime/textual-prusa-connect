from textual_serve.server import Server

server = Server("python app.py", host="0.0.0.0")
server = Server("python app.py")
server.serve()
