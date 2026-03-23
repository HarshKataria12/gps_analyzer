import plotly.graph_objects as go
import numpy as np

# ── clean light theme base ─────────────────────────────────────────────────
_BASE = dict(
    paper_bgcolor="white",
    plot_bgcolor="#f8f9fa",
    font=dict(family="sans-serif", color="#333333", size=12),
    margin=dict(l=50, r=30, t=50, b=50),
    title_font=dict(size=14, color="#1a1a2e"),
    xaxis=dict(
        gridcolor="#e0e0e0",
        linecolor="#cccccc",
        zeroline=False,
        tickfont=dict(size=11, color="#555555"),
    ),
    yaxis=dict(
        gridcolor="#e0e0e0",
        linecolor="#cccccc",
        zeroline=False,
        tickfont=dict(size=11, color="#555555"),
    ),
)

# ── colours ────────────────────────────────────────────────────────────────
BLUE   = "#2196F3"
ORANGE = "#FF9800"
GREEN  = "#4CAF50"
RED    = "#F44336"
TEAL   = "#009688"


def _clip_outliers(values, lo=2, hi=98):
    """Remove extreme outliers using percentile clipping."""
    arr = np.array(values)
    low, high = np.percentile(arr, lo), np.percentile(arr, hi)
    return np.clip(arr, low, high).tolist()


def plot_elevation(distances, elevations, rates):
    """
    Elevation area chart + smoothed slope overlay.
    Slope is clipped to remove GPS noise spikes.
    """
    # clip extreme slope values so the chart is readable
    rates_clean = _clip_outliers(rates, lo=1, hi=99)

    fig = go.Figure()

    # elevation fill
    fig.add_trace(go.Scatter(
        x=distances, y=elevations,
        mode="lines",
        name="Elevation (m)",
        line=dict(color=BLUE, width=2),
        fill="tozeroy",
        fillcolor="rgba(33,150,243,0.12)",
        hovertemplate="Distance: %{x:.2f} km<br>Elevation: %{y:.0f} m<extra></extra>",
    ))

    # slope overlay on secondary y-axis
    fig.add_trace(go.Scatter(
        x=distances, y=rates_clean,
        mode="lines",
        name="Slope (m/km)",
        line=dict(color=ORANGE, width=1.2, dash="dot"),
        yaxis="y2",
        opacity=0.8,
        hovertemplate="Slope: %{y:.1f} m/km<extra></extra>",
    ))

    fig.update_layout(
        **_BASE,
        title="Elevation Profile",
        xaxis_title="Distance (km)",
        yaxis_title="Elevation (m)",
        yaxis2=dict(
            title=dict(text="Slope (m/km)", font=dict(color=ORANGE, size=11)),
            overlaying="y", side="right",
            gridcolor="rgba(0,0,0,0)", zeroline=True,
            zerolinecolor="#cccccc", zerolinewidth=1,
            tickfont=dict(size=10, color=ORANGE),
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#dddddd", borderwidth=1,
            font=dict(size=11), x=0.01, y=0.99,
        ),
        height=380,
    )
    return fig


