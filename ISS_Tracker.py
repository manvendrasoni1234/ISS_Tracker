import requests
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from geopy.geocoders import Nominatim
from datetime import datetime

def get_iss_location():
    url = "http://api.open-notify.org/iss-now.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        timestamp = datetime.fromtimestamp(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        latitude = float(data['iss_position']['latitude'])
        longitude = float(data['iss_position']['longitude'])
        return timestamp, latitude, longitude
    else:
        print(f"Error: {response.status_code}")
        return None

def get_location_name(latitude, longitude):
    geolocator = Nominatim(user_agent="iss_tracker")
    location = geolocator.reverse((latitude, longitude), language='en')
    return location.address if location else "Unknown Location"

def update(frame):
    location_data = get_iss_location()
    if location_data:
        timestamp, latitude, longitude = location_data
        print(f"ISS location at {timestamp}: Latitude {latitude}, Longitude {longitude}")
        
        location_name = get_location_name(latitude, longitude)
        print(f"Location: {location_name}")
        
        scatter.set_data(longitude, latitude)
        text.set_text(f"ISS location at {timestamp}\nLatitude: {latitude}, Longitude: {longitude}\nLocation: {location_name}")

        # Ground track line
        track_line.set_data(lon_history[:frame+1], lat_history[:frame+1])

        # Time counter
        time_counter.set_text(f"Time: {frame * interval // 60} minutes")

        # Check if ISS is over India and highlight it
        if 68.0 < longitude < 89.0 and 7.0 < latitude < 35.0:
            india_highlight.set_color('orange')
            india_highlight.set_linewidth(2)
        else:
            india_highlight.set_color('none')
            india_highlight.set_linewidth(0)

    return scatter, text, track_line, time_counter, india_highlight

if __name__ == "__main__":
    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
    ax.add_feature(cfeature.LAND, edgecolor='k', facecolor='lightgreen')
    ax.add_feature(cfeature.BORDERS, linestyle='--', edgecolor='gray')  # Dashed borders
    ax.add_feature(cfeature.COASTLINE, edgecolor='k')

    # Change ocean color
    ax.add_feature(cfeature.OCEAN, edgecolor='k', facecolor='lightblue')

    # Graticules
    ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', linestyle='--', alpha=0.7)

    # ISS Model Marker
    scatter = ax.plot([], [], 'ro', markersize=12, label='ISS Model')[0]

    text = ax.text(-170, 0, '', transform=ccrs.Geodetic(), fontsize=10, color='black')

    # Ground track line
    track_line, = ax.plot([], [], 'r-', linewidth=2, label='Ground Track')

    # Time counter
    time_counter = ax.text(140, 70, '', fontsize=10, color='black')

    # Highlight for India
    india_highlight, = ax.plot([], [], color='none', linewidth=0)

    ax.set_title('International Space Station (ISS) Tracker', fontweight='bold', fontsize=14, color='navy')

    ax.legend()

    # Initialize history lists for ground track line
    lon_history, lat_history = [], []

    interval = 10  # Update every 10 seconds
    ani = FuncAnimation(fig, update, blit=False, frames=500, interval=interval * 1000)  # 500 frames, 10 seconds each

    plt.show()
