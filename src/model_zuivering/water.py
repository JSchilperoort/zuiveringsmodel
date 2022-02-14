class Water:
    def __init__(self, volume=0.0, NH4=0.0, NO3=0.0, bzv=0.0, O2=0.0):
        self.volume = volume  # m3
        self.NH4 = NH4  # mg/l
        self.NO3 = NO3  # mg/l
        self.bzv = bzv  # mg/l
        self.O2 = O2  # mg/l

        self.NH4_absoluut = (self.NH4 * (self.volume*1000))  # mg
        self.NO3_absoluut = (self.NO3 * (self.volume*1000))  # mg
        self.bzv_absoluut = (self.bzv * (self.volume*1000))  # mg
        self.O2_absoluut = (self.O2 * (self.volume*1000))  # mg

    def update_NH4(self, NH4):
        self.NH4 = NH4  # mg/l
        self.NH4_absoluut = (self.NH4 * (self.volume*1000))  # mg

    def update_NO3(self, NO3):
        self.NO3 = NO3  # mg/l
        self.NO3_absoluut = (self.NO3 * (self.volume*1000))  # mg

    def update_bzv(self, bzv):
        self.bzv = bzv  # mg/l
        self.bzv_absoluut = (self.bzv * (self.volume*1000))  # mg

    def update_O2(self, O2):
        self.O2 = O2  # mg/l
        self.O2_absoluut = (self.O2 * (self.volume*1000))  # mg

    def get_absoluut(self):
        '''
        returns
            volume 
                m3
            NH4
                mg
            NO3
                mg
            bzv
                mg
            O2
                mg
        '''
        return self.volume, self.NH4_absoluut, self.NO3_absoluut, self.bzv_absoluut, self.O2_absoluut

    def __str__(self):
        return "Volume = {:.1f}m3\tNH4 = {:.4f}mg/l\tNO3 = {:.4f}mg/l\tvaste_stof = {:.4f}mg/l".format(self.volume, self.NH4, self.NO3, self.bzv)


class Influent(Water):
    def __init__(self, volume=0.0, NH4=0.0, NO3=0.0, bzv=850, O2=0.0):
        super().__init__(volume=volume, NH4=NH4, NO3=NO3, bzv=bzv, O2=O2)
