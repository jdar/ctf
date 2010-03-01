import breve

# Globals defines as follows
# Too lazy to write a config file. Bad form on my part.

# Dimensions of the world. World is WORLD_SIZExWORLD_SIZE units.
WORLD_SIZE = 50

# The maximum range a sensor can read
SENSOR_DISTANCE = 20

# Constants for identifying teams
BLUE_TEAM = 0
RED_TEAM = 1

# Length of a single match in simulation time units.
GAME_LENGTH = 500

# Number of matches in a tournament
TOURNAMENT_LENGTH = 5

# Amount of time to pause before starting a new match.
PAUSE_TIME = 75

class CTFController(breve.Control):
    """
    Controls the state of the capture the flag game.
    All actions are routed through the controller so each player
    moves seemingly simultaniously. 
    """

    def __init__(self):
        """
        Traditionally __init__ in breve python simulations is used 
        for variable declarations. I follow that convention here.
        init is called to actually initialize the instance variables.

        NOTE: Calling the super classes __init__ method is manditory.
        """
        breve.Control.__init__(self)
        self.left = None
        self.right = None
        self.red_flag = None
        self.blue_flag = None
        self.red_jail = None
        self.blue_jail = None
        self.red_players_captured = 0
        self.blue_players_captured = 0
        self.total_red_flag_time = 0.0
        self.total_blue_flag_time = 0.0
        self.iterations = 1
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
        self.winners_str = 'Red: %d  Blue: %d   Ties: %d'

        self.init()

    def init(self):
        """
        Set up the simulation.
        """
        # Simulation settings
        self.disableReflections()
        self.enableLighting()
        self.moveLight(breve.vector(0, 10, 0))
        self.disableShadows()
        self.pointCamera(breve.vector(0, 0, 0), breve.vector(0, 60, 60))
        self.setIntegrationStep(.2)
        self.interations = 0

        # Set up some text for the screen
        # and interpolate the text properly (WOAH)
        self.setDisplayText(self.winners_str % \
                (self.red_wins, self.blue_wins, self.ties), -.3, .8, 3)
        self.setDisplayTextScale(.7)

        # Set up timers and the number of matches to play
        self.pause_track = 0.0
        self.tournament_length = TOURNAMENT_LENGTH

        # Set up playing field
        # First initialize the shape and set its size
        field_shape = breve.createInstances(breve.Cube, 1)
        field_shape.initWith(breve.vector(WORLD_SIZE/2, .2, WORLD_SIZE))

        # Generate two halves of the playing field. 
        # Set their shape the the shape we just created
        # Change its color
        self.left = breve.createInstances(breve.Stationary, 1)
        self.left.register(field_shape, breve.vector(-1 * WORLD_SIZE / 4, 0, 0))
        self.left.setColor(breve.vector(.7, .7, 1.0))

        self.right = breve.createInstances(breve.Stationary, 1)
        self.right.register(field_shape, breve.vector(WORLD_SIZE / 4, 0, 0))
        self.right.setColor(breve.vector(1.0, .7, .7))

        # Set up the jails
        # NOTE: Jail is a subclass of a breve class. We can use common
        #       python syntax for pure python subclasses.
        self.blue_jail = Jail()
        self.blue_jail.move(breve.vector(WORLD_SIZE / 2 - 5, 0, WORLD_SIZE / 2 - 5))
        self.blue_jail.setTeam(BLUE_TEAM)
        
        self.red_jail = Jail()
        self.red_jail.move(breve.vector(-1 * WORLD_SIZE / 2 + 5, 0, -1 * WORLD_SIZE / 2 + 5))
        self.red_jail.setTeam(RED_TEAM)

        # Set up the flags
        # Randomness makes sure the position is random every time.
        # The most common way to generate random vector is:
        # breve.randomExpression(breve.vector(1, 1, 1)) - breve.vector(1, 1, 1)
        # This ensures the random vector will be within (0, 0, 0) and (1, 1, 1)
        # randomExpression knows how to generate random floats, ints, vectors and matrixs
        # but python's random is always an option.
        randomness = breve.randomExpression(breve.vector(0, 0, WORLD_SIZE/2)) - breve.vector(0, 0, WORLD_SIZE/2)

        self.blue_flag = Flag()
        self.blue_flag.setTeam(BLUE_TEAM)
        self.blue_flag.move(breve.vector((-1 * WORLD_SIZE / 2) + 5, 1, 0) + randomness)
        self.blue_flag.makeNoTagZone()
        self.blue_flag.setStartPosition(self.blue_flag.getLocation())

        self.red_flag = Flag()
        self.red_flag.setTeam(RED_TEAM)
        self.red_flag.move(breve.vector((WORLD_SIZE / 2) - 5, 1, 0) + randomness)
        self.red_flag.makeNoTagZone()
        self.red_flag.setStartPosition(self.red_flag.getLocation())
 
    def getBlueJailLocation(self):
        """
        Returns the location of the blue jail in breve vector form.
        """
        return self.blue_jail.getLocation()

    def getRedJailLocation(self):
        """
        Returns the location of the red jail in breve vector form.
        """
        return self.red_jail.getLocation()

    def getGameTime(self):
        """
        Returns the remaining game time, in simulation units.
        """
        return self.getTime() - self.start_time

    def getRedWins(self):
        """
        Returns the number of red wins.
        """
        return self.red_wins

    def getBlueWins(self):
        """
        Returns the number of blue wins.
        """
        return self.blue_wins

    def getTies(self):
        """
        Returns the number of ties.
        """
        return self.ties

    def resetWorld(self):
        """
        Resets the state of the world for a new match.
        """
        # Generate the randomness for the flag position
        location_randomizer = breve.randomExpression(breve.vector(0, 0, WORLD_SIZE/2))
        location_randomizer -= breve.vector(0, 0, WORLD_SIZE/4)

        # Reset flag locations
        self.blue_flag.move(breve.vector(-1*WORLD_SIZE/2+5, 1, 0) + location_randomizer)
        self.blue_flag.resetFlag()

        self.red_flag.move(breve.vector(WORLD_SIZE/2-5, 1, 0) + location_randomizer)
        self.red_flag.resetFlag()

        # Reset all of the player locations
        # This call varies from traditional breve python syntax. To iterate over all
        # objects of a certian class the call is usually:
        # for item in breve.allInstances(CTFPlayer)
        # But since CTFPlayer is a pure python subclass it is not added to the 
        # breve object counter properly. We have to handle our own player count.
        for item in CTFPlayer.players:
            item.resetPlayer()

        # set the pause timer, reset the iteration count
        # reset the red and blue caputer count
        # Display the winners of the match properly.
        self.pause_track = PAUSE_TIME
        self.iterations = 1
        self.red_players_captured = 0
        self.blue_players_captured = 0
        self.total_red_flag_time = 0.0
        self.total_blue_flag_time = 0.0
        self.setDisplayText(self.winners_str % \
                (self.red_wins, self.blue_wins, self.ties), -.3, .8, 3)

    def winner(self, team):
        """
        Handles a game win!
        """
        # Print the winner to the log.
        # Report some (very limited) stats.
        # Add 1 to the win count for the appropriate team.
        if team == RED_TEAM:
            print "*** The Red team wins! ***"
            self.red_wins += 1
        elif team == BLUE_TEAM:
            print "*** The Blue team wins! ***"
            self.blue_wins += 1
        else:
            print "*** Tie Game ***"
            self.ties += 1

        self.report()

        # If the tournament isn't over yet
        # Report the winner otherwise reset the world.
        if (self.red_wins + self.blue_wins + self.ties >= self.tournament_length):
            self.reportTournamentWinner()
        else:
            self.resetWorld()

    def report(self):
        """
        Logs minimal statistics to output window.
        """
        # Calculate the precentage of time red and blue had posetion of the flag for
        ### BROKEN
        self.total_red_flag_time /= self.iterations
        self.total_red_flag_time *= 100

        self.total_blue_flag_time /= self.iterations
        self.total_blue_flag_time *= 100

        # Print start and stop times.
        print "Game started at: ", self.start_time
        print "Game ended at: ", self.end_time

        # Mention if all of one team was captured.
        if self.blue_players_captured == 10:
            print "All of the Blue players were captured."
        if self.red_players_captured == 10:
            print "All of the Red players were captured."

        # Also mention who captured the flag
        if self.blue_flag.checkIfOffsides():
            print "The Blue flag was captured."
        if self.red_flag.checkIfOffsides():
            print "The Red flag was captured."

        # Print out the holding statistics
        # They look off to me...
        # Almost better...
        print "Blue had posession for %f percent of the game." % \
                (self.total_blue_flag_time)
        print "Red had posession for %f percent of the game." % \
                (self.total_red_flag_time)
        print "*********************************************************" 

    def reportTournamentWinner(self):
        """
        Reports the winner of the tournament.
        """
        # Print the win count to the console.
        print "The Blue team won %d games!" % (self.blue_wins)
        print "The Red team won %d games!" % (self.red_wins)
        print "There were %d tie games!" % (self.ties)

        # Print the tournament winner to the console.
        if self.blue_wins > self.red_wins:
            print "The Blue team wins the tournament!"
            self.setDisplayText("Blue wins the Tournament!", -.3, .8, 3)
        elif self.red_wins > self.blue_wins:
            print "The Red team wins the tournament!"
            self.setDisplayText("Red wins the Tournament!", -.3, .8, 3)
        else:
            print "Red and Blue tied!"
            self.setDisplayText("The Tournament was a Tie!", -.3, .8, 3)

    def getJailedBlueCount(self):
        """
        Returns the number of blue players in jail.
        Kept to make the API clearer.
        """
        return self.blue_players_captured

    def getJailedRedCount(self):
        """
        Returns the number of red players in jail.
        Kept to make the API clearer.
        """
        return self.red_players_captured

    def changePrisoners(self, team, n):
        """
        Changes the number of captured players (on the specified team) by n.
        """
        if team == RED_TEAM:
            self.red_players_captured += n
        else:
            self.blue_players_captured += n

    def getNextIdNumber(self, agent):
        """
        Gets the next id number for the agent.
        Used on agent initalization only.
        """
        # Set the class name of the first encountered class
        if self.first_class == "":
            self.first_class = agent.getType()

        # If agents are part of the first encountered class
        # Then use the first id counter
        # Otherwise use the second
        if agent.getType() == self.first_class:
            self.id_counter_1 += 1
            return self.id_counter_1
        else:
            self.id_counter_2 += 1
            return self.id_counter_2

    def iterate(self):
        """
        Iterate method, runs the world another step.
        """
        # If the game is over let it rest.
        if (self.red_wins + self.blue_wins + self.ties >= self.tournament_length):
            return breve.Control.iterate(self)
            

        # If we are in a pause track, ignore the shit that
        # usually needs to happen
        if self.pause_track > 0:
            self.pause_track -= 1
        else:
            # Check to see if the match is just starting.
            # If it is log the start time.
            # Iterations must be <= 2 because the engine can sort of 
            # glance over timesteps. If set_time isn't properly set, 
            # a timeout happens around game 5.
            if self.iterations <= 2:
                self.start_time = self.getTime()

            # If the blue flag has moved, kill the no tag zone.
            if self.blue_flag.hasMoved():
                self.blue_flag.killNoTagZone()

            # If the red flag has moved, kill the no tag zone.
            if self.red_flag.hasMoved():
                self.red_flag.killNoTagZone()

            # If all the red players were captured, report a win for blue.
            # Log end time.
            if self.red_players_captured == 10:
                self.end_time = self.getTime()
                self.winner(BLUE_TEAM)

            # If all the blue players were captured, report a win for red.
            # Log end time.
            if self.blue_players_captured == 10:
                self.end_time = self.getTime()
                self.winner(RED_TEAM)

            # If the blue flag is on the red side. Red team has won.
            # Log the end time.
            if self.blue_flag.checkIfOffsides():
                self.end_time = self.getTime()
                self.winner(RED_TEAM)

            # If the red flag is on the red side. Blue team has won.
            # Log the end time.
            if self.red_flag.checkIfOffsides():
                self.end_time = self.getTime()
                self.winner(BLUE_TEAM)

            # Counts the number of time units either team
            # is in control of either flag.
            if self.red_flag.getCarrier() != None:
                self.total_blue_flag_time += 1

            if self.blue_flag.getCarrier() != None:
                self.total_red_flag_time += 1

            self.iterations += 1
            game_time = self.getGameTime()

            # If time is up and no one has won.
            # It's a tie.
            if game_time >= GAME_LENGTH:
                self.end_time = self.getTime()
                self.winner(-1)

            # NOTE: used to use a format string, 
            #       but it noticably slowed down the simulation.
            time_left_str = "Time Left: %.2f" % (500 - game_time)

            self.setDisplayText(time_left_str, -.2, -.9, 0)
            breve.Control.iterate(self)

