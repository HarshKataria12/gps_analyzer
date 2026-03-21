import gpxpy # type: ignore
import pandas as pd
def read_gpx_file(file_path):
    with open(file_path, 'r') as file:
        gpx = gpxpy.parse(file)
    
    data = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                data.append({
                    'latitude': point.latitude,
                    'longitude': point.longitude,
                    'elevation': point.elevation,
                    'time': point.time
                })
    # convert to DataFrame for easier analysis
    df = pd.DataFrame(data)
    return df
# Example usage
print(read_gpx_file('12253908.gpx'))