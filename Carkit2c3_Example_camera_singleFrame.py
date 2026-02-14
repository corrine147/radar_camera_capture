#%% Carkit2c3 Example
# The following example can be executed on a Carkit Board containing
# 2 CTRX8191F and one TC39xx Aurix.
# It configures CTRX A in Primary mode, CTRX B in secondary mode 
# and performs a radar-measurement using a ramp sequence,
# which has been generated and encoded in advance by the RDT
# (Ramp Design Tool).
# It reads the time data, process 1st and 2nd FFT and generate plots 
# dependent on plot-settings.
import sys
sys.path.append(r'C:\Infineon\CTRX8191-Radar-eval-kit_Strata_2.6.1\Python')
# import sys
from pathlib import Path
filepath = Path.cwd()
sys.path.insert(0, '..')
import warnings
import importlib  
import numpy as np
import strata
from strata.BoardIdentifier import BoardIdentifier
from examples.Carkit2c3_example_cfg import Carkit2c3_example_cfg
from strata.CtrxHelperFunctions import CtrxHelperFunctions
import argparse

import os
import cv2  # 摄像头操作核心库
import time  # 时间戳同步，原代码隐含引用，显式声明更清晰
from datetime import datetime  # 生成可读时间戳，用于图片命名

from camera_capture import capture_camera_photo

parser = argparse.ArgumentParser()
parser.add_argument('-p','--process_plot', default = "True", nargs= '?', help= ' Flag for processing and plotting')
args = parser.parse_args()
# Add ram FW path
sys.path.append( str(Path(filepath).parents[1]) +'/ram_fw/8191_Ram_A_Release_0.2.0')
CFWI = importlib.import_module("+CFWI")


# -------------------------- 雷达+摄像头采集配置（复刻MATLAB） --------------------------
COLLECT_RADAR_DATA = True    # 雷达bin数据采集开关
COLLECT_CAMERA = True  # 摄像头jpg采集开关
ADC_path = "radar_data"  # ADC数据保存目录
# CAMERA_path = "camera_image"  # 摄像头保存目录
i = 1  # 采集序号，循环采集时需在脚本中做i自增（比如i = 1, 2, 3...）
CAMERA_ID = 1  # 外接摄像头设备号，内置=0
# ---------------------------------------------------------------------------------------

if COLLECT_RADAR_DATA:
    if not os.path.exists(ADC_path):
        os.makedirs(ADC_path)
        print(f"[毫米波雷达] 自动创建保存目录：{os.path.abspath(ADC_path)}")


# if COLLECT_CAMERA:
#     if not os.path.exists(CAMERA_path):
#         os.makedirs(CAMERA_path)
#         print(f"[摄像头] 自动创建保存目录：{os.path.abspath(CAMERA_path)}")

# Connect to the board. The returned BoardInstance reflects the connection
# to the board and provides access to its functionality and the device
# under test.
board = strata.connection.withAutoAddress()

#%%# Retrieve useful interfaces
[vid,pid]       = board.getVid(),board.getPid()
h               = CtrxHelperFunctions()
boardName       = BoardIdentifier.getBoardName(vid, pid)
boardExtension  = board.getBridgeSpecificInterface('CtrxP2sBoardExtension')

print(f"Strata Version: {strata.getVersion()}")
print(f"Board Image Version: {board.getVersion()}")

if(strata.getVersion() != board.getVersion()):
    warnings.warn("Strata version does not match with board image version!")
#%% Create Interface objects for each MMIC.

#  MMIC A
MMIC_A                   = lambda:0
MMIC_A.name              = 'MMIC A'
MMIC_A.radarCtrx         = board.getIRadarCtrx(0)
MMIC_A.module            = board.getIModuleRadarCtrx(0)
MMIC_A.ipins             = MMIC_A.radarCtrx.getIPinsCtrx()
MMIC_A.ispiProt          = MMIC_A.radarCtrx.getICtrxSpiProtocol()
MMIC_A.CTRX_FW_Cmd       = CFWI.CTRX_FW_Cmd_Access(MMIC_A.radarCtrx)
MMIC_A.CTRX_FW_Cmd_Param = CFWI.CTRX_FW_Cmd_Param(MMIC_A.radarCtrx)

