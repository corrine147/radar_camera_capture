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
parser = argparse.ArgumentParser()
parser.add_argument('-p','--process_plot', default = "True", nargs= '?', help= ' Flag for processing and plotting')
args = parser.parse_args()
# Add ram FW path
sys.path.append( str(Path(filepath).parents[1]) +'/ram_fw/8191_Ram_A_Release_0.2.0')
CFWI = importlib.import_module("+CFWI")

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

seq_file_A = str(Path(filepath).parents[1]) +'/ramp_designs/ddm_0.2m_512_384_primary_phase_post'
seq_file_B = str(Path(filepath).parents[1]) +'/ramp_designs/ddm_0.2m_512_384_secondary_phase_post'

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