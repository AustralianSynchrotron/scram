from scram_web import app
from scram_web.config import server_host,server_port,server_debug

if server_debug:
    app.debug = True

app.run(host=server_host, port=int(server_port))