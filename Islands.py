from enum import IntFlag, IntEnum, auto

import Islands


class IslandSize(IntEnum):
    """
    enum for island sizes
    """
    EXTRALARGE = auto(),
    LARGE = auto(),
    MEDIUM = auto(),
    SMALL = auto()


class LatiumFertility(IntFlag):
    """
    bitmapped enum for latium island fertilities
    """
    NONE = auto(0),
    MACKEREL = auto(),
    LAVENDAR = auto(),
    RESIN = auto(),
    OLIVE = auto(),
    GRAPES = auto(),
    FLAX = auto(),
    MUREX_SNAILS = auto(),
    SANDARAC = auto(),
    OYSTER = auto(),
    STURGEON = auto(),
    MARBLE = auto(),
    IRON = auto(),
    MINERAL = auto(),
    GOLD_ORE = auto()


class LatiumIsland:

    def __init__(self,
                 island_name: str,
                 fert_values: LatiumFertility = LatiumFertility.NONE,
                 river_slots: int = 0,
                 mountain_slots: int = 0,
                 island_size: IslandSize = IslandSize.LARGE
                 ):
        self.island_name = island_name
        self.fertilities = fert_values
        self.river_slots = river_slots
        self.mountain_slots = mountain_slots
        self.island_size = island_size

        # todo - albion marshes

        # dictionary of fertility types and their weights
        self.fertility_weight = {}
        self.island_size_weight = {}
        self.define_weights()

    @classmethod
    def from_string(cls, island_string):
        fields = island_string.strip().split(',')
        print(fields)
        island_name = fields[0]

        fertilities = Islands.LatiumFertility.NONE
        # ndx = 1
        for ndx, fert_value in enumerate(Islands.LatiumFertility):
            if fields[ndx+1] != '':
                fertilities |= fert_value

        mountains = int(fields[15])
        rivers = int(fields[16])

        size = IslandSize.SMALL
        if fields[17] == 'XL':
            size = IslandSize.EXTRALARGE
        elif fields[17] == 'L':
            size = IslandSize.LARGE
        elif fields[17] == 'M':
            size = IslandSize.MEDIUM
        else:
            size = IslandSize.SMALL

        return cls(island_name, fertilities, rivers, mountains, size)


    def define_weights(self):
        """
        Weighting Scheme
        Tier2 - 5 points per production chain
        Tier3 - 3 points
        Tier4 - 1 point per production chain
        Construction material - use tier scores, but divide by 2
        River slots - 1 point per slot, adjusted by gold ore and/or sturgeon presence
        Mountain slots - 1 point per slot, adjusted by mineral score?
        """

        # tier2 chains - garum, soap
        self.fertility_weight[LatiumFertility.MACKEREL] = 5
        self.fertility_weight[LatiumFertility.LAVENDAR] = 5

        # tier3 chains - amphorae, olives
        self.fertility_weight[LatiumFertility.RESIN] = 3
        self.fertility_weight[LatiumFertility.OLIVE] = 3

        # tier4 chains - wine, togas, loungers, writing tablets, lyres, oysters w caviar, necklaces
        self.fertility_weight[LatiumFertility.GRAPES] = 1           # wine
        self.fertility_weight[LatiumFertility.FLAX] = 2             # togas, loungers
        self.fertility_weight[LatiumFertility.MUREX_SNAILS] = 2     # togas, loungers
        self.fertility_weight[LatiumFertility.SANDARAC] = 3         # writing tablets, loungers, lyres
        self.fertility_weight[LatiumFertility.OYSTER] = 1           # oysters with caviar
        self.fertility_weight[LatiumFertility.STURGEON] = 1         # oysters with caviar

        # construction material for tier3 and tier4 buildings
        # tier3 buildings - forum, baths
        # tier4 buildings - temple, libarary, amphitheatre
        # (3 + 3 + 1 + 1 + 1)/2
        self.fertility_weight[LatiumFertility.MARBLE] = 4.5

        # construction material for tier2 weapons and armor
        # (5 + 5)/2
        self.fertility_weight[LatiumFertility.IRON] = 5

        # tier4 production chains - fine glass, necklaces
        # tier4 mosaics used in buildings temple, library, amphitheatre
        # (1 + 1 + (1+1+1)/2)
        self.fertility_weight[LatiumFertility.MINERAL] = 3.5

        # tier4 - necklaces, lyres
        self.fertility_weight[LatiumFertility.GOLD_ORE] = 2

        # island size
        self.island_size_weight[IslandSize.EXTRALARGE] = 7
        self.island_size_weight[IslandSize.LARGE] = 5
        self.island_size_weight[IslandSize.MEDIUM] = 3
        self.island_size_weight[IslandSize.SMALL] = 1


    def calculate_score(self) -> float:
        """
        determine score based purely on this island's fertilities
        and the associated weighting values for each fertility
        :return:
        score
        """
        rv = 0.0

        # start with basic fertilities
        fert: LatiumFertility
        for fert in LatiumFertility:
            if self.has_fertility(fert.value):
                rv += self.fertility_weight[fert.value]

        # river slots. increase weighting if there is also a Sturgeon or Gold fertility
        rv += self.river_slots
        if self.has_fertility(LatiumFertility.STURGEON):
            rv += (self.river_slots) / 2.0
        if self.has_fertility(LatiumFertility.GOLD_ORE):
            rv += (self.river_slots) / 2.0

        # mountain slots. increase weighting if there is also a Mineral fertility
        rv += self.mountain_slots
        if self.has_fertility(LatiumFertility.MINERAL):
            rv += (self.mountain_slots) / 2.0

        # island size
        if self.island_size == IslandSize.EXTRALARGE:
            rv += 7
        elif self.island_size == IslandSize.LARGE:
            rv += 5
        elif self.island_size == IslandSize.MEDIUM:
            rv += 3
        elif self.island_size == IslandSize.SMALL:
            rv += 1

        return rv

    def add_fertility(self, fert_value: LatiumFertility):
        """
        Add a fertility to this island
        :param fert_value:
        LatiumFertility value to be added
        :return:
        None
        """
        self.fertilities |= fert_value

    def remove_fertility(self, fert_value: LatiumFertility):
        """
        Remove a fertility to this island
        :param fert_value:
        LatiumFertility value to be removed
        :return:
        None
        """
        self.fertilities &= ~fert_value

    def has_fertility(self, fert_value: LatiumFertility) -> bool:
        """
        Does this island have this fertility?
        :param fert_value: LatiumFertility to be checked
        :return:
        True | False
        """
        return self.fertilities & fert_value == fert_value

    def set_river_slots(self, slots: int):
        self.river_slots = slots

    def set_mountain_slots(self, slots: int):
        self.mountain_slots = slots

    def set_island_size(self, island_size: IslandSize):
        self.island_size = island_size

    def dump(self):
        """
        utility function to dump all class data to stdout
        :return:
        """
        print(f"{vars(self)}")



