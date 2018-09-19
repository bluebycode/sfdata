""" Profiling """
from timeit import default_timer as timer

from flask import Flask, render_template, request, jsonify, json, send_file
from flask_caching import Cache
app = Flask(__name__)

""" Persistence services """
from flask_cassandra import CassandraCluster

import geopandas

""" Folium maps stuff"""
import folium
from folium         import plugins
from folium.plugins import FastMarkerCluster

""" General """
from io import StringIO,BytesIO
import asyncio
import base64 
import json
import io
sio = BytesIO() 

""" Application services """
from services.models import testing_models, initialization, get_overall, get_by_attributes, get_all_districts, get_all_categories
from services.views import generate_map

YEAR = 2017
LIMIT = 1000

cache = None
cassandra = None
attributes = []

def init_db():
    global cassandra
    cassandra = CassandraCluster()

def init_cache_layout(application):
    """ Setting a simple cache layout """
    global cache
    cache = Cache(app,config={'CACHE_TYPE': 'simple'})
    cache.init_app(app)

def init_services():
    initialization(cassandra)
    testing_models()

def create_app():
    app = Flask(__name__)
    with app.app_context():
        init_db()
        init_services()
        init_cache_layout(app)
    return app

import os

print("Initialisation...")
print("* CASSANDRA_HOST:\t", os.environ['CASSANDRA_HOST'])
CASSANDRA_IP = os.environ.get('CASSANDRA_HOST') 

""" Inicialización de la aplicación: servicios y configuración. 
    Haciendo prefetching de la información necesaria para el filtrado
    por tags """
app = create_app()
app.config['CASSANDRA_NODES'] = [CASSANDRA_IP]
with app.app_context():
    @cache.cached(timeout=15000, key_prefix='load_categories')
    def loadCategories():
        return get_all_categories()

    @cache.cached(timeout=15000, key_prefix='load_districts')
    def loadDistricts():
        return get_all_districts()


@cache.cached(timeout=15000, key_prefix='generated_maps_%s')
@app.route('/generated_map/<attributes>')
def mapWithAttributes(attributes=None):
    """ Necesario para renderizar un mapa con unos ajustes personalizados dados por los atributos
    codificados mediante la parte de cliente (js): json -> base64.
    La función esta cacheada en base al token generado (attributes) por lo que cada petición
    con las mismas características son guardadas en memoria sin necesidad de realizar carga
    sobre la base de datos """
    attributesJson = base64.b64decode(attributes).decode('utf-8')
    variables = json.loads(attributesJson)
    start = timer()
    sample = get_by_attributes(variables)
    print("[/generated_map/%s] Query: incidentsWhere... %0.5f secs."  % (attributes, timer() - start))
    byYear = 2017
    if 'year' in variables:
        byYear = int(variables['year'])

    # Generamos el map e indicamos el template a utilizar si se
    # indicó un año determinado.
    print("[/generated_map/%s] year %s", attributes, byYear)
    sfMap = generate_map(sample, year=byYear);
    if (attributes == None):
        sfMap.save('templates/generated_map.html')
        return render_template('generated_map.html')
    else:
        sfMap.save('templates/generated/generated_map_%s.html' % attributes)
        return render_template('generated/generated_map_%s.html' % attributes)

@app.route('/generated_map')
def map(attributes=None):
    """ Renderizado del mapa existente """
    if (attributes == None):
        return render_template('generated_map.html')
    else:
        return render_template('generated/generated_map_%s.html' % attributes)


@app.route('/data/attributes.json')
def districts():
    """ Prefetching de los atributos distritos y categorias necesarios para
    el componente de tags """
    attributes = []
    attributes.extend(loadDistricts())
    attributes.extend(loadCategories())
    return jsonify(attributes)

@app.route("/healtcheck")
def healtcheck():
    return "OK, cassandra: %s" % CASSANDRA_IP

@cache.cached(timeout=300, key_prefix='absolute_path')
@app.route("/")
def absolute():
    # @todo. Si google loadbalancer hace healtcheck sobre / es necesario realizar este cambio para
    # evitar la carga.
    if request.headers is not None:
        print(request.headers)
        if 'User-Agent' in request.headers and request.headers['User-Agent'] == 'GoogleHC/1.0':
            return "OK, cassandra: %s" % CASSANDRA_IP

    # Obtiene y renderiza el mapa con la información inicial sin filtros.
    print("application\t[/]\t")
    start = timer()    
    sample = get_overall(year=YEAR, limit=LIMIT)
    print("[/] Query: allIncidents... %0.5f secs."  % (timer() - start))
    sfMap = generate_map(sample);
    sfMap.save('templates/generated_map.html')
    return render_template('index.html', incidents= 1)

if __name__ == "__main__":
    app.run(host='0.0.0.0')