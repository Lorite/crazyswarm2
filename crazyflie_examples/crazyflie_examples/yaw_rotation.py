#!/usr/bin/env python

from pathlib import Path

from crazyflie_py import Crazyswarm
from crazyflie_py.uav_trajectory import Trajectory


def main():
    swarm = Crazyswarm()
    timeHelper = swarm.timeHelper
    first_cf = swarm.allcfs.crazyflies[0]

    traj1 = Trajectory()
    traj1.loadcsv(Path(__file__).parent / 'data/yaw_rotation.csv')

    TAKEOFF_DURATION = 2.5
    HOVER_DURATION = 2.0
    TIMESCALE = 1.0

    first_cf.uploadTrajectory(0, 0, traj1)

    first_cf.takeoff(targetHeight=1.2, duration=TAKEOFF_DURATION)
    timeHelper.sleep(TAKEOFF_DURATION + HOVER_DURATION)

    first_cf.startTrajectory(0, timescale=TIMESCALE, relative=True)
    timeHelper.sleep(traj1.duration * TIMESCALE + 2.0)

    first_cf.land(targetHeight=0.06, duration=2.5)
    timeHelper.sleep(3.0)


if __name__ == '__main__':
    main()
