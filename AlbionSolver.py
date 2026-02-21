from AlbionIsland import *
from SimulatedAnnealingSolver import *

###########################################################################################
#
#
class AlbionSolver(SimulatedAnnealingSolver):
    """
    Solver for Albion Islands.
    Find an optimum set of Albion Islands which provides all Albion fertilities
    """
    def __init__(self):
        # call parent ctor
        super().__init__()

        # set up a basic array of islands
        self.load_islands()

        # use this to target All, Celtic or Roman fertilities in the solution
        self.starting_fertilities = AlbionFertility.all_fertilities()

        # solution tuning factors
        self.max_anneals = 200      # black art = set as approx log(.01/Temperature)/(log(coolingrate))
        self.max_trials = 1000      # max trials per annealing temperature
        self.temperature = 1000.0    # black art = pick this to be ~150% of a typical score change
        self.cooling_rate = 0.95    # a slower rate allows solution to better avoid local maxima to find a true maxima

        self.extra_island_reduction_rate = 0.9
        self.extra_island_penalty = 100


    def load_islands(self):
        """
        load island info from a CSV file
        # todo - read this info from a savegame file
        ideally this function should be replaced to read the island info
        directly from a save file
        """

        # ensure list starts empty
        self.the_list = []

        # todo - make this more general, rather than hardcoding it
        # filename = 'corners_seed7324_albion.csv'
        filename = 'archipelago_seed8689_albion.csv'

        # walk the input file list
        with open(filename, 'r') as file:
            for line in file:
                # Process each line here
                if line[0] != '#':
                    island = AlbionIsland.from_string(line.strip())
                    self.the_list.append(island)
                    # island.dump()
                    # print(f"Island: [{island.island_name}]")
                    # print(f"    Celtic Score: [{island.calculate_score(AlbionFertility.celtic())}]")
                    # print(f"    Roman Score:  [{island.calculate_score(AlbionFertility.roman())}]")

    def set_coverage(self, starting_fertilities: AlbionFertility):
        self.starting_fertilities = starting_fertilities

    # define the virtual score() function
    def score(self, candidate_list: list) -> float:

        # determine a score for the first N islands, where N is the number of islands required
        # to provide one of every fertility

        # walk the list until we have gotten all the fertilities
        # order matters, so reduce the score in subsequent islands by 'extra_island_reduction_rate'
        # also, we only want the minimum number of islands to cover all fertilities, so
        # add a penalty for every island beyond the first
        rv = 0.0
        covered_fertilities: AlbionFertility = self.starting_fertilities
        island: AlbionIsland
        for ndx, island in enumerate(candidate_list):
            rv += (self.extra_island_reduction_rate ** ndx) * island.calculate_score(covered_fertilities)
            rv -= ndx * self.extra_island_penalty
            # removed this island's fertilities from the overall list
            covered_fertilities = covered_fertilities.remove(island.fertilities)
            if covered_fertilities == AlbionFertility.no_fertilities():
                break
        # print(f"highest index to cover all ferts = {ndx}")

        return rv

    def report(self) -> []:

        rv = []
        covered_fertilities: AlbionFertility = self.starting_fertilities

        print(f"Islands: [", end = '')
        island: AlbionIsland
        for ndx, island in enumerate(self.the_list):
            rv.append(island)
            print(f"{island.island_name}", end = '')
            # removed this island's fertilities from the overall list
            covered_fertilities = covered_fertilities.remove(island.fertilities)
            if covered_fertilities == AlbionFertility.no_fertilities():
                break
            print(", ", end = '')

        print(f"] (Score = {self.score(self.the_list):.0f})")

        # return a list of the solution islands
        return rv





#
###########################################################################################
#
def main():

    # Albion solver
    alb_solver = AlbionSolver()
    # alb_solver.report()

    # alb_solver.solve()
    # print("Roman+Celtic Combined Optimized Island Set:")
    # alb_solver.report()


    print('Beginning Island Optimization Process...')
    print('')


    # solve for islands for first population
    # print(f"num islands = {len(alb_solver.the_list)}")
    print("Roman then Celtic Optimized Island Set:")
    alb_solver.set_coverage(AlbionFertility.roman())
    alb_solver.solve()
    print("      Roman ", end = '')
    solution_islands = alb_solver.report()

    # remove islands used in first population as not available for second population
    new_list = [island for island in alb_solver.the_list if island not in solution_islands]
    alb_solver.the_list = new_list
    # print(f"num islands = {len(alb_solver.the_list)}")

    # solve for islands for second population
    alb_solver.set_coverage(AlbionFertility.celtic())
    alb_solver.solve()
    print("     Celtic ", end = '')
    alb_solver.report()

    # reload islands, and do it in the reverse order
    alb_solver.load_islands()

    # solve for islands for first population
    # print(f"num islands = {len(alb_solver.the_list)}")
    print("Celtic then Roman Optimized Island Set:")
    alb_solver.set_coverage(AlbionFertility.celtic())
    alb_solver.solve()
    print("     Celtic ", end = '')
    solution_islands = alb_solver.report()

    # remove islands used in first population as not available for second population
    new_list = [island for island in alb_solver.the_list if island not in solution_islands]
    alb_solver.the_list = new_list
    # print(f"num islands = {len(alb_solver.the_list)}")

    # solve for islands for second population
    alb_solver.set_coverage(AlbionFertility.roman())
    alb_solver.solve()
    print("      Roman ", end = '')
    alb_solver.report()



    print('')
    print("Done")



if __name__ == '__main__':
    main()