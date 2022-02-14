# from model_zuivering.tanks import AnoxischeTank, Beluchtingstank
# from model_zuivering.water import Influent, Water
import pandas as pd
from tqdm import tqdm
from model_zuivering import water, tanks


def main():
    recirculatie_w_range = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200, 250, 300, 400, 500, 600, 700, 800,
                            900, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000, 3250, 3500, 3750, 4000, 4250, 4500, 4750, 5000]
    print(len(recirculatie_w_range))

    df = pd.DataFrame(columns=('influent_nh4', 'influent_volume',
                      'beluchting', 'recirculatie', 'effluent_eind_Ntot', 't_end'))
    i = 0
    # w, rw, v_n, v_b, v_d,

    # bij influent = Water(volume=100, NH4=50, bzv=850)
    # w_range = [100 * i for i in range(0, 50)]
    # r_w_range = [100 * i for i in range(0, 50)]

    beluchting_w_range = [10000 * i for i in range(0, 4 + 1)]
    recirculatie_w_range = [1000 * i for i in range(0, 5 + 1)]

    influent_nh4_range = [50]  # [5 * i for i in range(7, 11 + 1)]
    influent_volume_range = [25]  # [10 * i for i in range(0 + 1, 10 + 1)]

    for influent_nh4 in tqdm(influent_nh4_range):
        for influent_volume in influent_volume_range:
            # influent per kwartier
            influent = water.Influent(volume=influent_volume, NH4=influent_nh4)
            for w in beluchting_w_range:
                for r_w in recirculatie_w_range:
                    anoxische_tank = tanks.AnoxischeTank(volume=1440)
                    beluchtingstank = tanks.Beluchtingstank(volume=960)

                    recirculatie = water.Water()
                    effluent = water.Water()

                    time_range = list(range(1344))  # 1344 kwartier = 2 weken
                    previous_ntot = -10000000
                    for t in time_range:
                        beluchtingstank_stroom, _ = anoxische_tank.step(
                            influent, recirculatie)
                        beluchting_W = w  # W
                        recirculatie_W = r_w  # W
                        recirculatie, effluent, _ = beluchtingstank.step(
                            beluchtingstank_stroom, beluchting_W, recirculatie_W)
                        if (effluent.NH4 + effluent.NO3) == previous_ntot:
                            break
                        previous_ntot = effluent.NH4 + effluent.NO3

                    df.loc[i] = [influent_nh4, influent_volume,
                                 w, r_w, effluent.NH4 + effluent.NO3, t]
                    i += 1

    df.to_csv("test_df.csv")


if __name__ == "__main__":
    main()
