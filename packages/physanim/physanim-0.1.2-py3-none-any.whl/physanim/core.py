import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from abc import ABC, abstractmethod

class Simulation(ABC):
    """Abstract base class for physics simulations."""
    
    @abstractmethod
    def equations(self, t, state):
        """Standard ODE equations method: dy/dt = f(t, y)."""
        pass

    @abstractmethod
    def get_initial_state(self):
        """Returns the initial state vector."""
        pass

    @abstractmethod
    def get_time_interval(self):
        """Returns (t_start, t_end)."""
        pass
    
    @abstractmethod
    def get_plot_limits(self):
        """Returns ((x_min, x_max), (y_min, y_max)) for plot setup."""
        pass

    @abstractmethod
    def get_coordinates(self, state):
        """
        Converts state vector to (x, y) coordinates for animation.
        Returns a tuple of x-arrays and y-arrays for each object to define lines/points.
        Example for double pendulum: ([x1, x2], [y1, y2])
        """
        pass

def animate(simulation, frames=500, interval=20, filename=None, theme=None):
    """
    Solves the simulation and creates an animation.
    
    Args:
        simulation: Instance of a Simulation subclass.
        frames: Number of frames in the animation.
        interval: Delay between frames in milliseconds.
        filename: If provided, saves the animation to this file.
        theme: Dict for visual customization.
               Keys: 'background_color', 'line_color', 'trail_length', 'trail_color', 'grid_alpha'.
    """
    default_theme = {
        'background_color': 'white',
        'line_color': 'black',
        'trail_length': 0,
        'trail_color': 'red',
        'grid_alpha': 1.0,
        'grid_color': 'gray'
    }
    
    if theme:
        default_theme.update(theme)
    theme = default_theme

    t_span = simulation.get_time_interval()
    t_eval = np.linspace(t_span[0], t_span[1], frames)
    y0 = simulation.get_initial_state()
    
    solution = solve_ivp(simulation.equations, t_span, y0, t_eval=t_eval, method='RK45')
    
    fig, ax = plt.subplots(figsize=(6, 6))
    
    fig.patch.set_facecolor(theme['background_color'])
    ax.set_facecolor(theme['background_color'])
    
    plot_xlim, plot_ylim = simulation.get_plot_limits()
    ax.set_xlim(plot_xlim)
    ax.set_ylim(plot_ylim)
    ax.set_aspect('equal')
    ax.grid(True, alpha=theme['grid_alpha'], color=theme['grid_color'])
    
    line, = ax.plot([], [], 'o-', lw=2, color=theme['line_color'])
    
    trail, = ax.plot([], [], '-', lw=1, color=theme['trail_color'], alpha=0.5)
    
    time_template = 'Time = %.1fs'
    text_color = 'white' if theme['background_color'] in ['black', '#000000', 'dark'] else 'black'
    time_text = ax.text(0.05, 0.9, '', transform=ax.transAxes, color=text_color)

    trail_x = []
    trail_y = []

    def init():
        line.set_data([], [])
        trail.set_data([], [])
        time_text.set_text('')
        return line, trail, time_text

    def update(i):
        current_state = solution.y[:, i]
        xs, ys = simulation.get_coordinates(current_state)
        
        line.set_data(xs, ys)
        
        if theme['trail_length'] > 0:
            trail_x.append(xs[-1])
            trail_y.append(ys[-1])
            
            if len(trail_x) > theme['trail_length']:
                trail_x.pop(0)
                trail_y.pop(0)
            
            trail.set_data(trail_x, trail_y)
        
        time_text.set_text(time_template % solution.t[i])
        return line, trail, time_text

    anim = FuncAnimation(fig, update, frames=len(t_eval), 
                         init_func=init, interval=interval, blit=True)

    if filename:
        writer = 'ffmpeg' if filename.endswith('.mp4') else 'pillow'
        try:
            anim.save(filename, writer=writer, fps=1000/interval)
            print(f"Animation saved to {filename}")
        except Exception as e:
             print(f"Failed to save animation: {e}")
    else:
        plt.show() 
    
    return anim
