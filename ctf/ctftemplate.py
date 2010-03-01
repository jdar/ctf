import breve
from ctf import *

class MyCTFController(CTFController):
    def __init__(self):
        CTFController.__init__(self)

        self.blue_team = []
        for i in range(10):
            member = MyBluePlayer()
            member.setTeam(0)
            self.blue_team.append(member)

        self.red_team = []
        for member in range(10):
            member = MyRedPlayer()
            member.setTeam(1)
            self.red_team.append(member)

class MyBluePlayer(CTFPlayer):
    def __init__(self):
        CTFPlayer.__init__(self)

    def iterate(self):
        self.setSpeed(1)

        if (self.hasFlag()):
            angle = self.getAngle(self.getMyHomeLocation())

            if angle > 0: 
                self.turnRight()
            elif angle < 0:
                self.turnLeft()

            CTFPlayer.iterate(self)
            return

        flag = self.senseOtherFlag()

        if flag != None:
            angle = self.getAngle(flag.getLocation())

            if angle > 0:
                self.turnRight()
            elif angle < 0:
                self.turnLeft()

            CTFPlayer.iterate(self)
            return

        if self.getLocation() == self.getOtherHomeLocation():
            angle = 0
        else:
            angle = self.getAngle(self.getOtherHomeLocation())
            if angle < 0: 
                self.turnLeft()
            elif angle > 0:
                self.turnRight()

        CTFPlayer.iterate(self)

class MyRedPlayer(CTFPlayer):
    def __init__(self):
        CTFPlayer.__init__(self)

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

        CTFPlayer.iterate(self)

MyCTFController()
