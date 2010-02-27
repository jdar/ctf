import breve

WORLD_SIZE = 50
SENSOR_DISTANCE = 20

BLUE = 0
RED = 1

GAME_LENGTH = 500
TOURNAMENT_LENGTH = 5
PAUSE_TIME = 75

class CTFController(breve.Control):
    def __init__(self):
        breve.Control.__init__(self)
        self.left = None
        self.right = None
        self.red_flag = None
        self.blue_flag = None
        self.red_jail = None
        self.blue_jail = None
        self.red_p = 0
        self.blue_p = 0
        self.total_red_p = 0.0
        self.total_blue_p = 0.0
        self.iterations = 0.0
        self.id_counter_1 = 0
        self.id_counter_2 = 0
        self.first_class = ''
        self.red_wins = 0
        self.blue_wins = 0
        self.ties = 0
        self.tournament_length = 0
        self.pause_track = 0
        self.start_time = 0.0
        self.end_time = 0.0

        self.init()

    def init(self):
        # Simulation settings
        self.disableReflections()
        self.enableLighting()
        self.moveLight(breve.vector(0, 10, 0))
        self.disableShadows()
        self.pointCamera(breve.vector(0, 0, 0), breve.vector(0, 60, 60))
        self.setIntegrationStep(.2)

        # Set up some text for the screen
        self.setDisplayText('Red: $red_wins   Blue: $blue_wins   Ties: $ties', -.95, .6, 3)
        self.setDisplayTextScale(.7)

        # Set up timers
        self.pause_track = 0.0
        self.setTournamentLength(TOURNAMENT_LENGTH)

        # Set up playing field
        field_shape = breve.createInstances(breve.Cube, 1)
        field_shape.initWith(breve.vector(WORLD_SIZE/2, .2, WORLD_SIZE))

        self.left = breve.createInstances(breve.Stationary, 1)
        self.left.register(field_shape, breve.vector(-1 * WORLD_SIZE / 4, 0, 0))
        self.left.setColor(breve.vector(.7, .7, 1.0))

        self.right = breve.createInstances(breve.Stationary, 1)
        self.right.register(field_shape, breve.vector(WORLD_SIZE / 4, 0, 0))
        self.right.setColor(breve.vector(1.0, .7, .7))

        # Set up the jails
        self.blue_jail = Jail()
        self.blue_jail.move(breve.vector(WORLD_SIZE / 2 - 5, 0, WORLD_SIZE / 2 - 5))
        self.blue_jail.setTeam(BLUE)
        
        self.red_jail = Jail()
        self.red_jail.move(breve.vector(-1 * WORLD_SIZE / 2 + 5, 0, -1 * WORLD_SIZE / 2 + 5))
        self.red_jail.setTeam(RED)

        # Set up the flags
        randomness = breve.randomExpression(breve.vector(0, 0, WORLD_SIZE/2)) - breve.vector(0, 0, WORLD_SIZE/2)

        self.blue_flag = Flag()
        self.blue_flag.setTeam(BLUE)
        self.blue_flag.move(breve.vector((-1 * WORLD_SIZE / 2) + 5, 1, 0) + randomness)
        self.blue_flag.makeBounds()
        self.blue_flag.setStartPosition(self.blue_flag.getLocation())

        self.red_flag = Flag()
        self.red_flag.setTeam(RED)
        self.red_flag.move(breve.vector((WORLD_SIZE / 2) - 5, 1, 0) + randomness)
        self.red_flag.makeBounds()
        self.red_flag.setStartPosition(self.red_flag.getLocation())
 
    def setTournamentLength(self, length):
        self.tournament_length = length

    def getBlueJailLocation(self):
        return self.blue_jail.getLocation()

    def getRedJailLocation(self):
        return self.red_jail.getLocation()

    def getGameTime(self):
        return self.getTime() - self.start_time

    def getRedWins(self):
        return self.red_wins

    def getBlueWins(self):
        return self.blue_wins

    def getTies(self):
        return self.ties

    def resetWorld(self):
        location_randomizer = breve.randomExpression(breve.vector(0, 0, WORLD_SIZE/2))
        location_randomizer -= breve.vector(0, 0, WORLD_SIZE/4)

        self.blue_flag.move(breve.vector(-1*WORLD_SIZE/2+5, 1, 0) + location_randomizer)
        self.blue_flag.resetFlag()

        self.red_flag.move(breve.vector(WORLD_SIZE/2-5, 1, 0) + location_randomizer)
        self.red_flag.resetFlag()

        for item in CTFPlayer.players:
            item.resetPlayer()

        self.pause_track = PAUSE_TIME
        self.iterations = 0
        self.red_p = 0
        self.blue_p = 0
        self.setDisplayText('Red: $redWins   Blue: $blueWins   Ties: $ties', -.95, .6, 3)

    def setText(self, text):
        self.setDisplayText(text, -.95, -.95)

    def winForRed(self):
        print "*** The Red team wins! ***"
        self.report()
        self.red_wins += 1
        if (self.red_wins + self.blue_wins + self.ties >= self.tournament_length):
            self.reportWinner()
        else:
            self.resetWorld()

    def winForBlue(self):
        print "*** The Blue team wins! ***"
        self.report()
        self.blue_wins += 1
        if (self.red_wins + self.blue_wins + self.ties >= self.tournament_length):
            self.reportWinner()
        else:
            self.resetWorld()

    def tie(self):
        print "*** Tie Game ***"
        self.report()
        self.ties += 1
        if (self.red_wins + self.blue_wins + self.ties >= self.tournament_length):
            self.reportWinner()
        else:
            self.resetWorld()

    def report(self):
        self.total_red_p /= self.iterations
        self.total_red_p *= 10

        self.total_blue_p /= self.iterations
        self.total_blue_p *= 10

        if self.blue_p == 10:
            print "All of the Blue players were captured."
        if self.red_p == 10:
            print "All of the Red players were captured."

        if self.blue_flag.checkIfOffsides():
            print "The Blue flag was captured."
        if self.red_flag.checkIfOffsides():
            print "The Red flag was captured."

        print "Blue had posession for $totalBlueP percent of the game."
        print "Red had posession for $totalRedP percent of the game."
        print "*********************************************************" 

    def reportWinner(self):
        print "The Blue team won $blueWins games!"
        print "The Red team won $blueWins games!"
        print "There were $ties tie games!"
        if self.blue_wins > self.red_wins:
            print "The Blue team wins the tournament!"
        elif self.red_wins > self.blue_wins:
            print "The Red team wins the tournament!"
        else:
            print "Red and Blue tied!"

    def getJailedBlueCount(self):
        return self.blue_p

    def getJailedRedCount(self):
        return self.red_p

    def changeRedPrisoners(self, n):
        self.red_p += n

    def changeBluePrisoners(self, n):
        self.blue_p += n

    def getNextIdNumber(self, agent):
        if self.first_class == "":
            self.first_class = agent.getType()

        if agent.getType() == self.first_class:
            self.id_counter_1 += 1
            return self.id_counter_1

        self.id_counter_2 += 1
        return self.id_counter_2

    def iterate(self):
        if self.pause_track > 0:
            self.pause_track -= 1
        else:
            if self.iterations == 1:
                self.start_time = self.getTime()

            if self.blue_flag.hasMoved():
                self.blue_flag.killTheSphere()

            if self.red_flag.hasMoved():
                self.red_flag.killTheSphere()

            if self.red_p == 10:
                self.winForBlue()
                self.end_time = self.getTime()

            if self.blue_p == 10:
                self.winForRed()
                self.end_time = self.getTime()

            if self.blue_flag.checkIfOffsides():
                self.winForRed()
                self.end_time = self.getTime()

            if self.red_flag.checkIfOffsides():
                self.winForBlue()
                self.end_time = self.getTime()

            if self.blue_flag.getCarrier() == None:
                self.total_red_p += 1

            if self.red_flag.getCarrier() == None:
                self.total_blue_p += 1

            self.iterations += 1
            self.game_time = self.getGameTime()

            if self.getGameTime() >= GAME_LENGTH: 
                if self.end_time < self.start_time:
                    r_avg = self.total_red_p / self.iterations
                    b_avg = self.total_blue_p / self.iterations

                    if r_avg == b_avg:
                        self.tie()
                    elif r_avg > b_avg: 
                        self.winForRed()
                    else:
                        self.winForBlue()

                    self.end_time = self.getTime()

            self.setDisplayText("Game Time: $gameTime", 0)
            breve.Control.iterate(self)

