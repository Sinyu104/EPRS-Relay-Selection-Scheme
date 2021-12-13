# import
#from matplotlib import rc
import numpy as np
#from pylab import *
import matplotlib.pyplot as plt
import sys
import random
import math
import time



### glbal variables
class glb:
    snrdBmin = 0
    snrdBmax = 45
    snrdBinterval = 5
    num_rly = 3 #the total number of relays
    data_size = 3
    eng_size = 5
    eng_ratio = 5
    eg_eff = 0.5 # the energy efficiency of the reley
    snr_th = 3 # Obtain by channel compacity, Shannon
    report_eng = 1
    mean_snr1 = []
    mean_snr2 = []
    lsnr_num_bits = pow(10,5)
    hsnr_num_bits = pow(10,5)
    shsnr_num_bits = pow(10,6)
    num_RS_empty = 0
    num_TS_empty = 0
    trans_char = [[None for _ in range(3)] for _ in range(3)] # The range should be same as relay number
    relay_dist = [[None for _ in range(3)] for _ in range(3)] # The range should be same as relay number
    pass_loss_cf = -2
    num_no_transmit = 0
    num_no_receive = 0
    num_engbf_empty = 0
    num_or_outage = 0
    num_enter_or = 0
    num_dbrs_engbf_empty = 0
    num_no_rly_report = 0
    outage = 0
    RS = []
    TS = []
    AfterReport = []
    worthreceive = []
    worthtransmit = []
    minchargeeff = []
    mindatarly = []
    maxengrly = []
    maxdatarly = []
    steadystate = []
    eng_len = []
    recep_rly_id = 0
    trans_rly_id = 0
    N0 = 0.01

### convert decibels to absolute values ###
def db2val(db):
    return pow(10,db/10.0)

def passloss_dist_init(rlylist):
    for i in range(glb.num_rly):
        for j in range(i,glb.num_rly):
            if(i==j):
                glb.relay_dist[i][j] = dist(rlylist[i].location[0]+2, rlylist[i].location[1])
            else:
                glb.relay_dist[i][j] = dist(rlylist[i].location[0]-rlylist[j].location[0], rlylist[i].location[1]-rlylist[j].location[1]) if dist(rlylist[i].location[0]-rlylist[j].location[0], rlylist[i].location[1]-rlylist[j].location[1])>1 else 1+dist(rlylist[i].location[0]-rlylist[j].location[0], rlylist[i].location[1]-rlylist[j].location[1])
                glb.relay_dist[j][i] = glb.relay_dist[i][j]

def dist(x,y):
    return math.sqrt(x*x+y*y)

def ChannelRefresh(rlylist, Ps): # the quality of the channel is random
    Pr = Ps/glb.eng_ratio
    
    for r in rlylist:
        r.h_1 = 1/math.sqrt(2)*(np.random.normal(0,1)+np.random.normal(0,1)*1j) # rayleigh channel of 1st hop
        r.n_1 = 1/math.sqrt(2)*(np.random.normal(0,1)+np.random.normal(0,1)*1j) # whilte gaussian of 1st hop
        r.h_2 = 1/math.sqrt(2)*(np.random.normal(0,1)+np.random.normal(0,1)*1j) # rayleigh channel of 2nd hop
        r.n_2 = 1/math.sqrt(2)*(np.random.normal(0,1)+np.random.normal(0,1)*1j) # whilte gaussian of 2nd hop
        r.snr1 = Ps*pow(abs(r.h_1),2)/glb.N0
        r.snr2 = Pr*pow(abs(r.h_2),2)/glb.N0
    
    for i in range(glb.num_rly):
        for j in range(i,glb.num_rly):
            if(i==j):
                glb.trans_char[i][j] = 0
            else:
                glb.trans_char[i][j] = 1/math.sqrt(2)*(np.random.normal(0,1)+np.random.normal(0,1)*1j)
                glb.trans_char[j][i] = glb.trans_char[i][j]
    
    
    glb.mean_snr1.append(rlylist[0].snr1)
    glb.mean_snr2.append(rlylist[0].snr2)
        

