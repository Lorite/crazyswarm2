#!/usr/bin/env python

from pathlib import Path

import numpy as np

from crazyflie_py import Crazyswarm
from crazyflie_py.uav_trajectory import Trajectory


def main():
    swarm = Crazyswarm()
    timeHelper = swarm.timeHelper
    allcfs = swarm.allcfs
    first_cf = allcfs.crazyflies[0]

    traj1 = Trajectory()
    traj1.loadcsv(Path(__file__).parent / 'data/small_rectangle_absolute.csv')

    TRIALS = 1
    TIMESCALE = 1.0
    for i in range(TRIALS):
        first_cf.uploadTrajectory(0, 0, traj1)

        first_cf.takeoff(targetHeight=1.2, duration=3.0)
        timeHelper.sleep(2.5)
        pos = np.array(first_cf.initialPosition) + np.array([0, 0, 1.2])
        first_cf.goTo(pos, 0, 2.0)
        timeHelper.sleep(2.5)

        first_cf.startTrajectory(0, timescale=TIMESCALE, relative=False) # Be careful! This will execute the trajectory in absolute coordinates, so make sure the initial position is correct and be aware of heights and collisions!
        timeHelper.sleep(traj1.duration * TIMESCALE + 2.0)

        first_cf.land(targetHeight=0.06, duration=3.0)
        timeHelper.sleep(3.0)


if __name__ == '__main__':
    main()
