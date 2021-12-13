#
# The script providing implementation of structures and functions used in
# the Novelty Search method.
#
from functools import total_ordering

# how many nearest neighbors to consider for calculating novelty score?
KNNNoveltyScore = 15
# The maximal allowed size for fittest items list
FittestAllowedSize = 5
# The minimal number of items to include in the archive unconditionaly
ArchiveSeedAmount = 1

@total_ordering
class NoveltyItem:
    """
    The class to encapsulate information about particular item that
    holds information about novelty score associated with specific
    genome along with auxiliary information. It is used in combination
    with NoveltyArchive
    """
    def __init__(self, generation=-1, genomeId=-1, fitness=-1, novelty=-1):
        """
        Creates new item with specified parameters.
        Arguments:
            generation: The evolution generation when this item was created
            genomeId:   The ID of genome associated with it
            fitness:    The goal-oriented fitness score of genome associated with this item
            novelty:    The novelty score of genome
        """
        self.generation = generation
        self.genomeId = genomeId
        self.fitness = fitness
        self.novelty = novelty
        # Indicates whether this item was already added to the archive
        self.in_archive = False
        # The list holding data points associated with this item that will be used
        # to calculate distance between this item and any other item. This distance
        # will be used to estimate the novelty score associated with the item.
        self.data = []

    def __str__(self):
        """
        The function to create string representation
        """
        return "%s: id: %d, at generation: %d, fitness: %f, novelty: %f\tdata: %s" % \
            (self.__class__.__name__, self.genomeId, self.generation, self.fitness, self.novelty, self.data)

    def _is_valid_operand(self, other):
        return (hasattr(other, "fitness") and
                hasattr(other, "novelty"))

    def __lt__(self, other):
        """
        Compare if this item is less than supplied other item by
        goal-oriented fitness value.
        """
        if not self._is_valid_operand(other):
            return NotImplemented

        if self.fitness < other.fitness:
            return True
        elif self.fitness == other.fitness:
            # less novel is less
            return self.novelty < other.novelty
        return False

@total_ordering
class ItemsDistance:
    """
    Holds information about distance between the two NoveltyItem objects based
    on the nearest neighbour metric.
    """
    def __init__(self, first_item, second_item, distance):
        """
        Creates new instance for two NoveltyItem objects
        Arguments:
            first_item:     The item from which distance is measured
            second_item:    The item to which distance is measured
            distance:       The distance value
        """
        self.first_item = first_item
        self.second_item = second_item
        self.distance = distance

    def _is_valid_operand(self, other):
        return hasattr(other, "distance")

    def __lt__(self, other):
        """
        Compare if the distance in this object is less that in other.
        """
        if not self._is_valid_operand(other):
            return NotImplemented

        return self.distance < other.distance