def main():


    print(IslandSize)
    print(f"{IslandSize._member_map_}")

    # print(LatiumFertility.NONE)
    print(LatiumFertility)
    print(f"{LatiumFertility._member_names_}")
    print(f"{LatiumFertility._member_map_}")
    print(f"{LatiumFertility.__members__}")

    name = 'sample island'
    li = LatiumIsland(name)
    li.add_fertility(LatiumFertility.MACKEREL)
    li.add_fertility(LatiumFertility.LAVENDAR | LatiumFertility.RESIN)
    print(f"name = [{li.island_name}]")
    print(f"Island has resin?   [{li.has_fertility(LatiumFertility.RESIN)}]")
    print(f"Island has gold?    [{li.has_fertility(LatiumFertility.GOLD_ORE)}]")
    print(f"Island score: [{li.island_name}], [{li.calculate_score()}]")
    # li.dump()

    li2 = LatiumIsland("island two", LatiumFertility.MACKEREL | LatiumFertility.OLIVE | LatiumFertility.MARBLE, 12, 8)
    print(f"Island score: [{li2.island_name}], [{li2.calculate_score()}]")
    # li2.dump()

    li_max = LatiumIsland('all fertilities')
    for fert in LatiumFertility:
        li_max.add_fertility(fert.value)
    li_max.set_river_slots(12)
    li_max.set_mountain_slots(8)
    li_max.set_island_size(IslandSize.EXTRALARGE)
    # li_max.dump()
    print(f"Island score: [{li_max.island_name}], [{li_max.calculate_score()}]")

    # set every flag
    fertility_coverage = LatiumFertility.NONE
    for fert in LatiumFertility:
        fertility_coverage |= fert

    print(fertility_coverage)

    # return self.fertilities & fert_value == fert_value
    # is Lavendar set?
    if fertility_coverage & LatiumFertility.LAVENDAR == LatiumFertility.LAVENDAR:
        print("Lavendar set")
    else:
        print("Lavendar clear")

    # clear lavendar
    fertility_coverage &= ~LatiumFertility.LAVENDAR
    print(fertility_coverage)

    # is Lavendar set?
    if fertility_coverage & LatiumFertility.LAVENDAR == LatiumFertility.LAVENDAR:
        print("Lavendar set")
    else:
        print("Lavendar clear")






if __name__ == '__main__':
    main()
