import ipywidgets as widgets
from ipywidgets import interactive
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display

def interact(simulation_class, **kwargs):
    """
    Creates an interactive plot for a given simulation class.
    
    Args:
        simulation_class: The Simulation subclass (e.g., DoublePendulum).
        **kwargs: Parameter ranges for the simulation __init__.
                  Format: param_name=(min, max, step) or (min, max).
                  Example: m1=(0.1, 5.0, 0.1)
    """
    
    plt.ioff()
    fig, ax = plt.subplots(figsize=(6, 6))
    plt.ion()
    
    line, = ax.plot([], [], 'o-', lw=2)
    ax.set_aspect('equal')
    ax.grid(True)
    
    def update(**params):
        sim = simulation_class(**params)
        
        t_span = sim.get_time_interval()
        
        y0 = sim.get_initial_state()
        
        from scipy.integrate import solve_ivp
        sol = solve_ivp(sim.equations, t_span, y0, dense_output=True)
        t = np.linspace(t_span[0], t_span[1], 200)
        states = sol.sol(t)
        
        xs, ys = sim.get_coordinates(states)
        
        xlim, ylim = sim.get_plot_limits()
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        
        plot_xs = []
        plot_ys = []
        
        trace_x = []
        trace_y = []
        
        for i in range(len(t)):
            state = states[:, i]
            sx, sy = sim.get_coordinates(state)
            if i == 0:
                line.set_data(sx, sy)
            
            trace_x.append(sx[-1])
            trace_y.append(sy[-1])
            
        if not hasattr(update, 'trail_line'):
             update.trail_line, = ax.plot([], [], 'r-', alpha=0.3, lw=1)
        
        update.trail_line.set_data(trace_x, trace_y)
        
        fig.canvas.draw_idle()

    widget = interactive(update, **kwargs)
    
    display(widget)
    display(fig)
