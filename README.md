# config_waveform
use python to config waveform parameters
# 配置文件说明
2026/2/13
set_ddm_phase_location包含不同分辨率
t_config = [20, 2, 20.48, 2, 6.12, 3.2, 1]   一般此项固定，分辨率之改变调频斜率
如果改动20.48（应为1.024的整数倍,6.12应随之变化），采样点数会变化，在配置函数里应该对应改变该参数和采样点数的设置
注意采样率变化时，sample_num也会发生变化


ddm_0.2m_512_384_primary.dat和ddm_0.2m_512_384_secondary.dat，配置距离分辨率0.2m、实采样512点、384个chirp的波形，配置见共享云文档
ddm_0.2m_512_384_hp_rx_primary.dat和ddm_0.2m_512_384_hp_rx_secondary.dat，配置距离分辨率0.2m、实采样512点、384个chirp的波形，滤波器设置为5/4，rx设置为0dB
ddm_0.2m_512_384_hp_primary.dat和ddm_0.2m_512_384_hp_secondary.dat，配置距离分辨率0.2m、实采样512点、384个chirp的波形，滤波器设置为5/4

ddm_0.4m_512_384_primary.dat和ddm_0.4m_512_384_secondary.dat，配置距离分辨率0.4m、实采样512点、384个chirp的波形，配置见共享云文档
ddm_0.4m_512_384_hp_primary.dat和ddm_0.4m_512_384_hp_secondary.dat，配置距离分辨率0.4m、实采样512点、384个chirp的波形，滤波器设置为5/4

ddm_ccm_0.75m_512_384_primary.dat和ddm_ccm_0.75m_512_384_secondary.dat，配置距离分辨率0.75m、实采样512点、384个chirp的跳频波形，配置见共享云文档
