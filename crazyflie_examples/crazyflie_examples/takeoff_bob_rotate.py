#!/usr/bin/env python

from pathlib import Path

import numpy as np

from crazyflie_py import Crazyswarm
from crazyflie_py.uav_trajectory import Trajectory


def main():
    swarm = Crazyswarm()
    timeHelper = swarm.timeHelper
    first_cf = swarm.allcfs.crazyflies[0]

    traj1 = Trajectory()
    traj1.loadcsv(Path(__file__).parent / 'data/takeoff_bob_rotate.csv')

    TAKEOFF_DURATION = 2.5
    TIMESCALE = 1.0

    first_cf.uploadTrajectory(0, 0, traj1)

    first_cf.takeoff(targetHeight=0.3, duration=TAKEOFF_DURATION)
    timeHelper.sleep(TAKEOFF_DURATION + 1.0)

    start_pos = np.array(first_cf.initialPosition) + np.array([0.0, 0.0, 0.3])
    first_cf.goTo(start_pos, 0.0, 2.0)
    timeHelper.sleep(2.5)

    first_cf.startTrajectory(0, timescale=TIMESCALE, relative=False)
    timeHelper.sleep(traj1.duration * TIMESCALE + 2.0)

    first_cf.land(targetHeight=0.06, duration=2.5)
    timeHelper.sleep(3.0)


if __name__ == '__main__':
    main()