class AgentShape(breve.CustomShape):
    def __init__(self):
        breve.CustomShape.__init__(self)

        a = breve.vector(0, 1, 0)
        b = breve.vector(.25, 0, 0)
        c = breve.vector(-.25, 0, 0)
        d = breve.vector(0, -.1, .5)

        self.addFace([a, b, c])
        self.addFace([a, b, d])
        self.addFace([a, c, d])
        self.addFace([d, c, b])
        self.finishShape(1.0)

class CTFMobile(breve.Mobile): 
    def __init__(self):
        breve.Mobile.__init__(self)
        self.team = -1

    def setTeam(self, team):
        self.team = team

    def getTeam(self):
        return self.team

    def checkIfOffsides(self):
        if self.team == 1 and self.getLocation().x < 0.0:
            return True
        elif self.team == 0 and self.getLocation().x > 0.0:
            return True
        else:
            return False

class Jail(CTFMobile):
    jails = []

    def __init__(self):
        CTFMobile.__init__(self)
        shape = breve.createInstances(breve.Cube, 1)
        shape.initWith(breve.vector(3, 1, 3))
        self.setShape(shape)
        self.setColor(breve.vector(0, 1, 0))
        self.setTransparency(.1)
        Jail.jails.append(self)

    def jailBreak(self):
        for item in CTFPlayer.players:
            if (item.getTeam()) == self.team:
                item.getFreed()

