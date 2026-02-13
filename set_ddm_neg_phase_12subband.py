import header as hd
# 配置基础DDM波形，使用两次循环配置移相码(后续均采样这种方式)，使用8个子带和相位码（或配成同样的相位码），8个子带配置成加移向值

# 设置参数，t0~t6,slope1,slope2,NSTART
# 这一组对应0.2m分辨率,512个采样点，384个chirp，注意修改采样数和chirp数
t_config = [20, 2, 20.48, 2, 6.12, 3.2, 1]            # 0.2m
slope1 = 36.5
primary_file_name = "C:/Infineon/set_code/congfig_file/ddm_0.2m_512_256_neg_phase_8_test_primary.dat"
secondary_file_name = "C:/Infineon/set_code/congfig_file/ddm_0.2m_512_256_neg_phase_8_test_secondary.dat"

NSTEP1 = hd.calSlope(slope1)
NSTEP2 = -4*NSTEP1
if NSTEP2 < 0:
    NSTEP2 = 2**30 + NSTEP2
f_lock = 77.00
NCW = hd.calNCW(f_lock)
start_freq = 76.001
NSTART = hd.calStartFreq(start_freq, NCW)

ddm_words = []
# 序列器结构
setup_words = ['31','00','00','20',                         # word0~word5，setup，word6~7无用
             '00','00','00','00',
             '00','00','00','00',
             '00','00','00','00',        
             '00','00','00','00',
             '00','00','00','00',
             '00','00','00','00',
             '00','00','00','00']
ddm_words.append(setup_words)

# 循环开始前的等待操作码
wait_code_words = ['C4','02','00','00']                     # 等待操作码，8
ddm_words.append(wait_code_words)

# 循环开始前的等待段，设置时长
wait_seg_code_words1 = ['47','80','00','00',                # 等待段分段操作码，9~14
                        '00','00','00','00',                # 参数，NTIME，10
                        '03','80','A3','D0',                # 参数，NSTART，11
                        '00','00','00','00',                # 参数，NSTEP，12
                        '00','01','00','00',                # 参数，CONFIG0，13  
                        '10','00','00','00']                # 参数，CONFIG1，14
wait_time = t_config[0]                                     # 20us，t0
NTIME = hd.calTime(wait_time)
wait_time_hex = hd.writeConfigValue(hex(NTIME))
hd.copyData(wait_seg_code_words1, wait_time_hex, 4)
ddm_words.append(wait_seg_code_words1)

# 循环操作码，设置循环次数，0x0180->384,0x0008->8,0x0020->32
loop_code_words1 = ['E0','01','00','20']                    # 循环操作码，开始循环，外部循环
ddm_words.append(loop_code_words1)

# 修改相位操作码1，用于设置初始相位
modify_phase_code_words1 =  ['B1','00','04','00',           # 修改相位操作码，设置初始相位，15~16
                            '01','00','04','00']
ddm_words.append(modify_phase_code_words1)

# 循环操作码，设置循环次数，0x0180->384,0x0008->8,0x0020->32
loop_code_words1 = ['E0','01','00','08']                    # 循环操作码，开始循环，内部循环
ddm_words.append(loop_code_words1)

# 预负载段，设置时长，起始频率和调频斜率
pre_seg_code_words = ['47','80','00','00',                  # 预负载段分段操作码，预负载段，18~23
                      '00','00','01','90',                  # 参数，NTIME，19
                      '03','80','A3','E0',                  # 参数，NSTART，20
                      '00','1B','50','00',                  # 参数，NSTEP，21
                      '00','03','04','00',                  # 参数，CONFIG0，22
                      '10','00','00','0F']                  # 参数，CONFIG1，23
pre_time = t_config[1]                                      # t1
NTIME = hd.calTime(pre_time)
pre_time_hex = hd.writeConfigValue(hex(NTIME))
hd.copyData(pre_seg_code_words, pre_time_hex, 4)

start_freq_hex = hd.writeConfigValue(hex(NSTART))
hd.copyData(pre_seg_code_words, start_freq_hex, 8)

slope1_hex = hd.writeConfigValue(hex(NSTEP1))
hd.copyData(pre_seg_code_words, slope1_hex, 12)
ddm_words.append(pre_seg_code_words)

# 修改相位操作码2，用于设置每个chirp的循环相位码，这里不分子带
# modify_phase_code_words2 = ['B1','00','04','00',            # 修改相位操作码，设置循环相位，24~25
#                             '01','00','04','00']

# 修改相位操作码2，用于设置每个chirp的循环相位码，这里分8个子带
# modify_phase_code_words2 = ['B2','08','04','00',            # 修改相位操作码，设置循环相位，24~25
#                             '02','18','08','40']

# ddm_words.append(modify_phase_code_words2)

# 有效负载段，设置时长
payload_seg_code_words = ['46','00','00','00',              # 有效负载段分段操作码，26~29
                          '00','00','10','00',              # 参数，NTIME，27
                          '00','00','C5','00',              # 参数，CONFIG0，28
                          '10','00','00','0F']              # 参数，CONFIG1，29
