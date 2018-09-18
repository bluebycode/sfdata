""" Profiling """
from timeit import default_timer as timer

""" Folium maps stuff"""
import folium
from folium import plugins

from services.models import testing_models, get_overall, get_per_district

start_coords = (37.778209, -122.450070)

def create_marker(row, popup=None):
    """Returns a L.marker object"""
    icon = L.AwesomeMarkers.icon({markerColor: row.color})    
    marker = L.marker(L.LatLng(row.Y, row.X))
    marker.setIcon(icon)
    if popup:
        marker.bindPopup(row['description'])
    return marker

from folium.plugins import MarkerCluster

class MarkerClusterScript(MarkerCluster):
    def __init__(self, data, callback, popup=None):
        from jinja2 import Template
        super(MarkerClusterScript, self).__init__([])
        self._name = 'Density'
        self._data = data
        self._popup = popup
        if callable(callback):
            from flexx.pyscript import py2js
            self._callback = py2js(callback, new_name="callback")
        else:
            self._callback = "var callback = {};".format(_callback)

        self._template = Template(u"""
            {% macro script(this, kwargs) %}
            (function(){
                var data = {{this._data}};
                var map = {{this._parent.get_name()}};
                var cluster = L.markerClusterGroup();
                {{this._callback}}

                for (var i = 0; i < data.length; i++) {
                    var row = data[i];
                    var marker = callback(row, popup='names');
                    marker.addTo(cluster);
                }

                cluster.addTo(map);
            })();
            {% endmacro %}
                        """)

def generate_map(data, feature=False, year=2017):
    sfMap = folium.Map(location=start_coords, zoom_start=12)
    start = timer()
    total_start = start;

    if (feature is None):
        print("    generateMap: without feature")
        marker = folium.plugins.MarkerCluster(name="Density").add_to(sfMap)
        for name, row in data.iterrows():
            folium.Marker([row["Y"], row["X"]],popup=folium.Popup(row["description"])).add_to(marker)
    elif (feature is True):
        callback = ('function (row) {' 
                'var marker = L.circle(new L.LatLng(row[1], row[0]), {color: "red",  radius: 20000});'
                'marker.bindPopup("example");'
                'return marker};')
        sfMap.add_child(FastMarkerCluster(data[['Y','X']].values.tolist(), callback=callback))

    else:
        print("    generateMap: with feature",data[['Y','X','description']])
        MarkerClusterScript(data[['Y','X','description']].to_json(orient="records"), callback=create_marker).add_to(sfMap)

    print("    generateMap:markers elapsed", timer() - start)
    start = timer()
    district_geo = r'static/datasets/sfpddistricts.geojson'
    
    incidentsCountPerDistrict = get_per_district(year)
    #if (year == 2017):
    #    incidentsCountPerDistrict = incidentsPerDistrict2017();
    #elif (year == 2016):
    #    incidentsCountPerDistrict = incidentsPerDistrict2016();
    #elif (year == 2015):
    #    incidentsCountPerDistrict = incidentsPerDistrict2015();
    #else:
    #    incidentsCountPerDistrict = []

    # creation of the choropleth
    sfMap.choropleth(geo_data = district_geo, 
                name = "Incidents per district",
                data = incidentsCountPerDistrict,
                columns = ['district', 'count'],
                key_on = 'feature.properties.DISTRICT',
                fill_color = 'YlOrRd', 
                fill_opacity = 0.7, 
                line_opacity = 0.2,
                legend_name = 'Number of incidents per district')

    folium.LayerControl().add_to(sfMap)
    
    print("    generateMap:layers elapsed", timer() - start)
    print("generateMap elapsed", timer() - total_start)
    return sfMap
