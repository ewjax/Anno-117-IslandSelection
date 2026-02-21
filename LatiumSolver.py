from LatiumIsland import *
from SimulatedAnnealingSolver import *
import sys

###########################################################################################
#
#
class LatiumSolver(SimulatedAnnealingSolver):
    """
    Solver for Latium Islands.
    Find an optimum set of Latium Islands which provides all Latium fertilities
    """
    def __init__(self):
        # call parent ctor
        super().__init__()

        # input file
        self.filename = ''

        # solution tuning factors
        self.max_anneals = 200      # black art = set as approx log(.01/Temperature)/(log(coolingrate))
        self.max_trials = 1000      # max trials per annealing temperature
        self.temperature = 1000.0    # black art = pick this to be ~150% of a typical score change
        self.cooling_rate = 0.95    # a slower rate allows solution to better avoid local maxima to find a true maxima

        self.extra_island_reduction_rate = 0.9
        self.extra_island_penalty = 200

    def set_filename(self, filename: str):
        # set up a basic array of islands
        self.filename = filename
        self.load_islands()

    def load_islands(self):
        """
        load island info from a CSV file
        # todo - read this info from a savegame file rather than a CSV file
        ideally this function should be replaced to read the island info
        directly from a save file
        """

        # ensure list starts empty
        self.the_list = []

        # walk the input file list
        with open(self.filename, 'r') as file:
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
            covered_fertilities = covered_fertilities.remove(island.fertilities)
            if covered_fertilities == LatiumFertility.no_fertilities():
                break
        # print(f"highest index to cover all ferts = {ndx}")

        return rv

    def report(self) -> list:
        """
        write results of the solve action to stdout

        :return: list of the islands in the solution
        """
        rv = list()
        covered_fertilities = LatiumFertility.all_fertilities()

        print(f"Islands: [", end = '')
        island: LatiumIsland
        for island in self.the_list:
            rv.append(island)
            print(f"{island.island_name}", end = '')
            # removed this island's fertilities from the overall list
            covered_fertilities = covered_fertilities.remove(island.fertilities)
            if covered_fertilities == LatiumFertility.no_fertilities():
                break
            print(", ", end = '')

        print(f"] (Score = {self.score(self.the_list):.0f})")

        # return a list of the solution islands
        return rv


#
###########################################################################################
#
def main():

    # command line
    #       python LatiumSolver.py inputfile.csv
    if len(sys.argv) != 2:
        print("Usage:")
        print("     python LatiumSolver.py inputfile.csv")
        exit(-1)

    # latium solver
    lat_solver = LatiumSolver()
    lat_solver.set_filename(sys.argv[1])
    print('')
    print(f"Region map: [{lat_solver.filename}]")
    # score = lat_solver.score(lat_solver.the_list)
    # print(f"Score: [{score}]")
    # lat_solver.report()


    print("Optimized Island Set, Latium Islands:")
    lat_solver.solve()
    print("            ", end = '')
    lat_solver.report()


    print("Done")



if __name__ == '__main__':
    main()