#  MMIC B
MMIC_B                   = lambda:0
MMIC_B.name              = 'MMIC B'
MMIC_B.radarCtrx         = board.getIRadarCtrx(1)
MMIC_B.module            = board.getIModuleRadarCtrx(1)
MMIC_B.ipins             = MMIC_B.radarCtrx.getIPinsCtrx()
MMIC_B.ispiProt          = MMIC_B.radarCtrx.getICtrxSpiProtocol()
MMIC_B.CTRX_FW_Cmd       = CFWI.CTRX_FW_Cmd_Access(MMIC_B.radarCtrx)
MMIC_B.CTRX_FW_Cmd_Param = CFWI.CTRX_FW_Cmd_Param(MMIC_B.radarCtrx)

#%% Config:
# This section sets the parameters for the ram firmware commands using the
# configuration function. The ramp design file and the LO configuration are
# also set.

seq_file_A = str(Path(filepath).parents[1]) +'/ramp_designs/ddm_0.732m_512_384_primary'
seq_file_B = str(Path(filepath).parents[1]) +'/ramp_designs/ddm_0.732m_512_384_secondary'

LO_config_A = 0b1111 # Primary using LOIN 2
LO_config_B = 0b0100 # Secondary using LOIN 1 

LOIN_pwr_target_A = h.dBm2Qval(-2,8,7)

# Call a common configuration script for individual MMIC with parameters
# for settings which are changed between MMICs
[MMIC_A, config_A, dataProperties, dataSettings, processingConfig, radarInfo] = Carkit2c3_example_cfg(MMIC_A, boardName, LO_config_A, seq_file_A, 'Primary', LOIN_pwr_target_A) # configuring parameters for MMIC_A
[MMIC_B, config_B, dataProperties, dataSettings, processingConfig, radarInfo] = Carkit2c3_example_cfg(MMIC_B, boardName, LO_config_B, seq_file_B,'Secondary') # configuring parameters for MMIC_B

MMIC_A.CTRX_FW_Cmd.set_config(MMIC_A.CTRX_FW_Cmd_Param)
MMIC_B.CTRX_FW_Cmd.set_config(MMIC_B.CTRX_FW_Cmd_Param)


#%% Low Power - Goto Operation sequence

# Setup_MMIC_operation (it also contains initial RX-calibration)
strata.Setup_MMIC_Operation(MMIC_A, config_A)
strata.Setup_MMIC_Operation(MMIC_B, config_B)

# camera
# #%% -------------------------- 新增：摄像头初始化 --------------------------
# # 初始化摄像头（0为默认电脑摄像头，若外接摄像头可尝试1/2）
# cap = cv2.VideoCapture(0)
# # 检查摄像头是否成功打开
# if not cap.isOpened():
#     raise Exception("摄像头打开失败！请检查摄像头是否连接、是否被其他程序占用")
# # 设置摄像头分辨率（可选，根据硬件调整，注释则用默认）
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
# # 预留极短时间让摄像头完成曝光/对焦初始化（避免首张图片模糊）
# time.sleep(0.1)
# # -------------------------------------------------------------------------
if COLLECT_CAMERA:
    capture_camera_photo()


# Execute Goto operation for primary MMIC
MMIC_A.CTRX_FW_Cmd.run_Goto_Operation()

# Execute Goto Operation for other MMICs
MMIC_B.CTRX_FW_Cmd.run_Goto_Operation()

#%% Execute Warm up calibration, clock-triggered (LO and TX sub-calibration)

# Set Calibration sub functions 
MMIC_A.CTRX_FW_Cmd_Param.Execute_Calibration['calib_sub_func_id'] = 0b000001100011011 # PRIMARY MMIC: Lo input power 
MMIC_B.CTRX_FW_Cmd_Param.Execute_Calibration['calib_sub_func_id'] = 0b000001100001011

# Call Execute calibration for secondary MMIC using Async start
MMIC_B.CTRX_FW_Cmd.run_Execute_Calibration("Execute_Directly_FW_CMD_Async_Start")

# Execute Calibration command for Primary MMIC
Calib_response_A = MMIC_A.CTRX_FW_Cmd.run_Execute_Calibration()

# Receive Execute calibration response for secondary MMIC using Async Finish
Calib_response_B = MMIC_B.CTRX_FW_Cmd.run_Execute_Calibration("Execute_Directly_FW_CMD_Async_Finish")

# Set TX output for all MMIC to enable TX PA
MMIC_A.CTRX_FW_Cmd.run_Set_TX_Output()
MMIC_B.CTRX_FW_Cmd.run_Set_TX_Output()

