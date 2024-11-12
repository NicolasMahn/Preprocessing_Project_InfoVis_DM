import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime, timedelta
from analyze_data.gps_data_preprocessing import get_gps_data_sorted_by_id


def visualize_gps_by_id(id, time_window_minutes=15, save_gif=True, save_mp4=True):
    data = get_gps_data_sorted_by_id()

    coordinates = data[id]

    # Extract time, latitude, and longitude
    times = [entry[0] for entry in coordinates]
    latitudes = [entry[1] for entry in coordinates]
    longitudes = [entry[2] for entry in coordinates]

    # Ensure the data is sorted by time (times are already datetime objects)
    sorted_data = sorted(zip(times, latitudes, longitudes), key=lambda x: x[0])
    times, latitudes, longitudes = zip(*sorted_data)

    # Set the time window for each frame (e.g., 1 hour in real time)
    time_window = timedelta(minutes=time_window_minutes)

    # Create figure and axis
    fig, ax = plt.subplots()
    ax.set_title(f'Trajectory of ID {id}')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    # Set up line object and a text object for displaying current time
    line, = ax.plot([], [], lw=2)
    time_text = ax.text(0.95, 1.1, '', transform=ax.transAxes, ha='right')

    # Function to interpolate positions based on time
    def interpolate_position(t, t0, t1, pos0, pos1):
        """ Linearly interpolate the position at time `t` between times `t0` and `t1`."""
        if t1 == t0:  # Prevent division by zero
            return pos0
        ratio = (t - t0) / (t1 - t0)
        return pos0 + ratio * (pos1 - pos0)

    # Function to initialize the graph
    def init():
        line.set_data([], [])
        ax.set_xlim(min(longitudes), max(longitudes))
        ax.set_ylim(min(latitudes), max(latitudes))
        time_text.set_text('')
        return line, time_text

    # Function to update the frame
    def update(frame):
        current_time = times[0] + frame * time_window

        # Stop the animation if the current time exceeds 20.01.2014
        if current_time > datetime(2014, 1, 20):
            ani.event_source.stop()
            return line, time_text

        x_data = []
        y_data = []

        for i in range(1, len(times)):
            if times[i - 1] <= current_time <= times[i]:
                # Interpolate between known positions
                interp_lat = interpolate_position(current_time, times[i - 1], times[i], latitudes[i - 1], latitudes[i])
                interp_lon = interpolate_position(current_time, times[i - 1], times[i], longitudes[i - 1],
                                                  longitudes[i])
                x_data.append(interp_lon)
                y_data.append(interp_lat)
                break
            else:
                # Add known positions up to the current time
                x_data.append(longitudes[i - 1])
                y_data.append(latitudes[i - 1])

        line.set_data(x_data, y_data)

        # Update the displayed time
        time_text.set_text(current_time.strftime('%Y-%m-%d %H:%M:%S'))

        return line, time_text

    # Calculate the total number of frames based on the time range
    total_frames = int((times[-1] - times[0]) / time_window) + 1

    # Create the animation
    ani = animation.FuncAnimation(fig, update, frames=total_frames, init_func=init, blit=True, interval=500)

    print("The animation has been calculated")

    # Save the animation to a file (mp4 or gif)
    if save_mp4:
        print("saving as mp4")
        ani.save(f'animations/movement_of_{id}.mp4', writer='ffmpeg')
    if save_gif:
        print("saving as gif")
        ani.save(f'animations/movement_of_{id}.gif', writer='pillow')
