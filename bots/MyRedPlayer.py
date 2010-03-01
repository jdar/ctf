import ctf
from ctf import base

class MyRedPlayer(base.CTFPlayer):
    def __init__(self):
        base.CTFPlayer.__init__(self)

    def iterate(self):
        flag = self.senseMyFlag()

        if flag != None:
            angle = self.getAngle(flag.getLocation())

            if angle > 0:
                self.turnRight()
            elif angle < 0:
                self.turnLeft()
            self.setSpeed(.3)
        else:
            self.setSpeed(1)

        base.CTFPlayer.iterate(self)
