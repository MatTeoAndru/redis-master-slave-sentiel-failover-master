# Fare funzione che effettua ping degli host e sceglie quella che risulta come master alla string

# Altre soluzioni potrebbero essere state , utilizzare in sentinel.conf  sentinel script o nella libreria
# sentinel che punta a tutto il nodo

# I would recommend to look into Redis Cluster (version 3.2 as latest stable today). Cluster this is a new approach, 
# no sentinels any more. Fail over principle is the same, slave promotes to master in case of master is down plus new more functionality 
# including sharding logic supported by Redis. Application just needs to connect to cluster having set of nodes, that's 

# You should configure a Redis instance as a slave of your master instance, either using the slaveof command or more likely by adding a slaveof directive in the
# configuration file (something like 'slaveof 127.0.0.1 6380' ; look at the documentation for more info); 
# then use Redis Sentinel to monitor the instances and promote the Slave as Master when the master fails.
# Moreover you either have to use a Redis client that supports sentinel and handles the redirection when the slave is promoted to slave, or use a network configuration (like virtual IP) to make the redirection transparent for your application.

#https://log.cyconet.org/2014/09/25/redis-ha-with-redis-sentinel-and-vip/ , notify script per cambiare  sentinel client-reconfig-script

#redis = Redis(host='redis-slave-2', port=6379)
# https://stackoverflow.com/questions/57714028/naming-current-redis-master-run-in-docker-in-python
# https://stackoverflow.com/questions/76184653/flask-session-with-redis-sentinel-cluster-app-dies-on-new-redis-master/76731062#76731062
# https://stackoverflow.com/questions/70913043/how-to-connect-k8s-redis-sentinel-flask-caching
# https://forum.redis.com/t/failover-issue-for-redis-sentinel-on-docker-compose/2511
# https://stackoverflow.com/questions/40941997/how-to-failover-to-new-master-node-when-using-redis-with-sentinel-and-redis-py
# https://stackoverflow.com/questions/76184653/flask-session-with-redis-sentinel-cluster-app-dies-on-new-redis-master/76731062#76731062 sentinel object during app startup , discover master. Uso poi il sentinel per scopre master o slave
# repo utile per il link sopra https://github.com/exponea/flask-redis-sentinel/blob/master/flask_redis_sentinel.py
# wsgi auto reload https://stackoverflow.com/questions/16344756/auto-reloading-python-flask-app-upon-code-changes


import os
import socket
import redis
from redis.exceptions import ConnectionError, ReadOnlyError
from flask import Flask, send_file, render_template_string

app = Flask(__name__)

def check_redis_role(host):
    port = 6379
    try:
        print(f"Connessione a {host}...")
        # Connessione al server Redis
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)  # Imposta un timeout di 5 secondi per la connessione
        s.connect((host, port))

        # Invia il comando PING
        s.sendall(b"PING\r\n")
        response = s.recv(1024).decode()

        # Controlla se la risposta è +PONG
        if response.strip() != "+PONG":
            print(f"{host} non ha risposto correttamente al ping.")
            return False

        # Invia il comando INFO replication
        s.sendall(b"INFO replication\r\n")
        info_response = s.recv(4096).decode()

        # Controlla se la risposta contiene role:master
        if "role:master" in info_response:
            print(f"{host} è il master!")
            return True
        else:
            print(f"{host} non è il master.")
            return False

    except Exception as e:
        # Gestione degli errori di connessione
        print(f"Errore durante la connessione a {host}: {e}")
        return False

    finally:
        # Chiudi la connessione
        s.close()

def get_connection(host):
    other_host = "redis-slave" if "master" in host else "redis-master"
    try:
        r = redis.StrictRedis(host=host, port=6379, db=0)
        r.ping() 
    except (ConnectionError, ReadOnlyError):
        # Connessione al server Redis fallita, prova other_host
        host = other_host
        r = redis.StrictRedis(host=host, port=6379, db=0)
        r.ping()  
    return host

def get_redis_host():
    hosts = ["redis-slave", "redis-slave-2", "redis-master"]
    for host in hosts:
        if check_redis_role(host):
            return host
    return None

host = get_redis_host()
if host is None:
    raise Exception("Nessun server Redis master disponibile.")

redis_instance = redis.Redis(host, port=6379)

@app.route('/')
def hello():
    counter = str(redis_instance.get('hits'), 'utf-8')
    hostname = os.environ.get("HOSTNAME", "N/A")
    connection_label = "master" if host == "redis-master" else "slave"
    return render_template_string("""
    <html>
    <body>
        <p>Questa pagina è stata vista {{ counter }} volte(s)</p>
        <p>Container: {{ hostname }}</p>
        <p>Connessione: {{ connection_label }}</p>
        <form action="/add" method="POST">
            <button type="submit">Aggiungi visita</button>
        </form>
        <form action="/delete" method="POST">
            <button type="submit">Elimina visita</button>
        </form>
    </body>
    </html>
    """, counter=counter, hostname=hostname , connection_label=connection_label)

@app.route('/add', methods=['POST'])
def increment():
    redis_instance.incr('hits')  # Incrementa il contatore Redis
    counter = str(redis_instance.get('hits'), 'utf-8')
    connection_label = "master" if host == "redis-master" else "slave"
    return render_template_string("""
    <html>
    <body>
        <p>Totali visite pagina: {{ counter }}</p>
        <p>Connessione: {{ connection_label }}</p>
        <form action="http://localhost:5000/">
        <button type="submit" > Torna alla home ! </button>
        </form>
    </body>                        
    </html>
    """ ,counter = counter , connection_label = connection_label)

@app.route('/delete', methods=['POST'])
def delete():
    redis_instance.incr('hits')  # Decrementa il contatore Redis
    counter = str(redis.get('hits'), 'utf-8')
    connection_label = "master" if host == "redis-master" else "slave"
    return render_template_string("""
    <html>
    <body>
        <p>Totali visite pagina: {{ counter }}</p>
        <p>Connessione: {{ connection_label }}</p>
        <form action="http://localhost:5000/">
        <button type="submit" > Torna alla home ! </button>
        </form>
    </body>                        
    </html>
    """ ,counter = counter , connection_label = connection_label )


@app.route('/meme')
def image():
    image_path = os.path.join(app.root_path, 'redis.png')
    return send_file(image_path, mimetype='redis.png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
