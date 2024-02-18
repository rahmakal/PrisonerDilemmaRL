import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot(p1_wins, p2_wins,ties):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    labels = ['Player 1 Wins= '+str(p1_wins), 'Player 2 Wins= '+str(p2_wins), 'Ties= '+str(ties)]
    values = [p1_wins, p2_wins, ties]

    plt.bar(labels, values, color=['blue', 'orange', 'green'])
    plt.ylim(ymin=0)
    plt.show(block=False)
    plt.pause(.1)
    