#2.3
from AutomaticSimulation import *
from src.GridMap import GridMap

# importing Ursina Engine
try:
    from ursina import *
    # from ursina.camera import Camera
    from ursina.prefabs.first_person_controller import FirstPersonController
except(e):
    print('Make sure to install Ursina Engine via "pip install ursina"')
    exit()




# Camera Class
# inherits the FirstPersonController from Ursina module
# converts the 1st person camera to 3rd person and modifies the
# default controls to be clamped between the ground at normal of ground
class Camera(FirstPersonController):

    # Called when instantiated in @GraphicsEngine.__init__
    # modifies the default FirstPersonController fields
    # and mouse settings
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cursor.color = color.rgba(0, 0, 0, 0)
        mouse.locked = False

        # default camera rotation
        self.rotation_y = -45
        self.camera_pivot.rotation_x = -45
        
        # global camera settings
        camera.rotation_x = 90
        camera.y = 100  # distance from origin
        camera.fov = 120
        camera.clip_plane_near = 0.1

    # Update called every frame of the GraphicsEngine automatically
    # moves the camera rotation based on the mouse only when the mouse
    # is locked which is when the right mouse button is held down
    # mouse will be locked/unlocked in @GraphicsEngine.input
    def update(self):
        if mouse.locked:
            self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]
            self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
            self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 0)





# Graphics Engine for 2.3 implementation with graphics.
# Using Ursina Engine
# Documentation for the Ursina engine can be found @ https://www.ursinaengine.org/api_reference.html#Ursina
# Make sure to install Ursina before running this file. 'pip install ursina'
# This class creates the window and displays the simulation to the screen.
class GraphicsEngine(Ursina):

    # CLASS VARIABLES
    SCALE = 20              # the size of tiles (ex. 100 = 100x100 units)
    ROAD_SCALE = 50         # block size of road (ex. 50 => road.len = 100 => 2 blocks)
    ZOOM_SENSITIVITY = 5    # sensitivity of zoooooom
    MIN_PADDING = 4         # minimum distance between roads \ These two can't equal
    MAX_PADDING = 10        # maximum distance between roads / or problems happen

    # Called when the GraphicsEngine class is instantiated
    # this will be a child class of the Ursina game engine
    # setup the window & camera settings
    # then it will start the loading process of the game 'self.start()'
    def __init__(self):
        super().__init__(development_mode=True)

        # window module settings
        window.title = "Traffic Simulation 3D"
        window.vsync = True
        window.borderless = True
        window.fullscreen = False
        window.exit_button.visible = False
        window.fps_counter.enable = True

        # create custom camera class
        Camera(gravity = 0)

        # create simulation data object
        self.simData = AutomaticSimulation()
        self.Map = GridMap(self.simData.road_list, self.simData.intersection_list)
        GridMap.SCALE = self.ROAD_SCALE
        GridMap.MIN_PADDING = self.MIN_PADDING
        GridMap.MAX_PADDING = self.MAX_PADDING

        self.createScene()



    # Called after the Ursina engine is setup and 
    # calls the functions that creates the scene up.
    def createScene(self):
        self.createWorldMap()
        self.createEnvironment()



    # Gathers the data from the input file and
    # creates the road layout based on the input.
    # the worldMap field should hold the grid layout of the road.
    def createWorldMap(self):
        self.Map.createCrossRoad(self.Map.crossRoads)
        self.Map.createRoads()
        self.worldMap = self.Map.map



    # Creates the environment of the scene (Sky, Fog, Terrain, Roads)
    # Uses the worldMap field to create the road layout
    # createWorldMap function must be called before this function
    def createEnvironment(self):
        # terrain
        self.terrain = Entity(model = 'quad', 
                              scale = (self.Map.xSize*200, self.Map.ySize*200, 0), 
                              position = (0, -1, 0), 
                              texture = 'grass', 
                              rotation_x = 90)
        self.terrain.texture_scale = Vec2(50, 50)


        # create roads
        for x in range(self.Map.xSize):
            for y in range(self.Map.ySize):
                if self.worldMap[y][x] != '':
                    Entity( model = 'quad', 
                            scale = self.SCALE, 
                            x = (self.Map.xSize // 2 - x) * self.SCALE,
                            y = 0,
                            z = (self.Map.ySize // 2 - y) * self.SCALE, 
                            rotation_x = 90, 
                            color = self.worldMap[y][x],
                            # texture = self.worldMap[x][z], <-- we will use this in final implementation
                            collider = None)
        

        # sky
        scene.fog_density = 0.001
        Sky()



    # Called when an input is given to the application on key down.
    # parameters:
    #   key -   the value that is inputted from the keyboard or mouse.
    #       keybinds:
    #           'esc'       -   quits & closes the app
    #           'wheel_up'  -   zooms in
    #           'wheel_down'-   zooms out
    #           'mouse3'    -   rmb : locks mouse
    def input(self, key, is_raw=False):
        match key:
            case 'mouse1':
                quit()
            case Keys.escape:
                quit()
            case 'wheel_up':
                camera.y -= self.ZOOM_SENSITIVITY
            case 'wheel_down':
                camera.y += self.ZOOM_SENSITIVITY
            case 'mouse3':
                mouse.position = Vec3(0, 0, 0)
                mouse.locked = True



    # Called when an input is given to the application on key up
    # parameters:
    #   key -   the value that is inputted from the keyboard or mouse.
    #       keybinds:
    #           'mouse3' -  rmb : unlocks mouse
    def input_up(self, key, is_raw=False):
        match key:
            case 'mouse3':
                mouse.locked = False



# Start simulation by running this file
if __name__ == "__main__":
    simulation = GraphicsEngine()
    simulation.run()