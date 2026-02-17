from enum import IntFlag, IntEnum, auto

#
###########################################################################################
#

class IslandSize(IntEnum):
    """
    enum for island sizes
    """
    EXTRALARGE = auto()
    LARGE = auto()
    MEDIUM = auto()
    SMALL = auto()


#
###########################################################################################
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

#
###########################################################################################
#
class AlbionFertility(IntFlag):
    """
    bitmapped enum for latium island fertilities
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


#
###########################################################################################
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
        self.island_size_weight[IslandSize.EXTRALARGE] = 150
        self.island_size_weight[IslandSize.LARGE] = 80
        self.island_size_weight[IslandSize.MEDIUM] = 40
        self.island_size_weight[IslandSize.SMALL] = 20


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
        rv += self.river_weight * self.river_slots
        # if self.has_fertility(LatiumFertility.STURGEON):
        #     rv += 0.5 * self.river_weight * self.river_slots
        # if self.has_fertility(LatiumFertility.GOLD_ORE):
        #     rv += 0.5 * self.river_weight * self.river_slots

        # mountain slots. increase weighting if there is also a Mineral fertility
        # count these even if they've already been counted already on a previous island
        rv += self.mountain_weight * self.mountain_slots
        # if self.has_fertility(LatiumFertility.MINERAL):
        #     rv += 0.5 * self.mountain_weight * self.mountain_slots

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






#
###########################################################################################
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

        # finally construct the LatiumIsland object
        return cls(island_name, fertilities, marshes, mountains, size)

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

        # initialize all weights, so we can use the += notation later
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
        # (50 + 50)/2
        self.fertility_weight[AlbionFertility.IRON] = 50

        # construction material for celtic tier3 buildings
        # tier3 buildings - alder council, barrow, sacred grove
        # (50 + 50 + 50)/2
        self.fertility_weight[AlbionFertility.GRANITE] += 75

        # mountain slot weight
        self.mountain_weight = 5

        # marsh slot weight
        self.marsh_weight = 5

        # island size
        self.island_size_weight[IslandSize.EXTRALARGE] = 150
        self.island_size_weight[IslandSize.LARGE] = 80
        self.island_size_weight[IslandSize.MEDIUM] = 40
        self.island_size_weight[IslandSize.SMALL] = 20




    # todo - fix
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
        f: LatiumFertility
        for f in LatiumFertility:
            if self.has_fertility(f) and include_fertilities & f == f:
                rv += self.fertility_weight[f.value]

        # river slots. increase weighting if there is also a Sturgeon or Gold fertility
        # count these even if they've already been counted already on a previous island
        rv += self.river_weight * self.river_slots
        # if self.has_fertility(LatiumFertility.STURGEON):
        #     rv += 0.5 * self.river_weight * self.river_slots
        # if self.has_fertility(LatiumFertility.GOLD_ORE):
        #     rv += 0.5 * self.river_weight * self.river_slots

        # mountain slots. increase weighting if there is also a Mineral fertility
        # count these even if they've already been counted already on a previous island
        rv += self.mountain_weight * self.mountain_slots
        # if self.has_fertility(LatiumFertility.MINERAL):
        #     rv += 0.5 * self.mountain_weight * self.mountain_slots

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

    # # print(LatiumFertility.NONE)
    # print(LatiumFertility)
    # print(f"{LatiumFertility._member_names_}")
    # print(f"{LatiumFertility._member_map_}")
    # print(f"{LatiumFertility.__members__}")
    # print("---------------------------------------------")
    #
    name = 'sample island'
    li = LatiumIsland(name)
    li.add_fertility(LatiumFertility.MACKEREL)
    li.add_fertility(LatiumFertility.SANDARAC | LatiumFertility.RESIN)
    print(f"Name:               [{li.island_name}]")
    print(f"Score:              [{li.calculate_score(LatiumFertility.all_fertilities())}]")
    print(f"Score (none):       [{li.calculate_score(LatiumFertility.no_fertilities())}]")
    # li.dump()
    print(f"Island has resin?   [{li.has_fertility(LatiumFertility.RESIN)}]")
    print(f"Island has gold?    [{li.has_fertility(LatiumFertility.GOLD_ORE)}]")
    print("---------------------------------------------")
    #
    # li2 = LatiumIsland("island two", LatiumFertility.MACKEREL | LatiumFertility.OLIVE | LatiumFertility.MARBLE, 12, 8)
    # print(f"Name:               [{li2.island_name}]")
    # print(f"Score:              [{li2.calculate_score(LatiumFertility.all_fertilities())}]")
    # print(f"Score (none):       [{li2.calculate_score(LatiumFertility.no_fertilities())}]")
    # # li2.dump()
    # print("---------------------------------------------")
    #
    # li_max = LatiumIsland('all fertilities', LatiumFertility.all_fertilities())
    # li_max.set_river_slots(12)
    # li_max.set_mountain_slots(8)
    # li_max.set_island_size(IslandSize.EXTRALARGE)
    # print(f"Name:               [{li_max.island_name}]")
    # print(f"Score:              [{li_max.calculate_score(LatiumFertility.all_fertilities())}]")
    # print(f"Score (none):       [{li_max.calculate_score(LatiumFertility.no_fertilities())}]")
    # # li_max.dump()
    # print("---------------------------------------------")
    #
    # # set every flag
    # f = LatiumFertility.all_fertilities()
    # print(f"All fertilities:                    [{f}]")
    # print(f"Lavendar:                           [{LatiumFertility.LAVENDAR}]")
    #
    # # is Lavendar set?
    # print(f"Lavendar set: {f & LatiumFertility.LAVENDAR == LatiumFertility.LAVENDAR}")
    #
    # # clear lavendar
    # f &= ~LatiumFertility.LAVENDAR
    # print(f"All fertilities minus lavendar:     [{f}]")
    #
    # # is Lavendar set?
    # print(f"Lavendar set: {f & LatiumFertility.LAVENDAR == LatiumFertility.LAVENDAR}")
    #



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
    # print(f"Score:              [{alb_island.calculate_score(AlbionFertility.all_fertilities())}]")
    # print(f"Score (none):       [{alb_island.calculate_score(AlbionFertility.no_fertilities())}]")
    # li.dump()
    print(f"Island has saltwort?    [{alb_island.has_fertility(AlbionFertility.SALTWORT)}]")
    print(f"Island has silver?      [{alb_island.has_fertility(AlbionFertility.SILVER)}]")
    print("---------------------------------------------")

    # li2 = LatiumIsland("island two", LatiumFertility.MACKEREL | LatiumFertility.OLIVE | LatiumFertility.MARBLE, 12, 8)
    # print(f"Name:               [{li2.island_name}]")
    # print(f"Score:              [{li2.calculate_score(LatiumFertility.all_fertilities())}]")
    # print(f"Score (none):       [{li2.calculate_score(LatiumFertility.no_fertilities())}]")
    # # li2.dump()
    # print("---------------------------------------------")
    #
    # li_max = LatiumIsland('all fertilities', LatiumFertility.all_fertilities())
    # li_max.set_river_slots(12)
    # li_max.set_mountain_slots(8)
    # li_max.set_island_size(IslandSize.EXTRALARGE)
    # print(f"Name:               [{li_max.island_name}]")
    # print(f"Score:              [{li_max.calculate_score(LatiumFertility.all_fertilities())}]")
    # print(f"Score (none):       [{li_max.calculate_score(LatiumFertility.no_fertilities())}]")
    # # li_max.dump()
    # print("---------------------------------------------")
    #
    # # set every flag
    # f = LatiumFertility.all_fertilities()
    # print(f"All fertilities:                    [{f}]")
    # print(f"Lavendar:                           [{LatiumFertility.LAVENDAR}]")
    #
    # # is Lavendar set?
    # print(f"Lavendar set: {f & LatiumFertility.LAVENDAR == LatiumFertility.LAVENDAR}")
    #
    # # clear lavendar
    # f &= ~LatiumFertility.LAVENDAR
    # print(f"All fertilities minus lavendar:     [{f}]")
    #
    # # is Lavendar set?
    # print(f"Lavendar set: {f & LatiumFertility.LAVENDAR == LatiumFertility.LAVENDAR}")
    #



if __name__ == '__main__':
    main()