class rly: # randomly setting up the relay
    def __init__(self, id):
        
        self.id = id
        self.location = [-1,0]
        self.bf = self.Buffer()
        self.h_1 = 1/math.sqrt(2)*(random.random()+random.random()*1j) # rayleigh channel of 1st hop
        self.n_1 = 1/math.sqrt(2)*(random.random()+random.random()*1j) # whilte gaussian of 1st hop
        self.h_2 = 1/math.sqrt(2)*(random.random()+random.random()*1j) # rayleigh channel of 2nd hop
        self.n_2 = 1/math.sqrt(2)*(random.random()+random.random()*1j) # whilte gaussian of 2nd hop
        self.snr1 = 0
        self.snr2 = 0
        self.chargeeff = 0

    
    def charge(self):
        if(self.bf.getEngBuffer() < self.bf.engsize):
            self.bf.Charge(pow(abs(self.h_1),2)*glb.eg_eff*glb.eng_ratio)
        else:
            return
    
    
    def consume(self):
        self.bf.Discharge(1)
    
    def trans_charge(self, trans_rly_id):
        if(self.bf.getEngBuffer() < self.bf.engsize):
            self.bf.Charge(pow(abs(glb.trans_char[self.id][trans_rly_id]),2)*glb.eg_eff)
        else:
            return
    
    def report(self):
        self.bf.Discharge(glb.report_eng)
        
    def MinSNR(self):
        return min(self.snr1, self.snr2)

    class Buffer:
        def __init__(self):
            self.datasize = glb.data_size
            self.__datalen = 1
            self.__EngBuffer = 1.0
            self.engsize = glb.eng_size

        def getDataBuffer(self):
            return self.__datalen

        def getEngBuffer(self):
            return self.__EngBuffer

        def storedata(self):
            self.__datalen += 1

        def transmitdata(self):
            self.__datalen -= 1

        def popdata(self):
            self.__datalen -= 1

        def Charge(self, eng):
            self.__EngBuffer = min(self.__EngBuffer + math.floor(eng*10)/10, self.engsize)

        def Discharge(self, eng):
            self.__EngBuffer = min(math.floor((self.__EngBuffer - eng)*10/10), self.engsize)


def setRS(rlylist):
    glb.RS.clear()
    for rly in glb.AfterReport:
        if(rly.snr1 > glb.snr_th):
            glb.RS.append(rly)
        else:
            pass
    if(len(glb.RS)==0):
        RSEmpty()
        return False
    else:
        return True

def setTS(rlylist):
    glb.TS.clear()
    for rly in glb.AfterReport: 
        
        if(rly.snr2 > glb.snr_th):
            glb.TS.append(rly)
        else:
            pass
    if(len(glb.TS)==0):
        TSEmpty()
        return False
    else:
        return True

def Receive(rlylist):
    for r in rlylist:  # transmit data to the reception reley, while the others charging
        if r.id != glb.recep_rly_id:
            r.charge()
        else:
            r.bf.storedata()

def FindMinChargeEff(rlylist):
    minCharge = 100
    for r in glb.worthreceive:
        if(r.chargeeff<minCharge):
            minCharge = r.chargeeff
    glb.minchargeeff.clear()
    for r in reversed(glb.worthreceive):
        if(r.chargeeff == minCharge):
            glb.minchargeeff.append(r)
            glb.worthreceive.remove(r)

def FindMaxEngForTrans():
    maxEng = 0
    for r in glb.maxdatarly:
        if(r.bf.getEngBuffer()>maxEng):
            maxEng = r.bf.getEngBuffer()
    glb.maxengrly.clear()
    for r in reversed(glb.maxdatarly):
        if(r.bf.getEngBuffer() == maxEng):
            glb.maxengrly.append(r)
            glb.maxdatarly.remove(r)

def FindMaxEngForRecei():
    maxEng = 0
    for r in glb.mindatarly:
        if(r.bf.getEngBuffer()>maxEng):
            maxEng = r.bf.getEngBuffer()
    glb.maxengrly.clear()
    for r in reversed(glb.mindatarly):
        if(r.bf.getEngBuffer() == maxEng):
            glb.maxengrly.append(r)
            glb.mindatarly.remove(r)
   

def SelectRecei(rlylist):
    glb.worthreceive.clear()
    for r in glb.RS:
        chargeEng = min(math.floor(r.bf.getEngBuffer() + pow(abs(r.h_1),2)*glb.eg_eff*glb.eng_ratio), r.bf.engsize)
        r.chargeeff = chargeEng - r.bf.getEngBuffer()
       
    glb.worthreceive = glb.RS.copy()
    while glb.worthreceive:
        FindMinChargeEff(rlylist)
        if(len(glb.minchargeeff)>1):
            while glb.minchargeeff:
                FindMinData()
                if(len(glb.mindatarly)>1):
                    while glb.mindatarly:
                        FindMaxEngForRecei()
                        if(len(glb.maxengrly)>1):
                            while glb.maxengrly:
                                glb.recep_rly_id = random.choice(glb.maxengrly)
                                if(glb.recep_rly_id.bf.getDataBuffer()==glb.data_size-1):
                                    glb.maxengrly.remove(glb.recep_rly_id)
                                    NoReceive()
                                    return False
                                else:
                                    glb.recep_rly_id = glb.recep_rly_id.id
                                    return True
                        else:
                            if(glb.maxengrly[0].bf.getDataBuffer()==glb.maxengrly[0].bf.datasize-1):
                                glb.maxengrly.clear()
                                NoReceive()
                                return False
                            else:
                                glb.recep_rly_id = glb.maxengrly[0].id
                                return True
                else:
                    if(glb.mindatarly[0].bf.getDataBuffer()==glb.mindatarly[0].bf.datasize-1):
                        glb.mindatarly.clear()
                        NoReceive()
                        return False
                    else:
                        glb.recep_rly_id = glb.mindatarly[0].id
                        return True
        else:
            if(glb.minchargeeff[0].bf.getDataBuffer()==glb.minchargeeff[0].bf.datasize-1):
                glb.minchargeeff.clear()
                NoReceive()
                return False
            else:
                glb.recep_rly_id = glb.minchargeeff[0].id
                return True
    
    
    
