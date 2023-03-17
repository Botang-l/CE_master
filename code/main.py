from gurobipy import*
import pandas as pd
from optimization import *
import numpy as np
import time
#定義車班類別
class train:
    def __init__(self, SS, ES, ST,ET):
        self.SS = SS
        self.ES = ES
        self.ST = ST
        self.ET = ET
    def get_value(self):
        print("； 出發站 :", self.SS, "； 到達站 :", self.ES, "； 出發時間 :", self.ST, "； 到達時間 :", self.ET)

# 讀取車班資料
df = pd.read_csv('TRA1.csv', sep=",")
#df = df[df['INDEX']<=50]

# 將每個車班資料的類別逐一定義並放進 List 中。
T = []
for data in df.iterrows():
    data = data[1]
    T.append(train(data['ID_FROM'],data['ID_TO'],data['TIME_START'],data['TIME_END']))

start_time = time.time()
objs = []
train_number = 50
print('第 1 次迭代')
x_val, num_of_crewscheduling, obj = optimization(T[:50], limit=True,gap=0.5, dnum=25)

print('第 2 次迭代   目前經過時間:',time.time()-start_time)
x_val, num_of_crewscheduling, obj = optimization(T[:80], param=x_val, number=num_of_crewscheduling, limit=True, use_param=True, reoptimization_number=10, dnum=40, gap=0.5)
print('第 3 次迭代   目前經過時間:',time.time()-start_time)
x_val, num_of_crewscheduling, obj = optimization(T[:110], param=x_val, number=num_of_crewscheduling, limit=True, use_param=True, reoptimization_number=10, dnum=55, gap=0.5)
print('第 4 次迭代   目前經過時間:',time.time()-start_time)
x_val, num_of_crewscheduling, obj = optimization(T, param=x_val, number=num_of_crewscheduling, limit=True, use_param=True, reoptimization_number=10, dnum=70, gap=0.5)
objs.append(obj)

iteration_times = 5
for i in range(1000):
    print('第' + str(iteration_times) + '次迭代   目前經過時間 :',time.time()-start_time)
    try:
        x_val, num_of_crewscheduling, obj = optimization(T, param=x_val,number=num_of_crewscheduling, limit=True, use_param=True,pre_obj=obj,reoptimization_number=10,dnum=num_of_crewscheduling+3, gap=0.03, time=600)
    except:
        pass
    objs.append(obj)
    iteration_times += 1
print('目標函數 :',objs)
print(time.time()-start_time)