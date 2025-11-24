import random


# parent class for all species
class Species:
    def __init__(self, strength, speed, toughness, coordination, health, reproduction_rate, survivability,
                 harvest_rate=0):
        self.strength = strength
        self.speed = speed
        self.toughness = toughness
        self.coordination = coordination
        self.health = health
        self.reproduction_rate = reproduction_rate
        self.survivability = survivability  # chance to survive random death each round
        self.harvest_rate = harvest_rate
        self.tamed_rounds = 0  # number of rounds of dino tamed

    def attack(self, target_health, target_toughness, coord_bonus=1.0):
        # damage dealt and gives kill chance
        damage = self.strength * coord_bonus * (1 - target_toughness)
        kill_chance = damage / target_health
        return kill_chance

    def move(self):
        # True if species moves this turn
        return random.random() < self.speed

    def reproduce(self):
        # if species reproduces
        return random.random() < self.reproduction_rate

    def survives_round(self):
        #True if species survives random death
        return random.random() < self.survivability

    def harvest(self):
        # True if herbivore successfully harvests
        return random.random() < self.harvest_rate


# Velociraptor class
class Velociraptor(Species):
    def __init__(self):
        super().__init__(
            strength=0.6,  # medium
            speed=0.75,  # very high
            toughness=0.35,  # low
            coordination=0.85,  # very high
            health=55,  # medium
            reproduction_rate=0.6,  # medium
            survivability=0.975
        )


# T-Rex class
class TRex(Species):
    def __init__(self):
        super().__init__(
            strength=0.95,  # very high
            speed=0.6,  # medium/high
            toughness=0.7,  # high
            coordination=0.25,  # very low
            health=90,  # high
            reproduction_rate=0.33,  # low
            survivability=0.975
        )


# Triceratops class
class Triceratops(Species):
    def __init__(self):
        super().__init__(
            strength=0.5,  # medium
            speed=0.5,  # medium
            toughness=0.5,  # medium
            coordination=0.5,  # medium
            health=60,  # medium
            reproduction_rate=0.35,  # high
            harvest_rate=0.4,  # medium/high
            survivability=0.71
        )


# Brachiosaurus class
class Brachiosaurus(Species):
    def __init__(self):
        super().__init__(
            strength=0.8,  # very high
            speed=0.2,  # very low
            toughness=0.8,  # very high
            coordination=0.2,  # very low
            health=100,  # very high
            reproduction_rate=0.25,  # very low
            harvest_rate=0.5,  # medium
            survivability=0.78
        )


# Human class
class Human(Species):
    def __init__(self):
        super().__init__(
            strength=0.3,  # low
            speed=0.6,  # medium/high
            toughness=0.55,  # high
            coordination=0.9,  # very high
            health=30,  # very low
            reproduction_rate=0.3,  # medium
            harvest_rate=0.15,  # low/medium
            survivability=0.825
        )

    def tame(self, target_species):
        # humans tame raptors and t-rexes to make them docile for 5 rounds
        if target_species in [1, 2]:  # raptor/Trex
            if random.random() < 0.3:  # 30% chance to tame
                return True
        return False

species_stats = {
    1: Velociraptor(),
    2: TRex(),
    3: Triceratops(),
    4: Brachiosaurus(),
    5: Human()
}
# tame length (key = (row, col), value = # of rounds left)
tamed_dinos = {}


def get_neighbors(domain, row, col):
    # checks adjacent tiles
    neighbors = []
    rows, cols = domain.shape
    for neighbor_row in [-1, 0, 1]:
        for neigbor_column in [-1, 0, 1]:
            if neighbor_row == 0 and neigbor_column == 0:
                continue
            new_row = row + neighbor_row
            new_col = col + neigbor_column
            if 0 <= new_row < rows and 0 <= new_col < cols:
                neighbors.append((new_row, new_col))
    return neighbors


def count_same_species_neighbors(domain, row, col, species_type):
    # count how many of the same species are adjacent
    neighbors = get_neighbors(domain, row, col)
    count = 0
    for nr, nc in neighbors:
        if domain[nr, nc] == species_type:
            count += 1
    return count