def FindMinData():
    minDatalen = 10
    glb.mindatarly.clear()
    for rly in glb.minchargeeff: 
        if(rly.bf.getDataBuffer()<minDatalen):
            minDatalen = rly.bf.getDataBuffer()
        else:
            pass
    for rly in reversed(glb.minchargeeff):
        if(rly.bf.getDataBuffer() == minDatalen):
            glb.mindatarly.append(rly)
            glb.minchargeeff.remove(rly)
def FindMaxData():
    maxDatalen = -1
    for rly in glb.worthtransmit: 
        maxDatalen = max(rly.bf.getDataBuffer(), maxDatalen)
        
    glb.maxdatarly.clear()
    for rly in reversed(glb.worthtransmit):
        if(rly.bf.getDataBuffer() == maxDatalen):
            glb.maxdatarly.append(rly)
            glb.worthtransmit.remove(rly)

def SelectTrans(rlylist):
    glb.worthtransmit.clear()
    glb.worthtransmit = glb.TS.copy()
   
    while glb.worthtransmit:
        FindMaxData()
        if(len(glb.maxdatarly)>1):
            while glb.maxdatarly:
                FindMaxEngForTrans()
                if(len(glb.maxengrly)>1):
                    while glb.maxengrly:
                        glb.trans_rly_id = random.choice(glb.maxengrly)
                        if(glb.trans_rly_id.bf.getEngBuffer()==0 or glb.trans_rly_id.bf.getDataBuffer()==0):
                            glb.maxengrly.remove(glb.trans_rly_id)
                            NoTransmit()
                            return False
                        else:
                            glb.trans_rly_id = glb.trans_rly_id.id
                            return True
                else:
                    if(glb.maxengrly[0].bf.getEngBuffer()==0 or glb.maxengrly[0].bf.getDataBuffer()==0):
                        glb.maxengrly.clear()
                        NoTransmit()
                        return False
                    else:
                        glb.trans_rly_id = glb.maxengrly[0].id
                        return True
        else:
            if(glb.maxdatarly[0].bf.getEngBuffer()==0 or glb.maxdatarly[0].bf.getDataBuffer()==0):
                glb.maxdatarly.clear()
                NoTransmit()
                return False
            else:
                glb.trans_rly_id = glb.maxdatarly[0].id
                return True
    
    
    
    

def ORSelection(rlylist):
    glb.num_enter_or += 1
    select_rly = glb.AfterReport[0] #initailize the first relay as the best selected relay
    for r in glb.AfterReport:  # doing OR selection scheme
        if(r.MinSNR()>select_rly.MinSNR()):
            select_rly = r
    if(select_rly.snr2<glb.snr_th or select_rly.snr1<glb.snr_th):
        OrOutage()
        glb.outage += 1
    for r in rlylist:  # transmit data to the reception reley, while the others charging
        if r.id != select_rly.id:
            r.charge()
        else:
            r.bf.storedata()
   
    for r in rlylist:  # transmit data to the reception reley, while the others charging
        if r.id == select_rly.id:
            r.consume()
            r.bf.transmitdata() 
        else:
            r.trans_charge(select_rly.id)
   
    
def Transmit(rlylist):
    for r in rlylist:  # transmit data to the reception reley, while the others charging
        if r.id == glb.trans_rly_id:
            r.consume()
            r.bf.transmitdata() 
        else:
            r.trans_charge(glb.trans_rly_id)
    

def ReportEng(rlylist):
    glb.AfterReport.clear()
    for r in rlylist:  # transmit data to the reception reley, while the others charging
        if r.bf.getEngBuffer()>= 2:
            r.report()
            glb.AfterReport.append(r)
        
    if(len(glb.AfterReport)==0):
        NoRlyReport()
        glb.outage += 1
        return False

    return True



def RSEmpty():
    glb.num_RS_empty += 1

def TSEmpty():
    glb.num_TS_empty += 1

def NoReceive(): 
    glb.num_no_receive += 1

def OrEngEmpty():
    glb.num_engbf_empty += 1 

def NoTransmit():    
    glb.num_no_transmit += 1 


def OrOutage():
    glb.num_or_outage += 1

