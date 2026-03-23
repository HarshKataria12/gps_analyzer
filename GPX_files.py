import gpxpy 
import pandas as pd
def read_gpx_file(file_path):

    gpx = gpxpy.parse(file_path)
    
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
