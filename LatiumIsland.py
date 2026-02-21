from enum import IntFlag, IntEnum, auto
from typing import Self

###########################################################################################
#
#
class IslandSize(IntEnum):
    """
    enum for island sizes
    """
    EXTRALARGE = auto()
    LARGE = auto()
    MEDIUM = auto()
    SMALL = auto()


###########################################################################################
#
#
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
    FLAX = auto()
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
        rv = LatiumFertility.NONE
        for f in LatiumFertility:
            rv |= f.value
        return rv

    def dump(self):
        print(f"Name:   [{self.name}]")
        print(f"Value:  [{self.value}]")

    def add(self, bits: int) -> Self:
        return LatiumFertility(self.value | bits)

    def remove(self, bits: int) -> Self:
        return LatiumFertility(self.value & ~bits)

    def has(self, bits: int) -> bool:
        return self.value & bits == bits


###########################################################################################
#
#
class LatiumIsland:

    def __init__(self,
                 island_name: str,
                 fert_values: LatiumFertility = LatiumFertility.NONE,
                 river_slots: int = 0,
                 mountain_slots: int = 0,
                 island_size: IslandSize = IslandSize.LARGE
                 ):
        self.island_name = island_name
        self.fertilities: LatiumFertility = fert_values
        self.river_slots = river_slots
        self.mountain_slots = mountain_slots
        self.island_size = island_size

        # dictionary of fertility types and their weights
        self.fertility_weight = {}
        self.island_size_weight = {}

        # mountain and river slot weights
        self.mountain_weight = 0
        self.river_weight = 0

        # call function to set all tuning values
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
        Tier2 - 70 points per production chain
        Tier3 - 50 points per production chain
        Tier4 - 30 points per production chain
        Construction material - use tier scores, but divide by 2
        River slots - 5 point per slot, adjusted by gold ore and/or sturgeon presence
        Mountain slots - 5 point per slot, adjusted by mineral score?
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
        # (50 + 50 + 30 + 30 + 30)/2
        self.fertility_weight[LatiumFertility.MARBLE] = 80

        # construction material for tier2 weapons and armor
        # (50 + 50)/2
        self.fertility_weight[LatiumFertility.IRON] = 50

        # tier4 production chains - fine glass, necklaces
        # tier4 mosaics used in buildings temple, library, amphitheatre
        # (30 + 30 + (30+30+30)/2)
        self.fertility_weight[LatiumFertility.MINERAL] = 105

        # tier4 - necklaces, lyres
        self.fertility_weight[LatiumFertility.GOLD_ORE] = 60

        # mountain slot weight
        self.mountain_weight = 5

        # river slot weight
        self.river_weight = 5

        # island size
        self.island_size_weight[IslandSize.EXTRALARGE] = 300
        self.island_size_weight[IslandSize.LARGE] = 150
        self.island_size_weight[IslandSize.MEDIUM] = 75
        self.island_size_weight[IslandSize.SMALL] = 30


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
            if self.has_fertility(f) and include_fertilities.has(f):

                # sturgeon: base weighting assumes 10 river slots, adjust up or down if not 10
                if f == LatiumFertility.STURGEON:
                    rv += self.fertility_weight[f.value] * self.river_slots / 10.0

                # gold: base weighting assumes 10 river slots, adjust up or down if not 10
                elif f == LatiumFertility.GOLD_ORE:
                    rv += self.fertility_weight[f.value] * self.river_slots / 10.0

                # mineral: base weighting assumes 10 mountainn slots, adjust up or down if not 10
                elif f == LatiumFertility.MINERAL:
                    rv += self.fertility_weight[f.value] * self.mountain_slots / 10.0

                # all other fertilities
                else:
                    rv += self.fertility_weight[f.value]

        # river slots.
        rv += self.river_weight * self.river_slots

        # mountain slots.
        rv += self.mountain_weight * self.mountain_slots

        # island size
        rv += self.island_size_weight[self.island_size]

        # todo - need some way to assess total travel distance.  Get (x,y) info from savegame?

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
    lat_island = LatiumIsland(name)
    lat_island.add_fertility(LatiumFertility.MACKEREL)
    lat_island.add_fertility(LatiumFertility.SANDARAC | LatiumFertility.RESIN)
    print(f"Name:               [{lat_island.island_name}]")
    print(f"Score:              [{lat_island.calculate_score(LatiumFertility.all_fertilities())}]")
    print(f"Score (none):       [{lat_island.calculate_score(LatiumFertility.no_fertilities())}]")
    print(f"Island has resin?   [{lat_island.has_fertility(LatiumFertility.RESIN)}]")
    print(f"Island has gold?    [{lat_island.has_fertility(LatiumFertility.GOLD_ORE)}]")
    print("---------------------------------------------")

    lat_island2 = LatiumIsland("island two", LatiumFertility.MACKEREL | LatiumFertility.OLIVE | LatiumFertility.MARBLE, 12, 8)
    print(f"Name:               [{lat_island2.island_name}]")
    print(f"Score:              [{lat_island2.calculate_score(LatiumFertility.all_fertilities())}]")
    print(f"Score (none):       [{lat_island2.calculate_score(LatiumFertility.no_fertilities())}]")
    print("---------------------------------------------")

    lat_island_max = LatiumIsland('all fertilities', LatiumFertility.all_fertilities())
    lat_island_max.set_river_slots(12)
    lat_island_max.set_mountain_slots(8)
    lat_island_max.set_island_size(IslandSize.EXTRALARGE)
    print(f"Name:               [{lat_island_max.island_name}]")
    print(f"Score:              [{lat_island_max.calculate_score(LatiumFertility.all_fertilities())}]")
    print(f"Score (none):       [{lat_island_max.calculate_score(LatiumFertility.no_fertilities())}]")
    # li_max.dump()
    print("---------------------------------------------")

    # set every flag
    f = LatiumFertility.all_fertilities()
    # f.set()

    print(f"All fertilities:                    [{f}]")
    print(f"Lavendar:                           [{LatiumFertility.LAVENDAR}]")

    # is Lavendar set?
    print(f"Lavendar set: {f & LatiumFertility.LAVENDAR == LatiumFertility.LAVENDAR}")

    # clear lavendar
    f &= ~LatiumFertility.LAVENDAR
    print(f"All fertilities minus lavendar:     [{f}]")

    # is Lavendar set?
    print(f"Lavendar set: {f & LatiumFertility.LAVENDAR == LatiumFertility.LAVENDAR}")

    print("---------------------------------------------")
    # playing with bits
    f = LatiumFertility.OLIVE|LatiumFertility.GOLD_ORE
    f.dump()

    f = f.remove(LatiumFertility.OLIVE)
    f.dump()

    f = f.add(LatiumFertility.MACKEREL)
    f.dump()

    print(f"Island has resin?   [{f.has(LatiumFertility.RESIN)}]")
    print(f"Island has gold?    [{f.has(LatiumFertility.GOLD_ORE)}]")
    print(f"Island has olives?  [{f.has(LatiumFertility.OLIVE)}]")







if __name__ == '__main__':
    main()