def NoRlyReport():
    glb.num_no_rly_report += 1


def main():
    plist_ber = []
    outage_ber = []
    RSempty = []
    TSempty = []
    NoRlyReceive = []
    NoRlyTransmit = []
    EngBfEmpty = []
    OrOutage = []
    DBRSEngEmpty = []
    EnterOR = []
    SNR1mean = []
    SNR2mean = []
    NoReleyReport = []
    
    
    snrdBlist = range(glb.snrdBmin,glb.snrdBmax,glb.snrdBinterval) #[-5, 0, 5, 10, 15, 20, 25, 30]
    rlylist = [rly(d) for d in range(glb.num_rly)]
    for x in range(glb.num_rly):
        rlylist[x].location[1] = -1+x
    passloss_dist_init(rlylist)

    for snrdB in snrdBlist:
        glb.outage = 0
        glb.num_no_transmit = 0
        glb.num_no_receive = 0
        glb.num_engbf_empty = 0
        glb.num_or_outage = 0
        glb.num_TS_empty = 0
        glb.num_RS_empty = 0
        glb.num_enter_or = 0
        glb.num_dbrs_engbf_empty = 0
        glb.num_no_rly_report = 0
        glb.mean_snr1.clear()
        glb.mean_snr2.clear()
        Ps = db2val(snrdB) * glb.N0
        

        lsnr = 20
        hsnr = 30
        if snrdB<= lsnr:
            test_bits = glb.lsnr_num_bits
        elif snrdB> lsnr and snrdB<=hsnr:
            test_bits = glb.hsnr_num_bits
        else :
            test_bits = glb.shsnr_num_bits               
        t0 = time.time()
        for bits in range(test_bits):  #[3, ...10^5-1]  

            ChannelRefresh(rlylist, Ps) 
            
            
            if(ReportEng(rlylist)):
                if(setRS(rlylist) and setTS(rlylist)): 
                    if(SelectRecei(rlylist) and SelectTrans(rlylist)):
                        Receive(rlylist)
                        Transmit(rlylist)
                        continue
                ORSelection(rlylist)
                
            else:
                for r in rlylist:
                    r.charge()
       
        
        
        ber = (glb.outage)/float(test_bits)
        
        print("The procedure time", time.time()-t0)
        print("The SNR is ", snrdB)
        print("The rly number is ", glb.num_rly, "The data size is ", glb.data_size, "The energy size is ", glb.eng_size)
        print("The number of outage is ", glb.outage)
        print("The ber is ", ber)
        print("The number of empty RS", glb.num_RS_empty)
        print("The number of empty TS", glb.num_TS_empty)
        print("The number of no receive ", glb.num_no_receive)
        print("The number of no transmit ", glb.num_no_transmit)
        print("The number of empty energy buffer in OR", glb.num_engbf_empty)
        print("The number of entering OR selection ",glb.num_enter_or)
        print("The number of empty energy buffer in DBRS",glb.num_dbrs_engbf_empty)
        print("The number of no reley reoprt in DBRS",glb.num_no_rly_report)
        print("The number of OR outage ", glb.num_or_outage)
        print("The mean of snr1 = ", sum(glb.mean_snr1)/test_bits)
        print("The mean of snr2 = ", sum(glb.mean_snr2)/test_bits)
        print("------------------------------------------------")
        RSempty.append(glb.num_RS_empty)
        TSempty.append(glb.num_TS_empty)
        NoRlyReceive.append(glb.num_no_receive)
        NoRlyTransmit.append(glb.num_no_transmit)
        EngBfEmpty.append(glb.num_engbf_empty)
        outage_ber.append(glb.outage)
        EnterOR.append(glb.num_enter_or)
        DBRSEngEmpty.append(glb.num_dbrs_engbf_empty)
        NoReleyReport.append(glb.num_no_rly_report)
        plist_ber.append(ber)
        OrOutage.append(glb.num_or_outage)
        SNR1mean.append(sum(glb.mean_snr1)/test_bits)
        SNR2mean.append(sum(glb.mean_snr2)/test_bits)
        
    
    print('The ber is',plist_ber)
    print('The outage is',outage_ber)
    print('The RSempty',RSempty)
    print('The TSempty',TSempty)
    print('The NoRlyReceive',NoRlyReceive)
    print('The NoRlyTransmit', NoRlyTransmit)
    print('The EngBfEmpty',EngBfEmpty)
    print('The OR outage', OrOutage)
    print('The EnterOR',EnterOR)
    print('The DBRSEngEmpty', DBRSEngEmpty)
    print('The NoReleyReport', NoReleyReport)
    print('The SNR1mean', SNR1mean)
    print('The SNR2mean', SNR2mean)
    plt.semilogy(snrdBlist,plist_ber,'b--', linewidth=3)
    plt.show()
    



if __name__ == '__main__': main()
