import random
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import indominus_functions as el  # Custom module containing the update functions for the simulation


# Function to plot the spatial distribution of the environment
def plotSpatial(data, fileNumber):
    # grass, velociraptor, t-rex, triceratops, brachiosaurus, human
    cmap = colors.ListedColormap(['lawngreen', 'orange', 'red', 'purple', 'darkgreen', 'yellow'])
    plt.figure(figsize=(7, 6))
    plt.pcolor(data, cmap=cmap, edgecolors='k', linewidths=1, vmin=0, vmax=5)
    cbar = plt.colorbar(label="", orientation="vertical", ticks=[0.4, 1.2, 2, 2.8, 3.6, 4.4])
    cbar.ax.set_yticklabels(['grass', 'velociraptor', 'indominus-rex', 'triceratops', 'brachiosaurus', 'human'])
    plt.savefig('figure_' + str(fileNumber) + '.jpg', bbox_inches='tight', pad_inches=0.02)
    plt.close()


# Function to plot the temporal dynamics over time
def plotDynamics(data):
    fig, axes = plt.subplots(figsize=(7, 6))
    axes.plot(data[0], data[2], label='velociraptor', color='orange')
    axes.plot(data[0], data[3], label='indominus-rex', color='red')
    axes.plot(data[0], data[4], label='triceratops', color='purple')
    axes.plot(data[0], data[5], label='brachiosaurus', color='darkgreen')
    axes.plot(data[0], data[6], label='human', color='yellow')
    axes.set_xlabel('Time (months)')
    axes.set_ylabel('Number of individuals')
    axes.legend(bbox_to_anchor=(1.05, 1), fontsize=10, fancybox=False, shadow=False, frameon=False)
    plt.savefig('temporalDynamics.pdf', bbox_inches='tight', pad_inches=0.02)
    plt.close()


# Main function to run the simulation
def main():
    random.seed(time.time())
    sizeX, sizeY = 50, 50  # increased domain size to 50x50

    # Initialize domain with weighted probabilities - more grass at start
    domain = np.zeros((sizeY, sizeX), dtype=int)
    for i in range(sizeY):
        for j in range(sizeX):
            rand_val = random.random()
            if rand_val < 0.5:  # 60% grass
                domain[i, j] = 0
            elif rand_val < 0.65:  # 15% velociraptor
                domain[i, j] = 1
            elif rand_val < 0.70:  # 5% i-rex
                domain[i, j] = 2
            elif rand_val < 0.84:  # 14% triceratops
                domain[i, j] = 3
            elif rand_val < 0.89:  # 5% brachiosaurus
                domain[i, j] = 4
            else:  # 11% human
                domain[i, j] = 5

    # Initialize lists to store simulation data over time
    simTime, grass, velociraptors, irexes, triceratops, brachiosaurus, humans = [], [], [], [], [], [], []
    currTime = 0

    # Plot the initial state of the grid
    plotSpatial(domain, currTime)

    # Collect initial counts
    simTime.append(currTime)
    grass.append(np.count_nonzero(domain == 0))
    velociraptors.append(np.count_nonzero(domain == 1))
    irexes.append(np.count_nonzero(domain == 2))
    triceratops.append(np.count_nonzero(domain == 3))
    brachiosaurus.append(np.count_nonzero(domain == 4))
    humans.append(np.count_nonzero(domain == 5))

    # Run the simulation for 100 time steps
    for currTime in range(1, 101):
        print(currTime)
        domain = el.update_states(domain)  # Update the states (growth, movement, etc.) in the grid
        domain = el.update_positions(domain)  # Update the positions of animals in the grid

        # Plot the spatial distribution at each time step
        plotSpatial(domain, currTime)

        # Collect population data at each time step
        simTime.append(currTime)
        grass.append(np.count_nonzero(domain == 0))
        velociraptors.append(np.count_nonzero(domain == 1))
        irexes.append(np.count_nonzero(domain == 2))
        triceratops.append(np.count_nonzero(domain == 3))
        brachiosaurus.append(np.count_nonzero(domain == 4))
        humans.append(np.count_nonzero(domain == 5))

    # Prepare data for plotting temporal dynamics
    temporal_dynamics = [simTime, grass, velociraptors, irexes, triceratops, brachiosaurus, humans]
    plotDynamics(temporal_dynamics)


# Run the main function to execute the simulation
main()
