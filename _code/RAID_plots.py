import numpy as np
from matplotlib import rc
import matplotlib.pyplot as plt

#style!
gsize=5
gw=0.5
rc('path', simplify=True)
rc('figure', figsize=(gsize*1.718,gsize))
rc('font', family='serif', weight=100, size=14)
rc('mathtext', default='regular')
rc('xtick', labelsize=16)
rc('ytick', labelsize=16)
rc('xtick.major', size=8, width=gw)
rc('ytick.major', size=8, width=gw)
rc('xtick.minor', size=4, width=gw, visible=True)
rc('ytick.minor', size=4, width=gw, visible=True)
rc('lines', markeredgewidth=1)
rc('figure.subplot', top=0.93, bottom=0.15)#, right=0.95, left=0.15)
rc('legend', numpoints=1, scatterpoints=1, frameon=False, handletextpad=0.3)
rc('axes', linewidth=gw, labelweight=100, labelsize=18)

def main(outpre='../images/RAID/RAID', dpi=100):

    #The raw data; gross

    #block sizes
    bs = np.array([128, 512, 1024])

    #for the 3 disk array
    disk3_chunks = np.array([64, 512, 1024])
    # shape = (bs, chunk)
    disk3_write = np.array([[6.8, 10, 10],
                   [6.3, 9.9, 9.8],
                   [7.3, 9.6, 9.0]])
    disk3_unbuff = np.array([[35, 37, 39],
                             [35, 35, 38],
                             [35, 37, 39]])
    disk3_buff = np.array([[580, 531, 500],
                          [535, 500, 550],
                          [35, 37, 39]])

    #for the 4 disk array
    disk4_chunks = np.array([4, 64, 512, 1024, 4096])
    disk4_write = np.array([[24, 18, 18, 18, 5.9],
                            [13, 8, 10, 7.3, 3.6],
                            [15, 8.3, 12, 8.3, 4.5]])
    disk4_unbuff = np.array([[35, 45, 45, 45, 43],
                             [35, 45, 45, 38, 43],
                             [35, 38, 38, 41, 43]])
    disk4_buff = np.array([[580, 560, 570, 560, 570],
                           [530, 550, 550, 550, 550],
                           [35, 45, 38, 40, 42]])

    #for the 4 disk RAID 10
    disk4_10_write = np.array([[13, 14, 12, 12, 14],
                                [12, 13, 13, 13, 14],
                                [12, 13.5, 13, 13, 14]])
    disk4_10_unbuff = np.array([[29, 29, 30, 39, 43],
                                [35, 25, 40, 41, 42],
                                [27, 26, 30, 35, 41]])
    disk4_10_buff = np.array([[41, 42, 44, 42, 40],
                              [41, 41, 44, 43, 43],
                              [41, 42, 44, 42, 42]])
    
    # colors to use
    colors = ['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00']

    #make the write plot
    write_ax = plt.figure().add_subplot(111)
    write_ax.set_xlabel('chunk size [kb]')
    write_ax.set_ylabel('disk speed [MB/s]')
    write_ax.set_title('write speed')
    write_ax.set_xscale('log')
        
    for i in range(3):
        write_ax.plot(disk3_chunks, disk3_write[i], color=colors[i], ls='--')    
        write_ax.plot(disk4_chunks, disk4_write[i], color=colors[i], label=bs[i])
        write_ax.plot(disk4_chunks, disk4_10_write[i], color=colors[i], ls=':')        

    write_ax.legend(frameon=False, loc=0, title='block size [kb]')

    write_ax.figure.savefig(outpre+'_write.png', dpi=dpi)

    # the unbuffered read plot
    unbuff_ax = plt.figure().add_subplot(111)
    unbuff_ax.set_xlabel('chunk size [kb]')
    unbuff_ax.set_ylabel('disk speed [MB/s]')
    unbuff_ax.set_title('unbuffered read speed')
    unbuff_ax.set_xscale('log')
        
    for i in range(3):
        unbuff_ax.plot(disk3_chunks, disk3_unbuff[i], color=colors[i], ls='--')    
        unbuff_ax.plot(disk4_chunks, disk4_unbuff[i], color=colors[i], label=bs[i])
        unbuff_ax.plot(disk4_chunks, disk4_10_unbuff[i], color=colors[i], ls=':')

    unbuff_ax.figure.savefig(outpre+'_unbuff.png', dpi=dpi)

    # the buffered read plot
    buff_ax = plt.figure().add_subplot(111)
    buff_ax.set_xlabel('chunk size [kb]')
    buff_ax.set_ylabel('disk speed [MB/s]')
    buff_ax.set_title('buffered read speed')
    buff_ax.set_xscale('log')
        
    for i in range(3):
        buff_ax.plot(disk3_chunks, disk3_buff[i], color=colors[i], ls='--')    
        buff_ax.plot(disk4_chunks, disk4_buff[i], color=colors[i], label=bs[i])
        buff_ax.plot(disk4_chunks, disk4_10_buff[i], color=colors[i], ls=':')

    buff_ax.figure.savefig(outpre+'_buff.png', dpi=dpi)

    plt.close('all')
    
    return
