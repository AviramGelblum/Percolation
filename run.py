"""
Performs running of simulation/analysis method. Different simulation/analysis types are
defined as different classes herein.
"""


import misc
from point import P
from general_region import GRegion
from configuration import Configuration
from rectangle import Rectangle


class Runner:
    """
    Superclass for different simulation/analysis methods.
    Subclass must be defined.
    """

    def __init__(self, cfg: Configuration, max_steps=None, seed=None):
        self.cfg = cfg  # Configuration of cube maze
        self.max_steps = max_steps  # maximum number of steps in the simulation
        self.seed = misc.init_rand(seed)  # returns random seed if seed is not defined, seed the RNG

    def step(self):
        """Dummy method, must be overridden by subclasses."""
        return P(0, 0), True

    def restart(self):
        """Re-generate random seed (if needed) as part of restart procedure."""
        self.seed = misc.init_rand(self.seed)


class SimulationError(Exception):
    """
    Define Error class for simulation.
    Raised when there is no possible allowed motion direction.
    """
    def __init__(self):
        pass


#####################################################################


class AntRunner(Runner):
    """Subclass used for creating a partial trajectory from the load trajectory data."""
    def __init__(self, cfg: Configuration, index=1):
        super().__init__(cfg)
        self.index = index  # Defined initial point in trajectory

    def step(self):
        """Get next load location"""
        cheerio = self.cfg.path.points[self.index]  # Return current load location. cheerio - tuple
        self.index += 1
        if self.index >= len(self.cfg.path.points):  # finished trajectory or not
            return cheerio, True
        else:
            return cheerio, False


#####################################################################


class DeterministicRunner(Runner):
    """
    Subclass simulation with the following rules (always aligning with nest direction):

    1)Go in the direction of the nest (defined by actual load data motion for each real cube maze)
    for as long as possible.

    2)When blocked - aligns its movement with the direction as close as possible to the direction
    of the nest.
    """

    def __init__(self, cfg: Configuration, max_steps=10000):
        super().__init__(cfg, max_steps)
        self.speed = self.cfg.cheerio_radius * 0.05  # step size
        self.cheerio = self.cfg.start  # class P
        self.v = P(0, 0)
        self.last = False  # ?

    def restart(self):
        """Resets the runner to the first location with given/random seed.
        """
        super().restart()
        self.cheerio = self.cfg.start  # initial location based on real data/(0,mid-y)
        self.v = P(0, 0)  # no initial velocity direction

    def step(self):
        """
        Perform one time step of the simulation.
        :return: cheerio - next load location (point P), False - signifying the simulation is not
        finished.
        """
        cfg = self.cfg  # cube maze configuration - Configuration Class
        cheerio = self.cheerio

        # Where can we currently go
        allowable = cfg.stones.open_direction_for_circle(cheerio, cfg.cheerio_radius, self.speed)
        if not allowable:  # can't go anywhere. This is a bug if happens.
            for stone in cfg.stones:  # cfg.stones - PolygonSet class, stone - Polygon class with
                                        #  points property which is a list of points (Point class)
                if stone.center().dist(cheerio) < cfg.cheerio_radius + cfg.stone_size:
                                        # cheerio is inside cube - print data in console
                    print("stone=Polygon([")
                    for p in stone.points:
                        print("aff(", p.x, ", ", p.y, "),")
                    print("])")
            print("center=aff(", cheerio.x, ", ", cheerio.y, ")")
            print("radius=", cfg.cheerio_radius, " * f")
            print("step=", self.speed, "* f")
            raise SimulationError()

        # Update speed
        v = self.v
        # v = v+1/5*v_nest and then resize to set speed - change in v is not abrupt, but rather
        # updates slowly
        v += (cfg.nest - cheerio).resize(self.speed / 5)
        v = v.resize(self.speed)

        # if direction of resulting v is not allowed, pick the closest possible
        if not allowable.contains(v):
            v = allowable.align_with_closest_side(v)
        self.v = v

        # Move cheerio
        self.cheerio = cheerio + self.v.resize(self.speed)

        # #TEST
        # if cfg.stones.intersect_with_circle(self.cheerio, cfg.cheerio_radius):
        #     for stone in cfg.stones:
        #         for s in stone.segments:
        #             closest, dist = s.closest_point(self.cheerio)
        #             if dist < cfg.cheerio_radius:
        #                 print(cfg.cheerio_radius - dist)
        #             if dist < cfg.cheerio_radius - 0.0000000001:
        #                 print("DIST= ", cfg.cheerio_radius - dist)
        #                 print("before=", cheerio, " after=", self.cheerio,
        #                       "stone=", stone,
        #                       "radius=", cfg.cheerio_radius,
        #                       "step=", self.speed)
        #

        return self.cheerio, False  # second argument is used to determine whether the simulation is
        # finished


