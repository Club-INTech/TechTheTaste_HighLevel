import numpy as np
import matplotlib.pyplot as plt
from rich import print as rprint
from scipy.signal import savgol_filter
import timeit
import time

def generate_noisy_data(n_points, mean, std_dev):
    """
    Generates a list of n_points random data points with added noise.
    
    Parameters:
        - n_points (int): the number of data points to generate
        - mean (float): the mean of the data points
        - std_dev (float): the standard deviation of the noise
    
    Returns:
        - A list of n_points floats
    """
    # Generate n_points random data points with a normal distribution
    data = np.random.normal(mean, std_dev, n_points)
    return data

def smooth_data(signal_raw,polynomial_order_,window_size_):
    """
    Applies a Savitzky-Golay filter to smooth out the data.
    
    Parameters:
        - signal_raw (list): the list of data points to be smoothed
        - window_size_ (int): the window size for the filter, must be an odd integer
        - polynomial_order_ (int): the polynomial order for the filter
    
    Returns:
        - A list of smoothed data points
    """
    window_ = signal_raw[:window_size_]
    for i in range(window_size_, len(signal_raw)):
        window_ = np.roll(window_, -1)
        window_[-1] = signal_raw[i]
        signal_raw = savgol_filter(window_, window_size_, polynomial_order_)
    return signal_raw

# Parameters used
StopTime = 1 
Fs = 1024 
f = 30     
# Generate sample times
t = np.linspace(0,StopTime, StopTime*Fs)
# Generate signal
x = np.sin(2*np.pi*t*f)
# Generate len(t) data points with a mean of 5 and a standard deviation of 0.5
noise = generate_noisy_data(len(t), 5, 0.5)
y_raw_value = x+noise

# Define the window size and polynomial order
window_size = 20
polynomial_order = 2

# Initialize the window with the first window_size data points
window = y_raw_value[:window_size]

# start the timer
start_time = time.time()

y_smooth = savgol_filter(y_raw_value, window_size, polynomial_order)

# stop the timer
end_time = time.time()

# calculate the execution time
execution_time = end_time - start_time

# print the execution time
print("Execution time: {:.6f} seconds".format(execution_time))


'''ax1 = plt.subplot(121)
ax1.plot(t,y_raw_value)
ax1.set_title("Non filtré")

ax2 = plt.subplot(122)
ax2.plot(t,y_smooth)
ax2.set_title("Filtré")

plt.show()'''