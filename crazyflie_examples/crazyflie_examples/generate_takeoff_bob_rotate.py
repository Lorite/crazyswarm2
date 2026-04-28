#!/usr/bin/env python

from pathlib import Path
import importlib.util
import sys

import numpy as np


def _workspace_root():
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / 'lib/uav_trajectories').is_dir():
            return parent
    raise RuntimeError('Unable to locate workspace root')


def main():
    workspace_root = _workspace_root()
    generator_dir = workspace_root / 'lib/uav_trajectories/scripts'
    if str(generator_dir) not in sys.path:
        sys.path.insert(0, str(generator_dir))

    module_path = generator_dir / 'generate_trajectory.py'
    spec = importlib.util.spec_from_file_location('uav_trajectories_generate_trajectory', module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Unable to load {module_path}')

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    generate_trajectory = module.generate_trajectory

    data_dir = workspace_root / 'ros2_ws/src/crazyswarm2/crazyflie_examples/crazyflie_examples/data'
    data_dir.mkdir(parents=True, exist_ok=True)
    waypoints_file = data_dir / 'takeoff_bob_rotate_waypoints.csv'
    output_file = data_dir / 'takeoff_bob_rotate.csv'

    data = np.loadtxt(waypoints_file, delimiter=',', skiprows=1)
    traj = generate_trajectory(data, num_pieces=data.shape[0] - 1)
    traj.savecsv(output_file)
    print(f'Wrote {output_file}')


if __name__ == '__main__':
    main()
