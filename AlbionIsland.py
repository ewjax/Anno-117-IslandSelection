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
class AlbionFertility(IntFlag):
    """
    bitmapped enum for Albion island fertilities
    """
    NONE = 0
    BARLEY = auto()
    HERBS = auto()
    DYE_PLANT = auto()
    RESIN = auto()
    SALTWORT = auto()
    SMALL_BIRDS = auto()
    FLAX = auto()
    BEAVER = auto()
    PONY = auto()
    SEA_SHELL = auto()
    IRON = auto()
    COPPER = auto()
    SILVER = auto()
    TIN = auto()
    GRANITE = auto()

    @staticmethod
    def no_fertilities():
        return AlbionFertility.NONE

    @staticmethod
    def all_fertilities():
        rv = AlbionFertility.NONE
        for f in AlbionFertility:
            rv |= f.value
        return rv

    # define which fertilities are Celtic and which are Roman
    @staticmethod
    def celtic():
        rv = (
            AlbionFertility.BARLEY |
            AlbionFertility.DYE_PLANT |
            AlbionFertility.COPPER |
            AlbionFertility.TIN |
            AlbionFertility.SALTWORT |
            AlbionFertility.BEAVER |
            AlbionFertility.PONY |
            AlbionFertility.IRON |
            AlbionFertility.GRANITE
        )
        return rv

    # define which fertilities are Celtic and which are Roman
    @staticmethod
    def roman():
        rv = (
            AlbionFertility.HERBS |
            AlbionFertility.SILVER |
            AlbionFertility.RESIN |
            AlbionFertility.SMALL_BIRDS |
            AlbionFertility.FLAX |
            AlbionFertility.SEA_SHELL |
            AlbionFertility.IRON
        )
        return rv

    def dump(self):
        print(f"Name:   [{self.name}]")
        print(f"Value:  [{self.value}]")

    def add(self, bits: int) -> Self:
        return AlbionFertility(self.value | bits)

    def remove(self, bits: int) -> Self:
        return AlbionFertility(self.value & ~bits)

    def has(self, bits: int) -> bool:
        return self.value & bits == bits




