import pandas as pd
import folium
import json
import os
from folium.plugins import MarkerCluster
from flask import Flask, render_template

app = Flask(__name__)

# Ensure 'static' directory exists before saving the heatmap
STATIC_DIR = "static"
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

# File paths
csv_file = "student_mobility_with_coordinates.csv"
geojson_file = "world-countries.json"

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

# Extract country names from GeoJSON for validation
geojson_countries = {feature["properties"]["name"] for feature in world_geo["features"]}

# Debug: Check if any countries are still unmatched
missing_countries = set(df["Country"].unique()) - geojson_countries
print("Countries not matched:", missing_countries)

# Create a Folium map centered globally
m = folium.Map(location=[20, 0], zoom_start=2, tiles="cartodb positron")

# Add Choropleth layer for heatmap visualization
folium.Choropleth(
    geo_data=world_geo,
    name="Choropleth Heatmap",
    data=df,
    columns=["Country", "Number_of_Students"],
    key_on="feature.properties.name",
    fill_color="YlOrRd",  # Yellow-Orange-Red gradient
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
heatmap_path = os.path.join(STATIC_DIR, "choropleth_heatmap.html")
m.save(heatmap_path)

# Flask Routes
@app.route("/")
def index():
    return render_template("index.html", heatmap_path=heatmap_path)

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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
