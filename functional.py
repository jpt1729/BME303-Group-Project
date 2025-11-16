import numpy as np
import random

# Species constants
GRASS = 0
TRICERATOPS = 1
BRACHIOSAURUS = 2
VELOCIRAPTOR = 3
TREX = 4
HUMAN = 5

# Ecological parameters
GRASS_REGROW_RATE = 0.15  # Probability grass regrows in empty cell
HERBIVORE_REPRODUCTION_RATE = 0.12  # Reproduction rate for herbivores when well-fed
HERBIVORE_STARVATION_RATE = 0.08  # Death rate when no food nearby
CARNIVORE_REPRODUCTION_RATE = 0.10  # Reproduction rate for carnivores after successful hunt
CARNIVORE_STARVATION_RATE = 0.15  # Death rate when no prey nearby
HUMAN_REPRODUCTION_RATE = 0.05  # Reproduction rate in safe zones
HUMAN_DEATH_RATE = 0.35  # Death rate when near predators


def get_neighbors(domain, x, y):
    """Get all 8 neighbors of a cell"""
    neighbors = []
    rows, cols = domain.shape

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols:
                neighbors.append((nx, ny, domain[nx, ny]))

    return neighbors


def count_species_nearby(neighbors, species):
    """Count how many neighbors are of a specific species"""
    return sum(1 for _, _, n_species in neighbors if n_species == species)


def get_empty_neighbors(neighbors):
    """Get list of empty (grass) neighbor positions"""
    return [(x, y) for x, y, species in neighbors if species == GRASS]


