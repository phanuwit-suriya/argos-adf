import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation

#result_1 to result_9
with open('result_1.json') as fp:
    read_output = json.load(fp)

# read from json file
output = read_output['output']
data_k = read_output['data']
mode = read_output['mode']
threshold = read_output['threshold']
window_k = read_output['window_k']
algorithm = read_output['algorithm']

if len(output) != len(data_k):
    raise Exception

##initialize plot
f, ax = plt.subplots()
line1, = ax.plot([], [], 'k-')
sc = ax.scatter([],[],color='red')

def animate(i):
    if i <= len(output):
        #update data
        try:
            line1.set_data(*zip(*data_k[i]))
            # in case there is no peak detected.
            if len(output) != 0:
                sc.set_offsets(output[i])
            ax.relim()
            ax.autoscale()
            # specific maximum length in y axis
            ax.set_ylim(0, 7500)

        except Exception as ke:
            print(ke)

def init():
    #initialize data
    line1.set_data(*zip(*data_k[0]))
    if len(output) != 0:
        sc.set_offsets(output[0])
    ax.set_ylabel('Amplitudes')
    ax.set_title('Peak detection algorithm (S' + str(mode) + ') with ' + str(threshold) + \
                    'x threshold, window_k =' + str(window_k) + ' points')
    ax.set_xlabel('Number of points')

ani = animation.FuncAnimation(f, animate,init_func=init, interval=750)

#save as .gif format
#ani.save('S' + str(mode) + '_with_' + str(threshold) + \
         #'x_threshold,window=' + str(window_k) + '.gif', writer='imagemagick')
plt.show()



