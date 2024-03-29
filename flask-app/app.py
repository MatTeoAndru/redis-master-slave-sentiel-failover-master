#redis = Redis(host='redis-slave-2', port=6379)
# https://stackoverflow.com/questions/57714028/naming-current-redis-master-run-in-docker-in-python
# https://stackoverflow.com/questions/76184653/flask-session-with-redis-sentinel-cluster-app-dies-on-new-redis-master/76731062#76731062
# https://stackoverflow.com/questions/70913043/how-to-connect-k8s-redis-sentinel-flask-caching

from flask import Flask, send_file , render_template_string
from redis import Redis
import os

app = Flask(__name__)

redis = Redis(host='redis-master', port=6379)


@app.route('/')
def hello():
    counter = str(redis.get('hits'), 'utf-8')
    hostname = os.environ.get("HOSTNAME" , "N/A")
    return render_template_string("""
    <html>
    <body>
        <p>Questa pagina è stata vista {{ counter }} volte(s)</p>
        <p>Container: {{ hostname }}</p>
        <form action="/add" method="POST">
            <button type="submit">Aggiungi visita</button>
        </form>
        <form action="/delete" method="POST">
            <button type="submit">Elimina visita</button>
        </form>
    </body>
    </html>
    """, counter=counter , hostname=hostname)

@app.route('/add', methods=['POST'])
def increment():
    redis.incr('hits')  # Incrementa il contatore Redis
    counter = str(redis.get('hits'), 'utf-8')
    return render_template_string("""
    <html>
    <body>
        <p>Totali visite pagina: {{ counter }}</p>
        <form action="http://localhost:5000/">
        <button type="submit" > Torna alla home ! </button>
        </form>
    </body>                        
    </html>
    """ ,counter = counter )

@app.route('/delete', methods=['POST'])
def delete():
    redis.decr('hits')  # Decrementa il contatore Redis
    counter = str(redis.get('hits'), 'utf-8')
    return render_template_string("""
    <html>
    <body>
        <p>Totali visite pagina: {{ counter }}</p>
        <form action="http://localhost:5000/">
        <button type="submit" > Torna alla home ! </button>
        </form>
    </body>                        
    </html>
    """ ,counter = counter )


@app.route('/meme')
def image():
    image_path = os.path.join(app.root_path, 'redis.png')
    return send_file(image_path, mimetype='redis.png')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)