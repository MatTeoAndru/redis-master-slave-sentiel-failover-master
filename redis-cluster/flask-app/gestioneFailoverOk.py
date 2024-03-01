from flask import Flask, send_file , render_template_string
from redis import Redis
from redis.exceptions import ConnectionError, ReadOnlyError, ResponseError, TimeoutError
from redis.commands import SentinelCommands
from redis.connection import Connection, ConnectionPool, SSLConnection
from redis.exceptions import ConnectionError, ReadOnlyError, ResponseError, TimeoutError , RedisError
from redis.utils import str_if_bytes
from redis.sentinel import Sentinel
from datetime import timedelta
from flask import Flask, render_template_string, request, session, redirect, url_for
from flask_session import Session
import os
#Importazione classe da sentinel.py
from sentinel import SentinelManagedConnection

# ENDPOINT Disponibili register , login , get ,  add   ,  delete 


app = Flask(__name__ )


#Scoperta Master
sentinel = Sentinel([('redis-sentinel', 26379), ('redis-sentinel-2', 26379) , ('redis-sentinel-3', 26379)])
redis_master = sentinel.discover_master("mymaster")
host, port = redis_master
master_object = Redis(host, port)
master_object.get("data")
print(redis_master)
master_ip = redis_master[0]
master_ip_str = str(master_ip)
print(master_ip_str)

# # #Creazione Sessione
# app.secret_key = os.getenv('SECRET_KEY', default='ADVRFGMKRRKKGK')
# app.config['SESSION_TYPE'] = 'redis'
# app.config['SESSION_PERMANENT'] = False
# app.config['SESSION_USE_SIGNER'] = True
# app.config['SESSION_REDIS'] = Redis(host=host, port=port)
# server_session = Session(app)

app.secret_key = os.getenv('SECRET_KEY', default='ADVRFGMKRRKKGK')

@app.route('/get', methods=['GET'])
def get_email_and_items():
        #Scoperta Master
    sentinel = Sentinel([('redis-sentinel', 26379), ('redis-sentinel-2', 26379) , ('redis-sentinel-3', 26379)])
    redis_master = sentinel.discover_master("mymaster")
    host, port = redis_master
    master_object = Redis(host, port)
    master_object.get("data")
    print(redis_master)
    master_ip = redis_master[0]
    master_ip_str = str(master_ip)
    print(master_ip_str)

    try:
        email = session.get('email')
        items = session.get('items')
        return f"Email: {email}<br>Items: {items}"
    except ConnectionError as ex:
        print('Error:', ex)


@app.route('/add', methods=['GET', 'POST'])
def set_email_and_items():
    try:
        #Scoperta Master
        sentinel = Sentinel([('redis-sentinel', 26379), ('redis-sentinel-2', 26379) , ('redis-sentinel-3', 26379)])
        redis_master = sentinel.discover_master("mymaster")
        host, port = redis_master
        master_object = Redis(host, port)
        master_object.get("data")
        print(redis_master)
        master_ip = redis_master[0]
        master_ip_str = str(master_ip)
        print(master_ip_str)

        if request.method == 'POST':
            session['items'] = {}  
            for i in range(1, 6): 
                item_name = f'item_{i}'
                quantity = int(request.form.get(f'quantity_{i}', 0))
                session['items'][item_name] = quantity
            return redirect(url_for('get_email_and_items'))

        return """
            <form method="post">
                """ + ''.join([f"""
                <label for="item{i}">Item {i}</label>
                <select id="item{i}" name="quantity_{i}">
                    <option value="0">0</option>
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <!-- Aggiungi altre opzioni se necessario -->
                </select><br><br>
                """ for i in range(1, 6)]) + """
                <button type="submit">Invia</button>
            </form>
            """
    except ConnectionError as ex:
        print('Error:', ex)




