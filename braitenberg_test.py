import breve

class AggressorController(breve.BraitenbergControl):
    def __init__(self):
        # parent init
        breve.BraitenbergControl.__init__(self)
        self.vehicle = None
        self.leftSensor, self.rightSensor = [None, None]
        self.leftWheel, self.rightWheel = [None, None]
        self.light = None

        # Logical break between instance variable initialization and 
        # simulation dependent code
        AggressorController.init(self)

    def init(self):
        # create the light for the vehicle to follow
        self.light = breve.createInstances(breve.BraitenbergLight, 1)
        self.light.move(breve.vector(10, 1, 0))

        # create the vehicle
        self.vehicle = breve.createInstances(breve.BraitenbergVehicle, 1)
        self.vehicle.move(breve.vector( 0, 2, 5))

        # create and add the wheels to the vehicle
        self.leftWheel = self.vehicle.addWheel(breve.vector(-0.500000, 0, -1.500000))
        self.rightWheel = self.vehicle.addWheel(breve.vector( -0.500000, 0, 1.500000))

        # make sure the wheels don't spin if there are no lights around
        self.leftWheel.setNaturalVelocity(1) 
        self.rightWheel.setNaturalVelocity(1)

        # create and attach sensors to the vehicle
        self.rightSensor = self.vehicle.addSensor(breve.vector(2.000000, 0.400000, 1.500000))
        self.leftSensor = self.vehicle.addSensor(breve.vector(2.000000, 0.400000, -1.500000))

        # link the sensors to the wheels
        self.leftSensor.link(self.leftWheel)
        self.rightSensor.link(self.rightWheel)
        
        # set the sensor bias
        self.leftSensor.setBias(-.125)
        self.rightSensor.setBias(-.125)

        # make sure we watch our vehicle
        self.watch(self.vehicle)

# instantiate the controller to run the simulation
AggressorController()
