import plotext as plt

def plot_bars(x, y, title='', width=200, ylabel=[], color=''):
    if color == '':
        color = 'white'
    ylabel = [' ' + label for label in ylabel]
    x = [i + '  ' for i in x]
    plt.bar(x, y, orientation="horizontal", width = 1 / 100, color=color, marker = "▇")
    plt.title(title)

    [plt.text(
        ylabel[i], x = y[i], y = i + 1,
        alignment = 'left', color=color, style="bold", background="default", orientation="h",
    ) for i in range(len(x))]
    plt.xaxes(False, False)
    plt.yaxes(False, False)
    plt.axes_color('transparent')
    plt.xlim(0, max(y) + 2 * max([len(label) for label in ylabel]) + 10)
    plt.plot_size(width, len(x) + int(len(title) > 0))
    plt.theme('clear')
    plt.ticks_style('bold')
    plt.xfrequency(0)
    plt.yfrequency(0)
    plt.show()
