import math
import numpy

# import Islands
from Islands import LatiumIsland
from Islands import LatiumFertility


#
###########################################################################################
#
class SimulatedAnnealing_Base:
    """
    Base class for Simulated Annealing Solver derived classes
    child classes should
        - define the array to be sorted
        - specify the score() virtual function for a particular sequence of list members
        - note that this solver logic finds high scores, i.e. maximums
    """

    def __init__(self):
        # the list of items to be sorted
        self.the_list = []

        # simulated annealing solver tuning parameters
        self.max_anneals = 200      # black art = set as approx log(.01/Temperature)/(log(coolingrate))
        self.max_trials = 1000      # max trials per annealing temperature
        self.temperature = 500.0    # black art = pick this to be ~150% of a typical score change
        self.cooling_rate = 0.95    # a slower rate allows solution to better avoid local maxima to find a true maxima

    def score(self, candidate_list: list) -> float:
        """
        function to define the value or score of this particular list arrangement
        """
        raise NotImplementedError()

    def solve(self) -> list:
        """
        Simulated Annealing basic algorithm
            - start with initial random solution, and a high initial temperature T
            -   anneal_counter loop
            -       trial_counter loop
            -           determine a neighboring, perturbed solution
            -           determine difference in "cost", DeltaE
            -           if new solution is better, accept it
            -           if new solution is worse, accept it based on probability P = exp(-DeltaE/T)
            -       cool the temperature according to a schedule, T_new = cooling_rate * T_old
        :return: optimized list
        """
        current_score = self.score(self.the_list)

        for anneal_counter in range(self.max_anneals):

            # print(f"Outer loop: [{anneal_counter}] Temperature: [{self.temperature}]------------------------------------")
            # print(f"{anneal_counter} ", end = '')
            for trial_counter in range(self.max_trials):
                perturbed_list = self.perturb_list(self.the_list.copy())
                perturbed_score = self.score(perturbed_list)

                accept = False
                # if perturbed_score is better, accept the change
                if perturbed_score > current_score:
                    accept = True

                # if perturbed_score is worse, maybe accept the change
                elif perturbed_score < current_score:
                    # this delta will be a negative value, which is needed
                    delta_score = perturbed_score - current_score
                    prob_acceptance = math.exp(delta_score / self.temperature)
                    # print(f"prob: [{prob_acceptance}]")
                    if numpy.random.rand() < prob_acceptance:
                        accept = True

                # if perturbed_score is unchanged, do not accept the change

                # if accepted...
                if accept:
                    self.the_list = perturbed_list
                    current_score = perturbed_score
                    # print(f"New score: [{current_score}]")

            # cool off the annealing process
            self.temperature *= self.cooling_rate

        return self.the_list

    @staticmethod
    def perturb_list(the_list: list) -> list:
        """
        Take an existing list, and perturb it by
            - taking a segment of list members beginning at a random list position,
            - of random length,
            - and inserting the segment back into the list at a new random position
        :param the_list: the original list
        :return: the perturbed list
        """

        # print("---")
        # print(f"Initial List    : {the_list}")
        # print(f"Length          : {len(the_list)}")

        # pick a random segment to remove from current list, in range [0, my_list_len)
        segment_start = numpy.random.randint(0, len(the_list))
        segment_length = numpy.random.randint(1, len(the_list) - segment_start + 1)

        # get the segment using slice syntax, and then remove it from original list
        segment = the_list[segment_start:segment_start+segment_length]
        del the_list[segment_start:segment_start+segment_length]

        # print("---")
        # print(f"Segment start   : {segment_start}")
        # print(f"Segment length  : {segment_length}")
        # print(f"Segment         : {segment}")
        # print(f"Segment length  : {len(segment)}")
        # print(f"Modified List   : {the_list}")
        # print(f"Length          : {len(the_list)}")

        # ensure new segment start isn't the old one, which would just put the segment back where it came from
        new_segment_start = numpy.random.randint(0, len(the_list) + 1)

        # insert segment back into list in the new position
        the_list = the_list[:new_segment_start] + segment + the_list[new_segment_start:]

        # print("---")
        # print(f"New Seg start   : {new_segment_start}")
        # print(f"Modified List   : {the_list}")
        # print(f"Length          : {len(the_list)}")

        return the_list