class AgentShape(breve.CustomShape):
    """
    The pointy shape of an agent.
    """

    def __init__(self):
        """
        Creates the new agent shape.
        """
        # make a breve custom shape class
        breve.CustomShape.__init__(self)

        # define some points
        a = breve.vector(0, 1, 0)
        b = breve.vector(.25, 0, 0)
        c = breve.vector(-.25, 0, 0)
        d = breve.vector(0, -.1, .5)

        # use those points to define planes
        self.addFace([a, b, c])
        self.addFace([a, b, d])
        self.addFace([a, c, d])
        self.addFace([d, c, b])

        # finish the shape.
        self.finishShape(1.0)

class CTFMobile(breve.Mobile): 
    """
    The class of anything that can move and has a team in the sim.
    """
    def __init__(self):
        breve.Mobile.__init__(self)
        # set the team to unknown
        self.team = -1

    def setTeam(self, team):
        """
        Sets the team to the specified team number.
        """
        self.team = team

    def getTeam(self):
        """
        Returns the team number.
        """
        return self.team

    def checkIfOffsides(self):
        """
        Returns true if this mobile is offsides,
        false otherwise.
        """
        if self.team == 1 and self.getLocation().x < 0.0:
            return True
        elif self.team == 0 and self.getLocation().x > 0.0:
            return True
        else:
            return False

