import numpy as np
from .core import Simulation

class DoublePendulum(Simulation):
    def __init__(self, L1=1.0, L2=1.0, m1=1.0, m2=1.0, theta1_0=np.pi/2, theta2_0=np.pi/2, t_max=10.0):
        self.L1 = L1
        self.L2 = L2
        self.m1 = m1
        self.m2 = m2
        self.initial_state = [theta1_0, 0.0, theta2_0, 0.0]
        self.t_max = t_max
        self.g = 9.81

    def equations(self, t, state):
        theta1, omega1, theta2, omega2 = state
        
        delta = theta2 - theta1
        den1 = (self.m1 + self.m2) * self.L1 - self.m2 * self.L1 * np.cos(delta) * np.cos(delta)
        den2 = (self.L2 / self.L1) * den1

        d_omega1 = (
            self.m2 * self.L1 * omega1 * omega1 * np.sin(delta) * np.cos(delta)
            + self.m2 * self.g * np.sin(theta2) * np.cos(delta)
            + self.m2 * self.L2 * omega2 * omega2 * np.sin(delta)
            - (self.m1 + self.m2) * self.g * np.sin(theta1)
        ) / den1

        d_omega2 = (
            - self.m2 * self.L2 * omega2 * omega2 * np.sin(delta) * np.cos(delta)
            + (self.m1 + self.m2) * self.g * np.sin(theta1) * np.cos(delta)
            - (self.m1 + self.m2) * self.L1 * omega1 * omega1 * np.sin(delta)
            - (self.m1 + self.m2) * self.g * np.sin(theta2)
        ) / den2

        return [omega1, d_omega1, omega2, d_omega2]

    def get_initial_state(self):
        return self.initial_state

    def get_time_interval(self):
        return (0, self.t_max)
    
    def get_plot_limits(self):
        limit = self.L1 + self.L2 + 0.5
        return ((-limit, limit), (-limit, limit))

    def get_coordinates(self, state):
        theta1, _, theta2, _ = state
        
        x1 = self.L1 * np.sin(theta1)
        y1 = -self.L1 * np.cos(theta1)
        
        x2 = x1 + self.L2 * np.sin(theta2)
        y2 = y1 - self.L2 * np.cos(theta2)
        
        return ([0, x1, x2], [0, y1, y2])

class SpringMass(Simulation):
    def __init__(self, k=10.0, m=1.0, length=2.0, damping=0.5, y0=0.0, v0=0.0, t_max=10.0):
        self.k = k
        self.m = m
        self.length = length
        self.damping = damping
        self.state0 = [y0, v0]
        self.t_max = t_max
    
    def equations(self, t, state):
        y, v = state
        
        d_y = v
        d_v = (-self.k * y - self.damping * v) / self.m
        return [d_y, d_v]
        
    def get_initial_state(self):
        return self.state0
        
    def get_time_interval(self):
        return (0, self.t_max)
        
    def get_plot_limits(self):
        amp = abs(self.state0[0]) + 1.0
        return ((-1, 1), (-amp - self.length, amp + self.length))
        
    def get_coordinates(self, state):
        y, _ = state
        mass_y = -self.length + y
        return ([0, 0], [0, mass_y])

class PlanetarySystem(Simulation):
    """
    N-body Gravitational Simulation.
    Note: 'state' is flattened [x1, y1, vx1, vy1, x2, y2, vx2, vy2, ...]
    """
    def __init__(self, masses, positions, velocities, G=1.0, t_max=10.0):
        self.masses = np.array(masses)
        self.n = len(masses)
        self.G = G
        self.t_max = t_max
        
        state = []
        for p, v in zip(positions, velocities):
            state.extend([p[0], p[1], v[0], v[1]])
        self.initial_state = np.array(state)
        
    def equations(self, t, state):
        params = state.reshape((self.n, 4))
        pos = params[:, :2]
        vel = params[:, 2:]
        
        d_state = np.zeros_like(params)
        
        d_state[:, :2] = vel
        
        for i in range(self.n):
            acc = np.zeros(2)
            for j in range(self.n):
                if i == j: continue
                
                r_vec = pos[j] - pos[i]
                r_mag = np.linalg.norm(r_vec)
                
                if r_mag < 1e-9: continue
                
                acc += self.G * self.masses[j] * r_vec / (r_mag**3)
            
            d_state[i, 2:] = acc
            
        return d_state.flatten()
        
    def get_initial_state(self):
        return self.initial_state
        
    def get_time_interval(self):
        return (0, self.t_max)
        
    def get_plot_limits(self):
        xs = self.initial_state[0::4]
        ys = self.initial_state[1::4]
        
        max_range = max(np.max(np.abs(xs)), np.max(np.abs(ys))) * 2.0
        return ((-max_range, max_range), (-max_range, max_range))
        
    def get_coordinates(self, state):
        xs = state[0::4]
        ys = state[1::4]
        
        return (xs, ys)