#####################################################################


class StickyRunner(Runner):
    """
    Subclass simulation with the following rules (sticking to cube edges):

    1)Go in the direction of the nest (defined by actual load data motion for each real cube maze)
    when there are no cubes in the vicinity of the load.

    2)When there are cubes - determine the following directions:
        a) Closest side of the allowed regions to the direction of the nest
        b) Closest side of the allowed regions to the direction of the current velocity.
    Thereupon, determine which of these directions is closest to the current velocity, and set it as
    the current velocity.
    """

    def __init__(self, cfg: Configuration, max_steps=10000):
        super().__init__(cfg, max_steps)
        self.speed = self.cfg.cheerio_radius * 0.05  # step size
        self.cheerio = self.cfg.start  # initialize load location based on real data/(0,mid-y)
        self.v = P(0, 0)  # no initial velocity direction

    def restart(self):
        """Resets the runner to the first location with given/random seed.
         """
        super().restart()
        self.cheerio = self.cfg.start  # initial location based on real data/(0,mid-y)
        self.v = P(0, 0)  # no initial velocity direction

    def step(self):
        """
        Perform one time step of the simulation.
        :return: cheerio - next load location (point P), False - signifying the simulation is not
        finished.
        """
        cfg = self.cfg
        cheerio = self.cheerio

        # Where can we currently go
        allowable = cfg.stones.open_direction_for_circle(cheerio, cfg.cheerio_radius, self.speed)
        if not allowable:
            raise SimulationError()

        # Update speed
        to_nest = (self.cfg.nest - self.cheerio).resize(self.speed)  # speed vector in the direction
        # of the nest (determined by the last data point of the load in that maze)
        if allowable.full:
            # Case where there is no cubes in the way of the load
            self.v = to_nest
        else:
            # When there are any cubes in the vicinity of the load, it aligns with the closest
            # side of the allowed region to the current velocity direction or the closest to the
            # side of the allowed region to the nest direction, whichever is closer to to the
            # current velocity direction

            v1 = allowable.align_with_closest_side(self.v)  # closest side of the allowed regions
            #  to the current velocity direction
            if not allowable.contains(to_nest):
                to_nest = allowable.align_with_closest_side(to_nest)  # closest side of the allowed
                # regions to the nest direction

            # Determine which of v1 or to_nest are closest to the current velocity direction and
            # set it as the new current velocity
            if self.v.cos(v1) > self.v.cos(to_nest):
                self.v = v1
            else:
                self.v = to_nest

        # Move cheerio
        self.cheerio = cheerio + self.v
        return cheerio, False  # second argument is used to determine whether the simulation is
        # finished


#####################################################################


