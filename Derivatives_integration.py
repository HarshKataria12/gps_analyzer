def elevation_stats(elevations, distances):
    
    # derivative
    rates = [0.0]
    for i in range(1, len(elevations)):
        rate_of_change = (elevations[i] - elevations[i-1]) / (distances[i] - distances[i-1])
        direction = "uphill" if rate_of_change > 0 else "downhill"
        print(f"Point {i}: {rate_of_change:.2f} m/km ({direction})")
        rates.append(rate_of_change)

    # integration
    total_ascent = 0
    for i in range(1, len(rates)):
        dx = distances[i] - distances[i-1]
        avg_elevation = (rates[i] + rates[i-1]) / 2
        if avg_elevation > 0:
            total_ascent += avg_elevation * dx

    return rates, total_ascent