def update_states(domain):
    """Update the states of all cells based on ecological interactions"""
    new_domain = domain.copy()
    rows, cols = domain.shape

    for i in range(rows):
        for j in range(cols):
            current = domain[i, j]
            neighbors = get_neighbors(domain, i, j)

            if current == GRASS:
                # Grass can be eaten by herbivores or regrow
                herbivores_nearby = count_species_nearby(neighbors, TRICERATOPS) + \
                                    count_species_nearby(neighbors, BRACHIOSAURUS)

                # Grass gets eaten with higher probability when more herbivores nearby
                if herbivores_nearby > 0 and random.random() < 0.25 * herbivores_nearby:
                    new_domain[i, j] = GRASS  # Stays grass (eaten)

            elif current == TRICERATOPS:
                # Triceratops: herbivore, needs grass, afraid of predators
                grass_nearby = count_species_nearby(neighbors, GRASS)
                predators_nearby = count_species_nearby(neighbors, VELOCIRAPTOR) + \
                                   count_species_nearby(neighbors, TREX)

                # Gets eaten by predators
                if predators_nearby > 0 and random.random() < 0.35:
                    new_domain[i, j] = GRASS
                # Starves without grass
                elif grass_nearby == 0 and random.random() < HERBIVORE_STARVATION_RATE:
                    new_domain[i, j] = GRASS
                # Reproduces when plenty of grass
                elif grass_nearby >= 3 and random.random() < HERBIVORE_REPRODUCTION_RATE:
                    empty = get_empty_neighbors(neighbors)
                    if empty:
                        rx, ry = random.choice(empty)
                        new_domain[rx, ry] = TRICERATOPS

            elif current == BRACHIOSAURUS:
                # Brachiosaurus: large herbivore, needs more grass, harder to kill
                grass_nearby = count_species_nearby(neighbors, GRASS)
                predators_nearby = count_species_nearby(neighbors, VELOCIRAPTOR) + \
                                   count_species_nearby(neighbors, TREX)

                # Large size makes it MUCH harder to kill (only T-Rex or large pack of raptors)
                trex_nearby = count_species_nearby(neighbors, TREX)
                raptor_nearby = count_species_nearby(neighbors, VELOCIRAPTOR)

                if trex_nearby >= 2 and random.random() < 0.20:  # Needs multiple T-Rex
                    new_domain[i, j] = GRASS
                elif raptor_nearby >= 4 and random.random() < 0.25:  # Needs large pack
                    new_domain[i, j] = GRASS
                # Starves without sufficient grass
                elif grass_nearby < 2 and random.random() < HERBIVORE_STARVATION_RATE:
                    new_domain[i, j] = GRASS
                # Reproduces when lots of grass
                elif grass_nearby >= 4 and random.random() < HERBIVORE_REPRODUCTION_RATE * 0.8:
                    empty = get_empty_neighbors(neighbors)
                    if empty:
                        rx, ry = random.choice(empty)
                        new_domain[rx, ry] = BRACHIOSAURUS

            elif current == VELOCIRAPTOR:
                # Velociraptor: pack hunter, targets herbivores
                prey_nearby = count_species_nearby(neighbors, TRICERATOPS) + \
                              count_species_nearby(neighbors, BRACHIOSAURUS)
                raptor_nearby = count_species_nearby(neighbors, VELOCIRAPTOR)
                humans_nearby = count_species_nearby(neighbors, HUMAN)

                # Hunts herbivores (more effective in packs)
                if prey_nearby > 0:
                    hunt_success = 0.20 + (0.10 * raptor_nearby)  # Pack bonus
                    if random.random() < hunt_success:
                        # Successful hunt, can reproduce
                        if random.random() < CARNIVORE_REPRODUCTION_RATE and raptor_nearby >= 1:
                            empty = get_empty_neighbors(neighbors)
                            if empty:
                                rx, ry = random.choice(empty)
                                new_domain[rx, ry] = VELOCIRAPTOR
                # Can also hunt humans (intelligent hunters)
                elif humans_nearby > 0 and raptor_nearby >= 2 and random.random() < 0.25:
                    # Pack hunts human
                    pass
                # Starves without prey
                elif prey_nearby == 0 and humans_nearby == 0 and random.random() < CARNIVORE_STARVATION_RATE:
                    new_domain[i, j] = GRASS

            elif current == TREX:
                # T-Rex: apex predator, hunts everything
                herbivore_nearby = count_species_nearby(neighbors, TRICERATOPS) + \
                                   count_species_nearby(neighbors, BRACHIOSAURUS)
                raptor_nearby = count_species_nearby(neighbors, VELOCIRAPTOR)
                human_nearby = count_species_nearby(neighbors, HUMAN)

                total_prey = herbivore_nearby + raptor_nearby + human_nearby

                # T-Rex hunts successfully
                if total_prey > 0 and random.random() < 0.40:
                    # Successful hunt, can reproduce
                    if random.random() < CARNIVORE_REPRODUCTION_RATE * 0.7:  # Lower reproduction
                        empty = get_empty_neighbors(neighbors)
                        if empty:
                            rx, ry = random.choice(empty)
                            new_domain[rx, ry] = TREX
                # Starves without prey (but survives longer)
                elif total_prey == 0 and random.random() < CARNIVORE_STARVATION_RATE * 0.6:
                    new_domain[i, j] = GRASS

            elif current == HUMAN:
                # Human: intelligent, avoids predators, survives in safe zones, hunts in groups
                predators_nearby = count_species_nearby(neighbors, TREX) + \
                                   count_species_nearby(neighbors, VELOCIRAPTOR)
                herbivores_nearby = count_species_nearby(neighbors, TRICERATOPS) + \
                                    count_species_nearby(neighbors, BRACHIOSAURUS)
                raptors_nearby = count_species_nearby(neighbors, VELOCIRAPTOR)
                other_humans = count_species_nearby(neighbors, HUMAN)

                # Humans hunt in groups (3+ humans can hunt herbivores, 5+ can hunt raptors)
                if other_humans >= 3 and herbivores_nearby > 0 and random.random() < 0.15:
                    # Successful group hunt on herbivore - humans reproduce
                    empty = get_empty_neighbors(neighbors)
                    if empty and random.random() < 0.3:
                        rx, ry = random.choice(empty)
                        new_domain[rx, ry] = HUMAN
                elif other_humans >= 5 and raptors_nearby > 0 and random.random() < 0.10:
                    # Successful group hunt on raptor - humans reproduce
                    empty = get_empty_neighbors(neighbors)
                    if empty and random.random() < 0.25:
                        rx, ry = random.choice(empty)
                        new_domain[rx, ry] = HUMAN
                # Gets eaten by predators
                elif predators_nearby > 0:
                    death_prob = HUMAN_DEATH_RATE * predators_nearby
                    if random.random() < death_prob:
                        new_domain[i, j] = GRASS
                # Reproduces in safe zones with other humans
                elif predators_nearby == 0 and other_humans >= 1 and random.random() < HUMAN_REPRODUCTION_RATE:
                    empty = get_empty_neighbors(neighbors)
                    if empty:
                        rx, ry = random.choice(empty)
                        new_domain[rx, ry] = HUMAN

    # Grass regrowth pass
    for i in range(rows):
        for j in range(cols):
            if new_domain[i, j] == GRASS:
                neighbors = get_neighbors(new_domain, i, j)
                grass_nearby = count_species_nearby(neighbors, GRASS)

                # Grass regrows better near other grass
                if grass_nearby >= 2 and random.random() < GRASS_REGROW_RATE:
                    new_domain[i, j] = GRASS

    return new_domain


