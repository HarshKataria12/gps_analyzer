elevations = [100, 150, 200, 250, 300]
distances = [0,10,  20,  30,  40,  50]
# rates of elevation change (derivatives) 
for i in range(1, len(elevations)):
    # 
    rate_of_change = (elevations[i] - elevations[i-1]) / (distances[i] - distances[i-1])
    direction = "uphill" if rate_of_change > 0 else "downhill"
    print(f"Point {i}: {rate_of_change:.2f} m/m ({direction})")

# integrating the elevation to find total ascent

def elevation_ascent(elevations, dists):
    total_ascent = 0
    for i in range(1, len(elevations)):
        dx = dists[i] - dists[i-1]
        avg_elevation = (elevations[i] + elevations[i-1]) / 2
        if avg_elevation > 0:  # only consider ascent
            total_ascent += (avg_elevation - elevations[i-1]) * dx
    return total_ascent
rates =[0, 1.0, 1.5, -0.5, -1.2, -1.3]
gain = elevation_ascent(rates, distances)
print(f"Total ascent: {gain:.2f} m")

