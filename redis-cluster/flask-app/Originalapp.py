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

#redis = Redis(host='redis-slave-2', port=6379)


from flask import Flask, send_file , render_template_string
from redis import Redis
import os
import subprocess

app = Flask(__name__)

def get_connected_redis_container():
    redis_containers = {
        "redis-master": "redis-master",
        "redis-slave": "redis-slave",
        "redis-slave-2": "redis-slave-2"
    }
    host_collegato = None
    for container_name, host_name in redis_containers.items():
        try:
            output = subprocess.check_output(
                f"echo 'info replication' | nc {host_name} 6379",
                shell=True
            ).decode("utf-8")
            if "role:master" in output:
                host_collegato = host_name
                break
        except subprocess.CalledProcessError:
            pass
    return host_collegato

connected_host = get_connected_redis_container()

if connected_host:
    redis = Redis(host=connected_host, port=6379)
else:
    print("Connessione non disponibile!")

@app.route('/')
def hello():
    counter = redis.get("hits")
    if counter is not None:
        counter = counter.decode("utf-8")
    else:
        counter = "0"
    hostname = os.environ.get("HOSTNAME", "N/A")
    host_collegato = f"Connesso a {connected_host}" if connected_host else "Nessun server Redis disponibile"
    return render_template_string("""
    <html>
    <body>
        <p>Questa pagina è stata vista {{ counter }} volte(s)</p>
        <p>Container: {{ hostname }}</p>
        <p>{{ host_collegato }}</p>
        <form action="/add" method="POST">
            <button type="submit">Aggiungi visita</button>
        </form>
        <form action="/delete" method="POST">
            <button type="submit">Elimina visita</button>
        </form>
    </body>
    </html>
    """, counter=counter, hostname=hostname, host_collegato=host_collegato)


@app.route('/add', methods=['POST'])
def increment():

    redis.incr('hits')  # Incrementa il contatore Redis
    counter = redis.get('hits').decode('utf-8')
    hostname = os.environ.get("HOSTNAME", "N/A")
    host_collegato = f"Connesso a {connected_host}" if connected_host else "Nessun server Redis disponibile"
    return render_template_string("""
    <html>
    <body>
        <p>Questa pagina è stata vista {{ counter }} volte(s)</p>
        <p>Container: {{ hostname }}</p>
        <p>{{ host_collegato }}</p>
        <form action="/">
        <button type="submit" > Torna alla home ! </button>
        </form>
    </body>                        
    </html>
    """, counter=counter, hostname=hostname, host_collegato=host_collegato)

@app.route('/delete', methods=['POST'])
def delete():
    redis.decr('hits')  # Decrementa il contatore Redis
    counter = str(redis.get('hits'), 'utf-8')
    hostname = os.environ.get("HOSTNAME", "N/A")
    host_collegato = f"Connesso a {connected_host}" if connected_host else "Nessun server Redis disponibile"
    return render_template_string("""
    <html>
    <body>
        <p>Questa pagina è stata vista {{ counter }} volte(s)</p>
        <p>Container: {{ hostname }}</p>
        <p>{{ host_collegato }}</p>
        <form action="http://localhost/">
        <button type="submit" > Torna alla home ! </button>
        </form>
    </body>                        
    </html>
    """ , counter=counter, hostname=hostname, host_collegato=host_collegato)

@app.route('/meme')
def image():
    image_path = os.path.join(app.root_path, 'redis.png')
    return send_file(image_path, mimetype='redis.png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)