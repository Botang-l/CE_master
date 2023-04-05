from gurobipy import*
import pandas as pd
from optimization import *
import numpy as np
import time
import random
# 讀取車班資料
df = pd.read_csv('TRA1.csv', sep=",")
#df = df[df['INDEX']<=50]

# 將每個車班資料的類別逐一定義並放進 List 中。
T = []
for num,data in enumerate(df.iterrows()):
    data = data[1]
    T.append(train(data['ID_FROM'],data['ID_TO'],data['TIME_START'],data['TIME_END'],num))

start_time = time.time()
objs = []

start = 0
end = 50
addNum = 30
nT = T[:end]
dnum = 40
while(1):
    print('========================')
    print('資訊欄')
    print('資料筆數 :',len(nT))
    print('工作班數 :',dnum)
    print('資料取樣位置 :',end)
    print('========================')
    
    x_val, num_of_crewscheduling, obj = Optimization(nT, limit=True, dnum=dnum, gap=0.5)
    start = end
    end = min(start+addNum,len(T)) 
    nT = Scheduling(nT, x_val, num_of_crewscheduling, 5, T) + T[start:end]
    for i in nT:
        i.get_value()
    dnum = min(len(nT) // 3 * 2,55) 
    if(end == start):
        break

iteration_times = 1
pass_times = 0
for i in range(100):

    print('========================')
    print('資訊欄')
    print('資料筆數 :',len(nT))
    print('工作班數 :',num_of_crewscheduling+3)
    print('第' + str(iteration_times) + '次迭代   目前經過時間 :',time.time()-start_time, ' Pass 次數 :',pass_times)
    print('========================')
    
    try:
        random.shuffle(nT)
        x_val, num_of_crewscheduling, obj = Optimization(nT[:30], limit=True, pre_obj=obj+0.01, dnum=num_of_crewscheduling+3, gap=0.3)#, time=600)
        nT = Scheduling(nT, x_val, num_of_crewscheduling, 10, T)

    except:
        pass_times += 1
    objs.append(obj)
    iteration_times += 1
print('目標函數 :',objs)
print(time.time()-start_time)