from gurobipy import*
import pandas as pd
import re


#建構Model https://www.gurobi.com/documentation/9.5/refman/py_model2.html 
m = Model()  # Model ( name="", env=defaultEnv )


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
df =pd.read_csv('TRA.csv', sep=",")


# 將每個車班資料的類別逐一定義並放進 List 中。
T = []
for data in df.iterrows():
    data = data[1]
    T.append(train(data['ID_FROM'],data['ID_TO'],data['TIME_START'],data['TIME_END']))


#定義參數
M = 3000 # 極大值
OTP = 6.5 # 每分鐘加班費
CSP = 2100 # 每日花費
SP = 2 # 準備時間 --> SP = SSP = ESP
AVT = 400 # 期望平均工時 400 分鐘
dN = list(range(100)) # 工作班數目 
iN = list(range(4)) # 乘務最大值
tN = list(range(len(T))) # 車數


#以 addVar() 加入變數 https://www.gurobi.com/documentation/9.5/refman/py_model_addvar.html
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


m.optimize() 
# 透過屬性varName、x顯示決策變數名字及值
for v in m.getVars():
    if (v.varName[0] == 'x') and (v.x == 1):
        keyword = re.findall('\d+',v.varName)
        print('第', int(keyword[0])+1, '個工作班的第', int(keyword[1])+1, '個乘務之列車資訊 ====>', end= " ")
        T[int(keyword[2])].get_value()
    #print(v.varName, v.x)
# 透過屬性objVal顯示最佳解
print('Obj: %g' % m.objVal)

