import struct
# 把数据保存到dat文件
def save_to_dat(file_name, set_list):
    with open(file_name, 'wb')as fp:
        for x in set_list:
            a = struct.pack('B', int(x,16))
            fp.write(a)
    fp.close()

# 根据计算得到的数值（负数需要补码），从后往前按16进制赋值，比如0xFA0，顺序为0、A、F，分别赋值给'00','00','00','00'的后3个字符
def writeConfigValue(config_value):
    write_test = ['0','0','0','0','0','0','0','0']
    string_len = len(config_value)
    for i in range(2, string_len):
        write_test[7+i-string_len+1] = config_value[i]
    write_list = [(write_test[i] + write_test[i+1]) for i in range(0, len(write_test),2)]       # 把字符串拼接
    return write_list

# 计算频率配置参数，默认为76.05~76.99GHz，0.98GHz带宽
def calculateFreqParam(f_lock, f_bw, f_static):
        """ This function calculates the nmod from the frequency data 
        as per the formula provided in the CTRX user manual B-step.
        
        Parameters: 
            f_lock : upper boundary of DPLL frequency range in GHz
            f_bw : relative frequency range in GHz 
            f_static : static frequency between upper and lower in GHz
        
        Returns: 
            nmod value 
            NCW value
            RampBW value
        """
        NCW = round(f_lock*1000/(2**(-16) *300))*16
        nmod = round(((f_static*1000 - f_lock*1000)/(2**(-16)*300)))*16
        RampBW = round(f_bw*1000/(2**(-16) *300))*16
        if nmod < 0:
            nmod = 2**26 + nmod
        return [nmod, NCW, RampBW]

def calNCW(f_lock):
    NCW = round(f_lock*1000/(2**(-16) *300))*16
    return NCW

# 计算NTIME，chirp分段时间，单位us，NTIME = round(t(us)*200)，分辨率5ns，占用20bit，x-xx-xx
def calTime(time):
    NTIME = round(time*200)
    return NTIME

# 计算NSTART，chirp的起始频率，单位MHz，NSTART = round(f/(2**(-16) *300))*16 - NCW，分辨率4.577637kHz，占用26bit，x-xx-xx-xx
# 注意：NCW = round(f/(2**(-16) *300))*16，计算公式类似
def calStartFreq(start_freq, NCW):
    NSTART = round(start_freq*1000/(2**(-16) *300))*16 - NCW
    if NSTART < 0:
        NSTART = 2**26 + NSTART
    return NSTART

# 计算NSTEP，调频斜率，可正可负，单位MHz/us，NSTEP = round(slope/(2**(-17)*2500*6))*(2**11)，分辨率114.44092kHz/us，占用30bit，xx-xx-xx-xx
def calSlope(slope):
    NSTEP = round(slope/(2**(-17)*2500*6))*(2**11) 
    if NSTEP < 0:
        NSTEP = 2**30 + NSTEP
    return NSTEP

# 将数据拷贝到操作码中
def copyData(dst, src, start_idx):
    for i in range(0,len(src)):
        dst[start_idx+i] = src[i]