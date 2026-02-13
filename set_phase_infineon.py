import math

def phase_setting(Tx_num, band_total_num, phase_location):
    phase_value_bin = []  # 初始化列表
    for tx_idx in range(1, Tx_num+1):
        increment = 2 * 180 * (phase_location[tx_idx-1] - 1) / band_total_num * 256 / 360
        # 将计算结果添加到列表中
        phase_value_bin.append(format(round(increment),'08b'))  # 使用bin()函数转换为二进制
    
    #==========================primary======================
    phase_code_bin = ['1011']
    phase_code_bin.append('0011') # sub 0011   add 0010   set 0001
    phase_code_bin.append('00')
    phase_code_bin.append(phase_value_bin[1])  # TX2

    phase_code_bin.append('0011') # sub 0011   add 0010   set 0001
    phase_code_bin.append('00')
    phase_code_bin.append(phase_value_bin[0])  # TX1

    phase_code_bin.append('0000')
    phase_code_bin.append('0011') # sub 0011   add 0010   set 0001
    phase_code_bin.append('00')
    phase_code_bin.append(phase_value_bin[3])  # TX4

    phase_code_bin.append('0011')
    phase_code_bin.append('00')
    phase_code_bin.append(phase_value_bin[2])  # TX3

    #=========================ssecondary=================#
    phase_code_bin.append('1011')
    phase_code_bin.append('0011') # sub 0011   add 0010   set 0001
    phase_code_bin.append('00')
    phase_code_bin.append(phase_value_bin[5])  # TX2

    phase_code_bin.append('0011') # sub 0011   add 0010   set 0001
    phase_code_bin.append('00')
    phase_code_bin.append(phase_value_bin[4])  # TX1

    phase_code_bin.append('0000')
    phase_code_bin.append('0011') # sub 0011   add 0010   set 0001
    phase_code_bin.append('00')
    phase_code_bin.append(phase_value_bin[7])  # TX4

    phase_code_bin.append('0011')
    phase_code_bin.append('00')
    phase_code_bin.append(phase_value_bin[6])  # TX3
    # print(phase_code_bin)

    # phase_code = bin2hex(phase_code_bin)
    phase_code_str = ''.join(phase_code_bin) 
    phase_code_temp = hex(int(phase_code_str, 2))

    #=============
    hex_str_clean = phase_code_temp.lower().replace('0x', '')
    
    # 2. 检查长度，如果是奇数则在末尾补一个 '0'
    if len(hex_str_clean) % 2 != 0:
        hex_str_clean += '0'
    
    # 3. 按每两位分割字符串
    phase_code = [hex_str_clean[i:i+2] for i in range(0, len(hex_str_clean), 2)]


    return phase_code

if __name__ == '__main__':
    Tx_num = 8
    # band_total_num = 32
    # phase_location = [3, 4, 5, 7, 9, 12, 21, 26]
    band_total_num = 8
    phase_location = [1, 2, 3, 4, 5, 6, 7, 8]
    phase_code = phase_setting(Tx_num, band_total_num, phase_location)
    print(phase_code)
