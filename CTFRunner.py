from ctf import base
import bots
import os

class CTFRunner(base.CTFController):
    def __init__(self):
        base.CTFController.__init__(self)
        
        blue = bots.get_player1()
        self.blue_team = []
        for i in range(10):
            member = blue()
            member.setTeam(0)
            self.blue_team.append(member)

        red = bots.get_player2()
        self.red_team = []
        for member in range(10):
            member = red()
            member.setTeam(1)
            self.red_team.append(member)

CTFRunner()
