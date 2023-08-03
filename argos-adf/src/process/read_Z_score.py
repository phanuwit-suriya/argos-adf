import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation

#result_10 to result_12
with open('result_10.json') as fp:
    read_output = json.load(fp)

# read from json file
output = read_output['output']
data_k = read_output['data']
threshold = read_output['threshold_Zscore']
windowSize = read_output['windowSize']
algorithm = read_output['algorithm']

#for debug
if len(output) != len(data_k):
    raise Exception

##initialize plot
f, ax = plt.subplots(1)
line1, = ax.plot([], [], 'k-')
sc = ax.scatter([],[],color='red')

def animate(i):
    if i <= len(output):
        #update data
        try:
            line1.set_data(*zip(*data_k[i]))
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
    ax.set_title('Z-score with ' + str(threshold) + \
                 'x threshold, window=' + str(windowSize))
    ax.set_xlabel('Number of points')

ani = animation.FuncAnimation(f, animate,init_func=init, interval=750)

#save as .gif format
#ani.save('Z-score with_' + str(threshold_Zscore) + \
         #'x_threshold,window=' + str(windowSize) + '.gif', writer='imagemagick')
plt.show()



