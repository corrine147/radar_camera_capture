#%% Carkit2c3 Example
import sys
sys.path.append(r'C:\Infineon\CTRX8191-Radar-eval-kit_Strata_2.6.1\Python')
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

# -------------------------- 新增：摄像头+路径依赖 --------------------------
import os
import cv2
import time
from datetime import datetime
# -------------------------------------------------------------------------

# ------------------------------ 采集参数配置 ------------------------------
COLLECT_RADAR_DATA = True    # 雷达数据采集开关
COLLECT_CAMERA = True        # 摄像头采集开关
ADC_SAVE_PATH = "radar_adc_data"   # 雷达ADC保存目录
CAMERA_SAVE_PATH = "camera_images" # 摄像头图片保存目录
TOTAL_FRAMES = 1000             # 要采集的总帧数（默认10帧）
CAMERA_ID = 1                 # 外接摄像头设备号（内置=0）
# -----------------------------------------------------------------------------

# 自动创建保存目录
if COLLECT_RADAR_DATA and not os.path.exists(ADC_SAVE_PATH):
    os.makedirs(ADC_SAVE_PATH)
    print(f"[雷达] 自动创建保存目录：{os.path.abspath(ADC_SAVE_PATH)}")

if COLLECT_CAMERA and not os.path.exists(CAMERA_SAVE_PATH):
    os.makedirs(CAMERA_SAVE_PATH)
    print(f"[摄像头] 自动创建保存目录：{os.path.abspath(CAMERA_SAVE_PATH)}")

# ----------------------------------- 雷达基础配置 -----------------------------------
parser = argparse.ArgumentParser()
parser.add_argument('-p','--process_plot', default = "False", nargs= '?', help= '关闭后处理绘图')
args = parser.parse_args()

# Add ram FW path
sys.path.append( str(Path(filepath).parents[1]) +'/ram_fw/8191_Ram_A_Release_0.2.0')
CFWI = importlib.import_module("+CFWI")

# Connect to the board
board = strata.connection.withAutoAddress()

# Retrieve useful interfaces
[vid,pid]       = board.getVid(),board.getPid()
h               = CtrxHelperFunctions()
boardName       = BoardIdentifier.getBoardName(vid, pid)
boardExtension  = board.getBridgeSpecificInterface('CtrxP2sBoardExtension')

print(f"Strata Version: {strata.getVersion()}")
print(f"Board Image Version: {board.getVersion()}")

if(strata.getVersion() != board.getVersion()):
    warnings.warn("Strata version does not match with board image version!")

# Create Interface objects for each MMIC
MMIC_A                   = lambda:0
MMIC_A.name              = 'MMIC A'
MMIC_A.radarCtrx         = board.getIRadarCtrx(0)
MMIC_A.module            = board.getIModuleRadarCtrx(0)
MMIC_A.ipins             = MMIC_A.radarCtrx.getIPinsCtrx()
MMIC_A.ispiProt          = MMIC_A.radarCtrx.getICtrxSpiProtocol()
MMIC_A.CTRX_FW_Cmd       = CFWI.CTRX_FW_Cmd_Access(MMIC_A.radarCtrx)
MMIC_A.CTRX_FW_Cmd_Param = CFWI.CTRX_FW_Cmd_Param(MMIC_A.radarCtrx)

MMIC_B                   = lambda:0
MMIC_B.name              = 'MMIC B'
MMIC_B.radarCtrx         = board.getIRadarCtrx(1)
MMIC_B.module            = board.getIModuleRadarCtrx(1)
MMIC_B.ipins             = MMIC_B.radarCtrx.getIPinsCtrx()
MMIC_B.ispiProt          = MMIC_B.radarCtrx.getICtrxSpiProtocol()
MMIC_B.CTRX_FW_Cmd       = CFWI.CTRX_FW_Cmd_Access(MMIC_B.radarCtrx)
MMIC_B.CTRX_FW_Cmd_Param = CFWI.CTRX_FW_Cmd_Param(MMIC_B.radarCtrx)