class NoveltyArchive:
    """
    The novelty archive contains all of the novel items we have encountered thus far.
    """
    def __init__(self, threshold, metric):
        """
        Creates new instance with specified novelty threshold and function
        defined novelty metric.
        Arguments:
            threshold:  The minimal novelty score of the item to be included into this archive.
            metric:     The function to calculate the novelty score of specific genome.
        """
        self.novelty_metric = metric
        self.novelty_threshold = threshold

        # the minimal possible value of novelty threshold
        self.novelty_floor = 0.25
        # the novel items added during current generation
        self.items_added_in_generation = 0
        # the counter to keep track of how many generations passed
        # since we've added to the archive
        self.time_out = 0
        # the parameter specifying how many neighbors to look at for the K-nearest
        # neighbor distance estimation to be used in novelty score
        self.neighbors = KNNNoveltyScore
        # the current evolutionary generation
        self.generation = 0

        # list with all novel items found so far
        self.archive_items = []
        # list with all novel items found that is related to the fittest
        # genomes (using the goal-oriented fitness score)
        self.fittest_items = []

    def evaluate_individual_novelty(self, item, current_items=None, for_neat_fitness=False):
        """
        The function to evaluate the novelty score of a single genome within
        population and update its fitness if appropriate (for_neat_fitness=True)
        Arguments:
            item:               The item of the genome to evaluate
            current_items:      The items for the current population
            for_neat_fitness:   The flag to indicate the purpose of this function.
                                If True, to evaluate fitness for neat. Otherwise, to evaluate just
                                novelty and to accept the genome into nevelty items archive.
        Returns:
            The calculated novelty score or fitness for individual genome.
        """
        # Check if individual was marked for extinction due to failure to meet minimal fitness criterion
        if item.fitness == -1.0:
            return -1.0

        novelty = 0.0
        if for_neat_fitness:
            # assign genome fitness according to the average novelty within archive and population
            compare_items = self.archive_items + current_items
            distances = self._map_novelty(item,compare_items)
            novelty = self._novelty_avg_knn(distances,k=self.neighbors)
        else:
            # consider adding a NoveltyItem to the archive based on the distance to a closest neighbor
            compare_items = self.archive_items
            distances = self._map_novelty(item,compare_items)
            novelty = self._novelty_avg_knn(distances,k=1)
            if novelty > self.novelty_threshold or len(self.archive_items) < ArchiveSeedAmount:
                self._add_novelty_item(item)

        # store found values to the novelty item
        item.novelty = novelty
        item.generation = self.generation

        return novelty

    def update_fittest_with_genome(self, items_map):
        """
        The function to update list of NovelItems for the genomes with the higher
        fitness scores achieved so far during the evolution.
        Arguments:
            items_map:    The map of novelty items for the current population by genome ID
        """

        n_items_list = list(items_map.values())
        # store novelty items into fittest
        self.fittest_items.extend(n_items_list)
        # sort in descending order by fitness
        self.fittest_items.sort(reverse=True)

        # remove overflow items
        if len(self.fittest_items) > FittestAllowedSize:
            del self.fittest_items[FittestAllowedSize:]

    def end_of_generation(self):
        """
        The function to update archive state at the end of the generation.
        """
        self.generation += 1
        self._adjust_archive_settings()

    def write_to_file(self, path):
        """
        The function to write all NoveltyItems stored in this archive.
        Arguments:
            path: The path to the file where to store NoveltyItems
        """
        with open(path, 'w') as file:
            for ni in self.archive_items:
                file.write("%s\n" % ni)

    def write_fittest_to_file(self, path):
        """
        The function to write the list of NoveltyItems of fittests genomes
        that was collected during the evolution.
        Arguments:
            path: The path to the file where to store NoveltyItems
        """
        with open(path, 'w') as file:
            for ni in self.fittest_items:
                file.write("%s\n" % ni)

    def _add_novelty_item(self, item):
        """
        The function to add specified NoveltyItem to this archive.
        Arguments:
            item: The NoveltyItem to be added
        """
        # add item
        item.in_archive = True
        item.generation = self.generation
        self.archive_items.append(item)
        self.items_added_in_generation += 1

    def _adjust_archive_settings(self):
        """
        The function to adjust the dynamic novelty threshold depending
        on how many have NoveltyItem objects have been added to the archive recently
        """
        if self.items_added_in_generation == 0:
            self.time_out += 1
        else:
            self.time_out = 0

        # if no items have been added for the last 10 generations lower the threshold
        if self.time_out >= 10:
            self.novelty_threshold *= 0.95
            if self.novelty_threshold < self.novelty_floor:
                self.novelty_threshold = self.novelty_floor
            self.time_out = 0

        # if more than four individuals added in last generation then raise threshold
        if self.items_added_in_generation >= 4:
            self.novelty_threshold *= 1.2

        # reset counters
        self.items_added_in_generation = 0

    def _map_novelty(self,item,archive_items):
        """
        The function to map the novelty metric across the list of item against the target item.
        Arguments:
            item:           The NoveltyItem to be used for archive mapping.
            compare_items:  The List of item to compare
        Returns:
            The list with distances (novelty scores) of provided item from list of item.
        """
        distances = []
        for a_item in archive_items:
            distance = ItemsDistance(
                first_item = a_item,
                second_item = item,
                distance = self.novelty_metric(a_item, item))
            distances.append(distance)
        return distances

    def _novelty_avg_knn(self,distances,k):
        """
        The function to calculate the novelty score of a given distances
        using a K-nearest neighbor algorithm.
        Argumnets:
            distances:  The list of distance
            k        : The number of neighbors to use for calculation
        Returns:
            The density within the vicinity of the provided distances calculated using the K-nearest neighbor
            algorithm. This density can be used either as a novelty score value or as a fitness value.
        """
        # sort by distance (novelty) in ascending order - the minimal first
        distances.sort()

        density, distance_sum = 0.0, 0.0
        length = len(distances)
        if length >= ArchiveSeedAmount:
            length = k
            if len(distances) < length:
                # the number of mapped distances is less than number of neighbors
                length = len(distances)
            for i in range(length):
                distance_sum += distances[i].distance

            # finding the average
            if length > 0:
                density = distance_sum / length

        return density
