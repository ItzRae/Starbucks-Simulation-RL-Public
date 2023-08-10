import numpy as np
import seaborn as sns
import matplotlib.pylab as plt
import matplotlib as mpl
import matplotlib.colors as mcolors
# mpl.rcParams['font.size'] = 20

def create_line_plot(label, lambdas, cashier_average_response_times, barista_average_response_times, system_average_response_times):
    plt.plot(lambdas, cashier_average_response_times, label='Cashier')
    plt.plot(lambdas, barista_average_response_times, label='Barista')
    plt.plot(lambdas, system_average_response_times, label='System')
    plt.xlabel('Rate of Arrival (lambda; jobs/sec)')
    plt.ylabel('Average Response Time (E[T]; sec)')
    plt.title(f'{label} Average Response Times')
    plt.legend()
    plt.savefig(f'{label}_output_plot.png')
    plt.show()
    plt.clf()  # Clear the current figure

# create steady state plot
def create_ss_plot(lam, arrivals, response_times):
    plt.plot(arrivals, response_times, c="seagreen")
    plt.gcf().set_figwidth(15)
    plt.xlabel('Arrivals (n)')
    plt.ylabel('Moving Avg Response Time of Arrival (sec)')
    plt.title(f'Response Times Per Arrival for {lam:.3f} lambda')
    plt.savefig('check_steady_state.png')
    plt.show()
    plt.clf()


def plot_heatmap(label, title, lam, data, thresholds, normalize, mean_serv_time):

    if normalize:
        norm_array = data/mean_serv_time
    else:
        norm_array = data
    vmin = norm_array.min()
    vmax = norm_array.max()

    colors1 = plt.cm.copper_r(np.linspace(0, 1, 30))
    colorW = plt.cm.BuGn(np.linspace(0, 0.2, 85))
    colors2 = plt.cm.Greens(np.linspace(0, 1, 36))
    colorW2 = plt.cm.BuGn(np.linspace(0, 0.2, 5))
    colors3 = plt.cm.Purples(np.linspace(0, 1, 52))
    colors = np.vstack((colors1, colorW, colors2, colorW2, colors3))
    mymap = mcolors.LinearSegmentedColormap.from_list('my_colormap', colors)

    
    # colors = [[0, 'darkblue'],
    #       [1 / 3, 'purple'],
    #       [2 / 3, 'purple'],
    #       [1, 'darkred']]

    ax = sns.heatmap(norm_array, 
                     linewidth=0.5, 
                     xticklabels=thresholds, 
                     yticklabels=thresholds, 
                     cmap='Greens',
                    #  vmin=1.50,
                    #  vmax=2.54,
                     annot=True, 
                     label=label, 
                     fmt='.3f', 
                     cbar=True, 
                    )
    ax.invert_yaxis()
    sns.set(font_scale=1.22)
    ax.set(xlabel='In-Person Queue Threshold', ylabel='Drive-Thru Queue Threshold')
    plt.title(f"{label} {title} of {lam:.3f} lambda", fontsize=16, fontweight='bold', wrap=True)
    plt.savefig(f'{label} _output_heatmap.png')
    plt.show()
    plt.clf() # Clear current figure
    return plt
    #5 7 9 11 13 15

""" def create_line_plot(lambdas, sim_average_response_times, actual_average_response_times):
    plt.plot(lambdas, sim_average_response_times, label='Simulated')
    plt.plot(lambdas, actual_average_response_times, label='Actual')
    plt.xlabel('Rate of Arrival (lambda; jobs/sec)')
    plt.ylabel('Average Response Time (E[T]; sec)')
    plt.title('Simulated vs Actual Average Response Times')
    plt.legend()
    plt.show()

def create_line_plot(lambdas, sim_average_response_times):
    plt.plot(lambdas, sim_average_response_times, label='Simulated')
    plt.xlabel('Rate of Arrival (lambda; jobs/sec)')
    plt.ylabel('Average Response Time (E[T]; sec)')
    plt.title('Simulated Average Response Times')
    plt.legend()
    plt.show() """