###########################################################################################
#
#
class AlbionIsland:

    def __init__(self,
                 island_name: str,
                 fert_values: AlbionFertility = AlbionFertility.NONE,
                 marsh_slots: int = 0,
                 mountain_slots: int = 0,
                 island_size: IslandSize = IslandSize.LARGE
                 ):
        self.island_name = island_name
        self.fertilities: AlbionFertility = fert_values
        self.marsh_slots = marsh_slots
        self.mountain_slots = mountain_slots
        self.island_size = island_size

        # dictionary of fertility types and their weights
        self.fertility_weight = {}
        self.island_size_weight = {}

        # mountain and marsh weights
        self.mountain_weight = 0
        self.marsh_weight = 0

        # which fertilities match up to different albion population types
        # self.albion_celtic_fertilities = AlbionFertility.NONE
        # self.albion_roman_fertilities = AlbionFertility.NONE

        # call function to set all tuning values
        self.define_weights()



    # Returns an instance of AlbionIsland
    @classmethod
    def from_string(cls, island_string):
        """
        provides functionality similar to C++ overloaded ctor
        allows contruction of a AlbionIsland from a string value taken from a .csv island file

        #Name,Barley,Herbs,Dye Plant,Resin,Saltwort,Small Birds,Flax,Beaver,Pony,Sea Shell,Iron,Copper,Silver,Tin,Granite,Mountains,Marshes,Size
            0       Name
            1-15    Fertilities, boolean [''|'1']
            16      number mountain slots
            17      number marsh slots
            18      Island size, ['XL'|'L'|'M'|'S']
        """
        fields = island_string.strip().split(',')
        # print(fields)
        island_name = fields[0]

        fertilities = AlbionFertility.NONE
        for ndx, fert_value in enumerate(AlbionFertility):
            if fields[ndx+1] != '':
                fertilities |= fert_value

        mountains = int(fields[16])
        marshes = int(fields[17])

        if fields[18] == 'XL':
            size = IslandSize.EXTRALARGE
        elif fields[18] == 'L':
            size = IslandSize.LARGE
        elif fields[18] == 'M':
            size = IslandSize.MEDIUM
        else:
            size = IslandSize.SMALL

        # finally construct the AlbionIsland object
        return cls(island_name, fertilities, marshes, mountains, size)

    def define_weights(self):
        """
        Weighting Scheme
        Tier2 - 70 points per production chain
        Tier3 - 50 points per production chain
        Construction material - use tier scores, but divide by 2
        River slots - 5 point per slot, adjusted by gold ore and/or sturgeon presence
        Mountain slots - 5 point per slot, adjusted by mineral score?
        """

        # initialize all weights to 0, so we can use the += notation later
        f: AlbionFertility
        for f in AlbionFertility:
            self.fertility_weight[f] = 0

        # tier2 chains (celt) - beer, trousers, torcs, horns, shields
        self.fertility_weight[AlbionFertility.BARLEY] += 70         # beer
        self.fertility_weight[AlbionFertility.DYE_PLANT] += 140     # trousers, shields
        self.fertility_weight[AlbionFertility.COPPER] += 140        # torcs, shields
        self.fertility_weight[AlbionFertility.TIN] += 140           # horns, shields

        # tier2 chains (roman) - sausage, brooches, amphorae
        self.fertility_weight[AlbionFertility.HERBS] += 70          # sausage
        self.fertility_weight[AlbionFertility.SILVER] += 70         # brooches
        self.fertility_weight[AlbionFertility.RESIN] += 70          # amphorae

        # tier3 chains (celt) - beef, cloak, pelt hats, chariots
        self.fertility_weight[AlbionFertility.SALTWORT] += 100      # beef, pelt hats
        self.fertility_weight[AlbionFertility.DYE_PLANT] += 50      # cloak
        self.fertility_weight[AlbionFertility.COPPER] += 50         # cloak
        self.fertility_weight[AlbionFertility.BEAVER] += 50         # pelt hats
        self.fertility_weight[AlbionFertility.PONY] += 50           # chariots

        # tier3 chains (roman) - aspic, wigs, mirrors
        self.fertility_weight[AlbionFertility.SMALL_BIRDS] += 50    # aspic
        self.fertility_weight[AlbionFertility.FLAX] += 50           # wigs
        self.fertility_weight[AlbionFertility.RESIN] += 50          # wigs
        self.fertility_weight[AlbionFertility.SILVER] += 50         # mirrors
        self.fertility_weight[AlbionFertility.SEA_SHELL] += 50      # mirrors

        # construction material for tier2 weapons and armor
        # (70 + 70)/2
        self.fertility_weight[AlbionFertility.IRON] = 70

        # construction material for celtic tier3 buildings
        # tier3 buildings - alder council, barrow, sacred grove
        # (50 + 50 + 50)/2
        self.fertility_weight[AlbionFertility.GRANITE] += 75

        # mountain slot weight
        self.mountain_weight = 5

        # marsh slot weight
        self.marsh_weight = 5

        # island size
        self.island_size_weight[IslandSize.EXTRALARGE] = 400
        self.island_size_weight[IslandSize.LARGE] = 200
        self.island_size_weight[IslandSize.MEDIUM] = 100
        self.island_size_weight[IslandSize.SMALL] = 10

    def calculate_score(self, include_fertilities: AlbionFertility) -> float:
        """
        determine score based purely on this island's fertilities
        and the associated weighting values for each fertility
        :return:
        score
        """
        rv = 0.0

        # start with basic fertilities
        # note we only count basic fertilities which have NOT been counted already on a previous island
        f: AlbionFertility
        for f in AlbionFertility:
            if self.has_fertility(f) and include_fertilities.has(f):
                rv += self.fertility_weight[f.value]

        # marsh slots.
        rv += self.marsh_weight * self.marsh_slots

        # mountain slots.
        rv += self.mountain_weight * self.mountain_slots

        # island size
        rv += self.island_size_weight[self.island_size]

        # todo - need some way to assess total travel distance.  Get (x,y) info from savegame?

        return rv

    def add_fertility(self, fert_value: AlbionFertility):
        """
        Add a fertility to this island
        :param fert_value:
        AlbionFertility value to be added
        :return:
        None
        """
        self.fertilities |= fert_value

    def remove_fertility(self, fert_value: AlbionFertility):
        """
        Remove a fertility to this island
        :param fert_value:
        AlbionFertility value to be removed
        :return:
        None
        """
        self.fertilities &= ~fert_value

    def has_fertility(self, fert_value: AlbionFertility) -> bool:
        """
        Does this island have this fertility?
        :param fert_value: AlbionFertility to be checked
        :return:
        True | False
        """
        return self.fertilities & fert_value == fert_value

    def set_marsh_slots(self, slots: int):
        self.marsh_slots = slots

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

    #
    # albion testing
    #


    # print(AlbionFertility.NONE)
    print(AlbionFertility)
    print(f"{AlbionFertility._member_names_}")
    print(f"{AlbionFertility._member_map_}")
    print(f"{AlbionFertility.__members__}")
    print("---------------------------------------------")

    name = 'sample albion island'
    alb_island = AlbionIsland(name)
    alb_island.add_fertility(AlbionFertility.BARLEY)
    alb_island.add_fertility(AlbionFertility.SALTWORT | AlbionFertility.COPPER)
    print(f"Name:                   [{alb_island.island_name}]")
    print(f"Score:                  [{alb_island.calculate_score(AlbionFertility.all_fertilities())}]")
    print(f"Score (none):           [{alb_island.calculate_score(AlbionFertility.no_fertilities())}]")
    print(f"Island has saltwort?    [{alb_island.has_fertility(AlbionFertility.SALTWORT)}]")
    print(f"Island has silver?      [{alb_island.has_fertility(AlbionFertility.SILVER)}]")
    print("---------------------------------------------")

    alb_island2 = AlbionIsland("island two", AlbionFertility.BARLEY | AlbionFertility.SALTWORT | AlbionFertility.HERBS, 12, 8)
    print(f"Name:               [{alb_island2.island_name}]")
    print(f"Score:              [{alb_island2.calculate_score(AlbionFertility.all_fertilities())}]")
    print(f"Score (none):       [{alb_island2.calculate_score(AlbionFertility.no_fertilities())}]")
    # li2.dump()
    print("---------------------------------------------")

    alb_island_max = AlbionIsland('all fertilities', AlbionFertility.all_fertilities())
    alb_island_max.set_marsh_slots(7)
    alb_island_max.set_mountain_slots(8)
    alb_island_max.set_island_size(IslandSize.EXTRALARGE)
    print(f"Name:               [{alb_island_max.island_name}]")
    print(f"Score:              [{alb_island_max.calculate_score(AlbionFertility.all_fertilities())}]")
    print(f"Score (none):       [{alb_island_max.calculate_score(AlbionFertility.no_fertilities())}]")
    # li_max.dump()
    print("---------------------------------------------")

    # set every flag
    f = AlbionFertility.all_fertilities()
    print(f"All fertilities:                    [{f}]")
    print("---------------------------------------------")

    # playing with bits
    f = AlbionFertility.SEA_SHELL|AlbionFertility.SILVER
    f.dump()
    print(f"Island has seashells?   [{f.has(AlbionFertility.SEA_SHELL)}]")

    f = f.remove(AlbionFertility.SEA_SHELL)
    f.dump()

    f = f.add(AlbionFertility.BEAVER)
    f.dump()

    print(f"Island has silver?      [{f.has(AlbionFertility.SILVER)}]")
    print(f"Island has granite?     [{f.has(AlbionFertility.GRANITE)}]")
    print(f"Island has seashells?   [{f.has(AlbionFertility.SEA_SHELL)}]")



if __name__ == '__main__':
    main()