class SimulationRunner(Runner):
    """
    Subclass simulation with the following rules (changing targets):

    1) At all times there is a current target the load tries to move towards. This target is updated
    every time a certain distance is travelled. The target is chosen randomly from a normal
    distribution based around the nest location (based on the final load location in the real data).
    The target is also updated if the load does not perform rolling and cannot move towards the
    target (see section 2 below).

    2) The load itself either performs rolling or does not (a switch parameter). If it does, this
    means that instead of just trying to go towards the current target, if the calculated
    velocity direction is not within the allowed motion regions, the load aligns with the
    closest side of the allowed regions to the direction of the current velocity.
    """

    def __init__(self, cfg: Configuration, seed=None, sigma=0, rolling=True, persistence_dist=6,
                 max_steps=10000):
        super().__init__(cfg, max_steps, seed)
        self.speed = self.cfg.cheerio_radius * 0.05  # step size
        self.sigma = sigma  # Standard deviation of normal distribution used to draw from a
        # random direction to update the current target
        self.rolling = rolling  # enable/disable rolling
        self.persistence_dist = persistence_dist * cfg.cheerio_radius  # define persistence
        # length of the load. This parameter determines the time/distance passed before
        # re-selecting a new target.

        self.dist_on_same_target = 0  # initialize distance counter for target
        self.cheerio = self.cfg.start  # initialize load location based on real data/(0,mid_y)
        self.current_target = self.cfg.nest  # initialize nest direction based on real last load
        # location/(1,mid_y)
        self.v = P(0, 0)  # initialize velocity direction to 0

    def restart(self):
        """Resets the runner to the first location/target with given/random seed.
         """
        super().restart()
        self.dist_on_same_target = 0
        self.cheerio = self.cfg.start
        self.current_target = self.cfg.nest
        self.v = P(0, 0)

    def step(self):
        """
        Perform one time step of the simulation.
        :return: cheerio - next load location (point P), False - signifying the simulation is not
        finished.
        """
        cfg = self.cfg
        cheerio = self.cheerio

        # Where can we currently go
        allowable = cfg.stones.open_direction_for_circle(cheerio, cfg.cheerio_radius, self.speed)
        if not allowable:
            raise SimulationError()

        if self.sigma:
            # Update target - conditions:no target OR exceeded persistence length walking towards
            # current target OR (not rolling and cannot persist in the same direction (cube in
            # the way))
            if not self.current_target or self.dist_on_same_target >= self.persistence_dist \
                    or (not self.rolling and not allowable.contains(self.v)):
                if self.rolling:
                    # no need to take into account the allowed regions
                    choices = GRegion()
                else:
                    choices = allowable
                # Choose random direction around nest direction (approximate normal
                # distribution). If there is no rolling, then to make sure the load does not get
                # stuck, choose a direction within the allowed regions.
                rand_dir = choices.rand_point_normal(cfg.nest - cheerio, self.sigma)
                self.current_target = cheerio + rand_dir.resize(0.2)   # create new target
                self.dist_on_same_target = 0  # Reset distance walked towards the target
            else:
                # Accumulate distance walked towards the target
                self.dist_on_same_target += self.speed

        # Update speed
        v = self.v
        if self.rolling:
            # try to move towards the target
            v += (self.current_target - cheerio).resize(self.speed / 5)
            v = v.resize(self.speed)
            if not allowable.contains(v):
                # load is blocked, needs to roll

                # if v2.cos(v) <= 0: STUCK
                v = allowable.align_with_closest_side(v)  # closest side of the allowed regions
                #  to the calculated velocity direction
        else:
            # move towards target, allowed regions considerations are taken care of in the target
            # choice part
            v = (self.current_target - cheerio).resize(self.speed)
        self.v = v

        # Move cheerio
        self.cheerio = cheerio + self.v
        return cheerio, False


#####################################################################


