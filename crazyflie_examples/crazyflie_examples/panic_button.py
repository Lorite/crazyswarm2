#!/usr/bin/env python

"""Always-on-top panic UI for a running Crazyswarm2 stack.

Three buttons:
  - LAND: graceful descent via /all/land.
  - LAND + DISARM: /all/land, then /all/arm False so stray setpoints can't relaunch.
  - EMERGENCY: /all/emergency. Latches in CF firmware; requires reboot to clear.
"""

import threading
import tkinter as tk
from tkinter import font as tkfont

import rclpy
from rclpy.node import Node
from builtin_interfaces.msg import Duration

from crazyflie_interfaces.srv import Arm, Land
from std_srvs.srv import Empty


class PanicNode(Node):
    def __init__(self):
        super().__init__('panic_button')

        self.declare_parameter('land_height', 0.04)
        self.declare_parameter('land_duration', 3.5)
        self.declare_parameter('disarm_delay', 4.0)

        self.land_client = self.create_client(Land, '/all/land')
        self.arm_client = self.create_client(Arm, '/all/arm')
        self.emergency_client = self.create_client(Empty, '/all/emergency')

    def _land_request(self):
        req = Land.Request()
        req.group_mask = 0
        req.height = float(self.get_parameter('land_height').value)
        secs = float(self.get_parameter('land_duration').value)
        req.duration = Duration(sec=int(secs), nanosec=int((secs % 1) * 1e9))
        return req

    def call_land(self, on_done):
        self.get_logger().warn('PANIC: calling /all/land')
        future = self.land_client.call_async(self._land_request())
        future.add_done_callback(lambda f: on_done('LAND', f))

    def call_emergency(self, on_done):
        self.get_logger().error('PANIC: calling /all/emergency')
        future = self.emergency_client.call_async(Empty.Request())
        future.add_done_callback(lambda f: on_done('EMERGENCY', f))

    def call_land_and_disarm(self, on_done):
        self.get_logger().warn('PANIC: calling /all/land, then /all/arm False')
        land_future = self.land_client.call_async(self._land_request())

        delay = float(self.get_parameter('disarm_delay').value)

        def after_land(_):
            timer = self.create_timer(delay, fire_disarm)
            # Hold a reference so the timer is not GC'd; we cancel inside fire_disarm.
            self._pending_disarm_timer = timer

        def fire_disarm():
            self._pending_disarm_timer.cancel()
            self.destroy_timer(self._pending_disarm_timer)
            req = Arm.Request()
            req.arm = False
            arm_future = self.arm_client.call_async(req)
            arm_future.add_done_callback(lambda f: on_done('LAND + DISARM', f))

        land_future.add_done_callback(after_land)


class PanicUI:
    def __init__(self, node: PanicNode):
        self.node = node
        self.root = tk.Tk()
        self.root.title('Crazyswarm2 Panic')
        self.root.attributes('-topmost', True)
        self.root.geometry('320x360')
        self.root.protocol('WM_DELETE_WINDOW', self._on_close)

        big = tkfont.Font(family='Helvetica', size=18, weight='bold')
        small = tkfont.Font(family='Helvetica', size=10)

        tk.Button(
            self.root, text='LAND', bg='#f1c40f', fg='black', font=big,
            activebackground='#d4ac0d',
            command=self._on_land,
        ).pack(fill='both', expand=True, padx=10, pady=(10, 5))

        tk.Button(
            self.root, text='LAND + DISARM', bg='#e67e22', fg='white', font=big,
            activebackground='#ca6f1e',
            command=self._on_land_disarm,
        ).pack(fill='both', expand=True, padx=10, pady=5)

        tk.Button(
            self.root, text='EMERGENCY', bg='#c0392b', fg='white', font=big,
            activebackground='#922b21',
            command=self._on_emergency,
        ).pack(fill='both', expand=True, padx=10, pady=(5, 10))

        self.status_var = tk.StringVar(value='ready')
        tk.Label(self.root, textvariable=self.status_var, font=small, anchor='w'
                 ).pack(fill='x', padx=10, pady=(0, 8))

    def _set_status(self, text):
        self.root.after(0, self.status_var.set, text)

    def _on_done(self, label, future):
        try:
            future.result()
            self._set_status(f'{label}: done')
        except Exception as exc:
            self._set_status(f'{label}: failed ({exc})')

    def _on_land(self):
        self._set_status('LAND: sent')
        self.node.call_land(self._on_done)

    def _on_land_disarm(self):
        self._set_status('LAND + DISARM: landing...')
        self.node.call_land_and_disarm(self._on_done)

    def _on_emergency(self):
        self._set_status('EMERGENCY: sent (reboot CF to clear)')
        self.node.call_emergency(self._on_done)

    def _on_close(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    rclpy.init()
    node = PanicNode()

    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    try:
        PanicUI(node).run()
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()
