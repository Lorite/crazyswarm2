#!/usr/bin/env python

from crazyflie_py import Crazyswarm
import numpy as np


def main():
    Z = 1.0

    swarm = Crazyswarm()
    timeHelper = swarm.timeHelper
    allcfs = swarm.allcfs

    # Arm before takeoff (required for Crazyflie 2.1 Brushless; harmless on
    # brushed — the brushed CF auto-armed, the brushless will not spin unarmed).
    for cf in allcfs.crazyflies:
        cf.arm(True)
    timeHelper.sleep(1.0)

    allcfs.takeoff(targetHeight=Z, duration=1.0+Z)
    timeHelper.sleep(1.5+Z)
    for cf in allcfs.crazyflies:
        pos = np.array(cf.initialPosition) + np.array([0, 0, Z])
        cf.goTo(pos, 0, 1.0)

    print('press button to continue...')
    swarm.input.waitUntilButtonPressed()

    allcfs.land(targetHeight=0.02, duration=1.0+Z)
    timeHelper.sleep(1.0+Z)
    allcfs.arm(False)


if __name__ == '__main__':
    main()
