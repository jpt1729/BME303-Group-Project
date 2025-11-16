import random
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import functional as el  # Custom module containing the update functions for the simulation


# Function to plot the spatial distribution of the environment
def plotSpatial(data, fileNumber):
    # Define custom colors: grass(0), triceratops(1), brachiosaurus(2), velociraptor(3), t-rex(4), human(5)
    cmap = colors.ListedColormap(['lawngreen', 'orange', 'brown', 'purple', 'red', 'yellow'])
    plt.figure(figsize=(10, 9))  # Increased figure size for larger grid
    plt.pcolor(data, cmap=cmap, edgecolors='k', linewidths=1, vmin=0, vmax=5)  # Plot the grid with boundaries
    cbar = plt.colorbar(label="", orientation="vertical", ticks=[0.42, 1.25, 2.08, 2.92, 3.75, 4.58])  # Add a color bar
    cbar.ax.set_yticklabels(['grass', 'triceratops', 'brachiosaurus', 'velociraptor', 't-rex', 'human'])  # Set labels
    plt.savefig('figure_' + str(fileNumber) + '.jpg', bbox_inches='tight', pad_inches=0.02)  # Save the figure
    plt.close()  # Close the plot to free memory


# Function to plot the temporal dynamics of all species over time
def plotDynamics(data):
    fig, axes = plt.subplots(figsize=(10, 6))
    axes.plot(data[0], data[2], label='triceratops', color='orange', linewidth=2)
    axes.plot(data[0], data[3], label='brachiosaurus', color='brown', linewidth=2)
    axes.plot(data[0], data[4], label='velociraptor', color='purple', linewidth=2)
    axes.plot(data[0], data[5], label='t-rex', color='red', linewidth=2)
    axes.plot(data[0], data[6], label='human', color='gold', linewidth=2)
    axes.set_xlabel('Time (months)')  # Label the x-axis
    axes.set_ylabel('Number of individuals')  # Label the y-axis
    axes.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=11, fancybox=False, shadow=False, frameon=False)
    plt.savefig('temporalDynamics.pdf', bbox_inches='tight', pad_inches=0.02)  # Save the temporal dynamics as a PDF
    plt.close()  # Close the plot to free memory


# Main function to run the simulation
def main():
    random.seed(time.time())  # Seed the random number generator with the current time
    sizeX, sizeY = 50, 50  # Increased grid size from 30x30 to 50x50

    # Initialize grid with random values:
    # 0: grass, 1: triceratops, 2: brachiosaurus, 3: velociraptor, 4: t-rex, 5: human
    domain = np.array([random.randint(0, 5) for x in range(sizeX * sizeY)]).reshape(sizeY, sizeX)

    # Initialize lists to store simulation data over time
    simTime, grass, triceratops, brachiosaurus, velociraptor, trex, human = [], [], [], [], [], [], []
    currTime = 0

    # Plot the initial state of the grid
    plotSpatial(domain, currTime)

    # Collect initial counts of all species
    simTime.append(currTime)
    grass.append(np.count_nonzero(domain == 0))  # Count cells with grass
    triceratops.append(np.count_nonzero(domain == 1))  # Count triceratops
    brachiosaurus.append(np.count_nonzero(domain == 2))  # Count brachiosaurus
    velociraptor.append(np.count_nonzero(domain == 3))  # Count velociraptors
    trex.append(np.count_nonzero(domain == 4))  # Count t-rex
    human.append(np.count_nonzero(domain == 5))  # Count humans

    # Run the simulation for 100 time steps
    for currTime in range(1, 101):
        print(currTime)  # Print the current time step
        domain = el.update_states(domain)  # Update the states (growth, movement, etc.) in the grid
        domain = el.update_positions(domain)  # Update the positions of species in the grid

        # Plot the spatial distribution at each time step
        plotSpatial(domain, currTime)

        # Collect population data for all species at each time step
        simTime.append(currTime)
        grass.append(np.count_nonzero(domain == 0))
        triceratops.append(np.count_nonzero(domain == 1))
        brachiosaurus.append(np.count_nonzero(domain == 2))
        velociraptor.append(np.count_nonzero(domain == 3))
        trex.append(np.count_nonzero(domain == 4))
        human.append(np.count_nonzero(domain == 5))

    # Prepare data for plotting temporal dynamics (populations over time)
    temporal_dynamics = [simTime, grass, triceratops, brachiosaurus, velociraptor, trex, human]
    plotDynamics(temporal_dynamics)  # Plot the population dynamics over time


# Run the main function to execute the simulation
main()