# Config
seq_file_A = str(Path(filepath).parents[1]) +'/ramp_designs/ddm_0.732m_512_384_primary'
seq_file_B = str(Path(filepath).parents[1]) +'/ramp_designs/ddm_0.732m_512_384_secondary'

LO_config_A = 0b1111 
LO_config_B = 0b0100 

LOIN_pwr_target_A = h.dBm2Qval(-2,8,7)

[MMIC_A, config_A, dataProperties, dataSettings, processingConfig, radarInfo] = Carkit2c3_example_cfg(MMIC_A, boardName, LO_config_A, seq_file_A, 'Primary', LOIN_pwr_target_A)
[MMIC_B, config_B, dataProperties, dataSettings, processingConfig, radarInfo] = Carkit2c3_example_cfg(MMIC_B, boardName, LO_config_B, seq_file_B,'Secondary')

MMIC_A.CTRX_FW_Cmd.set_config(MMIC_A.CTRX_FW_Cmd_Param)
MMIC_B.CTRX_FW_Cmd.set_config(MMIC_B.CTRX_FW_Cmd_Param)

# Low Power - Goto Operation sequence
strata.Setup_MMIC_Operation(MMIC_A, config_A)
strata.Setup_MMIC_Operation(MMIC_B, config_B)

MMIC_A.CTRX_FW_Cmd.run_Goto_Operation()
MMIC_B.CTRX_FW_Cmd.run_Goto_Operation()

# Warm up calibration
MMIC_A.CTRX_FW_Cmd_Param.Execute_Calibration['calib_sub_func_id'] = 0b000001100011011
MMIC_B.CTRX_FW_Cmd_Param.Execute_Calibration['calib_sub_func_id'] = 0b000001100001011

MMIC_B.CTRX_FW_Cmd.run_Execute_Calibration("Execute_Directly_FW_CMD_Async_Start")
Calib_response_A = MMIC_A.CTRX_FW_Cmd.run_Execute_Calibration()
Calib_response_B = MMIC_B.CTRX_FW_Cmd.run_Execute_Calibration("Execute_Directly_FW_CMD_Async_Finish")

MMIC_A.CTRX_FW_Cmd.run_Set_TX_Output()
MMIC_B.CTRX_FW_Cmd.run_Set_TX_Output()