class Flag(CTFMobile):
    flags = []

    def __init__(self):
        CTFMobile.__init__(self)
        self.carrier = None
        self.image = None
        self.start_position = breve.vector()
        self.my_sphere = None
        self.init()
        Flag.flags.append(self)

    def getCarrier(self):
        return self.carrier

    def setCarrier(self, carrier):
        self.carrier = carrier

    def killTheSphere(self):
        if self.my_sphere:
            breve.deleteInstances(self.my_sphere)
            self.my_sphere = None

    def hasMoved(self):
        distance = (self.getLocation() - self.start_position).length()
        if distance >= 5:
            return True
        else:
            return False

    def setStartPosition(self, vector):
        self.start_position = vector

    def setSphere(self, sphere):
        self.my_sphere = sphere

    def resetFlag(self):
        self.start_position = self.getLocation()
        self.setCarrier(None)
        if self.my_sphere:
            self.killTheSphere()
        self.makeBounds()
        self.my_sphere.move(self.getLocation())

    def makeBounds(self):
        self.my_sphere = breve.createInstances(FlagSphere, 1)
        self.my_sphere.move(self.getLocation())

    def init(self):
        shape = breve.createInstances(breve.Sphere, 1)
        shape.initWith(1.5)
        self.setShape(shape)

        image = breve.createInstances(breve.Image, 1)
        image.load('images/star.png')
        self.setBitmapImage(image)

    def move(self, location):
        if location.x > WORLD_SIZE / 2:
            location.x = WORLD_SIZE / 2
        if location.x < -WORLD_SIZE / 2:
            location.x = -WORLD_SIZE / 2
        if location.z > WORLD_SIZE / 2:
            location.z = WORLD_SIZE / 2
        if location.z < -WORLD_SIZE / 2:
            location.z = -WORLD_SIZE / 2

        CTFMobile.move(self, location)

class FlagSphere(breve.Mobile):
    flag_spheres = []

    def __init__(self):
        breve.Mobile.__init__(self)
        shape = None
        self.init()
        FlagSphere.flag_spheres.append(self)

    def init(self):
        shape = breve.createInstances(breve.Sphere, 1)
        shape.initWith(5)
        self.setShape(shape)
        self.setTransparency(.2)
        self.setColor(breve.vector(0, 0, 0))

