"""
bota_payload_utils
===========

Python bindings for the Bota Payload Utils C++ library.

Classes:
--------
BotaPayloadCompensator:
    Payload compensator block, inherits from BotaControlBlock.

    Methods:
        __init__(config_path: str)
            Initialize the compensator with a configuration file path.

        __del__()
            Destructor for the compensator.

        update(update_input_block: bool = False) -> bool
            Updates the compensator with new input data and computes compensated output.

        get_cached_output() -> BotaControlSensorSignalFrame
            Returns the most recent compensated sensor data frame.

        tare_compensated_wrench() -> bool  
            Computes and applies wrench offsets to zero the compensated output.


BotaPayloadEstimator:
    Payload estimator block, inherits from BotaControlBlock.

    Methods:
        __init__(config_path: str)
            Initialize the estimator with a configuration file path.

        __del__()
            Destructor for the estimator.

        update(update_input_block: bool = False) -> bool
            Updates the estimator with new input data and processes estimation algorithm.

        get_cached_output() -> BotaControlSensorSignalFrame
            Returns the most recent sensor data frame with estimation results.

        start_payload_estimation() -> bool  
            Starts the payload estimation process.
        
        is_estimator_running() -> bool
            Checks if the payload estimator is currently running.

        is_estimation_successful() -> bool
            Checks if the payload estimation completed successful. 

BotaControlSensorSignalFrame:   
    Represents a sensor signal frame used by the control blocks.

    Variables:
        input_block_name: str
            Name of the input block providing data.
        block_name: str
            Name of the control block.
        status: bool
            Status of the sensor data frame.
        force: List[double]
            Force vector [Fx, Fy, Fz].
        torque: List[double]
            Torque vector [Tx, Ty, Tz].
        lin_accel: List[double]
            Linear acceleration vector [Ax, Ay, Az].
        ang_vel: List[double]
            Angular velocity vector [Wx, Wy, Wz].
        temperature: double
            Temperature reading.
        timestamp: double
            Timestamp of the sensor data frame.

BotaControlBlock:
    Base class for control blocks.

    Methods:
        __init__(config_path: str)
            Initialize the control block with a configuration file path.

        __del__()
            Destructor for the control block.

        update(update_input_block: bool = False) -> bool
            Updates the control block with new input data.

        get_cached_output() -> BotaControlSensorSignalFrame
            Returns the most recent sensor data frame.            

"""

from .bota_payload_utils_ext import __doc__, BotaControlSensorSignalFrame, BotaControlBlock, BotaPayloadCompensator, BotaPayloadEstimator

from .hardware_interfaces import BotaFtSensorHWI, create_ft_sensor_hwi, create_ft_sensor_hwi_from_config