# 初始化摄像头 
cap = cv2.VideoCapture(CAMERA_ID, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 实时帧，无堆积
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
time.sleep(0.1)  # 预热避免首张模糊

# =============================== 循环采集多帧数据 ===========================
print(f"\n========== 开始连续采集{TOTAL_FRAMES}帧数据 ==========\n")
for i in range(1, TOTAL_FRAMES + 1):
    print(f"----- 采集第 {i}/{TOTAL_FRAMES} 帧 -----")

    # ------------------------------ 采集摄像头图片（序号_时间戳命名） --------------------------
    if COLLECT_CAMERA:

        # 拍摄并保存（命名规则：i_年日月_时分秒_毫秒.jpg）
        ret, frame = cap.read()
        if ret and frame is not None:
            # 生成毫秒级时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

            CAMERA_SAVE_PATH_temp = os.path.join(CAMERA_SAVE_PATH, f"{timestamp}")
            img_name = f"{i}.jpg"  # 如：1_20260206_163000_123.jpg
            
            img_path = os.path.join(CAMERA_SAVE_PATH, img_name)
            cv2.imwrite(img_path, frame)
            print(f"[摄像头] 第{i}帧保存成功 → {img_name}")
        else:
            print(f"[摄像头] 第{i}帧采集失败！")

        
    
    # -------------------------------- 雷达采数 -----------------------------
    # configure and start measurement
    MMIC_A.module.configure(config_A.dataIndex, 1, dataProperties, True)
    MMIC_A.module.start(config_A.dataIndex)
    MMIC_B.module.configure(config_B.dataIndex, 1, dataProperties, True)
    MMIC_B.module.start(config_B.dataIndex)

    # Start Ramp Scenario
    MMIC_B.CTRX_FW_Cmd.run_Start_Ramp_Scenario()
    MMIC_A.CTRX_FW_Cmd.run_Start_Ramp_Scenario()

    # Finish Ramp scenario
    MMIC_A.CTRX_FW_Cmd.run_Finish_Ramp_Scenario()
    MMIC_B.CTRX_FW_Cmd.run_Finish_Ramp_Scenario()

    # Get Frame Data
    Frame_1 = board.getFrame(2000)
    Frame_2 = board.getFrame(2000)

    # ----------------------------  保存雷达ADC数据（纯序号命名） --------------------------
    if COLLECT_RADAR_DATA:
        # 文件名：i_A.bin/i_B.bin（如1_A.bin、2_B.bin...）
        timestamp_adc = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        ADC_SAVE_PATH_temp = os.path.join(ADC_SAVE_PATH,  f"{timestamp_adc}")

        mmic_a_file = os.path.join(ADC_SAVE_PATH,  f"{i}_A.bin")
        mmic_b_file = os.path.join(ADC_SAVE_PATH, f"{i}_B.bin")
        
        # 转uint8二进制保存（和MATLAB格式一致）
        frame1_data = np.array(Frame_1.data, dtype=np.uint8)
        frame2_data = np.array(Frame_2.data, dtype=np.uint8)
        
        if Frame_1.virtualChannel == 0:
            with open(mmic_a_file, "wb") as fid:
                fid.write(frame1_data.tobytes())
            with open(mmic_b_file, "wb") as fid:
                fid.write(frame2_data.tobytes())
        else:
            with open(mmic_a_file, "wb") as fid:
                fid.write(frame2_data.tobytes())
            with open(mmic_b_file, "wb") as fid:
                fid.write(frame1_data.tobytes())
        print(f"[雷达] 第{i}帧保存成功 → {i}_A.bin / {i}_B.bin")

    # 释放临时帧数据
    Frame_1 = None
    Frame_2 = None

    strata.Get_Temp_Disable_TX(MMIC_A)
    strata.Get_Temp_Disable_TX(MMIC_B)
    

print(f"\n✅ {TOTAL_FRAMES}帧数据采集完成！")
# ===================== 循环采集结束 =====================
# 释放摄像头（每帧都释放，避免占用）
cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)

# --------------------------------------- 雷达后续处理 ---------------------------------
# strata.Get_Temp_Disable_TX(MMIC_A)
# strata.Get_Temp_Disable_TX(MMIC_B)

MMIC_A.CTRX_FW_Cmd_Param.Execute_Monitoring['monitoring_sub_func_id']   = 0b000001101010111 
MMIC_B.CTRX_FW_Cmd_Param.Execute_Monitoring['monitoring_sub_func_id']   = 0b000001101010111

MMIC_B.CTRX_FW_Cmd.run_Execute_Monitoring("Execute_Directly_FW_CMD_Async_Start")
Mon_response_A = MMIC_A.CTRX_FW_Cmd.run_Execute_Monitoring()
Mon_response_B = MMIC_B.CTRX_FW_Cmd.run_Execute_Monitoring("Execute_Directly_FW_CMD_Async_Finish")

MMIC_B.CTRX_FW_Cmd.run_Goto_Low_Power()
MMIC_A.CTRX_FW_Cmd.run_Goto_Low_Power()

# # 彻底关闭后处理绘图（注释所有绘图代码）
# if args.process_plot == "True":
#     strata.Plot_Frame_Data(config_A, Frame_A, 4, MMIC_A.name)
#     strata.Plot_Frame_Data(config_B, Frame_B, 4, MMIC_B.name)   
#     input('Script Finished, Waiting for Plots to load, press enter to close.')

print(f"\n========== 采集完成 ==========")
print(f"雷达数据路径：{os.path.abspath(ADC_SAVE_PATH)}")
print(f"摄像头图片路径：{os.path.abspath(CAMERA_SAVE_PATH)}")
print("雷达已进入低功耗模式，所有资源已释放！")