#
###########################################################################################
#
class SimpleArraySolver(SimulatedAnnealing_Base):
    """
    Proof of concept solver
    """
    def __init__(self):
        # call parent ctor
        super().__init__()

        # set up a basic array of numbers
        # [0, 10, 20, ... 230, 240]
        for i in range(25):
            self.the_list.append(10 * i)

    # define the virtual score() function
    # this one simply defines the score as a weighted sum of the first 3 list values
    # the perfect sorted order be [240, 230, 220, ...the rest doesn't matter]
    def score(self, candidate_list: list) -> float:
        rv = candidate_list[0] + 0.9 * candidate_list[1] + 0.8 * candidate_list[2]
        return rv

#
###########################################################################################
#
class LatiumIslandSolver(SimulatedAnnealing_Base):
    """
    Solver for Latium Islands.
    Find an optimum set of Latium Islands which provides all Latium fertilities
    """
    def __init__(self):
        # call parent ctor
        super().__init__()

        # set up a basic array of islands
        self.load_islands()

        # solution tuning factors
        self.max_trials = 500
        self.cooling_rate = 0.95
        self.extra_island_reduction_rate = 0.9
        self.extra_island_penalty = 100


    def load_islands(self):
        """
        load island info from a CSV file
        # todo - read this info from a savegame file
        ideally this function should be replaced to read the island info
        directly from a save file
        """

        # todo - make this more general, rather than hardcoding it
        filename = 'corners_seed7324_latium.csv'
        # filename = 'archipelago_seed8689_latium.csv'

        # walk the input file list
        with open(filename, 'r') as file:
            for line in file:
                # Process each line here
                if line[0] != '#':
                    island = LatiumIsland.from_string(line.strip())
                    self.the_list.append(island)
                    # island.dump()



    # define the virtual score() function
    def score(self, candidate_list: list) -> float:

        # determine a score for the first N islands, where N is the number of islands required
        # to provide one of every fertility

        # walk the list until we have gotten all the fertilities
        # order matters, so reduce the score in subsequent islands by 'extra_island_reduction_rate'
        # also, we only want the minimum number of islands to cover all fertilities, so
        # add a penalty for every island beyond the first
        rv = 0.0
        covered_fertilities: LatiumFertility = LatiumFertility.all_fertilities()
        island: LatiumIsland
        for ndx, island in enumerate(candidate_list):
            rv += (self.extra_island_reduction_rate ** ndx) * island.calculate_score(covered_fertilities)
            rv -= ndx * self.extra_island_penalty
            # removed this island's fertilities from the overall list
            covered_fertilities &= ~island.fertilities
            if covered_fertilities == LatiumFertility.no_fertilities():
                break
        # print(f"highest index to cover all ferts = {ndx}")

        return rv

    def report(self):

        print(f"Score: [{self.score(self.the_list)}] [", end = '')

        covered_fertilities = LatiumFertility.all_fertilities()

        island: LatiumIsland
        for island in self.the_list:
            print(f"{island.island_name}", end = '')
            covered_fertilities &= ~island.fertilities
            if covered_fertilities == LatiumFertility.no_fertilities():
                break
            print(", ", end = '')

        print("]")



#
###########################################################################################
#
def main():

    # simple_solver = SimpleArraySolver()
    # my_list = simple_solver.the_list
    # print(f"Initial List   [{len(my_list)}]    : {my_list}")
    #
    # my_list = simple_solver.solve()
    # print(f"Final List     [{len(my_list)}]    : {my_list}")

    # latium solver
    lat_solver = LatiumIslandSolver()
    # score = lat_solver.score(lat_solver.the_list)
    # print(f"Score: [{score}]")
    lat_solver.report()
    lat_solver.solve()
    lat_solver.report()

    print("Done")



if __name__ == '__main__':
    main()