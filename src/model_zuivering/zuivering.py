from . import water, tanks


class Zuivering:
    def __init__(self):
        self.anoxische_tank = tanks.AnoxischeTank(volume=1440)
        self.beluchtingstank = tanks.Beluchtingstank(volume=960)
        self.recirculatie = water.Water()
        self.effluent = water.Water()

        self.max_vermogen_beluchting = 40000  # W
        self.max_vermogen_recirculatie = 5500  # W

    def step(self, influent_volume, influent_NH4, beluchting_W, recirculatie_W):
        if beluchting_W > self.max_vermogen_beluchting or recirculatie_W > self.max_vermogen_recirculatie:
            raise ValueError(
                "Maximaal vermogen beluchting is {:.0f}W, maximaal vermogen recirculatie is {:.0f}W, respectievelijk {:.0f}W en {:.0f}W ontvangen."
                .format(self.max_vermogen_beluchting, self.max_vermogen_recirculatie, beluchting_W, recirculatie_W))
        if beluchting_W < 0 or recirculatie_W < 0:
            raise ValueError(
                "Vermogen kan niet negatief zijn, respectievelijk {:.0f}W en {:.0f}W ontvangen."
                .format(beluchting_W, recirculatie_W))

        influent = water.Influent(volume=influent_volume, NH4=influent_NH4)
        beluchtingstank_stroom, _ = self.anoxische_tank.step(
            influent, self.recirculatie)
        self.recirculatie, self.effluent, _ = self.beluchtingstank.step(
            beluchtingstank_stroom, beluchting_W, recirculatie_W)
        return self.effluent.NH4 + self.effluent.NO3