class SimulationRunner2(Runner):
    """
       Subclass simulation with the following rules (changing targets):

       1) Move with a small bias (towards the nest) and some persistence (considering velocity
       direction of last step). Once every 1/(number of steps) on average, move in the
       direction of the nest, completely disregarding the last velocity direction.

       2) Rolling is included in this motion - the new computed velocity will be aligned to
       the closest allowed region side if its direction is not originally within an allowed
       region. The motion is conditioned to be within 90 degrees of the original computed
       velocity direction / nest direction.
    """

    def __init__(self, cfg: Configuration, seed=None, max_steps=10000):
        super().__init__(cfg, max_steps, seed)
        self.speed = cfg.cheerio_radius * 0.05  # step size
        self.cheerio = cfg.start  # initialize load location based on real data/(0,mid_y)
        self.v = (cfg.nest - cfg.start).resize(self.speed)  # initialize velocity to direction of
        # nest (relative to initial location)

    def restart(self):
        """Resets the runner to the first location/velocity direciton with given/random seed.
         """
        super().restart()
        self.cheerio = self.cfg.start
        self.v = (self.cfg.nest - self.cfg.start).resize(self.speed)

    @staticmethod
    def align(v, allowable):
        """
        Method to compute rolling behavior. Allow only motion where the angle between
        aligned velocity (v1) and original velocity (v) is <90 degrees.
        :param v: computed velocity (class P)
        :param allowable: allowed set of regions (class GRegion)
        :return: final computed velocity (class P) or None
        """

        # Check if velocity is within the allowed regions of motion
        if allowable.contains(v):
            return v
        # If not, align v with the closest side of the allowed regions
        v1 = allowable.align_with_closest_side(v)
        # Check if the angle between the aligned velocity and the original velocity is >90
        if v1.cos(v) <= 0:
            return None
        else:
            return v1

    def step(self):
        """
        Perform one time step of the simulation.
        :return: cheerio - next load location (point P), False - signifying the simulation is not
        finished.
        """
        cfg = self.cfg
        cheerio = self.cheerio

        # Where can we currently go
        allowable = cfg.stones.open_direction_for_circle(cheerio, cfg.cheerio_radius, self.speed)
        if not allowable:
            raise SimulationError

        # Update speed
        nest_direction = (cfg.nest - cheerio).resize(self.speed)  # speed vector in the direction
        # of the nest (determined by the last data point of the load in that maze)

        # Compute two possible velocity directions:
        # 1)Align current velocity direction with some nest_direction bias (if needed)
        v1 = self.align((self.v + (nest_direction * 0.1)).resize(self.speed), allowable)
        # 2)Align nest_direction (if needed)
        v2 = self.align(nest_direction, allowable)
        if v1 and v2:  # Align can return None if original velocity and aligned velocity have
            # an angle >90 between them
            expected_steps = cfg.cheerio_radius * 4 / self.speed  # Average number of steps going
            #  in the direction of the velocity (with rolling and a small bias) - persistent
            # behavior
            if misc.rand() < 1 / expected_steps:
                self.v = v2
            else:
                self.v = v1
        elif v1:
            self.v = v1
        elif v2:
            self.v = v2
        else:
            # Both are None, move in a random (allowed) direction.
            self.v = allowable.rand_point(self.speed)
            # self.v = allowable.rand_point_normal(nest_direction, 1)

        # Move cheerio
        self.cheerio = cheerio + self.v
        return cheerio, False


#####################################################################


class Run:
    """
    Class Run is a shell class performing the simulation/analysis run by iteratively calling the
    step() method of the received runner object.
    If containing_box is declared, the simulation/analysis will only be performed within its
    boundaries.
    """
    def __init__(self, runner: Runner, containing_box=None):
        self.cfg = runner.cfg
        self.runner = runner  # Runner object - determining simulation/analysis type
        self.steps = 0  # initialize step number
        self.max_steps = self.runner.max_steps  # maximum steps before simulation is terminated
        # if containing_box exists, constrain the simulation/analysis to its boundaries
        if containing_box:
            self.containing_box = containing_box
        else:
            self.containing_box = Rectangle(0, 0, 1, 1)

    def is_done(self, p):
        """
        Check if max number of steps has been reached or the load is outside (after) the containing
        box (in x).
        :param p: current load location (class P)
        :return: boolean variable determining whether the simulation is done
        """
        return (self.max_steps and self.steps >= self.max_steps) \
            or p.x > self.containing_box.qx

    def is_inside_y(self, p):
        return self.containing_box.py <= p.y <= self.containing_box.qy

    def run(self):
        """
        Run the chosen simulation/analysis runner object by iteratively calling its step() method.
        :return: path - a list of load locations sequenced by time (list of class P),
        boolean variable - the result of the simulation - True means the simulation ended
        """
        try:
            path = []  # will be a list of load locations (list of class P)
            while True:
                cheerio, res = self.runner.step()  # perform one step. cheerio is the resulting
                # point location. res is a boolean variable (always false for simulations. For
                # real data is true when the loaded trajectory data is finished)
                path.append(cheerio)
                self.steps += 1
                if self.is_done(cheerio):
                    # simulation/analysis exceeded max time steps allowed or crossed the right
                    # side of the containing_box (in x).
                    if self.steps >= self.max_steps:
                        print("Timeout")
                    return path, True
                if res or not self.is_inside_y(cheerio):
                    # analysis exceeded the number of time steps within the actual data or
                    # simulation/analysis crossed the y-boundaries of the containing_box.
                    return path, False
        except SimulationError:
            self.steps = 0
            #self.runner.restart()
            print("Happened!!!")
            # if 'path' not in locals():
            #     path = []
            return path, True
            # return self.run()

    def did_it_pass_through(self, path):
        for p in path:
            if self.is_done(p):
                return True
            if not self.is_inside_y(p):
                return False
        return False