payload_time = t_config[2]                                  # t2
NTIME = hd.calTime(payload_time)
payload_time_hex = hd.writeConfigValue(hex(NTIME))
hd.copyData(payload_seg_code_words, payload_time_hex, 4)
ddm_words.append(payload_seg_code_words)

# 修改相位操作码2，用于设置每个chirp的循环相位码，这里分8个子带
# modify_phase_code_words2 = ['B2','08','04','00',            # 修改相位操作码，设置循环相位，24~25  8子带
#                             '02','18','08','40']
modify_phase_code_words2 = ['B3','05','44','00',            # 修改相位操作码，设置循环相位，24~25 12子带
                            '03','10','0C','2B']
ddm_words.append(modify_phase_code_words2)


# 后负载段，设置时长
post_seg_code_words =  ['46','00','00','00',                # 后负载段分段操作码，30~33
                        '00','00','00','08',                # 参数，NTIME，31
                        '00','00','05','00',                # 参数，CONFIG0，32
                        '10','00','00','0F']                # 参数，CONFIG1，33]
post_time = t_config[3]                                     # t3
NTIME = hd.calTime(post_time)
post_time_hex = hd.writeConfigValue(hex(NTIME))
hd.copyData(post_seg_code_words, post_time_hex, 4)
ddm_words.append(post_seg_code_words)

# 返回负载段，设置时长和调频斜率
fb_seg_code_words = ['47','00','00','00',                   # 返回负载段分段操作码，34~38
                     '00','00','00','C8',                   # 参数，NTIME，35
                     '3D','99','98','00',                   # 参数，NSTEP，36
                     '00','B0','00','0F',                   # 参数，CONFIG0，37
                     '10','00','00','0F']                   # 参数，CONFIG1，38]
fb_time = t_config[4]                                       # t4
NTIME = hd.calTime(fb_time)
fb_time_hex = hd.writeConfigValue(hex(NTIME))
hd.copyData(fb_seg_code_words, fb_time_hex, 4)

slope2_hex = hd.writeConfigValue(hex(NSTEP2))
hd.copyData(fb_seg_code_words, slope2_hex, 12)
ddm_words.append(fb_seg_code_words)

# 等待段，设置时长
wait_seg_code_words2 = ['47','00','00','00',                # 等待段分段操作码，，39~43
                        '00','00','02','5C',                # 参数，NTIME，40
                        '00','00','00','00',                # 参数，NSTEP，41
                        '00','B0','00','0F',                # 参数，CONFIG0，42
                        '10','00','00','0F']                # 参数，CONFIG1，43]
wait_time = t_config[5]                                     # t5
NTIME = hd.calTime(wait_time)
wait_time_hex = hd.writeConfigValue(hex(NTIME))
hd.copyData(wait_seg_code_words2, wait_time_hex, 4)
ddm_words.append(wait_seg_code_words2)

# 循环结束
loop_code_words2 = ['E0','02','00','00']                    # 循环操作码，结束内部循环
ddm_words.append(loop_code_words2)

# 循环结束
loop_code_words2 = ['E0','02','00','00']                    # 循环操作码，结束外部循环
ddm_words.append(loop_code_words2)

# 等待段，设置时长
wait_seg_code_words3 = ['47','00','00','00',                # 分段操作码，等待段，45~49
                        '00','00','00','C8',                # 参数，NTIME，46
                        '00','00','00','00',                # 参数，NSTEP，47
                        '00','B0','00','00',                # 参数，CONFIG0，48
                        '00','00','00','00']                # 参数，CONFIG1，49
wait_time = t_config[6]                                     # t6
NTIME = hd.calTime(wait_time)
wait_time_hex = hd.writeConfigValue(hex(NTIME))
hd.copyData(wait_seg_code_words3, wait_time_hex, 4)
ddm_words.append(wait_seg_code_words3)

# 结束操作码
last_code_words = ['FF','FF','FF','FF']                     # 终止操作码，50
ddm_words.append(last_code_words)

# 将数据重新组合，便于写入文件
primary_list = []
for i in range(0,len(ddm_words)):
    for j in range(0,len(ddm_words[i])):
        primary_list.append(ddm_words[i][j])
hd.save_to_dat(primary_file_name, primary_list)

# 给从雷达配置参数
secondary_list = primary_list
for i in range(0,len(secondary_list)):
    if secondary_list[i] == 'C4':
        secondary_list[i] = 'C0'                            # 同步方式与主雷达不同
    if secondary_list[i] == 'B3':                           # 从芯片相位设置
        secondary_list[i+1] = '1A'                          
        secondary_list[i+2] = 'CC'
        secondary_list[i+3] = '55'
        secondary_list[i+4] = '02'
        secondary_list[i+5] = '1A'
        secondary_list[i+6] = 'CC'
        secondary_list[i+7] = '80'
hd.save_to_dat(secondary_file_name, secondary_list)