#%% SEQUENCING

# configure measurement and start measurement
MMIC_A.module.configure(config_A.dataIndex, 1, dataProperties, True) # Configure the measurement. 'reorderToInterleavedFormat' is set to True by default for aurix.
MMIC_A.module.start(config_A.dataIndex) # Start the measurement

MMIC_B.module.configure(config_B.dataIndex, 1, dataProperties, True) # Configure the measurement. 'reorderToInterleavedFormat' is set to True by default for aurix.
MMIC_B.module.start(config_B.dataIndex) # Start the measurement

# Start Ramp Scenario for secondary MMICs
MMIC_B.CTRX_FW_Cmd.run_Start_Ramp_Scenario()

# Start Ramp Scenario for primary MMIC
MMIC_A.CTRX_FW_Cmd.run_Start_Ramp_Scenario()

# Finish Ramp scenario for all MMIC
MMIC_A.CTRX_FW_Cmd.run_Finish_Ramp_Scenario()
MMIC_B.CTRX_FW_Cmd.run_Finish_Ramp_Scenario()

# Get Frame Data
Frame_1 = board.getFrame(2000) # read received data (timeout = 2000msec)

Frame_2 = board.getFrame(2000) # read received data (timeout = 2000msec)

print(Frame_1)

if COLLECT_RADAR_DATA:
    mmic_a_file = os.path.join(ADC_path, f"{i}_A.bin")
    mmic_b_file = os.path.join(ADC_path, f"{i}_B.bin")
    # 转换雷达数据为uint8（原Frame.data是可迭代对象，转np.uint8保证格式一致）
    frame1_data = np.array(Frame_1.data, dtype=np.uint8)
    frame2_data = np.array(Frame_2.data, dtype=np.uint8)
    
    if  Frame_1.virtualChannel == 0:
        with open(mmic_a_file, "wb") as fid:
            fid.write(frame1_data.tobytes())
        with open(mmic_b_file, "wb") as fid:
            fid.write(frame2_data.tobytes())
    else:
        with open(mmic_a_file, "wb") as fid:
            fid.write(frame2_data.tobytes())
        with open(mmic_b_file, "wb") as fid:
            fid.write(frame1_data.tobytes())
    print(f"[雷达数据] 保存成功：{i}_A.bin / {i}_B.bin")

if Frame_1.virtualChannel == 0:
    Frame_A = np.array(Frame_1.data)
    Frame_B = np.array(Frame_2.data)
else:
    Frame_A = np.array(Frame_2.data)
    Frame_B = np.array(Frame_1.data)

Frame_1 = None
Frame_2 = None

#%% Get Temperature, Disable TX output and power down
strata.Get_Temp_Disable_TX(MMIC_A)
strata.Get_Temp_Disable_TX(MMIC_B)

#%% Execute Monitoring, clock Triggered

# Set Monitoring sub functions 
MMIC_A.CTRX_FW_Cmd_Param.Execute_Monitoring['monitoring_sub_func_id']   = 0b000001101010111 
MMIC_B.CTRX_FW_Cmd_Param.Execute_Monitoring['monitoring_sub_func_id']   = 0b000001101010111

# Call Execute Monitoring for secondary MMIC using Async start
MMIC_B.CTRX_FW_Cmd.run_Execute_Monitoring("Execute_Directly_FW_CMD_Async_Start")

# Execute Monitoring command for Primary MMIC
Mon_response_A = MMIC_A.CTRX_FW_Cmd.run_Execute_Monitoring()

# Receive Execute Monitoring response for secondary MMIC using Async Finish
Mon_response_B = MMIC_B.CTRX_FW_Cmd.run_Execute_Monitoring("Execute_Directly_FW_CMD_Async_Finish")

# Goto_Low_Power for Secondary MMICs
MMIC_B.CTRX_FW_Cmd.run_Goto_Low_Power()

# Goto_Low_power for Primary MMIC
MMIC_A.CTRX_FW_Cmd.run_Goto_Low_Power()

### Process and Plot Data for Primary MMIC:
if args.process_plot == "True":

    strata.Plot_Frame_Data(config_A, Frame_A, 4, MMIC_A.name)
    strata.Plot_Frame_Data(config_B, Frame_B, 4, MMIC_B.name)   
    input('Script Finished, Waiting for Plots to load, press enter to close.')