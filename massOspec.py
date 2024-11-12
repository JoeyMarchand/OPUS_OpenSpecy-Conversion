import pandas as pd
import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
import spectral
import ipywidgets as widgets
import sqlalchemy
from IPython.display import display

# Load the HDR file
img = spectral.open_image('/Users/joey/Desktop/St_Baja/SOC_W Fat 100um BOTTOM.hdr')
#### This is the first thing I'm going to change ^^^^

# Function to extract parameters from the .parms file
def parameters_extraction(parmsfile_path):
    max_wavelength, min_wavelength, data_points = None, None, None
    with open(parmsfile_path, 'r') as file:
        for line in file:
            if 'FXV=' in line:  # Max Wavelength - 3900
                min_wavelength = float(line.split('=')[1].strip())  # Calling Min to swap around the x axis
            elif 'LXV=' in line:  # Min Wavelength - 1300
                max_wavelength = float(line.split('=')[1].strip())  # Calling Max to swap around the x axis ordering
            elif 'NPT=' in line:  # Number of X - Data points
                data_points = int(line.split('=')[1].strip())
                
    return max_wavelength, min_wavelength, data_points

max_wavelength, min_wavelength, data_points = parameters_extraction('/Users/joey/Desktop/St_Baja/SOC_W Fat 100um BOTTOM.parms')
wavelengths = np.linspace(min_wavelength, max_wavelength, data_points)

# Function to extract spectrum for specific x, y coordinates
def get_spectrum(x, y):
    spectrum = img[y, x, :]
    intensity_values = spectrum.flatten()
    return wavelengths, intensity_values

# Function to calculate the first derivative
def calculate_derivative(x, y):
    # Use numpy to calculate the first derivative of y with respect to x
    derivative = np.gradient(y, x)
    return derivative

# Function to evaluate the flatness of the baseline in specified regions
def evaluate_flatness(x, derivative, region1=(3900, 3800), region2=(2600, 2300)):
    # Extract the indices for the two regions of interest
    region1_indices = np.where((x >= region1[1]) & (x <= region1[0]))  # 3900–3800
    region2_indices = np.where((x >= region2[1]) & (x <= region2[0]))  # 2600–2300

    # Calculate the mean derivative in the regions
    flatness1 = np.mean(np.abs(derivative[region1_indices]))
    flatness2 = np.mean(np.abs(derivative[region2_indices]))

    # Return the sum of flatness values for both regions as a score (lower is better)
    return flatness1 + flatness2

# Define the baseline correction function
def baseline_correction_poly(x, y, degree=1, max_iter=50):
    dev_prev = 0
    first_iter = True
    criteria_met = False
    iteration = 0
    
    # Store the original y values to return after baseline correction
    original_y = y.copy()
    
    best_flatness = float('inf')
    best_corrected_spectrum = y.copy()  # This will store the final baseline-corrected spectrum
    best_degree = degree  # Initialize with the given degree
    
    # Loop over different polynomial degrees
    for degree in range(1, 11):  # Try degrees 1 to 10, adjust as necessary
        y_copy = y.copy()
        while not criteria_met and iteration < max_iter:
            # Fit a polynomial to the spectrum
            model = np.polyfit(x, y_copy, degree)
            mod_poly = np.polyval(model, x)

            # Compute residual and deviation
            residual = y_copy - mod_poly
            dev_curr = np.std(residual)

            # Remove peaks
            if first_iter:
                peaks = np.where(y_copy > mod_poly + dev_curr)[0]
                y_copy[peaks] = mod_poly[peaks]  # Replace peaks with the baseline values
                first_iter = False

            # Test criteria to stop the loop
            criteria_met = np.abs((dev_curr - dev_prev) / dev_curr) <= 0.05

            # Update previous deviation and increment iteration
            dev_prev = dev_curr
            iteration += 1

        # Interpolate baseline and subtract from the original spectrum
        corrected_intensity = original_y - mod_poly
        
        # Calculate the derivative of the corrected spectrum
        derivative = calculate_derivative(x, corrected_intensity)

        # Evaluate flatness score for this degree
        flatness_score = evaluate_flatness(x, derivative)

        # If this baseline correction is better (lower flatness score), save it
        if flatness_score < best_flatness:
            best_flatness = flatness_score
            best_corrected_spectrum = corrected_intensity
            best_degree = degree  # Update best degree

    # Set negative values in the corrected spectrum to zero
    best_corrected_spectrum[best_corrected_spectrum < 0] = 0

    # Print the best polynomial degree
    print(f"Best Polynomial Degree: {best_degree}")
    
    return best_corrected_spectrum

# Function to update the plot based on slider values
def update_plot(x, y):
    wavelengths, intensity_values = get_spectrum(x, y)
    corrected_spectrum = baseline_correction_poly(wavelengths, intensity_values)
    normalized_intensity = corrected_spectrum / max(corrected_spectrum)

    # Plot the corrected spectrum
    plt.figure(figsize=(14, 3))
    plt.plot(wavelengths, normalized_intensity, color="black")
    plt.xlabel("Wavelength (cm-1)")
    plt.ylabel("Corrected Intensity")
    plt.title(f"Baseline Corrected Spectrum at Pixel ({x}, {y})")
    plt.gca().invert_xaxis()  # Flipping the x-axis visually
    plt.show()

# Create interactive sliders for x and y coordinates
x_slider = widgets.IntSlider(value=1360, min=0, max=img.shape[1]-1, step=1, description='X Coordinate:')
y_slider = widgets.IntSlider(value=80, min=0, max=img.shape[0]-1, step=1, description='Y Coordinate:')

# Use interactive function to update the plot when sliders change
interactive_plot = widgets.interactive(update_plot, x=x_slider, y=y_slider)

# Display the interactive dashboard
display(interactive_plot)