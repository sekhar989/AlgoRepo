import pandas as pd
import matplotlib.pyplot as plt
from functions import *
from numpy.matlib import repmat
import numpy as np

# Implementation of the first part of example 3.1 in Ernest Chang's 
# book Algorithmic trading : winning strategies and their rationale.
#
# Price Spread

if __name__ == "__main__":
   
    #import data from CSV file
    root_path = '/Users/Javi/Documents/MarketData/'
    # the paths
    # MAC: '/Users/Javi/Documents/MarketData/'
    # WIN: 'C:/Users/javgar119/Documents/Python/Data/'
    filename = 'GLD_USO_daily.csv' #version 2 is bloomberg data
    full_path = root_path + filename
    data = pd.read_csv(full_path, index_col='Date')
   
    y_ticket = 'USO'
    x_ticket = 'GLD'
    y = data[y_ticket]
    x = data[x_ticket]
    
    entryZscore = 1
    exitZscore = 1

    # lookback period for calculating the dynamically changing
    lookback = 20
    modelo = pd.ols(y=y, x=x, window_type='rolling', window=lookback)
    data = data[lookback-1:]
    betas = modelo.beta

    # calculate the number of units for the strategy in the form
    # y-beta*x
    yport = pd.DataFrame(data[y_ticket] - (betas['x'] * data[x_ticket]))
    # z score calculation
    moving_mean = pd.rolling_mean(yport, window=lookback)
    moving_std = pd.rolling_std(yport,window=lookback)
    Zscore = (yport - moving_mean) / moving_std

    # trade signal 
    long_entry = Zscore < -entryZscore
    long_exit = Zscore >= -entryZscore
    short_entry = Zscore > entryZscore
    short_exit = Zscore <= entryZscore
    

    
    numunits_long= np.zeros((len(yport),1))
    numunits_long = pd.DataFrame(np.where(long_entry,1,0))
    
    
    
    numunits_short= np.zeros((len(yport),1))
    numunits_short = pd.DataFrame(np.where(short_entry,-1,0))

    numunits = numunits_long + numunits_short
    
    #print(numunits.tail(200))
 
    # compute the $ position for each asset
    AA = pd.DataFrame(repmat(numunits,1,2))
    BB = pd.DataFrame(-betas['x'])
    BB['ones'] = np.ones((len(betas)))
    
    position = multiply(multiply(AA, BB), data)

    #print (BB.head(50))

    # compute the daily pnl in $$
    
    pnl = sum(multiply(position[:-1], divide(diff(data,axis = 0), data[:-1])),1)
 
        
    # gross market value of portfolio
    mrk_val = pd.DataFrame.sum(abs(position), axis=1)
    mrk_val = mrk_val[:-1]
   
    # return is P&L divided by gross market value of portfolio
    rtn = pnl / mrk_val
    acum_rtn = pd.DataFrame(cumsum(rtn))
    acum_rtn = acum_rtn.fillna(method='pad')
    # compute performance statistics
    sharpe = (np.sqrt(252)*np.mean(rtn)) / np.std(rtn)
    APR = np.prod(1+rtn)**(252/len(rtn))-1
    
    ##################################################
    # print the results
    ##################################################
    print('Price spread Sharpe: {:.4}'.format(sharpe))
    print('Price Spread APR: {:.4%}'.format(APR))
    

    #*************************************************
    # plotting the chart
    #*************************************************    
    #plot of numunits
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(acum_rtn)
    ax.set_title('{}-{} Bollinger Band     Acum Return'.format(x_ticket, y_ticket))
    ax.set_xlabel('Data points')
    ax.set_ylabel('acumm rtn')
    ax.text(1000, 0, 'Sharpe: {:.4}'.format(sharpe))
    ax.text(1000, -0.03, 'APR: {:.4%}'.format(APR))
    
    plt.show()
    