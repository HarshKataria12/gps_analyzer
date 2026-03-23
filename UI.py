import streamlit as st
import numpy as np
from GPX_files               import read_gpx_file
from HAVERSINE               import compute_distances
from Derivatives_integration import elevation_stats
from graph                   import plot_elevation, plot_map, plot_slope_histogram, plot_speed

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GPS Analyzer",
    page_icon="🛰",
    layout="wide",
)

# ── header ────────────────────────────────────────────────────────────────────
st.title("🛰 GPS Route Analyzer")
st.caption("Upload a GPX file exported from Strava, Garmin, Komoot or any GPS device.")
st.divider()

# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    smooth     = st.slider("Smoothing", 1, 30, 8,
                           help="Higher = smoother elevation line")
    show_speed = st.toggle("Show speed chart", value=True)
    show_raw   = st.toggle("Show raw data",    value=False)

# ── upload ────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader("Upload your GPX file", type=["gpx"])

if not uploaded:
    st.info("👆 Upload a .gpx file above to begin.")
    st.stop()

# ── process ───────────────────────────────────────────────────────────────────
with st.spinner("Analysing your route…"):
    df                = read_gpx_file(uploaded)
    df["distance_km"] = compute_distances(df)
    elev_smooth       = df["elevation"].rolling(smooth, min_periods=1).mean().tolist()
    distances         = df["distance_km"].tolist()
    rates, ascent     = elevation_stats(elev_smooth, distances)

# ── clip GPS noise from slope rates (1st–99th percentile) ─────────────────────
rates_arr   = np.array(rates)
lo, hi      = np.percentile(rates_arr, 1), np.percentile(rates_arr, 99)
rates_clean = np.clip(rates_arr, lo, hi).tolist()

# ── computed values ───────────────────────────────────────────────────────────
total_dist = round(distances[-1], 2)
elev_gain  = round(ascent, 2)
max_elev   = round(max(elev_smooth), 2)
min_elev   = round(min(elev_smooth), 2)

moving_time_str = "—"
avg_speed_str   = "—"
if df["time"].notna().all():
    total_secs = (df["time"].iloc[-1] - df["time"].iloc[0]).total_seconds()
    h, m       = int(total_secs // 3600), int((total_secs % 3600) // 60)
    moving_time_str = f"{h:02d}h {m:02d}m"
    if total_secs > 0:
        avg_speed_str = f"{round(total_dist / total_secs * 3600, 2)} km/h"

# ── slope stats from CLIPPED rates ────────────────────────────────────────────
up_rates = [r for r in rates_clean if r > 0]
dn_rates = [r for r in rates_clean if r < 0]
avg_up   = round(sum(up_rates) / max(len(up_rates), 1), 2)
avg_dn   = round(sum(dn_rates) / max(len(dn_rates), 1), 2)
max_up   = round(max(up_rates) if up_rates else 0, 2)
max_dn   = round(min(dn_rates) if dn_rates else 0, 2)

# ── summary metrics — 2 rows of 3 ────────────────────────────────────────────
st.subheader(" Summary")
r1c1, r1c2, r1c3 = st.columns(3)
r1c1.metric("Distance",      f"{total_dist:.2f} km")
r1c2.metric("Elevation Gain", f"{elev_gain:.2f} m")
r1c3.metric("Moving Time",   moving_time_str)

r2c1, r2c2, r2c3 = st.columns(3)
r2c1.metric("Max Elevation", f"{max_elev:.2f} m")
r2c2.metric("Min Elevation", f"{min_elev:.2f} m")
r2c3.metric("Avg Speed",     avg_speed_str)

st.divider()

# ── route map — full width ────────────────────────────────────────────────────
st.subheader("🗺️ Route Map")
st.caption("Colour shows elevation — blue (low) → green → orange (high). Hover any point for details.")
st.plotly_chart(plot_map(df), use_container_width=True,
                config={"displayModeBar": False})

st.divider()

# ── elevation profile — full width ────────────────────────────────────────────
st.subheader(" Elevation Profile")
st.caption("Blue area = elevation · Orange dotted line = slope gradient")
st.plotly_chart(plot_elevation(distances, elev_smooth, rates_clean),
                use_container_width=True, config={"displayModeBar": False})

st.divider()

# ── slope + speed ─────────────────────────────────────────────────────────────
st.subheader(" Slope & Speed")
speed_fig = plot_speed(df, distances)

if show_speed and speed_fig:
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.caption("Orange = uphill · Teal = downhill")
        st.plotly_chart(plot_slope_histogram(rates_clean),
                        use_container_width=True, config={"displayModeBar": False})
    with col2:
        st.caption("Speed smoothed to remove GPS noise")
        st.plotly_chart(speed_fig,
                        use_container_width=True, config={"displayModeBar": False})
else:
    st.caption("Orange = uphill · Teal = downhill")
    st.plotly_chart(plot_slope_histogram(rates_clean),
                    use_container_width=True, config={"displayModeBar": False})

st.divider()

# ── slope statistics — 2 rows of 2 so values never truncate ──────────────────
st.subheader(" Slope Statistics")
st.caption("GPS noise removed — values clipped to realistic range.")

ss1, ss2 = st.columns(2)
ss1.metric("Avg Uphill Slope",   f"{avg_up:.2f} m/km")
ss2.metric("Max Uphill Slope",   f"{max_up:.2f} m/km")

ss3, ss4 = st.columns(2)
ss3.metric("Avg Downhill Slope", f"{avg_dn:.2f} m/km")
ss4.metric("Max Downhill Slope", f"{max_dn:.2f} m/km")

# ── raw data ──────────────────────────────────────────────────────────────────
if show_raw:
    st.divider()
    st.subheader("🗃️ Raw Data")
    raw = df.copy()
    raw["distance_km"] = raw["distance_km"].round(2)
    raw["elevation"]   = raw["elevation"].round(2)
    raw["latitude"]    = raw["latitude"].round(6)
    raw["longitude"]   = raw["longitude"].round(6)
    st.dataframe(raw, use_container_width=True, height=300, hide_index=True)