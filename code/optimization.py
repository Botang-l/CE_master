from gurobipy import*
import pandas as pd
import re
import numpy as np
import random
from optimization import *

class train:
    def __init__(self, SS, ES, ST, ET,num, Children = None):
        self.SS = SS
        self.ES = ES
        self.ST = ST
        self.ET = ET
        self.num = num
        self.Children = Children
        
    
    def get_value(self):
        print("出發站 :", self.SS, "； 到達站 :", self.ES, "； 出發時間 :", self.ST, "； 到達時間 :", self.ET)
        if self.Children != None:
            print(self.Children)

def Optimization(
        T,
        limit=False,
        time=100000,
        gap=0.02,
        pre_obj=10000000,
        dnum=70,
        inum=3,
        ):

    #建構Model https://www.gurobi.com/documentation/9.5/refman/py_model2.html 
    m = Model()  # Model ( name="", env=defaultEnv )
    if(limit):
        m.Params.timelimit = time
        m.Params.MIPGap = gap
        #m.setParam('OutputFlag', 0) 

    #定義參數
    
    M = 3000 # 極大值
    OTP = 6.5 # 每分鐘加班費
    CSP = 2100 # 每日花費
    SP = 2 # 準備時間 --> SP = SSP = ESP
    AVT = 400 # 期望平均工時 400 分鐘
    dN = list(range(dnum)) # 工作班數目 
    iN = list(range(inum)) # 乘務最大值
    tN = list(range(len(T))) # 車數

    #以 addVar() 加入變數 https://www.gurobi.com/documentation/9.5/refman/py_model_addvar.html
    x_val = np.zeros((dnum*inum*len(T)))
    x = m.addVars(dN, iN, tN, vtype = GRB.BINARY, name='x') #二元變數
    st = m.addVars(dN, vtype = GRB.CONTINUOUS, name='st') # 上班時間
    et = m.addVars(dN, vtype = GRB.CONTINUOUS, name='et') # 下班時間
    ss = m.addVars(dN, vtype = GRB.CONTINUOUS, name='ss') # 上班地點
    es = m.addVars(dN, vtype = GRB.CONTINUOUS, name='es') # 下班地點
    ad = m.addVars(dN, vtype = GRB.CONTINUOUS, name='ad') # 有沒有這個工作班
    twt = m.addVars(dN, vtype = GRB.CONTINUOUS, name='twt') # 總上班時間

    #更新環境中的變量
    m.update()

    #m.setObjective()設置目標函數
    obj = 0
    for i in dN:
        obj += OTP * (twt[i]-AVT) + CSP * ad[i]
    m.setObjective(obj , GRB.MINIMIZE) 

    # m.addConstr()加入限制式
    const = 0
    for i in dN:
        const += OTP * (twt[i]-AVT) + CSP * ad[i]
    m.addConstr(const <= pre_obj) 

    # m.addConstr()加入限制式
    # constraint_1
    # 在有選第 n 個乘務的情況下才能選擇第 n+1 個乘務。
    for i in dN:
        for j in (iN[:-1]):
            const = 0
            for k in tN:
                const += x[i,j,k]
                const -= x[i,j+1,k]
            m.addConstr(const>=0)

    #constraint_2
    #確認乘務數
    for i in dN:
        const = 0
        for k in tN:
            const += x[i,0,k]
        m.addConstr(ad[i] == const)

    #constraint_3
    #旨於確保工作班排班係照工作班依序排入
    for i in dN[:-1]:
        m.addConstr(ad[i] >= ad[i+1])

    # constraint_4 and 5
    # 定義出發時間與地點 
    # 工作班的簽到時間(st[d])應等於第一個工作車次的開始執勤時間減去車次發車前準備時間。
    # 工作班的簽到地點(ss[d])應等於第一個工作車次的開始執勤地點。
    for i in dN:
        const_time = 0
        const_site = 0
        for k in tN:
            const_time += (T[k].ST - SP) * x[i,0,k]
            const_site += T[k].SS * x[i,0,k]
        m.addConstr(st[i] == const_time)
        m.addConstr(ss[i] == const_site)

    # constraint_6
    # 定義到達時間
    # 工作班的簽退時間(et[d])應該大於每個工作車次的結束執勤時間加上車次到站後準備時間。
    for i in dN:
        for j in iN:
            const = 0
            for k in tN:
                const += (T[k].ET + SP) * x[i,j,k]
            m.addConstr(et[i] >= const)

    # condytraint_7
    # 定義到達地點
    for i in dN:
        for j in iN:
            const = 0
            for k in tN:
                if(j != max(iN)):
                    const += T[k].ES * x[i,j,k] - M * (x[i,j,k] - x[i,j+1,k]) 
                else:  
                    const += T[k].ES * x[i,j,k] - M * x[i,j,k]
            const += M
            m.addConstr(es[i] <= const)

    # condytraint_8
    # 定義到達地點
    for i in dN:
        for j in iN:
            const = 0
            for k in tN:
                if (j != max(iN)):
                    const += T[k].ES * x[i,j,k] + M * (x[i,j,k] - x[i,j+1,k])    
                else:
                    const += T[k].ES * x[i,j,k] + M * x[i,j,k]
            const -= M
            m.addConstr(es[i] >= const)

    # constraint_9
    # 地點接續
    # 每個工作班的每個位置i車次的到達站必須等於第i+1位置車次的發車站。
    for i in dN:
        for j in iN[:-1]:
            const = 0
            for k in tN:
                const += T[k].SS * x[i,j+1,k]
                const -= T[k].ES * x[i,j,k] + M * x[i,j+1,k] 
            const += M
            m.addConstr(const >= 0)

    # constraint_10
    # 地點接續
    # 每個工作班的每個位置i車次的到達站必須等於第i+1位置車次的發車站。
    for i in dN:
        for j in iN[:-1]:
            const = 0
            for k in tN:
                const += T[k].SS * x[i,j+1,k]
                const -= T[k].ES * x[i,j,k] - M * x[i,j+1,k] 
            const -= M
            m.addConstr(const <= 0)

    # constraint_11
    # 一個工作班內的兩乘務時間不能重疊
    for i in dN:
        for j in iN[:-1]:
            const = 0
            for k in tN:
                const += (T[k].ST - SP) * x[i,j+1,k]
                const -= (T[k].ET + SP) * x[i,j,k] + M * x[i,j+1,k]  
            const += M
            m.addConstr(const >= 0)

    # constraint_12
    # 確保每台車都會被開到
    for k in tN:
        const = 0
        for i in dN:
            for j in iN:
                const += x[i,j,k] 
        m.addConstr(const >= 1)

    # constraint_13
    # 確保一個工作班內不會同時有多個乘務同時被執行
    for i in dN:
        for j in iN:
            const = 0
            for k in tN:
                const += x[i,j,k]
            m.addConstr(const <= 1)

    # constraint_14
    # 確保每個工作班都會在兩天內從嘉義出發並回到嘉義
    for i in dN:
        m.addConstr(es[i] == ad[i]) if(i%2) else m.addConstr(ss[i] == ad[i])

    # constraint_15 and 16
    # 確保車班連續
    for i in dN[:-1]:
        m.addConstr(ss[i+1] + M*(1-ad[i+1]) >= es[i])
        m.addConstr(ss[i+1] - M*(1-ad[i+1]) <= es[i])

    #constraint_17 and 18
    for i in dN:
        m.addConstr(et[i] - st[i] <= twt[i])
        m.addConstr(AVT <= twt[i])     
 

    # m.addConstr()加入限制式
    # constraint_extra
    # constrain_number = 0
    
    # if(number == 0):
    #     print('error')
    # elif(use_param):
    #     random_ints = random.sample(range(0, number-rescheduling), reoptimization_number-rescheduling) + list(range(number - rescheduling, number))
    #     print(random_ints)
    #     for i in dN:
    #         for j in iN:
    #             for k in tN:       
    #                 if ((i < param.shape[0]) and (j < param.shape[1]) and (k < param.shape[2])):
    #                     if ((i not in random_ints) and (param[i][j][k] == 1)):
    #                         m.addConstr(x[i,j,k] == 1)
    #                         constrain_number += 1
    
    #     print('重排的車量數:',constrain_number)

           
    m.optimize() 
    # 透過屬性varName、x顯示決策變數名字及值
    number_of_crewscheduling = 0
    for i ,v in enumerate(m.getVars()):
        if (v.varName[0] == 'x') and (v.x == 1):
            keyword = re.findall('\d+',v.varName)
            print('第', int(keyword[0])+1, '個工作班的第', int(keyword[1])+1, '個乘務之列車資訊 ====>', end= " ")
            T[int(keyword[2])].get_value()
            x_val[i] = 1
        elif (v.varName[:2] == 'ad') and (v.x == 1):
            number_of_crewscheduling += 1
         
    print('使用的工作班數 :',number_of_crewscheduling)
    print('Obj: %g' % m.objVal) 
    print('=========================')     
    return(x_val.reshape(dnum, inum, len(T)),number_of_crewscheduling,m.objVal)


def Decoder(D, List, ReferenceT):
    if (D.Children == None):
        List.append(D)
    else:
        for i in D.Children:
            List.append(ReferenceT[i])
    return (List)


def Scheduling(T, x_val, num_of_crewscheduling,random_number=5,ReferenceT=None):
    if (ReferenceT == None):
        ReferenceT = T
    random_ints = random.sample(range(0, num_of_crewscheduling), random_number)
    scheduling = []
    for i in range(x_val.shape[0]):
        branch = i in random_ints
        temp = []   
        for j in range(x_val.shape[1]):
            for k in range(x_val.shape[2]):
                if (x_val[i][j][k] == 1): 
                    if (branch):
                        scheduling = Decoder(T[k], scheduling, ReferenceT)
                    else:
                        if T[k].Children != None:
                            temp = temp + T[k].Children
                        else:
                            temp.append(T[k].num)
                    break
        if (not branch):
            if(temp == []):
                break
            else:
                start = temp[0]
                end = temp[-1]
                new_train = train(ReferenceT[start].SS, ReferenceT[end].ES, ReferenceT[start].ST, ReferenceT[end].ET, 0, temp)
                scheduling.append(new_train)
    return(list(set(scheduling)))