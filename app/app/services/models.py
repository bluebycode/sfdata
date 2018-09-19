""" Profiling """
from timeit import default_timer as timer

""" Data manipulation """
import pandas as pd

db = None
session = None

def initialization(dbConnector):
    """ Inicializacion del servicio con el conector a Cassandra """
    global db
    db = dbConnector
   
def runQuery(query, withCoordinates = None):
    """ Funcion auxiliar para obtener los datos encapsulados mediante objetos Panda
        una vez obtenidos de la base de datos """
    start = timer()
    session = db.connect()
    data = pd.DataFrame(list(session.execute(query)))
    # @todo: mover la transformación fuera de esta función
    if withCoordinates is not None and not data.empty:
        data['X'] = data['x'].astype('float64')
        data['Y'] = data['y'].astype('float64')
    print("Query: %s, time: ... %0.5f secs."  % (query, timer() - start))
    return data

def load(attribute, group, year=2017):
    """ Devuelve mediante listas de objetos de atributos los pares de distritos y categorias especificadas en el argumento
        delegando la petición a la base de datos """
    attributes_raw = runQuery("select %s from sf.by%s WHERE year=%d group by %s" % (attribute,attribute,year,attribute))
    attributes_list = [item for sublist in attributes_raw.values.tolist() for item in sublist]
    return [ { "value": (group*20)+i, "text": x.lower(), "attribute": attribute} for i, x in enumerate(attributes_list)]

def get_all_categories():
    return load('category', 1)

def get_all_districts():
    return load('district', 0)

def get_overall(year=2017, limit=None):
    return runQuery("select year, district, category, description, X, Y from sf.overall where year=%d %s" % (year, "" if limit is None else " limit %s" % limit), True)

def get_per_district(year=2017):
    return runQuery("select district, count(*) from sf.bydistrict where year=%d group by district" % year)

def buildQueryByAttribute(filterByCategories=None, filterBydDistricts=None, filterByYear=None):
    """ Selecciona el tipo de consulta necesaria en acorde al atributo/familia """
    inExpression = ""
    tableName = "overall"

    if filterByYear is None:
        filterByYear = '2017'

    if filterByCategories is not None:
        inExpression = "%s and category in (%s)" % (inExpression, filterByCategories)
        tableName = "bycategory"
    
    if filterBydDistricts is not None:
        inExpression = "%s and district in (%s)" % (inExpression, filterBydDistricts)
        tableName = "bydistrict"

    if filterByCategories is not None and filterBydDistricts is not None:
        tableName = "bycategories"

    query = "select year, district, category, description, X, Y from sf.%s where year=%s %s" % (tableName,filterByYear,inExpression)
    print(query)
    return query

def getAttributeDefault(attrs, attributeName, defaultValue = None):
    if (attributeName not in attrs):
        return defaultValue
    if (hasattr(attrs[attributeName], 'lower')):
        return attrs[attributeName]
    elif len(attrs[attributeName])>0:
        return ",".join(["'%s'" % x for x in attrs[attributeName]]).upper()
    return defaultValue

def get_by_attributes(attrs, limit=None):
    """ Obtiene la información filtrada por los tipo de atributos o familias """
    filterByCategories = getAttributeDefault(attrs, 'category', None)
    filterBydDistricts = getAttributeDefault(attrs, 'district', None)
    filterByYear = getAttributeDefault(attrs, 'year', 2017)
    print("incidentsWhere %s %s %s" %(filterByCategories,filterBydDistricts, filterByYear) )
    return runQuery(buildQueryByAttribute(filterByCategories, filterBydDistricts, filterByYear), True)