class CTFPlayer(CTFMobile):
    players = []

    def __init__(self):
        CTFMobile.__init__(self)
        self.shape = None
        self.velocity = 0.0
        self.angle = 0.0
        self.heading = breve.vector()
        self.turning_left = False
        self.turning_right = False
        self.at_edge = False
        self.carrying = None
        self.team_home = breve.vector()
        self.in_jail = False
        self.jailed_location = breve.vector()
        self.id_number = 0

        self.init()
        CTFPlayer.players.append(self)

    def init(self):
        self.heading = breve.vector(1, 0, 0)
        self.id_number = self.controller.getNextIdNumber(self)

        shape = AgentShape()
        self.setShape(shape)

        self.handleCollisions('Flag', 'pickUp')
        self.handleCollisions('Jail', 'jailBreak')

        for item in CTFPlayer.players:
            item_type = item.getType()
            self_type = self.getType()

            if item_type != self_type:
                item.handleCollisions(self_type, 'tagAgent')
                self.handleCollisions(item_type, 'tagAgent')

        self.setAngle(breve.randomExpression(6.29))

    def resetPlayer(self):
        self.moveToHomeside()
        self.in_jail = False
        self.drop()
        self.carrying = None

    def getIdNumber(self):
        return self.id_number

    def setTeam(self, n):
        CTFMobile.setTeam(self, n)
        
        if self.team == 1:
            self.setColor(breve.vector(1, 0, 0))
        else:
            self.setColor(breve.vector(0, 0, 1))

        self.moveToHomeside()

    def getInJail(self):
        return self.in_jail

    def moveToHomeside(self):
        r = breve.vector(WORLD_SIZE/4, 0, WORLD_SIZE)
        o = breve.vector()

        if self.team == 1:
            o = breve.vector(WORLD_SIZE/4, 0, -WORLD_SIZE/2)
            self.team_home = breve.vector(-1, 0, 0)
        else:
            o = breve.vector(-WORLD_SIZE/4, 0, -WORLD_SIZE/2)
            self.team_home = breve.vector(-1, 0, 0)

        self.move(breve.randomExpression(r)+o)

    def getMyHomeLocation(self):
        location = self.getLocation()

        if not self.checkIfOffsides():
            return location
        
        location.x = 0

        return location

    def getOtherHomeLocation(self):
        location = self.getLocation()

        if self.checkIfOffsides():
            return location
        
        location.x = 0

        return location

    def setTurningLeft(self, i):
        self.turning_left = i

    def setTurningRight(self, i):
        self.turning_right = i

    def getHeading(self):
        return self.heading

    def hasFlag(self):
        if self.carrying:
            return True
        else:
            return False

    def pickUp(self, flag):
        if flag.getTeam() == self.team:
            return

        if flag.getCarrier() != None:
            return

        if self.in_jail:
            return

        if self.carrying == None:
            self.carrying = flag
            flag.setCarrier(self)

    def drop(self):
        if self.carrying != None:
            self.carrying.setCarrier(None)

        self.carrying = None

    def tagAgent(self, agent):
        if agent.getTeam() == self.getTeam():
            return

        if self.tooCloseToFlag():
            return

        if agent.checkIfOffsides():
            agent.drop()
            agent.goToJail()

    def goToJail(self):
        if self.in_jail:
            return

        self.in_jail = True

        if self.team == 1:
            self.jailed_location = self.controller.getRedJailLocation()
            self.jailed_location += breve.randomExpression(breve.vector(1, 0, 1))
            self.jailed_location -= breve.vector(.5, -.5, .5)
            self.controller.changeRedPrisoners(1)
        else:
            self.jailed_location = self.controller.getBlueJailLocation()
            self.jailed_location += breve.randomExpression(breve.vector(1, 0, 1))
            self.jailed_location -= breve.vector(.5, -.5, .5)
            self.controller.changeBluePrisoners(1)

        self.move(self.jailed_location)

    def jailBreak(self, jail):
        if not self.in_jail and jail.getTeam() == self.team:
            jail.jailBreak()

    def tooCloseToFlag(self):
        myFlag = self.senseMyFlag()
        if myFlag != None:
            distance = breve.length(self.getLocation() - myFlag.getLocation())
            if distance <= 5 and not myFlag.hasMoved():
                return True
            else:
                return False

    def getFreed(self):
        if not self.in_jail: 
            return

        self.moveToHomeside()
        self.in_jail = False

        if self.team == 1:
            self.controller.changeRedPrisoners(-1)
        else:
            self.controller.changeBluePrisoners(-1)

    def accelerate(self):
        self.setSpeed(self.velocity + 0.1)

    def decelerate(self):
        self.setSpeed(self.velocity - 0.1)

    def setSpeed(self, value):
        self.velocity = value

        if self.velocity > 1.0:
            self.velocity = 1.0
        if self.velocity < 0.0:
            self.velocity = 0.0

    def setAngle(self, angle):
        self.angle = angle

        self.setRotation(breve.vector(-1, 0, 0), 1.57)
        self.relativeRotate(breve.vector(0, -1, 0), angle)

    def turnLeft(self):
        self.setAngle(self.angle - 0.03)

    def turnRight(self):
        self.setAngle(self.angle + 0.03)

    def senseMyJail(self):
        for item in Jail.jails:
            distance = breve.length(self.getLocation() - item.getLocation()) 
            if item.getTeam() == self.team and distance < SENSOR_DISTANCE:
                return item
        return None

    def senseOtherJail(self):
        for item in Jail.jails:
            distance = breve.length(self.getLocation() - item.getLocation()) 
            if item.getTeam() != self.team and distance < SENSOR_DISTANCE:
                return item
        return None

    def senseMyFlag(self):
        for item in Flag.flags:
            distance = breve.length(self.getLocation() - item.getLocation()) 
            if item.getTeam() == self.team and distance < SENSOR_DISTANCE:
                return item
        return None

    def senseOtherFlag(self):
        for item in Flag.flags:
            distance = breve.length(self.getLocation() - item.getLocation()) 
            if item.getTeam() != self.team and distance < SENSOR_DISTANCE:
                return item
        return None

    def senseMyTeam(self):
        result = []
        for item in CTFPlayer.players:
            distance = breve.length(self.getLocation() - item.getLocation()) 
            if item.getTeam() == self.team and not item.getInJail() and distance < SENSOR_DISTANCE:
                result.append(item)
        return result 

    def senseOtherTeam(self):
        result = []
        for item in CTFPlayer.players:
            distance = breve.length(self.getLocation() - item.getLocation()) 
            if item.getTeam() != self.team and not item.getInJail() and distance < SENSOR_DISTANCE:
                result.append(item)
        return result 

    def getClosestOpponent(self):
        best_distance = 200
        best = None

        for item in self.senseOtherTeam():
            distance_to_enemy = breve.length(self.getLocation() - item.getLocation()) 
            if distance_to_enemy < best_distance:
                best = item
                best_distance = distance_to_enemy 

        return best

    def getObjectAngle(self, obj):
        if obj != None:
            return self.getAngle(obj.getLocation())
        else:
            return

    def getAngle(self, vect):
        toO = vect - self.getLocation()
        a = breve.breveInternalFunctionFinder.angle(self, self.heading, toO)

        transpose = breve.breveInternalFunctionFinder.transpose(self, self.getRotation())
        transpose *= toO
        if transpose.x < 0.0:
            return -a
        else:
            return a

    def detectEdge(self):
        return self.at_edge

    def iterate(self):
        if self.in_jail:
            self.move(self.jailed_location)
            return

        if self.carrying != None:
            self.carrying.move(self.getLocation())

        if self.turning_left:
            self.turnLeft()

        if self.turning_right:
            self.turnRight()

        myloc = self.getLocation()
        myvel = self.getHeading()

        if myloc.x > (WORLD_SIZE / 2) and myvel.x > 0.0:
            self.setSpeed(0)
            self.at_edge = True
        elif myloc.z > (WORLD_SIZE / 2) and myvel.z > 0.0:
            self.setSpeed(0)
            self.at_edge = True
        elif myloc.x < -(WORLD_SIZE / 2) and myvel.x < 0.0:
            self.setSpeed(0)
            self.at_edge = True
        elif myloc.z < -(WORLD_SIZE / 2) and myvel.z < 0.0:
            self.setSpeed(0)
            self.at_edge = True
        else:
            self.at_edge = False

        myrot = self.getRotation()

        self.heading = myrot * breve.vector(0, 1, 0)

        self.setVelocity(.5 * self.velocity * self.heading)

        myloc.y = 0.2

        self.move(myloc)

        CTFMobile.iterate(self)

breve.FlagSphere = FlagSphere
breve.CTFController = CTFController
breve.Flag = Flag
breve.Jail = Jail
breve.AgentShape = AgentShape
breve.CTFMobile = CTFMobile