def plot_map(df):
    """
    Route as a coloured line on OpenStreetMap.
    Colour: blue (low elevation) → green → orange (high).
    START = green, END = red markers.
    """
    lats  = df["latitude"].tolist()
    lons  = df["longitude"].tolist()
    elevs = df["elevation"].tolist()

    e_min, e_max = min(elevs), max(elevs)
    e_range      = e_max - e_min if e_max != e_min else 1

    def elev_color(e):
        t = (e - e_min) / e_range
        if t < 0.5:
            t2 = t * 2
            r  = int(33  + t2 * (76  - 33))
            g  = int(150 + t2 * (175 - 150))
            b  = int(243 - t2 * (243 - 80))
        else:
            t2 = (t - 0.5) * 2
            r  = int(76  + t2 * (255 - 76))
            g  = int(175 - t2 * (175 - 152))
            b  = int(80  - t2 * 80)
        return f"rgb({r},{g},{b})"

    fig = go.Figure()

    # coloured route segments
    n      = len(lats)
    chunks = max(1, n // 200)
    for i in range(0, n - 1, chunks):
        end = min(i + chunks + 1, n)
        avg = sum(elevs[i:end]) / len(elevs[i:end])
        fig.add_trace(go.Scattermapbox(
            lat=lats[i:end], lon=lons[i:end],
            mode="lines",
            line=dict(width=4, color=elev_color(avg)),
            hoverinfo="skip",
            showlegend=False,
        ))

    # hover dots
    step = max(1, n // 150)
    fig.add_trace(go.Scattermapbox(
        lat=lats[::step], lon=lons[::step],
        mode="markers",
        marker=dict(
            size=7, opacity=0.6,
            color=elevs[::step],
            colorscale=[[0, BLUE], [0.5, GREEN], [1, ORANGE]],
            cmin=e_min, cmax=e_max,
            showscale=True,
            colorbar=dict(
                title=dict(text="Alt (m)", font=dict(size=11)),
                thickness=12, len=0.5,
                x=0.98, xanchor="right",
                y=0.97, yanchor="top",
                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="#cccccc", borderwidth=1,
                tickfont=dict(size=10),
            ),
        ),
        customdata=[[elevs[i]] for i in range(0, n, step)],
        hovertemplate=(
            "Alt: %{customdata[0]:.0f} m<br>"
            "Lat: %{lat:.5f}<br>"
            "Lon: %{lon:.5f}<extra></extra>"
        ),
        showlegend=False,
    ))

    # START marker
    fig.add_trace(go.Scattermapbox(
        lat=[lats[0]], lon=[lons[0]],
        mode="markers+text",
        marker=dict(size=16, color=GREEN),
        text=["START"], textposition="top right",
        textfont=dict(color=GREEN, size=12),
        hovertemplate=f"START — {elevs[0]:.0f} m<extra></extra>",
        name="Start",
    ))

    # END marker
    fig.add_trace(go.Scattermapbox(
        lat=[lats[-1]], lon=[lons[-1]],
        mode="markers+text",
        marker=dict(size=16, color=RED),
        text=["END"], textposition="top right",
        textfont=dict(color=RED, size=12),
        hovertemplate=f"END — {elevs[-1]:.0f} m<extra></extra>",
        name="End",
    ))

    # auto zoom
    span = max(max(lats) - min(lats), max(lons) - min(lons))
    zoom = 15 if span < 0.01 else 13 if span < 0.05 else 11 if span < 0.2 else 9 if span < 1 else 7

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=(max(lats)+min(lats))/2, lon=(max(lons)+min(lons))/2),
            zoom=zoom,
        ),
        paper_bgcolor="white",
        margin=dict(l=0, r=0, t=10, b=0),
        height=500,
        legend=dict(
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#dddddd", borderwidth=1,
            font=dict(size=11), x=0.01, y=0.99,
        ),
    )
    return fig


def plot_slope_histogram(rates):
    """Slope distribution with outliers clipped."""
    rates_clean = _clip_outliers(rates, lo=1, hi=99)

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=rates_clean, nbinsx=40,
        marker=dict(
            color=[ORANGE if r > 0 else TEAL for r in rates_clean],
            line=dict(width=0),
        ),
        opacity=0.8,
        hovertemplate="Slope: %{x:.1f} m/km<br>Count: %{y}<extra></extra>",
    ))
    fig.add_vline(x=0, line_width=1.5, line_dash="dash",
                  line_color=RED, opacity=0.7)
    fig.update_layout(
        **_BASE,
        title="Slope Distribution",
        xaxis_title="Slope (m/km)",
        yaxis_title="Count",
        height=340,
    )
    return fig


def plot_speed(df, distances):
    """Speed smoothed with a rolling average to remove GPS noise spikes."""
    if not df["time"].notna().all() or len(df) < 2:
        return None

    raw_speeds = [0.0]
    for i in range(1, len(df)):
        dt = (df["time"].iloc[i] - df["time"].iloc[i-1]).total_seconds()
        dd = (distances[i] - distances[i-1]) * 1000   # metres
        raw_speeds.append((dd / dt * 3.6) if dt > 0 else 0)

    # smooth + clip: rolling average over 10 points, cap at 99th percentile
    import pandas as pd
    s = pd.Series(raw_speeds).rolling(10, min_periods=1).mean()
    cap = float(np.percentile(s, 99))
    speeds = s.clip(0, cap).tolist()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=distances, y=speeds,
        mode="lines",
        name="Speed (km/h)",
        line=dict(color=TEAL, width=2),
        fill="tozeroy",
        fillcolor="rgba(0,150,136,0.12)",
        hovertemplate="Distance: %{x:.2f} km<br>Speed: %{y:.1f} km/h<extra></extra>",
    ))
    fig.update_layout(
        **_BASE,
        title="Speed Profile",
        xaxis_title="Distance (km)",
        yaxis_title="Speed (km/h)",
        height=340,
    )
    return fig