import strata
from strata.CtrxHelperFunctions import CtrxHelperFunctions
import numpy as np
from strata.IData import IData
def  Carkit2c3_example_cfg(MMIC, boardName, LO_Config, rampDesignfile, MMIC_type, LOIN_Pwr_target = CtrxHelperFunctions.dBm2Qval(-2,8,7)):
    # Carkit2c3 Example Configuration:
    
    config = lambda:0
    dataProperties      = strata.IDataProperties_t()
    dataSettings        = [0, 0, 0, 0]  #Support for legacy structs
    radarInfo           = strata.IProcessingRadarInput_t()
    antennaConfig       = [strata.IfxRsp_AntennaCalibration(), strata.IfxRsp_AntennaCalibration()]
    processingConfig    = strata.IfxRsp_Stages()

    # TX configuration:
    f_static = 79.65                   # static frequency in GHz before ramp sequence starts
    f_lock = 80.988002                 # Upper frequency of the RF modulation bandwidth in GHz
    f_bw = 2.499999                    # RF modulation bandwidth in GHz
    [nmod, NCW, RampBW] = CtrxHelperFunctions.calculateFreqParam( f_lock, f_bw, f_static)

    TX1_plevel = [0, 3, 10, 20]         # power back-off level 1-4 for TX1 in dB 
    TX2_plevel = [0, 3, 10, 20]         # power back-off level 1-4 for TX2 in dB 
    TX3_plevel = [0, 3, 10, 20]         # power back-off level 1-4 for TX3 in dB 
    TX4_plevel = [0, 3, 10, 20]         # power back-off level 1-4 for TX4 in dB 
    TX1_PA_Slope_Scaling_Factor = 1     # Slope cscaling factor for TX1 
    TX2_PA_Slope_Scaling_Factor = 1     # Slope cscaling factor for TX2 
    TX3_PA_Slope_Scaling_Factor = 1     # Slope cscaling factor for TX3 
    TX4_PA_Slope_Scaling_Factor = 1     # Slope cscaling factor for TX4 

    Channel_Mask = int('1',16)          # TX channels switched on before ramp sequence starts (b0: TX1, b1: TX2, b2: TX3, b3: TX4)

    PL_Tx1 = 0              # TX1 power level index before ramp sequence starts
    PL_Tx2 = 0              # TX2 power level index before ramp sequence starts
    PL_Tx3 = 0              # TX3 power level index before ramp sequence starts
    PL_Tx4 = 0              # TX4 power level index before ramp sequence starts

    Phase_TX1_Index = 0             # TX1 phase index: Nphase_Index=round((φ[deg]*points)/360) where points = 256 
    Phase_TX2_Index = 0             # TX2 phase index: Nphase_Index=round((φ[deg]*points)/360) where points = 256 
    Phase_TX3_Index = 0             # TX3 phase index: Nphase_Index=round((φ[deg]*points)/360) where points = 256 
    Phase_TX4_Index = 0             # TX4 phase index: Nphase_Index=round((φ[deg]*points)/360) where points = 256 

    # RX configuration:
    osrSel = 2              # output sample rate: 0 (50 MS/s)
    dataWidthSel = 2        # bitwidth of HSRIF data: 2 (12bits), (Value range: 1..3 (10..14bits in 2bit steps)
    csi2DataRate = 1        # 0: 1200Mbits/s
    csi2StartMode = 0       # 0: immediately after payload segment, 1: at next payload segment
    gain = 9                # gain setting: 3 (+15dB), (Value range: 0..6 (24..6dB in 3dB steps), 7 (0dB), 9..11 (-6..-18 in 6dB steps))
    HP1 = 0                 # 0: 200kHz
    HP2 = 0                 # 0: 120kHz
    HP2En = 0               # 0: HP2 bypassed

    # Ramp configuration:
    config.sequencerFile = rampDesignfile + '.dat'  # sequencer program to download into sequencer memory
    config.nSamples = 512                          # number of samples per ramp
    config.nRampsPerTx = 384                        # number of Ramps per Tx Channel
    config.nTx = 4                                  # number of Tx channels
    # config.nRamps = config.nRampsPerTx*config.nTx   # number of ramps
    config.nRamps = config.nRampsPerTx   # number of ramps
    rampScenarioSetupAddress = 0x0      # Sequencer setup structure start address of sequencer program 

    # DMUX configuration:
    configMask = 3                          # b0: DMUX1, b1: DMUX2
    dmuxDir = [1, 1]                     # Direction of CTRX DMUX1-2 pins (0: Input, 1: Output)
    dmuxPulseDuration = [63, 63]        # Pulse duration of DMUX1-2 (0: disabled, 3..63: (n+1)*5ns)
    dmuxSignalMap = [0xA0, 0xE9]      # Example: DMUX1=0xA0: RX Payload_gate_level, DMUX2=0xE9: DMUXA_level

    # Plot configuration:
    config.plotTimeData = False                  # True: time data plots generated, false: time data plots NOT generated
    config.plotFFT1 = False                      # True: FFT1 plots generated, false: FFT1 plots NOT generated
    config.plotFFT2 = True                      # True: RD plots generated, false: RD plots NOT generated
    config.rxPlotMask = [True,True,True,True]   # mask to define, which RX channels shall be plotted [RX1,RX2,RX3,RX4]

    ## Conversion of above config values to FW command parameters:

    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx1_plvl_1'] = TX1_plevel[0] * 2**7
    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx2_plvl_1'] = TX2_plevel[0] * 2**7
    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx3_plvl_1'] = TX3_plevel[0] * 2**7
    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx4_plvl_1'] = TX4_plevel[0] * 2**7
    
    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx1_plvl_2'] = TX1_plevel[1] * 2**7
    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx2_plvl_2'] = TX2_plevel[1] * 2**7
    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx3_plvl_2'] = TX3_plevel[1] * 2**7
    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx4_plvl_2'] = TX4_plevel[1] * 2**7
    
    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx1_plvl_3'] = TX1_plevel[2] * 2**7
    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx2_plvl_3'] = TX2_plevel[2] * 2**7
    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx3_plvl_3'] = TX3_plevel[2] * 2**7
    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx4_plvl_3'] = TX4_plevel[2] * 2**7
    
    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx1_plvl_4'] = TX1_plevel[3] * 2**7
    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx2_plvl_4'] = TX2_plevel[3] * 2**7
    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx3_plvl_4'] = TX3_plevel[3] * 2**7
    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx4_plvl_4'] = TX4_plevel[3] * 2**7
    
    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx1_pa_slope_scale_fact'] = TX1_PA_Slope_Scaling_Factor * 2**8
    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx2_pa_slope_scale_fact'] = TX2_PA_Slope_Scaling_Factor * 2**8
    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx3_pa_slope_scale_fact']= TX3_PA_Slope_Scaling_Factor * 2**8
    MMIC.CTRX_FW_Cmd_Param.Configure_TX_Power['tx4_pa_slope_scale_fact']= TX4_PA_Slope_Scaling_Factor * 2**8

    MMIC.CTRX_FW_Cmd_Param.Set_TX_Output['ch_mask'] = Channel_Mask
    MMIC.CTRX_FW_Cmd_Param.Set_TX_Output['action_mask'] = 1                  # to switch on selected TX channels
    
    MMIC.CTRX_FW_Cmd_Param.Set_TX_Output['pl_tx1'] = PL_Tx1
    MMIC.CTRX_FW_Cmd_Param.Set_TX_Output['pl_tx2'] = PL_Tx2
    MMIC.CTRX_FW_Cmd_Param.Set_TX_Output['pl_tx3'] = PL_Tx3
    MMIC.CTRX_FW_Cmd_Param.Set_TX_Output['pl_tx4'] = PL_Tx4
    
    MMIC.CTRX_FW_Cmd_Param.Set_TX_Output['phase_tx1'] = Phase_TX1_Index
    MMIC.CTRX_FW_Cmd_Param.Set_TX_Output['phase_tx2'] = Phase_TX2_Index
    MMIC.CTRX_FW_Cmd_Param.Set_TX_Output['phase_tx3'] = Phase_TX3_Index
    MMIC.CTRX_FW_Cmd_Param.Set_TX_Output['phase_tx4'] = Phase_TX4_Index
    
    MMIC.CTRX_FW_Cmd_Param.Configure_RX['gain'] = gain
    MMIC.CTRX_FW_Cmd_Param.Configure_RX['hp1'] = HP1
    MMIC.CTRX_FW_Cmd_Param.Configure_RX['hp2'] = HP2
    MMIC.CTRX_FW_Cmd_Param.Configure_RX['hp2_en'] = HP2En
    MMIC.CTRX_FW_Cmd_Param.Configure_RX['data_width'] = dataWidthSel
    MMIC.CTRX_FW_Cmd_Param.Configure_RX['dec_sel'] = osrSel
    MMIC.CTRX_FW_Cmd_Param.Configure_RX['hsrif_csi2_data_rate'] = csi2DataRate
    MMIC.CTRX_FW_Cmd_Param.Configure_RX['hsrif_start_mode'] = csi2StartMode

    MMIC.CTRX_FW_Cmd_Param.Configure_Ramp_Scenario['startoffset'] = rampScenarioSetupAddress

    MMIC.CTRX_FW_Cmd_Param.Configure_RF_Frequency['nmod'] = nmod
    MMIC.CTRX_FW_Cmd_Param.Configure_RF_Frequency['ncw'] = NCW
    MMIC.CTRX_FW_Cmd_Param.Configure_RF_Frequency['bc']= 1
    MMIC.CTRX_FW_Cmd_Param.Configure_RF_Frequency['rampbw'] = RampBW

    MMIC.CTRX_FW_Cmd_Param.Configure_DMUX['config_mask'] = configMask 
    MMIC.CTRX_FW_Cmd_Param.Configure_DMUX['dmux1_dir'] = dmuxDir[0]  
    MMIC.CTRX_FW_Cmd_Param.Configure_DMUX['dmux2_dir'] = dmuxDir[1]
    MMIC.CTRX_FW_Cmd_Param.Configure_DMUX['dmux1_pulse_duration_ext'] = dmuxPulseDuration[0]
    MMIC.CTRX_FW_Cmd_Param.Configure_DMUX['dmux2_pulse_duration_ext'] = dmuxPulseDuration[1]
    MMIC.CTRX_FW_Cmd_Param.Configure_DMUX['dmux1_alt_signal'] = dmuxSignalMap[0] 
    MMIC.CTRX_FW_Cmd_Param.Configure_DMUX['dmux2_alt_signal'] = dmuxSignalMap[1] 
    
    # Configure_MMIC_Clock 
    MMIC.CTRX_FW_Cmd_Param.Configure_MMIC_Clock['clkout_source_resistance'] = 1  # 0 = 50 ohm, 1 = 40 ohm
    MMIC.CTRX_FW_Cmd_Param.Configure_MMIC_Clock['clkout_bias_voltage'] = 0       # 0 = 0V (CLKOUT connecnted to ground/VSS), 1 = 1.2V (CLKOUT connected to 1.2V/VDD)
  
    # Clear Result area
    MMIC.CTRX_FW_Cmd_Param.Clear_Results['clr_areas_msk'] = 0b00011000
   
    # Execute_Monitoring
    MMIC.CTRX_FW_Cmd_Param.Execute_Monitoring['detail_result'] = 0
    MMIC.CTRX_FW_Cmd_Param.Execute_Monitoring['nmod']= nmod
    MMIC.CTRX_FW_Cmd_Param.Execute_Monitoring['tx_ch_mask'] = 0b1111
    MMIC.CTRX_FW_Cmd_Param.Execute_Monitoring['dec_sel'] = osrSel
    MMIC.CTRX_FW_Cmd_Param.Execute_Monitoring['hp1'] = 0
    MMIC.CTRX_FW_Cmd_Param.Execute_Monitoring['hp2_en'] = 0
    if MMIC.CTRX_FW_Cmd_Param.Execute_Monitoring['hp2_en'] == 1:
        MMIC.CTRX_FW_Cmd_Param.Execute_Monitoring['hp2'] = 0
    
    MMIC.CTRX_FW_Cmd_Param.Execute_Monitoring['pl_tx1'] = PL_Tx1
    MMIC.CTRX_FW_Cmd_Param.Execute_Monitoring['phase_tx1'] = Phase_TX1_Index
    MMIC.CTRX_FW_Cmd_Param.Execute_Monitoring['pl_tx2'] = PL_Tx2
    MMIC.CTRX_FW_Cmd_Param.Execute_Monitoring['phase_tx2'] = Phase_TX2_Index
    MMIC.CTRX_FW_Cmd_Param.Execute_Monitoring['pl_tx3'] = PL_Tx3
    MMIC.CTRX_FW_Cmd_Param.Execute_Monitoring['phase_tx3'] = Phase_TX3_Index
    MMIC.CTRX_FW_Cmd_Param.Execute_Monitoring['pl_tx4'] = PL_Tx4
    MMIC.CTRX_FW_Cmd_Param.Execute_Monitoring['phase_tx4'] = Phase_TX4_Index
    #%% Additional config parameters for dedicated FW commands
    MMIC.CTRX_FW_Cmd_Param.Measure_TX['ch_mask'] = 15                        # all TX
    MMIC.CTRX_FW_Cmd_Param.Measure_TX['mode'] = 0                            # 0: PLD forward direction, 1: PLD reverse direction, 2: ADC forward power and phase 

    MMIC.CTRX_FW_Cmd_Param.Execute_Calibration['calib_sub_func_id'] = switch_case_MMICtype(MMIC_type) # enable calibration subfunctions
    MMIC.CTRX_FW_Cmd_Param.Execute_Calibration['tx_ch_pow_idx'] = 0xFFFF     # enable power calibration for all power levels at all TX channels
    MMIC.CTRX_FW_Cmd_Param.Execute_Calibration['detail_result'] = 0          # Keep this parameter set to "0" for the current RAM FW version: RAMB_A_FS1_0.6.x-alpha
    MMIC.CTRX_FW_Cmd_Param.Execute_Calibration['ref_temp_idx'] = 0           # no reference temperature. Execute_Calibration() is based only on the LimitTemp. The user has to determine both the reported MMIC temperature and the temperature after the previous calibration.
    MMIC.CTRX_FW_Cmd_Param.Execute_Calibration['limit_temp ']= 0             # Calibration shall be called if |latest temperature - reference temperature| > LimitTemp (scaled in Q12.3 format), 0: calibrate regardless of current temperature.

    MMIC.CTRX_FW_Cmd_Param.Finish_Ramp_Scenario['timeout'] = int(0.1/5e-9) # timeout in 5ns
    
    config.hsrif = 0            # 0: Csi2 , 1: LVDS
    hsrifConfig = 0b0010000110         # Default value (0b0010000111), b0: Global CRC enable (CSI-2), b1: CRC checksum calculation data word bit order(LVDS, CSI-2)... See user manual for details

    MMIC.CTRX_FW_Cmd_Param.Initialize['index'] = [18, 21, 209, 210] # 18: LVDS/CSI-2 selection, 20: Logical to Physical lane mapping, 21: HSRIF Configuration, 22: CSI2 lane enable, 209: LO config
    MMIC.CTRX_FW_Cmd_Param.Initialize['value'] = [config.hsrif, hsrifConfig, LO_Config, LOIN_Pwr_target]
    MMIC.CTRX_FW_Cmd_Param.Initialize['length'] = len(MMIC.CTRX_FW_Cmd_Param.Initialize['index'])

    osr = [50, 33.33, 25, 20, 16.67, 12.5, 10, 8.33, 6.25, 5]       # Possible RX output sample rate values in MHz/us
    config.osrValue = osr[osrSel]

    dataWidth = [10, 12, 14]                                        # Possible RX data width values in bits

    config.dmuxDir = dmuxDir

    config.dataIndex = switch_case_configDataIndex(boardName)

    config.dataWidthValue = switch_case_configDataWidth(boardName, dataWidth, dataWidthSel)

    NoRx = 4

    # configure data properties / size #CHECKED:OK
    dataProperties.format = strata.DataFormat.Q15          # [1]    set the precision format of the received time domain signals, Q15 - 16 bit signed fixed point precision - real valued data (default)
    dataProperties.rxChannels = NoRx                       # [1]    set number of (enabled) receive channels 
    dataProperties.ramps = config.nRamps                   # [1]    set total number of (used) ramp segments
    dataProperties.samples = config.nSamples               # [1]    set number of samples captured during the payload segment
    dataProperties.channelSwapping = 0                     # [1]    set channel swapping: swap adjacent pair of rx channels fed into AURIX rif interface
    dataProperties.bitWidth = dataWidth[dataWidthSel-1]    # [1]    set data bit width: 12 bit or 14 bit
    
    
    crcEnabled = True                                                     # enable (true) or disable (false) CRC
    dataSettings[0] = crcEnabled * IData.FLAGS_CRC_ENABLED

    # Setup FFT settings
    processingConfig.fftSteps = 0                                           # [1]   set option to perform a FFT on captured time data.

    processingConfig.fftFormat = strata.DataFormat.ComplexQ31               # [1]   set output data format of the FFTs, only Real* or Complex*: 'ComplexQ31' 32 bit signed fixed point precision (default) -> Re{32bit} + Imag{32bit}
    processingConfig.nciFormat = strata.DataFormat.Disabled                 # [1]   shall be set to 'Disabled' (default)
    processingConfig.virtualChannels = strata.IfxRsp.VirtualChannel.RawData # [1]   shall be set to 'RawData' (default)

    #FFT setting (first FFT)
    processingConfig.fftSettings[0].size = 0                                # 0 = default number of samples (= smallest power of 2 greater than or equal to number of samples)
    processingConfig.fftSettings[0].window = strata.IfxRsp.FftWindow.Hann   # set window function to be applied: 'Hann' (default)
    processingConfig.fftSettings[0].windowFormat = strata.DataFormat.Q31    # set format of the window function data : 'Q31' (default)
    processingConfig.fftSettings[0].exponent = 0                            # right shift of the output data: '0' no shift is performed (default)
    processingConfig.fftSettings[0].acceptedBins = 0                        # 0 = all (disable rejection), otherwise number of accepted bins from the beginning

    # INPLACE: overwrite previous stored input time data
    # DISCARD_HALF: specify whether symmetric second half of FFT should be discarded (acceptedBins has to be set to 0) - only valid if time domain signal is defined as real valued format(Q15).
    processingConfig.fftSettings[0].flags = np.bitwise_or(strata.IfxRsp.FFT_FLAGS.INPLACE, strata.IfxRsp.FFT_FLAGS.DISCARD_HALF)
 
    #FFT setting (second FFT)
    processingConfig.fftSettings[1].size = 0
    processingConfig.fftSettings[1].window = strata.IfxRsp.FftWindow.Hann   # set window function to be applied: 'Hann' (default)
    processingConfig.fftSettings[1].windowFormat = strata.DataFormat.Q31    # set format of the window function data : 'Q31' (default)
    processingConfig.fftSettings[1].exponent = 0                            # right shift of the output data: '0' no shift is performed (default)
    processingConfig.fftSettings[1].acceptedBins = 0                        # 0 = all (disable rejection), otherwise number of accepted bins from the beginning

    # INPLACE: overwrite previous stored input range FFT(0) data
    processingConfig.fftSettings[1].flags = strata.IfxRsp.FFT_FLAGS.INPLACE
    
    processingConfig.dbfSetting[0].angles = 0
    processingConfig.dbfSetting[1].angles = 0                                          
                                                                                    
    processingConfig.virtualChannels = strata.IfxRsp.VirtualChannel.RawData  # [1]   shall be set to 'RawData' (default)

    # configure/set processing (SPU)
    radarInfo.txChannels = 4                                                 # [1]    set number of (enabled) transmit channels  
    radarInfo.virtualAnt = 4                                                 # [1]    set number of virtual receive channels
    radarInfo.rampsPerTx = 512                                               # [1]    set number of (used) ramp segments

    # Note: maxRange and maxVelocity must be set properly if PeakDetection
    # is performed on Aurix.
    radarInfo.maxRange = 0                                                   # [m]    set max. (unambiguous) range acc. to selected IF bandwidth
    radarInfo.maxVelocity = 0                                                # [m/s]  set max. (unambiguous) velocity acc. to selected ramp profile

    
    return [MMIC, config, dataProperties, dataSettings, processingConfig, radarInfo]

# Helper Functions For Switch Case
def switch_case_configDataIndex(boardName):
    switcher = {
        "a2gab" : 0,
        "a2gdb" : 0,
        "crk"   : 1,
        "carkit": 0,
        "carkit2c3": 0,
        "ultrascale": 0,
        "ultrascale 4.1": 0
    }
    if boardName not in switcher:
        raise ValueError("Invalid board.")
    return switcher[boardName]

def switch_case_configDataWidth(boardName, dataWidth, dataWidthSel):
    switcher = {
        "a2gab" : 16,
        "a2gdb" : 16,
        "crk"   : 16,
        "carkit": 16,
        "carkit2c3": 16,
        "ultrascale": dataWidth[dataWidthSel-1],
        "ultrascale 4.1": dataWidth[dataWidthSel-1]
    }
    if boardName not in switcher:
        raise ValueError("Invalid board.")
    return switcher[boardName]

def switch_case_MMICtype(MMIC_type):
    switcher = {
        "Primary" : 0b001101100000000,
        "Secondary" : 0b001101100000000,
        "Standalone"   : 0b001101100000000
    }
    return switcher[MMIC_type]