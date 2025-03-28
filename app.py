import os
import pandas as pd
import folium
import json
from folium.plugins import MarkerCluster
from flask import Flask

app = Flask(__name__)

# File paths
csv_file = os.path.join(os.path.dirname(__file__), "student_mobility_with_coordinates.csv")
geojson_file = os.path.join(os.path.dirname(__file__), "world-countries.json")

# Load the student mobility data
df = pd.read_csv(csv_file)

# Fix country name mismatches to align with GeoJSON
name_mapping = {
    "USA": "United States of America",
    "United States": "United States of America",
    "Russia Federation": "Russia",
    "South Korea": "South Korea",
    "Republic of Korea": "South Korea",
    "Iran, Islamic Republic of": "Iran",
    "Vietnam": "Vietnam",
    "Viet Nam": "Vietnam",
    "Hong Kong": "China",  # Hong Kong is part of China in most GeoJSON files
    "Brunei Darussalam": "Brunei",
    "Republic of Malta": "Malta",
    "Republic of Mauritius": "Mauritius",
    "Serbia": "Republic of Serbia",
    "Republic of Singapore": "Singapore"
}
df["Country"] = df["Country"].replace(name_mapping)

# Load GeoJSON world map data
with open(geojson_file, "r", encoding="utf-8") as file:
    world_geo = json.load(file)

# Create a Folium map centered globally
m = folium.Map(location=[20, 0], zoom_start=2, tiles="cartodb positron")

# Add Choropleth layer for heatmap visualization
folium.Choropleth(
    geo_data=world_geo,
    name="Choropleth Heatmap",
    data=df,
    columns=["Country", "Number_of_Students"],
    key_on="feature.properties.name",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Number of Students Studying Abroad",
).add_to(m)

# Add a Marker Cluster for better visualization
marker_cluster = MarkerCluster().add_to(m)

# Add markers for each country
for _, row in df.iterrows():
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=f'{row["Country"]}: {row["Number_of_Students"]} students',
        tooltip=row["Country"],
        icon=folium.Icon(color="blue", icon="info-sign"),
    ).add_to(marker_cluster)

# Save the heatmap to the static folder
heatmap_path = os.path.join(os.path.dirname(__file__), "static/choropleth_heatmap.html")
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