def update_states(domain):
    # for interactions between species per round
    rows, cols = domain.shape
    new_domain = domain.copy()

    # update tamed status
    global tamed_dinos
    tame_remove = []
    for pos in tamed_dinos:
        tamed_dinos[pos] -= 1
        if tamed_dinos[pos] <= 0:
            tame_remove.append(pos)
    for pos in tame_remove:
        del tamed_dinos[pos]

    # iterates through each cell and kills randomly based on survivability stat
    for i in range(rows):
        for j in range(cols):
            current = domain[i, j]
            if current != 0 and current in species_stats:
                species = species_stats[current]
                # check using survives_round()
                if not species.survives_round():
                    new_domain[i, j] = 0  # dies and then becomes grass
                    continue

    # iterates thru each cell
    for i in range(rows):
        for j in range(cols):
            current = new_domain[i, j]
            # skip past veg tile
            if current == 0:
                continue

            # species stats
            if current in species_stats:
                species = species_stats[current]
                neighbors = get_neighbors(new_domain, i, j)

                if current in [3, 4, 5]:  # triceratops, brachiosaurus, human
                    # check for adjacent grass to harvest
                    for nr, nc in neighbors:
                        if new_domain[nr, nc] == 0:  # grass tile
                            if species.harvest():
                                # try to reproduce
                                if species.reproduce():
                                    # find empty grass tile to place offspring
                                    empty_neighbors = [(r, c) for r, c in neighbors if new_domain[r, c] == 0]
                                    if empty_neighbors:
                                        spawn_r, spawn_c = random.choice(empty_neighbors)
                                        new_domain[spawn_r, spawn_c] = current
                                break

                # Carnivores hunt
                if current in [1, 2, 5]:  # velociraptor, t-rex, human
                    # look for prey
                    prey_neighbors = []
                    for nr, nc in neighbors:
                        neighbor_species = new_domain[nr, nc]

                        # humans try to tame first
                        if current == 5 and neighbor_species in [1, 2]:
                            if (nr, nc) not in tamed_dinos:
                                human = species_stats[5]
                                if human.tame(neighbor_species):
                                    tamed_dinos[(nr, nc)] = 5  # tamed for 3 rounds
                                    continue

                        # check if it's valid prey
                        if neighbor_species == 0:  # grass, skip
                            continue
                        if current == neighbor_species:  # same species, skip
                            continue
                        if (nr, nc) in tamed_dinos:  # tamed dino, humans can't attack
                            if current == 5:
                                continue

                        # herbivores don't attack humans or other herbivores
                        if current in [3, 4]:
                            if neighbor_species in [1, 2]:  # only attack carnivores
                                prey_neighbors.append((nr, nc, neighbor_species))
                        else:
                            prey_neighbors.append((nr, nc, neighbor_species))

                    # attack a random prey
                    if prey_neighbors:
                        target_r, target_c, target_species = random.choice(prey_neighbors)

                        # calculate coordination bonus
                        same_species_count = count_same_species_neighbors(new_domain, i, j, current)
                        coord_bonus = 1 + (species.coordination * same_species_count * 0.1)

                        # use attack method to calculate kill chance
                        target_stats = species_stats[target_species]
                        kill_chance = species.attack(target_stats.health, target_stats.toughness, coord_bonus)

                        # check if target dies
                        if random.random() < kill_chance:
                            # target dies
                            new_domain[target_r, target_c] = 0  # becomes grass

                            # carnivore tries to reproduce
                            if current in [1, 2]:
                                # reproduction chance varies by what was killed
                                base_repro = species.reproduction_rate
                                if target_species == 4:  # brachiosaurus
                                    repro_chance = base_repro * 1.5
                                elif target_species == 2:  # trex
                                    repro_chance = base_repro * 1.3
                                elif target_species == 3:  # triceratops
                                    repro_chance = base_repro * 1.1
                                elif target_species == 1:  # velociraptor
                                    repro_chance = base_repro * 0.9
                                elif target_species == 5:  # human
                                    repro_chance = base_repro * 0.7
                                else:
                                    repro_chance = base_repro

                                if random.random() < repro_chance:
                                    new_domain[target_r, target_c] = current

    return new_domain


def update_positions(domain):
    # this function handles movement of species
    rows, cols = domain.shape
    new_domain = domain.copy()

    # create a list of all non-grass positions
    positions = []
    for i in range(rows):
        for j in range(cols):
            if domain[i, j] != 0:
                positions.append((i, j))

    # shuffle to randomize movement order
    random.shuffle(positions)

    for i, j in positions:
        current = domain[i, j]
        if current == 0:
            continue

        # check if this species moves
        if current in species_stats:
            species = species_stats[current]
            if species.move():
                # find adjacent empty grass tiles
                neighbors = get_neighbors(domain, i, j)
                empty_neighbors = [(r, c) for r, c in neighbors if new_domain[r, c] == 0]

                if empty_neighbors:
                    # move to random empty neighbor
                    new_r, new_c = random.choice(empty_neighbors)
                    new_domain[new_r, new_c] = current
                    new_domain[i, j] = 0

    return new_domain