def authenticate_user(email, password):
    #Scoperta Master
    sentinel = Sentinel([('redis-sentinel', 26379), ('redis-sentinel-2', 26379) , ('redis-sentinel-3', 26379)])
    redis_master = sentinel.discover_master("mymaster")
    host, port = redis_master
    master_object = Redis(host, port)
    master_object.get("data")
    print(redis_master)
    master_ip = redis_master[0]
    master_ip_str = str(master_ip)
    print(master_ip_str)
    stored_password = master_object.get(f'user:{email}:password')
    if stored_password and stored_password.decode('utf-8') == password:
        return True
    return False

@app.route('/login', methods=['GET', 'POST'])
def login():
            #Scoperta Master
    sentinel = Sentinel([('redis-sentinel', 26379), ('redis-sentinel-2', 26379) , ('redis-sentinel-3', 26379)])
    redis_master = sentinel.discover_master("mymaster")
    host, port = redis_master
    master_object = Redis(host, port)
    master_object.get("data")
    print(redis_master)
    master_ip = redis_master[0]
    master_ip_str = str(master_ip)
    print(master_ip_str)
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if authenticate_user(email, password):
            session['email'] = email
            return redirect(url_for('get_email_and_items'))
        else:
            return "Credenziali non valide. Riprova."
    return """
        <form method="post">
            <h1>Pagina Login</h1>
            <label for="email">Email</label>
            <input type="email" id="email" name="email" required /><br><br>
            <label for="password">Password</label>
            <input type="password" id="password" name="password" required /><br><br>
            <button type="submit">Login</button>
        </form>
        """


@app.route('/register', methods=['GET', 'POST'])
def register():
        #Scoperta Master
    sentinel = Sentinel([('redis-sentinel', 26379), ('redis-sentinel-2', 26379) , ('redis-sentinel-3', 26379)])
    redis_master = sentinel.discover_master("mymaster")
    host, port = redis_master
    master_object = Redis(host, port)
    master_object.get("data")
    print(redis_master)
    master_ip = redis_master[0]
    master_ip_str = str(master_ip)
    print(master_ip_str)
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if master_object.exists(f'user:{email}:password'):
            return "Email già registrata."
        else:
            master_object.set(f'user:{email}:password', password)
            session['email'] = email
            return redirect(url_for('login'))
    return """
        <form method="post">
            <h1>Pagina Registrazione</h1>
            <label for="email">Email</label>
            <input type="email" id="email" name="email" required /><br><br>
            <label for="password">Password</label>
            <input type="password" id="password" name="password" required /><br><br>
            <button type="submit">Register</button>
            <h5>Già registrato?<a href="/login">Login</a></h5>
        </form>
        """

# # @app.route('/prova')
# # def test_connessione():
# #     try:
# #         master_object.ping() 
# #         connection_status = f"Connessione riuscita a {host}:{port}"
# #     except TimeoutError:
# #         connection_status = f"Timeout: Impossibile stabilire la connessione a {host}:{port}"
# #     except Exception as ex:
# #         connection_status = f"Errore di connessione: {ex}"
# #     return f"Stato della connessione: {connection_status}"


@app.route('/delete')
def delete_email():
            #Scoperta Master
    sentinel = Sentinel([('redis-sentinel', 26379), ('redis-sentinel-2', 26379) , ('redis-sentinel-3', 26379)])
    redis_master = sentinel.discover_master("mymaster")
    host, port = redis_master
    master_object = Redis(host, port)
    master_object.get("data")
    print(redis_master)
    master_ip = redis_master[0]
    master_ip_str = str(master_ip)
    print(master_ip_str)
    try:
        session.pop('email', None)
        session.pop('items', None) 
        return '<h1>Sessione cancellata!</h1>'
    except Exception as ex:
        print('Error:', ex)


# sentinel = Sentinel([('redis-sentinel', 26379), ('redis-sentinel-2', 26379) , ('redis-sentinel-3', 26379)])
# redis_master = sentinel.discover_master("mymaster")
# host, port = redis_master
# master_object = Redis(host, port)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)