class Jail(CTFMobile):
    """
    Class for the CTF Jails.
    """
    # Static variable used to count the number of instances
    # Since this class is not a builtin breve class we must
    # take care of the count on our own.
    jails = []

    def __init__(self):
        """
        Initializes the jail. Sets shape and color,
        and moves it to the right spot.
        """
        # Again, always call the parent's initalizer explicitly.
        CTFMobile.__init__(self)
        shape = breve.createInstances(breve.Cube, 1)
        shape.initWith(breve.vector(3, 1, 3))
        self.setShape(shape)
        self.setColor(breve.vector(0, 1, 0))
        self.setTransparency(.1)
        Jail.jails.append(self)

    def jailBreak(self):
        """
        Frees all of the agents in the jail.
        This method is executed when a collision is 
        detected between an agent and a jail.
        """
        # Cheat and do a super free for all team 
        # members. The team members see if they 
        # need to be freed.
        for item in CTFPlayer.players:
            if (item.getTeam()) == self.team:
                item.getFreed()

class Flag(CTFMobile):
    """
    Flag class. Handles shape and non-tag zone
    and carry methods.
    """
    # Again, we need to keep track of these since
    # breve doesn't.
    flags = []

    def __init__(self):
        """
        Initalizes the variables for the flag object.
        Calls proper initalizer.
        """
        # Parent initalization
        CTFMobile.__init__(self)

        # Variable initalization
        self.carrier = None
        self.image = None
        self.start_position = breve.vector()
        self.my_no_tag_zone = None

        # Flag initalization
        self.init()
        # Just ot keep track of the flags.
        Flag.flags.append(self)

    def getCarrier(self):
        """
        Returns the carrier of the flag.
        None if there is no carrier.
        """
        return self.carrier

    def setCarrier(self, carrier):
        """
        Sets the carrier of the flag.
        """
        self.carrier = carrier

    def killNoTagZone(self):
        """
        Destroys the no tag zone around the flag.
        """
        if self.my_no_tag_zone:
            # A call to the breve engine to delete the 
            # no tag zone. del won't do it here...
            breve.deleteInstances(self.my_no_tag_zone)
            self.my_no_tag_zone = None

    def hasMoved(self):
        """
        Returns true if the flag has moved 5 or more units.
        False otherwise. Used to tell if/when to kill the 
        no tag zone.
        """
        # Vectors have a length method!
        distance = (self.getLocation() - self.start_position).length()
        if distance >= 5:
            return True
        else:
            return False

    def setStartPosition(self, vector):
        """
        Remembers the starting position of the flag.
        Used to tell if the flag has moved.
        """
        self.start_position = vector

    def setSphere(self, sphere):
        """
        Sets the no tag zone sphere for a flag.
        """
        self.my_no_tag_zone = sphere

    def resetFlag(self):
        """
        Resets the flag and no tag zone.
        """
        # Reset starting location and carrier.
        self.start_position = self.getLocation()
        self.setCarrier(None)

        # If there is a no tag zone, kill it and 
        # make a fresh one.
        if self.my_no_tag_zone:
            self.killNoTagZone()
        self.makeNoTagZone()

        # Move the sphere to the location of the flag.
        self.my_no_tag_zone.move(self.getLocation())

    def makeNoTagZone(self):
        """
        Makes the no tag zone.
        """
        self.my_no_tag_zone = breve.createInstances(NoTagZone, 1)
        self.my_no_tag_zone.move(self.getLocation())

    def init(self):
        """
        Makes the flag and sets its shape and image.
        """
        # make a shape and set the flag to that shape
        shape = breve.createInstances(breve.Sphere, 1)
        shape.initWith(1.5)
        self.setShape(shape)

        # set image
        image = breve.createInstances(breve.Image, 1)
        image.load('images/star.png')
        self.setBitmapImage(image)

    def move(self, location):
        """
        Makes sure the flag doesn't go off the end of the world.
        Then calls the standard mobile move function.
        """
        # All checks for the edge of the world
        # If we want to change the board size we need
        # to change these accordingly.
        if location.x > WORLD_SIZE / 2:
            location.x = WORLD_SIZE / 2
        if location.x < -WORLD_SIZE / 2:
            location.x = -WORLD_SIZE / 2
        if location.z > WORLD_SIZE / 2:
            location.z = WORLD_SIZE / 2
        if location.z < -WORLD_SIZE / 2:
            location.z = -WORLD_SIZE / 2

        # Call to parent class's move function
        CTFMobile.move(self, location)

