#!/usr/bin/env python

from crazyflie_py import Crazyswarm


def main():
    swarm = Crazyswarm()
    timeHelper = swarm.timeHelper
    allcfs = swarm.allcfs

    # Arm before takeoff (required for Crazyflie 2.1 Brushless; harmless on
    # brushed — the brushed CF auto-armed, the brushless will not spin unarmed).
    for cf in allcfs.crazyflies:
        cf.arm(True)
    timeHelper.sleep(1.0)

    # set group mask to enable group 1 and 4 (one by one)
    for cf in allcfs.crazyflies:
        cf.setGroupMask(0b00001001)

    print('Takeoff with a different mask (2) -> nothing should happen')
    allcfs.takeoff(targetHeight=0.5, duration=3.0, groupMask=2)
    timeHelper.sleep(3)

    print('Takeoff with correct mask (1) -> should work')
    allcfs.takeoff(targetHeight=0.5, duration=3.0, groupMask=1)
    timeHelper.sleep(3)
    allcfs.land(targetHeight=0.02, duration=3.0)
    timeHelper.sleep(3)
    allcfs.arm(False)


if __name__ == '__main__':
    main()
