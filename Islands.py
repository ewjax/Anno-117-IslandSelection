from enum import IntFlag, IntEnum, auto


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
    NONE = 0
    MACKEREL = auto()
    LAVENDAR = auto()
    RESIN = auto()
    OLIVE = auto()
    GRAPES = auto()
    FLAX = auto(),
    MUREX_SNAILS = auto()
    SANDARAC = auto()
    OYSTER = auto()
    STURGEON = auto()
    MARBLE = auto()
    IRON = auto()
    MINERAL = auto()
    GOLD_ORE = auto()

    @staticmethod
    def no_fertilities():
        return LatiumFertility.NONE

    @staticmethod
    def all_fertilities():
        rv = 0
        for f in LatiumFertility:
            rv |= f.value
        return rv





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

    # Returns an instance of LatiumIsland
    @classmethod
    def from_string(cls, island_string):
        """
        provides functionality similar to C++ overloaded ctor
        allows contruction of a LatiumIsland from a string value taken from a .csv island file

        #Name,Mackerel,Lavender,Resin,Olive,Grapes,Flax,Murex Snail,Sandarac,Oyster,Sturgeon,Marble,Iron,Mineral,Gold Ore,Mountains,Rivers,Size
            0       Name
            1-14    Fertilities, boolean [''|'1']
            15      number mountain slots
            16      number river slots
            17      Island size, ['XL'|'L'|'M'|'S']
        """
        fields = island_string.strip().split(',')
        # print(fields)
        island_name = fields[0]

        fertilities = LatiumFertility.NONE
        for ndx, fert_value in enumerate(LatiumFertility):
            if fields[ndx+1] != '':
                fertilities |= fert_value

        mountains = int(fields[15])
        rivers = int(fields[16])

        if fields[17] == 'XL':
            size = IslandSize.EXTRALARGE
        elif fields[17] == 'L':
            size = IslandSize.LARGE
        elif fields[17] == 'M':
            size = IslandSize.MEDIUM
        else:
            size = IslandSize.SMALL

        # finally construct the LatiumIsland object
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
        self.fertility_weight[LatiumFertility.MACKEREL] = 70
        self.fertility_weight[LatiumFertility.LAVENDAR] = 70

        # tier3 chains - amphorae, olives
        self.fertility_weight[LatiumFertility.RESIN] = 50
        self.fertility_weight[LatiumFertility.OLIVE] = 50

        # tier4 chains - wine, togas, loungers, writing tablets, lyres, oysters w caviar, necklaces
        self.fertility_weight[LatiumFertility.GRAPES] = 30           # wine
        self.fertility_weight[LatiumFertility.FLAX] = 60             # togas, loungers
        self.fertility_weight[LatiumFertility.MUREX_SNAILS] = 30     # togas, loungers
        self.fertility_weight[LatiumFertility.SANDARAC] = 90         # writing tablets, loungers, lyres
        self.fertility_weight[LatiumFertility.OYSTER] = 30           # oysters with caviar
        self.fertility_weight[LatiumFertility.STURGEON] = 30         # oysters with caviar

        # construction material for tier3 and tier4 buildings
        # tier3 buildings - forum, baths
        # tier4 buildings - temple, libarary, amphitheatre
        # (3 + 3 + 1 + 1 + 1)/2
        self.fertility_weight[LatiumFertility.MARBLE] = 45

        # construction material for tier2 weapons and armor
        # (5 + 5)/2
        self.fertility_weight[LatiumFertility.IRON] = 50

        # tier4 production chains - fine glass, necklaces
        # tier4 mosaics used in buildings temple, library, amphitheatre
        # (1 + 1 + (1+1+1)/2)
        self.fertility_weight[LatiumFertility.MINERAL] = 35

        # tier4 - necklaces, lyres
        self.fertility_weight[LatiumFertility.GOLD_ORE] = 20

        # island size
        self.island_size_weight[IslandSize.EXTRALARGE] = 100
        self.island_size_weight[IslandSize.LARGE] = 50
        self.island_size_weight[IslandSize.MEDIUM] = 20
        self.island_size_weight[IslandSize.SMALL] = 10


    def calculate_score(self, include_fertilities: LatiumFertility) -> float:
        """
        determine score based purely on this island's fertilities
        and the associated weighting values for each fertility
        :return:
        score
        """
        rv = 0.0

        # start with basic fertilities
        # note we only count basic fertilities which have NOT been counted already on a previous island
        f: LatiumFertility
        for f in LatiumFertility:
            if self.has_fertility(f) and include_fertilities & f == f:
                rv += self.fertility_weight[f.value]

        # river slots. increase weighting if there is also a Sturgeon or Gold fertility
        # count these even if they've already been counted already on a previous island
        rv += self.river_slots
        if self.has_fertility(LatiumFertility.STURGEON):
            rv += 0.5 * self.river_slots
        if self.has_fertility(LatiumFertility.GOLD_ORE):
            rv += 0.5 * self.river_slots

        # mountain slots. increase weighting if there is also a Mineral fertility
        # count these even if they've already been counted already on a previous island
        rv += self.mountain_slots
        if self.has_fertility(LatiumFertility.MINERAL):
            rv += 0.5 * self.mountain_slots

        # island size
        rv += self.island_size_weight[self.island_size]

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
    print("---------------------------------------------")

    name = 'sample island'
    li = LatiumIsland(name)
    li.add_fertility(LatiumFertility.MACKEREL)
    li.add_fertility(LatiumFertility.LAVENDAR | LatiumFertility.RESIN)
    print(f"Name:               [{li.island_name}]")
    print(f"Score:              [{li.calculate_score(LatiumFertility.all_fertilities())}]")
    print(f"Score (none):       [{li.calculate_score(LatiumFertility.no_fertilities())}]")
    # li.dump()
    print(f"Island has resin?   [{li.has_fertility(LatiumFertility.RESIN)}]")
    print(f"Island has gold?    [{li.has_fertility(LatiumFertility.GOLD_ORE)}]")
    print("---------------------------------------------")

    li2 = LatiumIsland("island two", LatiumFertility.MACKEREL | LatiumFertility.OLIVE | LatiumFertility.MARBLE, 12, 8)
    print(f"Name:               [{li2.island_name}]")
    print(f"Score:              [{li2.calculate_score(LatiumFertility.all_fertilities())}]")
    print(f"Score (none):       [{li2.calculate_score(LatiumFertility.no_fertilities())}]")
    # li2.dump()
    print("---------------------------------------------")

    li_max = LatiumIsland('all fertilities', LatiumFertility.all_fertilities())
    li_max.set_river_slots(12)
    li_max.set_mountain_slots(8)
    li_max.set_island_size(IslandSize.EXTRALARGE)
    print(f"Name:               [{li_max.island_name}]")
    print(f"Score:              [{li_max.calculate_score(LatiumFertility.all_fertilities())}]")
    print(f"Score (none):       [{li_max.calculate_score(LatiumFertility.no_fertilities())}]")
    # li_max.dump()
    print("---------------------------------------------")

    # set every flag
    f = LatiumFertility.all_fertilities()
    print(f"All fertilities:                    [{f}]")
    print(f"Lavendar:                           [{LatiumFertility.LAVENDAR}]")

    # is Lavendar set?
    print(f"Lavendar set: {f & LatiumFertility.LAVENDAR == LatiumFertility.LAVENDAR}")

    # clear lavendar
    f &= ~LatiumFertility.LAVENDAR
    print(f"All fertilities minus lavendar:     [{f}]")

    # is Lavendar set?
    print(f"Lavendar set: {f & LatiumFertility.LAVENDAR == LatiumFertility.LAVENDAR}")







if __name__ == '__main__':
    main()
