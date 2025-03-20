import os
import pandas as pd
import folium
import json
from folium.plugins import MarkerCluster
from flask import Flask

app = Flask(__name__)

# Load the data
csv_file = "student_mobility_with_coordinates.csv"
geojson_file = "world-countries.json"

df = pd.read_csv(csv_file)

# Fix country name mismatches
name_mapping = {
    "USA": "United States",
    "Russia": "Russian Federation",
    "South Korea": "Korea, Republic of",
    "Iran": "Iran, Islamic Republic of",
    "Vietnam": "Viet Nam"
}
df["Country"] = df["Country"].replace(name_mapping)

# Load the GeoJSON file
with open(geojson_file, "r", encoding="utf-8") as file:
    world_geo = json.load(file)

# Create a Folium map
m = folium.Map(location=[20, 0], zoom_start=2, tiles="cartodb positron")

# Add Choropleth layer
folium.Choropleth(
    geo_data=world_geo,
    name="Choropleth",
    data=df,
    columns=["Country", "Number_of_Students"],
    key_on="feature.properties.name",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Number of Students Studying Abroad"
).add_to(m)

# Add a Marker Cluster for better visualization
marker_cluster = MarkerCluster().add_to(m)

# Add country markers with student numbers
for _, row in df.iterrows():
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=f'{row["Country"]}: {row["Number_of_Students"]} students',
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(marker_cluster)

# Ensure the 'static' directory exists before saving the file
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# Save the heatmap in the static directory
heatmap_path = os.path.join(static_dir, "choropleth_heatmap.html")
m.save(heatmap_path)

# Flask Routes
@app.route("/")
def index():
    return '<h2>Heatmap Available <a href="/heatmap" target="_blank">Here</a></h2>'

@app.route("/heatmap")
def heatmap():
    return '''
    <html>
      <head>
        <title>Choropleth Heatmap</title>
      </head>
      <body>
        <iframe src="/static/choropleth_heatmap.html" width="100%" height="800"></iframe>
      </body>
    </html>
    '''

if __name__ == "__main__":
    app.run(debug=True)
