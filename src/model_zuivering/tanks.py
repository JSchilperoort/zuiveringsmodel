from . import water


class Tank(water.Water):
    def __init__(self, volume=0.0, NH4=0.0, NO3=0.0, bzv=0.0, O2=0.0):
        super().__init__(volume=volume, NH4=NH4, NO3=NO3, bzv=bzv, O2=O2)

        self.volume_tank = volume


class AnoxischeTank(Tank):
    def __init__(self, volume=1440, NH4=0.0, NO3=0.0, bzv=0.0, denitrificatiesnelheid=100000):
        super().__init__(volume=volume, NH4=NH4, NO3=NO3, bzv=bzv)

        self.denitrificatiesnelheid = denitrificatiesnelheid  # mg/s

        # 5.16  # 1 mol bzv = 12.01070 g 1 mol no3 = 62.0049g, 1 mol n = 14.00670g
        self.molverhouding_bzv_n = 0.86

    def step(self, water_influent, water_recirculatie, t=900):
        volume_influent, NH4_influent, NO3_influent, bzv_influent, _ = water_influent.get_absoluut()
        volume_recirculatie, NH4_recirculatie, NO3_recirculatie, bzv_recirculatie, _ = water_recirculatie.get_absoluut()

        volume_tank, NH4_tank, NO3_tank, bzv_tank, _ = self.get_absoluut()

        volume_tot = volume_influent + volume_recirculatie + volume_tank  # m3
        NH4_tot = NH4_influent + NH4_recirculatie + NH4_tank  # mg
        NO3_tot = NO3_influent + NO3_recirculatie + NO3_tank  # mg
        bzv_tot = bzv_influent + bzv_recirculatie + bzv_tank  # mg

        # denitrificatie
        # 2NO3 + 4H + bzv(2c) --> N2 + 2H2O + 2CO2
        NO3_verlies = min(self.denitrificatiesnelheid * t,
                          NO3_tot, bzv_tot/self.molverhouding_bzv_n)  # mg
        bzv_verlies = self.molverhouding_bzv_n * NO3_verlies  # mg

        NO3_tot = NO3_tot - NO3_verlies  # mg
        bzv_tot = bzv_tot - bzv_verlies  # mg

        volume_effluent = volume_tot - self.volume_tank   # m3
        NH4_effluent = (NH4_tot / (volume_tot * 1000))  # mg/l
        NO3_effluent = (NO3_tot / (volume_tot * 1000))  # mg/l
        bzv_effluent = (bzv_tot / (volume_tot * 1000))  # mg/l

        water_effluent = water.Water(
            volume=volume_effluent, NH4=NH4_effluent, NO3=NO3_effluent, bzv=bzv_effluent)

        self.update_NH4(NH4_tot / (volume_tot * 1000))  # mg/l
        self.update_NO3(NO3_tot / (volume_tot * 1000))  # mg/l
        self.update_bzv(bzv_tot / (volume_tot * 1000))  # mg/l

        return water_effluent, NO3_verlies


class Beluchtingstank(Tank):
    def __init__(self, volume=960, NH4=0.0, NO3=0.0, O2=0.0, bzv=0.0, nitrificatiesnelheid=5500, bzv_snelheid=100):
        super().__init__(volume=volume, NH4=NH4, NO3=NO3, O2=O2, bzv=bzv)
        self.nitrificatiesnelheid = nitrificatiesnelheid  # mg/s
        self.bzv_snelheid = bzv_snelheid  # self.nitrificatiesnelheid/10#/0.1  # mg/s

        self.o2_per_kwh = 2500000  # mg/kWh
        self.recirculatie_rendement = 800  # m3/kWh

        # 3.55 # 1 mol NH4 = 18.03846 g, 2 mol O2 = 63.99760 g, 1 mol N = 14.00670 g
        self.molverhouding_N_2O2 = 4.57
        self.molverhouding_bzv_O2 = 2.66  # 1 mol bzv = 12.01070 g 1 mol O2 = 31.99880 g
        # 3.44  # 1 mol NH4 = 18.03846 g, 1 mol no3 = 62.0049g, 1 mol N = 14.00670 g
        self.molverhouding_N_N = 1.00

    def step(self, water_influent, beluchting, recirculatie, t=900):
        volume_influent, NH4_influent, NO3_influent, bzv_influent, O2_influent = water_influent.get_absoluut()
        volume_tank, NH4_tank, NO3_tank, bzv_tank, O2_tank = self.get_absoluut()

        volume_tot = volume_influent + volume_tank  # m3
        NH4_tot = NH4_influent + NH4_tank  # mg
        NO3_tot = NO3_influent + NO3_tank  # mg
        bzv_tot = bzv_influent + bzv_tank  # mg
        O2_tot = O2_influent + O2_tank  # mg

        # beluchting
        O2_tot += (beluchting / 1000) * (t / 3600) * self.o2_per_kwh  # mg

        # nitrificatie
        # NH4 + 2O2 --> NO3 + H2O + 2H
        NH4_verlies = min(self.nitrificatiesnelheid * t,
                          NH4_tot, O2_tot/self.molverhouding_N_2O2)  # mg
        O2_verlies = self.molverhouding_N_2O2 * NH4_verlies  # mg
        NO3_winst = self.molverhouding_N_N * NH4_verlies  # mg

        NH4_tot = NH4_tot - NH4_verlies  # mg
        O2_tot = O2_tot - O2_verlies  # mg
        NO3_tot = NO3_tot + NO3_winst  # mg

        # bzv
        # CZV + O2 --> CO2
        bzv_verlies = min(self.bzv_snelheid * t, bzv_tot,
                          O2_tot/self.molverhouding_bzv_O2)  # mg
        O2_verlies = self.molverhouding_bzv_O2 * bzv_verlies  # mg

        bzv_tot = bzv_tot - bzv_verlies  # mg
        O2_tot = O2_tot - O2_verlies  # mg

        volume_recirculatie = min((recirculatie / 1000) * (t / 3600) *
                                  self.recirculatie_rendement, volume_tot - self.volume_tank)  # m3

        NH4_recirculatie = (NH4_tot / (volume_tot * 1000))  # mg/l
        NO3_recirculatie = (NO3_tot / (volume_tot * 1000))  # mg/l
        bzv_recirculatie = (bzv_tot / (volume_tot * 1000))  # mg/l

        water_recirculatie = water.Water(
            volume=volume_recirculatie, NH4=NH4_recirculatie, NO3=NO3_recirculatie, bzv=bzv_recirculatie)

        volume_effluent = max(
            volume_tot - volume_recirculatie - self.volume_tank, 0)   # m3
        NH4_effluent = (NH4_tot / (volume_tot * 1000))  # mg/l
        NO3_effluent = (NO3_tot / (volume_tot * 1000))  # mg/l
        bzv_effluent = (bzv_tot / (volume_tot * 1000))  # mg/l

        water_effluent = water.Water(
            volume=volume_effluent, NH4=NH4_effluent, NO3=NO3_effluent, bzv=bzv_effluent)

        self.update_NH4(NH4_tot / (volume_tot * 1000))  # mg/l
        self.update_NO3(NO3_tot / (volume_tot * 1000))  # mg/l
        self.update_bzv(bzv_tot / (volume_tot * 1000))  # mg/l
        self.update_O2(O2_tot / (volume_tot * 1000))  # mg/l

        return water_recirculatie, water_effluent, NH4_verlies