class NoTagZone(breve.Mobile):
    """
    The no tag zone class.
    Used only for visualization.
    """
    # Keep track of our instances
    no_tag_zones = []

    def __init__(self):
        """
        Initalizes the NoTagZone.
        """
        # Parent constructor call, still needed.
        breve.Mobile.__init__(self)
        shape = breve.createInstances(breve.Sphere, 1)
        shape.initWith(5)
        self.setShape(shape)
        self.setTransparency(.2)
        self.setColor(breve.vector(0, 0, 0))
        NoTagZone.no_tag_zones.append(self)

class CTFPlayer(CTFMobile):
    """
    CTFPlayer class. Has all of the agent callable methods.
    """
    # Again, keep track
    players = []

    def __init__(self):
        """
        Initalizes all of the variables for the CTFPlayer.
        Then initalizes it.
        """
        # Parent constructor call. Necissary.
        CTFMobile.__init__(self)

        # Variable initalization
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

        # Initalization and instance storage.
        self.init()
        CTFPlayer.players.append(self)

    def init(self):
        """
        Initalizes the CTFPlayer.
        """
        # Set the heading and get id numbers from the controller.
        # Oh right, all objects have a link to the controller class
        # in breve. This makes it easy to cheat. Don't. I'll be sad.
        self.heading = breve.vector(1, 0, 0)
        self.id_number = self.controller.getNextIdNumber(self)

        # create a shape and set the players shape to that shape.
        shape = AgentShape()
        self.setShape(shape)

        # set up collision handlers
        self.handleCollisions('Flag', 'pickUp')
        self.handleCollisions('Jail', 'jailBreak')

        # set up collision handling with other agents.
        # we don't want to tag our own team do we?
        for item in CTFPlayer.players:
            item_type = item.getType()
            self_type = self.getType()

            if item_type != self_type:
                item.handleCollisions(self_type, 'tagAgent')
                self.handleCollisions(item_type, 'tagAgent')

        # Point ourselves in a random direction.
        self.setAngle(breve.randomExpression(6.29))

    def resetPlayer(self):
        """
        Resets the player to a beginning of a match state.
        """
        self.moveToHomeside()
        self.in_jail = False
        self.drop()

    def getIdNumber(self):
        """
        Returns the id number of this player.
        """
        return self.id_number

    def setTeam(self, n):
        """
        Sets the players team and color.
        Also moves the agent to the proper side.
        """
        CTFMobile.setTeam(self, n)
        
        if self.team == 1:
            self.setColor(breve.vector(1, 0, 0))
        else:
            self.setColor(breve.vector(0, 0, 1))

        self.moveToHomeside()

    def getInJail(self):
        """
        Returns true if the player is in jail.
        False otherwise.
        """
        return self.in_jail

    def moveToHomeside(self):
        """
        Moves a player to a random location on its home side.
        """
        # r = random
        # o = offset (offsets change depending on the side of the board)
        r = breve.vector(WORLD_SIZE/4, 0, WORLD_SIZE)
        o = breve.vector()

        if self.team == 1:
            o = breve.vector(WORLD_SIZE/4, 0, -WORLD_SIZE/2)
            self.team_home = breve.vector(-1, 0, 0)
        else:
            o = breve.vector(-WORLD_SIZE/4, 0, -WORLD_SIZE/2)
            self.team_home = breve.vector(-1, 0, 0)

        # Move the agent to random+offset location.
        self.move(breve.randomExpression(r)+o)

    def getMyHomeLocation(self):
        """
        Returns the closest point to the players home side if 
        the player is offsides, otherwise it returns the players
        location.
        """
        location = self.getLocation()

        if not self.checkIfOffsides():
            return location
         
        location.x = 0

        return location

    def getOtherHomeLocation(self):
        """
        Returns the closest point to the opponents side if 
        the player is home, otherwise it returns the players
        location.
        """
        location = self.getLocation()

        if self.checkIfOffsides():
            return location
        
        location.x = 0

        return location

    def getHeading(self):
        """
        Returns the heading of the player.
        """
        return self.heading

    def hasFlag(self):
        """
        Returns true if the player is carrying the flag,
        false otherwise.
        """
        if self.carrying:
            return True
        else:
            return False

    def pickUp(self, flag):
        """
        Collision handler with flag.
        Makes the player pick up the flag.
        """
        # make sure we don't move our flag.
        if flag.getTeam() == self.team:
            return

        # make sure no one else is holding the flag.
        if flag.getCarrier() != None:
            return

        # make sure we're not in jail.
        if self.in_jail:
            return

        # make sure we aren't carrying the flag already.
        if self.carrying == None:
            # ok carry the flag, and let the flag know we're carrying it.
            self.carrying = flag
            flag.setCarrier(self)

    def drop(self):
        """
        Drops the flag.
        """
        # If we're carrying the flag.
        if self.carrying != None:
            # Let the flag know we're dropping it.
            self.carrying.setCarrier(None)

        # drop the flag.
        self.carrying = None

    def tagAgent(self, agent):
        """
        Collision handler with other players.
        Tags them and sends them to jail, or vice versa.
        """
        # cant tag friends
        if agent.getTeam() == self.getTeam():
            return

        # Can't tag in the no tag zone
        if self.inNoTagZone():
            return

        # if we're offsides drop the flag and go to jail.
        if agent.checkIfOffsides():
            agent.drop()
            agent.goToJail()

    def goToJail(self):
        """
        Puts the player in jail.
        """
        # if we're in jail we don't need to go to jail
        if self.in_jail:
            return

        # set out in_jail flag to true
        self.in_jail = True

        # stick yourself in a random spot in red prison.
        # Add one to the capture count
        if self.team == 1:
            self.jailed_location = self.controller.getRedJailLocation()
            self.jailed_location += breve.randomExpression(breve.vector(1, 0, 1))
            self.jailed_location -= breve.vector(.5, -.5, .5)
            self.controller.changePrisoners(RED_TEAM, 1)
        # stick yourself in a random spot in red prison.
        # Add one to the capture count
        else:
            self.jailed_location = self.controller.getBlueJailLocation()
            self.jailed_location += breve.randomExpression(breve.vector(1, 0, 1))
            self.jailed_location -= breve.vector(.5, -.5, .5)
            self.controller.changePrisoners(BLUE_TEAM, 1)

        # Move to that location
        self.move(self.jailed_location)

    def jailBreak(self, jail):
        """
        Collision handler with jails.
        Frees the prisoners.
        """
        # If its the right jail and I'm not in jail, jailbreak
        if not self.in_jail and jail.getTeam() == self.team:
            jail.jailBreak()

    def inNoTagZone(self):
        """
        Returns true if in the no tag zone, false otherwise.
        """
        myFlag = self.senseMyFlag()
        if myFlag != None:
            distance = breve.length(self.getLocation() - myFlag.getLocation())
            if distance <= 5 and not myFlag.hasMoved():
                return True
            else:
                return False

    def getFreed(self):
        """
        Frees the player, and teleports them home.
        """
        # don't need freeing if we aren't in jail
        if not self.in_jail: 
            return

        # move home and toggle the in_jail flag
        self.moveToHomeside()
        self.in_jail = False

        # Update the prisoner count
        if self.team == 1:
            self.controller.changePrisoners(RED_TEAM, -1)
        else:
            self.controller.changePrisoners(BLUE_TEAM, -1)

    def accelerate(self):
        """
        Accelerates the player by 0.1 velocity units.
        """
        self.setSpeed(self.velocity + 0.1)

    def decelerate(self):
        """
        Decelerates the player by 0.1 velocity units.
        """
        self.setSpeed(self.velocity - 0.1)

    def setSpeed(self, value):
        """
        Sets the speed of the player (between 0 and 1 inclusive).
        """
        self.velocity = value

        if self.velocity > 1.0:
            self.velocity = 1.0
        if self.velocity < 0.0:
            self.velocity = 0.0

    def setAngle(self, angle):
        """
        Sets the angle of the agent for turning purposes.
        Internal use only.
        """
        self.angle = angle

        self.setRotation(breve.vector(-1, 0, 0), 1.57)
        self.relativeRotate(breve.vector(0, -1, 0), angle)

    def turnLeft(self):
        """
        Turns the player left.
        """
        self.setAngle(self.angle - 0.03)

    def turnRight(self):
        """
        Turns the player right.
        """
        self.setAngle(self.angle + 0.03)

    def senseMyJail(self):
        """
        Returns the players jail if within sensor range, none otherwise.
        """
        for item in Jail.jails:
            distance = breve.length(self.getLocation() - item.getLocation()) 
            if item.getTeam() == self.team and distance < SENSOR_DISTANCE:
                return item
        return None

    def senseOtherJail(self):
        """
        Returns the opponents jail if within sensor range, none otherwise.
        """
        for item in Jail.jails:
            distance = breve.length(self.getLocation() - item.getLocation()) 
            if item.getTeam() != self.team and distance < SENSOR_DISTANCE:
                return item
        return None

    def senseMyFlag(self):
        """
        Returns the players flag if within sensor range, none otherwise.
        """
        for item in Flag.flags:
            distance = breve.length(self.getLocation() - item.getLocation()) 
            if item.getTeam() == self.team and distance < SENSOR_DISTANCE:
                return item
        return None

    def senseOtherFlag(self):
        """
        Returns the opponents flag if within sensor range, none otherwise.
        """
        for item in Flag.flags:
            distance = breve.length(self.getLocation() - item.getLocation()) 
            if item.getTeam() != self.team and distance < SENSOR_DISTANCE:
                return item
        return None

    def senseMyTeam(self):
        """
        Returns all teammates within sensor range or an empty list.
        """
        result = []
        for item in CTFPlayer.players:
            distance = breve.length(self.getLocation() - item.getLocation()) 
            if item.getTeam() == self.team and not item.getInJail() \
                    and distance < SENSOR_DISTANCE:
                result.append(item)
        return result 

    def senseOtherTeam(self):
        """
        Returns all opponents within sensor range or an empty list.
        """
        result = []
        for item in CTFPlayer.players:
            distance = breve.length(self.getLocation() - item.getLocation()) 
            if item.getTeam() != self.team and not item.getInJail() \
                    and distance < SENSOR_DISTANCE:
                result.append(item)
        return result 

    def getClosestOpponent(self):
        """
        Returns the closest opponent to the player or None.
        """
        best_distance = 200
        best = None

        for item in self.senseOtherTeam():
            distance_to_enemy = breve.length(self.getLocation() - item.getLocation()) 
            if distance_to_enemy < best_distance:
                best = item
                best_distance = distance_to_enemy 

        return best

    def getObjectAngle(self, obj):
        """
        Returns the angle to an object.
        If the angle is positive the object is to the right of the player.
        If the angle is negitive the object is to the left of the player.
        """
        if obj != None:
            return self.getAngle(obj.getLocation())
        else:
            return

    def getAngle(self, vect):
        """
        Vector angle crap. 
        Given a vector and a players own locational vector what is the angle
        to the given vector.
        """
        toO = vect - self.getLocation()
        a = breve.breveInternalFunctionFinder.angle(self, self.heading, toO)

        transpose = breve.breveInternalFunctionFinder.transpose(self, self.getRotation())
        transpose *= toO
        if transpose.x < 0.0:
            return -a
        else:
            return a

    def detectEdge(self):
        """
        Returns true if the player is at the edge of the world, 
        false otherwise.
        """
        return self.at_edge

    def iterate(self):
        """
        Handles the agents iterate loop.
        """
        # if in jail stay in jail
        if self.in_jail:
            self.move(self.jailed_location)
            return

        # if we are carrying the flag, move the flag with us
        if self.carrying != None:
            self.carrying.move(self.getLocation())

        # if we are turning left, actually turn left.
        if self.turning_left:
            self.turnLeft()

        # if we are turning right, actually turn right.
        if self.turning_right:
            self.turnRight()

        myloc = self.getLocation()
        myvel = self.getHeading()

        # check if we are at the edge of the world and stop if we are.
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

        # Get the rotational matrix
        myrot = self.getRotation()

        # Do some vector multiplication
        # and get the heading out of it!
        self.heading = myrot * breve.vector(0, 1, 0)

        # set our velocity
        # I don't remember why this works, but it does.
        # Looks like half the speed times the heading vector 
        # gives us our velocity vector
        self.setVelocity(.5 * self.velocity * self.heading)

        # always hover above the ground a bit
        myloc.y = 0.2

        # move to myloc
        self.move(myloc)

        # call mobiles iterate 
        CTFMobile.iterate(self)

# Let the breve namespace know we have these classes.
breve.NoTagZone = NoTagZone
breve.CTFController = CTFController
breve.Flag = Flag
breve.Jail = Jail
breve.AgentShape = AgentShape
breve.CTFMobile = CTFMobile