def update_positions(domain):
    """Update positions - animals move to adjacent cells"""
    new_domain = domain.copy()
    rows, cols = domain.shape
    moved = np.zeros_like(domain, dtype=bool)

    # Randomize order of cell updates to avoid bias
    indices = [(i, j) for i in range(rows) for j in range(cols)]
    random.shuffle(indices)

    for i, j in indices:
        if moved[i, j]:
            continue

        current = domain[i, j]

        # Grass doesn't move
        if current == GRASS:
            continue

        neighbors = get_neighbors(domain, i, j)

        if current == TRICERATOPS:
            # Moves toward grass, away from predators
            grass_neighbors = [(x, y) for x, y, s in neighbors if s == GRASS]
            predator_neighbors = [(x, y) for x, y, s in neighbors if s in [VELOCIRAPTOR, TREX]]

            if predator_neighbors and grass_neighbors:
                # Flee from predators
                target = random.choice(grass_neighbors)
                new_domain[i, j] = GRASS
                new_domain[target[0], target[1]] = TRICERATOPS
                moved[target[0], target[1]] = True
            elif grass_neighbors and random.random() < 0.3:
                # Move toward food
                target = random.choice(grass_neighbors)
                new_domain[i, j] = GRASS
                new_domain[target[0], target[1]] = TRICERATOPS
                moved[target[0], target[1]] = True

        elif current == BRACHIOSAURUS:
            # Moves slowly toward grass
            grass_neighbors = [(x, y) for x, y, s in neighbors if s == GRASS]
            if grass_neighbors and random.random() < 0.2:  # Slower movement
                target = random.choice(grass_neighbors)
                new_domain[i, j] = GRASS
                new_domain[target[0], target[1]] = BRACHIOSAURUS
                moved[target[0], target[1]] = True

        elif current == VELOCIRAPTOR:
            # Moves toward prey or toward other raptors (pack behavior)
            prey_neighbors = [(x, y) for x, y, s in neighbors if s in [TRICERATOPS, BRACHIOSAURUS, HUMAN]]
            raptor_neighbors = [(x, y) for x, y, s in neighbors if s == VELOCIRAPTOR]
            empty_neighbors = [(x, y) for x, y, s in neighbors if s == GRASS]

            if prey_neighbors and random.random() < 0.5:
                # Chase prey
                target = random.choice(prey_neighbors)
                new_domain[i, j] = GRASS
                new_domain[target[0], target[1]] = VELOCIRAPTOR
                moved[target[0], target[1]] = True
            elif empty_neighbors and random.random() < 0.4:
                # Roam
                target = random.choice(empty_neighbors)
                new_domain[i, j] = GRASS
                new_domain[target[0], target[1]] = VELOCIRAPTOR
                moved[target[0], target[1]] = True

        elif current == TREX:
            # Moves toward any prey
            prey_neighbors = [(x, y) for x, y, s in neighbors if s in [TRICERATOPS, BRACHIOSAURUS, VELOCIRAPTOR, HUMAN]]
            empty_neighbors = [(x, y) for x, y, s in neighbors if s == GRASS]

            if prey_neighbors and random.random() < 0.4:
                # Chase prey
                target = random.choice(prey_neighbors)
                new_domain[i, j] = GRASS
                new_domain[target[0], target[1]] = TREX
                moved[target[0], target[1]] = True
            elif empty_neighbors and random.random() < 0.3:
                # Roam
                target = random.choice(empty_neighbors)
                new_domain[i, j] = GRASS
                new_domain[target[0], target[1]] = TREX
                moved[target[0], target[1]] = True

        elif current == HUMAN:
            # Moves away from predators, toward other humans or herbivores (safer)
            # Can also move strategically toward prey when in groups
            predator_neighbors = [(x, y) for x, y, s in neighbors if s in [VELOCIRAPTOR, TREX]]
            safe_neighbors = [(x, y) for x, y, s in neighbors if s == GRASS]
            human_neighbors = [(x, y) for x, y, s in neighbors if s == HUMAN]
            herbivore_neighbors = [(x, y) for x, y, s in neighbors if s in [TRICERATOPS, BRACHIOSAURUS]]
            raptor_neighbors = [(x, y) for x, y, s in neighbors if s == VELOCIRAPTOR]

            # Count nearby humans to determine if they should hunt
            nearby_humans = count_species_nearby(neighbors, HUMAN)

            if predator_neighbors and safe_neighbors:
                # Flee from predators
                furthest = safe_neighbors[0] if safe_neighbors else None
                if furthest and random.random() < 0.6:
                    new_domain[i, j] = GRASS
                    new_domain[furthest[0], furthest[1]] = HUMAN
                    moved[furthest[0], furthest[1]] = True
            elif nearby_humans >= 3 and herbivore_neighbors and random.random() < 0.3:
                # Group hunting behavior - move toward herbivores
                target = random.choice(herbivore_neighbors)
                new_domain[i, j] = GRASS
                new_domain[target[0], target[1]] = HUMAN
                moved[target[0], target[1]] = True
            elif nearby_humans >= 5 and raptor_neighbors and random.random() < 0.2:
                # Large group hunting - move toward raptors
                target = random.choice(raptor_neighbors)
                new_domain[i, j] = GRASS
                new_domain[target[0], target[1]] = HUMAN
                moved[target[0], target[1]] = True
            elif safe_neighbors and random.random() < 0.3:
                # Normal movement
                target = random.choice(safe_neighbors)
                new_domain[i, j] = GRASS
                new_domain[target[0], target[1]] = HUMAN
                moved[target[0], target[1]] = True

    return new_domain