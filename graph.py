import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
distances = [0, 1, 2, 3, 4, 5]
elevations = [300, 350, 420, 390, 310, 280]

fig = go.Figure()
fig.add_trace(go.Scatter(x=distances, y=elevations, mode='lines+markers', name='Elevation Profile', line=dict(color='red', width=2), marker=dict(size=8, color='red')))
fig.update_layout(title='Elevation Profile of a Hike', xaxis_title='Distance (km)', yaxis_title='Elevation (m)')
fig.show()  

# 2. Map plot (needs lat/lon data)
df = pd.DataFrame({
    "lat": [52.52, 52.53, 52.54],
    "lon": [13.40, 13.41, 13.42],
    "ele": [34, 40, 38]
})
fig = px.scatter_mapbox(df, lat="lat", lon="lon", color="ele", size="ele", color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(title='Hike Route on Map')
fig.show()