import ctf
from ctf import base

print base
class MyBluePlayer(base.CTFPlayer):
    def __init__(self):
        base.CTFPlayer.__init__(self)

    def iterate(self):
        self.setSpeed(1)

        if (self.hasFlag()):
            angle = self.getAngle(self.getMyHomeLocation())

            if angle > 0: 
                self.turnRight()
            elif angle < 0:
                self.turnLeft()

            base.CTFPlayer.iterate(self)
            return

        flag = self.senseOtherFlag()

        if flag != None:
            angle = self.getAngle(flag.getLocation())

            if angle > 0:
                self.turnRight()
            elif angle < 0:
                self.turnLeft()

            base.CTFPlayer.iterate(self)
            return

        if self.getLocation() == self.getOtherHomeLocation():
            angle = 0
        else:
            angle = self.getAngle(self.getOtherHomeLocation())
            if angle < 0: 
                self.turnLeft()
            elif angle > 0:
                self.turnRight()

        base.CTFPlayer.iterate(self)
