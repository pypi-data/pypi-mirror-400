#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   robot.py
@Time    :   2025/12/16 16:39:44
@Author  :   Wei Lindong
@Version :   1.0
@Desc    :   双臂机器人控制接口
'''

from typing import Optional, List, Dict, Tuple, Union
from .arm import Arm
from .exceptions import (
    CANInitializationError,
    InvalidMotorIDError,
    InvalidModeError
)
from ._lib.log_utils import log_output
import time

class Robot:
    """
    双臂机器人控制类

    管理左右两条机械臂，提供统一的控制接口。

    属性:
        left_arm (Arm): 左臂控制对象
        right_arm (Arm): 右臂控制对象

    示例:
        >>> robot = Robot(left_can_channel='can0', right_can_channel='can1')
        >>> robot.enable_all()
        >>> robot.set_mode_all('mit')
        >>> robot.move_all_to_zero_mit(kp=5.0, kd=0.5)
    """

    def __init__(self,
                 right_can_channel: str = 'can0',
                 left_can_channel: str = 'can1',
                 motor_ids: Optional[List[int]] = None,
                 auto_enable_can: bool = True,
                 bitrate: int = 1000000,
                 password: Optional[str] = None,
                 log=None,
                 **kwargs):
        """
        初始化双臂机器人

        参数:
            left_can_channel (str): 左臂 CAN 通道 (默认: 'can0')
            right_can_channel (str): 右臂 CAN 通道 (默认: 'can1')
            motor_ids (List[int], optional): 电机ID列表 (默认: [1,2,3,4,5,6,7,8])
            auto_enable_can (bool): 是否自动启用 CAN 接口 (默认: True)
            bitrate (int): CAN 波特率 (默认: 1000000)
            password (str, optional): sudo密码，用于自动启用CAN接口，默认 None（手动输入密码）
            log (callable, optional): 日志函数
            **kwargs: 传递给 Arm 的其他参数

        异常:
            CANInitializationError: CAN 总线初始化失败
        """
        self.right_can_channel = right_can_channel
        self.left_can_channel = left_can_channel
        self.log = log

        # 初始化左右臂（Arm 类会自动检测并启用 CAN 接口）
        self.right_arm = Arm(
            can_channel=right_can_channel,
            side='right',
            motor_ids=motor_ids,
            auto_enable_can=auto_enable_can,
            bitrate=bitrate,
            password=password,
            log=log,
            **kwargs
        )
        self.left_arm = Arm(
            can_channel=left_can_channel,
            side='left',
            motor_ids=motor_ids,
            auto_enable_can=auto_enable_can,
            bitrate=bitrate,
            password=password,
            log=log,
            **kwargs
        )
        
        # 机械臂列表（便于批量操作）
        self.arms = [self.right_arm, self.left_arm]
        self.arm_names = ['右臂', '左臂']

    def __enter__(self):
        """支持 with 语句"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出时自动关闭"""
        self.shutdown()

    def shutdown(self):
        """关闭所有 CAN 总线连接"""
        for arm in self.arms:
            try:
                arm.close()
            except:
                pass

    # ==================== 使能/失能控制 ====================

    def enable_all(self, motor_ids: Optional[List[int]] = None,
                   verbose: bool = False,
                   timeout: float = 1.0,
                   progress_callback=None):
        """
        使能所有机械臂的所有电机

        参数:
            motor_ids (List[int], optional): 指定电机ID列表，默认为所有电机
            verbose (bool): 是否打印详细信息
            timeout (float): 每个电机的超时时间（秒）
            progress_callback (callable, optional): 进度回调函数
                格式: callback(arm_name, motor_id, success, error_msg, exec_time)
                - arm_name: 'right' 或 'left'
                - motor_id: 电机ID
                - success: True/False
                - error_msg: 错误信息（成功时为None）
                - exec_time: 执行时间（秒）

        返回:
            dict: {
                'summary': {
                    'total': 总数,
                    'success': 成功数,
                    'failed': 失败数,
                    'total_time': 总耗时
                },
                'details': {
                    'right': {motor_id: {'success': bool, 'error': str, 'time': float}, ...},
                    'left': {motor_id: {'success': bool, 'error': str, 'time': float}, ...}
                }
            }

        示例:
            >>> def callback(arm, mid, success, error, time):
            >>>     print(f"{arm} - Motor {mid}: {'✓' if success else '✗'} ({time:.3f}s)")
            >>>
            >>> results = robot.enable_all(progress_callback=callback)
            >>> print(f"成功: {results['summary']['success']}/{results['summary']['total']}")
        """
        import time as time_module

        results = {
            'summary': {'total': 0, 'success': 0, 'failed': 0, 'total_time': 0},
            'details': {'right': {}, 'left': {}}
        }

        start_total = time_module.time()

        for arm, arm_name in zip(self.arms, ['right', 'left']):
            ids = motor_ids if motor_ids is not None else arm.motor_ids

            for motor_id in ids:
                results['summary']['total'] += 1
                start_time = time_module.time()
                success = False
                error_msg = None

                try:
                    state = arm.enable(motor_id, timeout=timeout, verbose=verbose)
                    success = (state == 0)
                    if not success:
                        error_msg = f"Enable returned state {state}"
                except Exception as e:
                    success = False
                    error_msg = f"Exception: {str(e)}"

                exec_time = time_module.time() - start_time

                # 记录结果
                results['details'][arm_name][motor_id] = {
                    'success': success,
                    'error': error_msg,
                    'time': exec_time
                }

                if success:
                    results['summary']['success'] += 1
                else:
                    results['summary']['failed'] += 1

                # 回调通知
                if progress_callback:
                    try:
                        progress_callback(arm_name, motor_id, success, error_msg, exec_time)
                    except Exception as e:
                        log_output(f"Callback error: {e}", "WARNING", self.log)
                time.sleep(0.01)
        results['summary']['total_time'] = time_module.time() - start_total
        return results

    def disable_all(self, motor_ids: Optional[List[int]] = None,
                    verbose: bool = False,
                    timeout: float = 1.0,
                    progress_callback=None):
        """
        失能所有机械臂的所有电机

        参数:
            motor_ids (List[int], optional): 指定电机ID列表，默认为所有电机
            verbose (bool): 是否打印详细信息
            timeout (float): 每个电机的超时时间（秒）
            progress_callback (callable, optional): 进度回调函数
                格式: callback(arm_name, motor_id, success, error_msg, exec_time)

        返回:
            dict: 详细结果字典（格式同 enable_all）
        """
        import time as time_module

        results = {
            'summary': {'total': 0, 'success': 0, 'failed': 0, 'total_time': 0},
            'details': {'right': {}, 'left': {}}
        }

        start_total = time_module.time()

        for arm, arm_name in zip(self.arms, ['right', 'left']):
            ids = motor_ids if motor_ids is not None else arm.motor_ids

            for motor_id in ids:
                results['summary']['total'] += 1
                start_time = time_module.time()
                success = False
                error_msg = None

                try:
                    state = arm.disable(motor_id, timeout=timeout, verbose=verbose)
                    success = (state == 0)
                    if not success:
                        error_msg = f"Disable returned state {state}"
                except Exception as e:
                    success = False
                    error_msg = f"Exception: {str(e)}"

                exec_time = time_module.time() - start_time

                # 记录结果
                results['details'][arm_name][motor_id] = {
                    'success': success,
                    'error': error_msg,
                    'time': exec_time
                }

                if success:
                    results['summary']['success'] += 1
                else:
                    results['summary']['failed'] += 1

                # 回调通知
                if progress_callback:
                    try:
                        progress_callback(arm_name, motor_id, success, error_msg, exec_time)
                    except Exception as e:
                        log_output(f"Callback error: {e}", "WARNING", self.log)
                time.sleep(0.01)
        results['summary']['total_time'] = time_module.time() - start_total
        return results

    def enable_left(self, motor_ids: Optional[List[int]] = None,
                    verbose: bool = False,
                    timeout: float = 1.0,
                    progress_callback=None):
        """
        使能左臂所有电机

        参数:
            motor_ids (List[int], optional): 指定电机ID列表
            verbose (bool): 是否打印详细信息
            timeout (float): 每个电机的超时时间（秒）
            progress_callback (callable, optional): 进度回调函数

        返回:
            dict: 详细结果字典
        """
        import time as time_module

        results = {
            'summary': {'total': 0, 'success': 0, 'failed': 0, 'total_time': 0},
            'details': {}
        }

        start_total = time_module.time()
        ids = motor_ids if motor_ids else self.left_arm.motor_ids

        for motor_id in ids:
            results['summary']['total'] += 1
            start_time = time_module.time()
            success = False
            error_msg = None

            try:
                state = self.left_arm.enable(motor_id, timeout=timeout, verbose=verbose)
                success = (state == 0)
                if not success:
                    error_msg = f"Enable returned state {state}"
            except Exception as e:
                success = False
                error_msg = f"Exception: {str(e)}"

            exec_time = time_module.time() - start_time

            results['details'][motor_id] = {
                'success': success,
                'error': error_msg,
                'time': exec_time
            }

            if success:
                results['summary']['success'] += 1
            else:
                results['summary']['failed'] += 1

            if progress_callback:
                try:
                    progress_callback('left', motor_id, success, error_msg, exec_time)
                except Exception as e:
                    log_output(f"Callback error: {e}", "WARNING", self.log)
            time.sleep(0.01)
        results['summary']['total_time'] = time_module.time() - start_total
        return results

    def enable_right(self, motor_ids: Optional[List[int]] = None,
                     verbose: bool = False,
                     timeout: float = 1.0,
                     progress_callback=None):
        """
        使能右臂所有电机

        参数:
            motor_ids (List[int], optional): 指定电机ID列表
            verbose (bool): 是否打印详细信息
            timeout (float): 每个电机的超时时间（秒）
            progress_callback (callable, optional): 进度回调函数

        返回:
            dict: 详细结果字典
        """
        import time as time_module

        results = {
            'summary': {'total': 0, 'success': 0, 'failed': 0, 'total_time': 0},
            'details': {}
        }

        start_total = time_module.time()
        ids = motor_ids if motor_ids else self.right_arm.motor_ids

        for motor_id in ids:
            results['summary']['total'] += 1
            start_time = time_module.time()
            success = False
            error_msg = None

            try:
                state = self.right_arm.enable(motor_id, timeout=timeout, verbose=verbose)
                success = (state == 0)
                if not success:
                    error_msg = f"Enable returned state {state}"
            except Exception as e:
                success = False
                error_msg = f"Exception: {str(e)}"

            exec_time = time_module.time() - start_time

            results['details'][motor_id] = {
                'success': success,
                'error': error_msg,
                'time': exec_time
            }

            if success:
                results['summary']['success'] += 1
            else:
                results['summary']['failed'] += 1

            if progress_callback:
                try:
                    progress_callback('right', motor_id, success, error_msg, exec_time)
                except Exception as e:
                    log_output(f"Callback error: {e}", "WARNING", self.log)
            time.sleep(0.01)
        results['summary']['total_time'] = time_module.time() - start_total
        return results

    def disable_left(self, motor_ids: Optional[List[int]] = None,
                     verbose: bool = False,
                     timeout: float = 1.0,
                     progress_callback=None):
        """
        失能左臂所有电机

        参数:
            motor_ids (List[int], optional): 指定电机ID列表
            verbose (bool): 是否打印详细信息
            timeout (float): 每个电机的超时时间（秒）
            progress_callback (callable, optional): 进度回调函数

        返回:
            dict: 详细结果字典
        """
        import time as time_module

        results = {
            'summary': {'total': 0, 'success': 0, 'failed': 0, 'total_time': 0},
            'details': {}
        }

        start_total = time_module.time()
        ids = motor_ids if motor_ids else self.left_arm.motor_ids

        for motor_id in ids:
            results['summary']['total'] += 1
            start_time = time_module.time()
            success = False
            error_msg = None

            try:
                state = self.left_arm.disable(motor_id, timeout=timeout, verbose=verbose)
                success = (state == 0)
                if not success:
                    error_msg = f"Disable returned state {state}"
            except Exception as e:
                success = False
                error_msg = f"Exception: {str(e)}"

            exec_time = time_module.time() - start_time

            results['details'][motor_id] = {
                'success': success,
                'error': error_msg,
                'time': exec_time
            }

            if success:
                results['summary']['success'] += 1
            else:
                results['summary']['failed'] += 1

            if progress_callback:
                try:
                    progress_callback('left', motor_id, success, error_msg, exec_time)
                except Exception as e:
                    log_output(f"Callback error: {e}", "WARNING", self.log)
            time.sleep(0.01)
        results['summary']['total_time'] = time_module.time() - start_total
        return results

    def disable_right(self, motor_ids: Optional[List[int]] = None,
                      verbose: bool = False,
                      timeout: float = 1.0,
                      progress_callback=None):
        """
        失能右臂所有电机

        参数:
            motor_ids (List[int], optional): 指定电机ID列表
            verbose (bool): 是否打印详细信息
            timeout (float): 每个电机的超时时间（秒）
            progress_callback (callable, optional): 进度回调函数

        返回:
            dict: 详细结果字典
        """
        import time as time_module

        results = {
            'summary': {'total': 0, 'success': 0, 'failed': 0, 'total_time': 0},
            'details': {}
        }

        start_total = time_module.time()
        ids = motor_ids if motor_ids else self.right_arm.motor_ids

        for motor_id in ids:
            results['summary']['total'] += 1
            start_time = time_module.time()
            success = False
            error_msg = None

            try:
                state = self.right_arm.disable(motor_id, timeout=timeout, verbose=verbose)
                success = (state == 0)
                if not success:
                    error_msg = f"Disable returned state {state}"
            except Exception as e:
                success = False
                error_msg = f"Exception: {str(e)}"

            exec_time = time_module.time() - start_time

            results['details'][motor_id] = {
                'success': success,
                'error': error_msg,
                'time': exec_time
            }

            if success:
                results['summary']['success'] += 1
            else:
                results['summary']['failed'] += 1

            if progress_callback:
                try:
                    progress_callback('right', motor_id, success, error_msg, exec_time)
                except Exception as e:
                    log_output(f"Callback error: {e}", "WARNING", self.log)
            time.sleep(0.01)
        results['summary']['total_time'] = time_module.time() - start_total
        return results

    # ==================== 模式设置 ====================

    def set_mode_all(self, mode: str,
                     motor_ids: Optional[List[int]] = None,
                     verbose: bool = False,
                     timeout: float = 1.0,
                     progress_callback=None):
        """
        设置所有机械臂的控制模式

        参数:
            mode (str): 控制模式 ('mit', 'csp', 'pp', 'speed', 'current')
            motor_ids (List[int], optional): 指定电机ID列表
            verbose (bool): 是否打印详细信息
            timeout (float): 每个电机的超时时间（秒）
            progress_callback (callable, optional): 进度回调函数

        返回:
            dict: 详细结果字典（格式同 enable_all）
        """
        import time as time_module

        results = {
            'summary': {'total': 0, 'success': 0, 'failed': 0, 'total_time': 0},
            'details': {'right': {}, 'left': {}}
        }

        start_total = time_module.time()

        for arm, arm_name in zip(self.arms, ['right', 'left']):
            ids = motor_ids if motor_ids is not None else arm.motor_ids

            for motor_id in ids:
                results['summary']['total'] += 1
                start_time = time_module.time()
                success = False
                error_msg = None

                try:
                    state = arm.set_mode(mode, motor_id, timeout=timeout, verbose=verbose)
                    success = (state == 0)
                    if not success:
                        error_msg = f"Set mode returned state {state}"
                except Exception as e:
                    success = False
                    error_msg = f"Exception: {str(e)}"

                exec_time = time_module.time() - start_time

                results['details'][arm_name][motor_id] = {
                    'success': success,
                    'error': error_msg,
                    'time': exec_time
                }

                if success:
                    results['summary']['success'] += 1
                else:
                    results['summary']['failed'] += 1

                if progress_callback:
                    try:
                        progress_callback(arm_name, motor_id, success, error_msg, exec_time)
                    except Exception as e:
                        log_output(f"Callback error: {e}", "WARNING", self.log)
                time.sleep(0.01)
        results['summary']['total_time'] = time_module.time() - start_total
        return results

    def set_mode_left(self, mode: str, motor_ids: Optional[List[int]] = None):
        """设置左臂控制模式"""
        ids = motor_ids if motor_ids else self.left_arm.motor_ids
        for motor_id in ids:
            self.left_arm.set_mode(motor_id, mode, True)
            time.sleep(0.01)

    def set_mode_right(self, mode: str, motor_ids: Optional[List[int]] = None):
        """设置右臂控制模式"""
        ids = motor_ids if motor_ids else self.right_arm.motor_ids
        for motor_id in ids:
            self.right_arm.set_mode(motor_id, mode)
            time.sleep(0.01)

    # ==================== MIT 模式控制 ====================
    def move_joints_mit(self,
                       left_positions: Optional[List[float]] = None,
                       right_positions: Optional[List[float]] = None,
                       kp: Union[float, List[float]] = 5.0,
                       kd: Union[float, List[float]] = 0.5):
        """
        同时控制左右臂关节位置 (MIT模式)

        参数:
            left_positions (List[float], optional): 左臂各关节位置 [pos1, pos2, ...]
            right_positions (List[float], optional): 右臂各关节位置
            kp (float or List[float]): 位置增益，可以是单个值（所有电机使用相同值）或列表（每个电机使用对应值）
            kd (float or List[float]): 速度增益，可以是单个值（所有电机使用相同值）或列表（每个电机使用对应值）

        示例:
            >>> # 左右臂对称运动，所有电机使用相同的kp和kd
            >>> robot.move_joints_mit(
            >>>     left_positions=[0.1, 0.2, 0.3, 0.4, 0, 0, 0],
            >>>     right_positions=[0.1, 0.2, 0.3, 0.4, 0, 0, 0],
            >>>     kp=10.0, kd=1.0
            >>> )
            >>>
            >>> # 每个电机使用不同的kp和kd值
            >>> robot.move_joints_mit(
            >>>     left_positions=[0.1, 0.2, 0.3, 0.4, 0, 0, 0],
            >>>     right_positions=[0.1, 0.2, 0.3, 0.4, 0, 0, 0],
            >>>     kp=[5.0, 6.0, 7.0, 8.0, 5.0, 5.0, 5.0],
            >>>     kd=[0.5, 0.6, 0.7, 0.8, 0.5, 0.5, 0.5]
            >>> )
        """
        if right_positions:
            for i, pos in enumerate(right_positions):
                motor_id = i + 1
                if motor_id in self.right_arm.motor_ids:
                    # 根据kp和kd的类型获取对应的值
                    kp_val = kp[i] if isinstance(kp, list) else kp
                    kd_val = kd[i] if isinstance(kd, list) else kd
                    self.right_arm.move_joint_mit(motor_id, position=pos, kp=kp_val, kd=kd_val)
                    time.sleep(0.01)
        if left_positions:
            for i, pos in enumerate(left_positions):
                motor_id = i + 1
                if motor_id in self.left_arm.motor_ids:
                    # 根据kp和kd的类型获取对应的值
                    kp_val = kp[i] if isinstance(kp, list) else kp
                    kd_val = kd[i] if isinstance(kd, list) else kd
                    self.left_arm.move_joint_mit(motor_id, position=pos, kp=kp_val, kd=kd_val)
                    time.sleep(0.01)

    def move_one_joint_mit(self,
                          arm: str,
                          motor_id: int,
                          position: float = 0.0,
                          velocity: float = 0.0,
                          torque: float = 0.0,
                          kp: float = 0.0,
                          kd: float = 0.0,
                          wait_response: bool = False,
                          timeout: float = 1.0,
                          verbose: bool = False) -> int:
        """
        控制单臂单个电机 (MIT模式)

        参数:
            arm (str): 机械臂选择 ('left' 或 'right')
            motor_id (int): 电机ID (1-8)
            position (float): 目标位置 (弧度)
            velocity (float): 目标速度 (弧度/秒)
            torque (float): 前馈扭矩 (牛米)
            kp (float): 位置增益
            kd (float): 速度增益
            wait_response (bool): 是否等待响应
            timeout (float): 超时时间(秒)
            verbose (bool): 是否打印详细信息

        返回:
            int: 0=成功, 1=失败

        异常:
            ValueError: 如果 arm 参数不是 'left' 或 'right'

        示例:
            >>> # 控制右臂的电机5移动到位置1.0
            >>> robot.move_one_joint_mit('right', motor_id=5, position=1.0, kp=10.0, kd=1.0)
            >>>
            >>> # 控制左臂的电机3
            >>> robot.move_one_joint_mit('left', motor_id=3, position=0.5, kp=8.0, kd=0.8)
        """
        if arm == 'left':
            return self.left_arm.move_joint_mit(
                motor_id=motor_id,
                position=position,
                velocity=velocity,
                torque=torque,
                kp=kp,
                kd=kd,
                wait_response=wait_response,
                timeout=timeout,
                verbose=verbose
            )
        elif arm == 'right':
            return self.right_arm.move_joint_mit(
                motor_id=motor_id,
                position=position,
                velocity=velocity,
                torque=torque,
                kp=kp,
                kd=kd,
                wait_response=wait_response,
                timeout=timeout,
                verbose=verbose
            )
        else:
            raise ValueError(f"arm 参数必须是 'left' 或 'right'，但得到了 '{arm}'")

    def test_motor_one_by_one(self,
                       left_positions: Optional[List[float]] = None,
                       right_positions: Optional[List[float]] = None,
                       kp: Union[float, List[float]] = 5.0,
                       kd: Union[float, List[float]] = 0.5):
        """
        逐个测试电机运动 (MIT模式) - 每个电机移动到指定位置后再回零

        参数:
            left_positions (List[float], optional): 左臂各关节位置 [pos1, pos2, ...]
            right_positions (List[float], optional): 右臂各关节位置
            kp (float or List[float]): 位置增益，可以是单个值（所有电机使用相同值）或列表（每个电机使用对应值）
            kd (float or List[float]): 速度增益，可以是单个值（所有电机使用相同值）或列表（每个电机使用对应值）

        示例:
            >>> # 所有电机使用相同的kp和kd值
            >>> robot.test_motor_one_by_one(
            >>>     left_positions=[0.1, 0.2, 0.3, 0.4, 0, 0, 0],
            >>>     right_positions=[0.1, 0.2, 0.3, 0.4, 0, 0, 0],
            >>>     kp=10.0, kd=1.0
            >>> )
            >>>
            >>> # 每个电机使用不同的kp和kd值
            >>> robot.test_motor_one_by_one(
            >>>     right_positions=[0.1, 0.2, 0.3, 0.4, 0, 0, 0],
            >>>     kp=[5.0, 6.0, 7.0, 8.0, 5.0, 5.0, 5.0],
            >>>     kd=[0.5, 0.6, 0.7, 0.8, 0.5, 0.5, 0.5]
            >>> )
        """
        if right_positions:
            for i, pos in enumerate(right_positions):
                motor_id = i + 1
                if motor_id in self.right_arm.motor_ids:
                    # 根据kp和kd的类型获取对应的值
                    kp_val = kp[i] if isinstance(kp, list) else kp
                    kd_val = kd[i] if isinstance(kd, list) else kd
                    self.right_arm.move_joint_mit(motor_id, position=pos, kp=kp_val, kd=kd_val)
                    time.sleep(0.5)
                    self.right_arm.move_joint_mit(motor_id, position=0.0, kp=kp_val, kd=kd_val)
                    time.sleep(0.5)

        if left_positions:
            for i, pos in enumerate(left_positions):
                motor_id = i + 1
                if motor_id in self.left_arm.motor_ids:
                    # 根据kp和kd的类型获取对应的值
                    kp_val = kp[i] if isinstance(kp, list) else kp
                    kd_val = kd[i] if isinstance(kd, list) else kd
                    self.left_arm.move_joint_mit(motor_id, position=pos, kp=kp_val, kd=kd_val)
                    time.sleep(0.5)
                    self.left_arm.move_joint_mit(motor_id, position=0.0, kp=kp_val, kd=kd_val)
                    time.sleep(0.5)

    # ==================== CSP 模式控制 ====================

    def move_joints_csp(self,
                       left_positions: Optional[List[float]] = None,
                       right_positions: Optional[List[float]] = None):
        """
        同时控制左右臂关节位置 (CSP模式)

        参数:
            left_positions (List[float], optional): 左臂各关节位置
            right_positions (List[float], optional): 右臂各关节位置
        """
        if right_positions:
            for i, pos in enumerate(right_positions):
                motor_id = i + 1
                if motor_id in self.right_arm.motor_ids:
                    self.right_arm.move_joint_csp(motor_id, position=pos)
                    time.sleep(0.01)

        if left_positions:
            for i, pos in enumerate(left_positions):
                motor_id = i + 1
                if motor_id in self.left_arm.motor_ids:
                    self.left_arm.move_joint_csp(motor_id, position=pos)
                    time.sleep(0.01)

    def move_one_joint_csp(self,
                          arm: str,
                          motor_id: int,
                          position: float,
                          wait_response: bool = False,
                          timeout: float = 0.2,
                          verbose: bool = False) -> int:
        """
        控制单臂单个电机 (CSP模式)

        参数:
            arm (str): 机械臂选择 ('left' 或 'right')
            motor_id (int): 电机ID (1-8)
            position (float): 目标位置 (弧度)
            wait_response (bool): 是否等待响应
            timeout (float): 超时时间(秒)
            verbose (bool): 是否打印详细信息

        返回:
            int: 0=成功, 1=失败

        异常:
            ValueError: 如果 arm 参数不是 'left' 或 'right'

        示例:
            >>> # 控制右臂的电机5移动到位置1.0
            >>> robot.move_one_joint_csp('right', motor_id=5, position=1.0)
            >>>
            >>> # 控制左臂的电机3
            >>> robot.move_one_joint_csp('left', motor_id=3, position=0.5)
        """
        if arm == 'left':
            return self.left_arm.move_joint_csp(
                motor_id=motor_id,
                position=position,
                wait_response=wait_response,
                timeout=timeout,
                verbose=verbose
            )
        elif arm == 'right':
            return self.right_arm.move_joint_csp(
                motor_id=motor_id,
                position=position,
                wait_response=wait_response,
                timeout=timeout,
                verbose=verbose
            )
        else:
            raise ValueError(f"arm 参数必须是 'left' 或 'right'，但得到了 '{arm}'")

    def set_csp_limits_all(self,
                          speed_limit: Optional[float] = None,
                          current_limit: Optional[float] = None,
                          motor_ids: Optional[List[int]] = None):
        """
        设置所有机械臂的 CSP 速度/电流限制

        参数:
            speed_limit (float, optional): 速度限制 (弧度/秒)
            current_limit (float, optional): 电流限制 (牛米)
            motor_ids (List[int], optional): 指定电机ID列表，默认为所有电机

        示例:
            >>> # 设置所有电机速度限制为 10 rad/s
            >>> robot.set_csp_limits_all(speed_limit=10.0)
            >>>
            >>> # 设置所有电机速度和电流限制
            >>> robot.set_csp_limits_all(speed_limit=10.0, current_limit=5.0)
        """
        for arm in self.arms:
            if motor_ids:
                for motor_id in motor_ids:
                    if motor_id in arm.motor_ids:
                        arm.set_csp_limits(motor_id=motor_id,
                                         speed_limit=speed_limit,
                                         current_limit=current_limit)
                    time.sleep(0.01)
            else:
                # 设置该臂的所有电机
                arm.set_csp_limits(motor_id=None,
                                 speed_limit=speed_limit,
                                 current_limit=current_limit)

    def set_csp_limits_left(self,
                           speed_limit: Optional[float] = None,
                           current_limit: Optional[float] = None,
                           motor_ids: Optional[List[int]] = None):
        """
        设置左臂的 CSP 速度/电流限制

        参数:
            speed_limit (float, optional): 速度限制 (弧度/秒)
            current_limit (float, optional): 电流限制 (牛米)
            motor_ids (List[int], optional): 指定电机ID列表，默认为左臂所有电机

        示例:
            >>> robot.set_csp_limits_left(speed_limit=10.0)
        """
        if motor_ids:
            for motor_id in motor_ids:
                if motor_id in self.left_arm.motor_ids:
                    self.left_arm.set_csp_limits(motor_id=motor_id,
                                                speed_limit=speed_limit,
                                                current_limit=current_limit)
                time.sleep(0.01)
        else:
            # 设置左臂所有电机
            self.left_arm.set_csp_limits(motor_id=None,
                                        speed_limit=speed_limit,
                                        current_limit=current_limit)

    def set_csp_limits_right(self,
                            speed_limit: Optional[float] = None,
                            current_limit: Optional[float] = None,
                            motor_ids: Optional[List[int]] = None):
        """
        设置右臂的 CSP 速度/电流限制

        参数:
            speed_limit (float, optional): 速度限制 (弧度/秒)
            current_limit (float, optional): 电流限制 (牛米)
            motor_ids (List[int], optional): 指定电机ID列表，默认为右臂所有电机

        示例:
            >>> robot.set_csp_limits_right(speed_limit=10.0)
        """
        if motor_ids:
            for motor_id in motor_ids:
                if motor_id in self.right_arm.motor_ids:
                    self.right_arm.set_csp_limits(motor_id=motor_id,
                                                 speed_limit=speed_limit,
                                                 current_limit=current_limit)
                time.sleep(0.01)
        else:
            # 设置右臂所有电机
            self.right_arm.set_csp_limits(motor_id=None,
                                         speed_limit=speed_limit,
                                         current_limit=current_limit)

    # ==================== 状态查询 ====================

    def get_all_status(self) -> Dict[str, Dict]:
        """
        获取所有机械臂的状态

        返回:
            dict: {
                'left': {motor_id: status_info, ...},
                'right': {motor_id: status_info, ...}
            }
        """
        return {
            'left': self.left_arm.get_all_status(),
            'right': self.right_arm.get_all_status()
        }

    def get_left_status(self, motor_id: Optional[int] = None) -> Dict:
        """获取左臂状态"""
        if motor_id:
            return self.left_arm.get_status(motor_id)
        return self.left_arm.get_all_status()

    def get_right_status(self, motor_id: Optional[int] = None) -> Dict:
        """获取右臂状态"""
        if motor_id:
            return self.right_arm.get_status(motor_id)
        return self.right_arm.get_all_status()

    def show_all_status(self):
        """
        显示双臂机器人的整体状态（统一表格）

        将左右臂的所有电机状态整合到一个表格中展示，
        更好地体现机器人的整体状态。
        """
        # 打印表头
        log_output("="*130, "INFO", self.log)
        log_output("机器人状态 (双臂)", "INFO", self.log)
        log_output("="*130, "INFO", self.log)
        log_output("臂   | ID | 角度(rad) | 速度(rad/s) | 力矩(Nm) |  温度    | 模式              | 状态", "INFO", self.log)
        log_output("-"*130, "INFO", self.log)

        # 显示右臂所有电机
        for motor_id in self.right_arm.motor_ids:
            try:
                info = self.right_arm.get_status(motor_id)
                if info:
                    self._print_robot_motor_status("右臂", motor_id, info)
                else:
                    log_output(f"右臂 | {motor_id:2d} | ✗ 无响应", "WARNING", self.log)
                time.sleep(0.01)
            except Exception as e:
                log_output(f"右臂 | {motor_id:2d} | ⚠ 异常 - {str(e)}", "ERROR", self.log)

        # 分隔线
        log_output("-"*130, "INFO", self.log)

        # 显示左臂所有电机
        for motor_id in self.left_arm.motor_ids:
            try:
                info = self.left_arm.get_status(motor_id)
                if info:
                    self._print_robot_motor_status("左臂", motor_id, info)
                else:
                    log_output(f"左臂 | {motor_id:2d} | ✗ 无响应", "WARNING", self.log)
                time.sleep(0.01)
            except Exception as e:
                log_output(f"左臂 | {motor_id:2d} | ⚠ 异常 - {str(e)}", "ERROR", self.log)

        log_output("="*130, "INFO", self.log)

    def _print_robot_motor_status(self, arm_name, motor_id, info):
        """
        打印单个电机状态（机器人整体表格格式）

        参数:
            arm_name (str): 臂名称（"左臂"或"右臂"）
            motor_id (int): 电机ID
            info (dict): 电机状态信息
        """
        angle = info.get('angle', 0.0)
        velocity = info.get('velocity', 0.0)
        torque = info.get('torque', 0.0)
        temperature = info.get('temperature', 0.0)
        mode_status = info.get('mode_status', '未知')
        fault_status = info.get('fault_status', '未知')

        # 根据模式状态选择图标
        if 'Motor模式' in mode_status or '运行' in mode_status:
            mode_icon = "🟢"
        elif 'Reset模式' in mode_status or '复位' in mode_status:
            mode_icon = "🔴"
        elif 'Cali模式' in mode_status or '标定' in mode_status:
            mode_icon = "🟡"
        else:
            mode_icon = "⚪"

        # 根据故障状态选择图标
        if fault_status == "正常":
            fault_icon = "✓"
        else:
            fault_icon = "✗"

        log_output(
            f"{arm_name} | {motor_id:2d} | {angle:9.3f} | {velocity:11.3f} | "
            f"{torque:8.3f} | {temperature:6.1f}°C | {mode_icon} {mode_status:15s} | {fault_icon} {fault_status}",
            "INFO", self.log
        )

    def show_left_status(self):
        """显示左臂状态"""
        self.left_arm.show_motor_status()

    def show_right_status(self):
        """显示右臂状态"""
        self.right_arm.show_motor_status()

    # ==================== 零点设置 ====================

    def set_zero_all(self, motor_ids: Optional[List[int]] = None,
                     verbose: bool = False,
                     timeout: float = 1.0,
                     progress_callback=None):
        """
        设置所有机械臂的零点

        参数:
            motor_ids (List[int], optional): 指定电机ID列表
            verbose (bool): 是否打印详细信息
            timeout (float): 每个电机的超时时间（秒）
            progress_callback (callable, optional): 进度回调函数

        返回:
            dict: 详细结果字典（格式同 enable_all）
        """
        import time as time_module

        results = {
            'summary': {'total': 0, 'success': 0, 'failed': 0, 'total_time': 0},
            'details': {'right': {}, 'left': {}}
        }

        start_total = time_module.time()

        for arm, arm_name in zip(self.arms, ['right', 'left']):
            ids = motor_ids if motor_ids is not None else arm.motor_ids

            for motor_id in ids:
                results['summary']['total'] += 1
                start_time = time_module.time()
                success = False
                error_msg = None

                try:
                    state = arm.set_zero(motor_id, timeout=timeout, verbose=verbose)
                    success = (state == 0)
                    if not success:
                        error_msg = f"Set zero returned state {state}"
                except Exception as e:
                    success = False
                    error_msg = f"Exception: {str(e)}"

                exec_time = time_module.time() - start_time

                results['details'][arm_name][motor_id] = {
                    'success': success,
                    'error': error_msg,
                    'time': exec_time
                }

                if success:
                    results['summary']['success'] += 1
                else:
                    results['summary']['failed'] += 1

                if progress_callback:
                    try:
                        progress_callback(arm_name, motor_id, success, error_msg, exec_time)
                    except Exception as e:
                        log_output(f"Callback error: {e}", "WARNING", self.log)
                time.sleep(0.01)

        results['summary']['total_time'] = time_module.time() - start_total
        return results

    def set_zero_left(self, motor_ids: Optional[List[int]] = None):
        """设置左臂零点"""
        ids = motor_ids if motor_ids else self.left_arm.motor_ids
        for motor_id in ids:
            self.left_arm.set_zero(motor_id)
            time.sleep(0.01)

    def set_zero_right(self, motor_ids: Optional[List[int]] = None):
        """设置右臂零点"""
        ids = motor_ids if motor_ids else self.right_arm.motor_ids
        for motor_id in ids:
            self.right_arm.set_zero(motor_id)
            time.sleep(0.01)

    def set_zero_range_all(self, zero_sta: int = 1, motor_ids: Optional[List[int]] = None):
        """
        设置所有机械臂的零点表示范围

        参数:
            zero_sta (int): 0=范围 0~2π, 1=范围 -π~π，默认为1
            motor_ids (List[int], optional): 指定电机ID列表，默认为所有电机

        示例:
            >>> # 设置所有电机零点范围为 -π~π
            >>> robot.set_zero_range_all(zero_sta=1)
            >>>
            >>> # 设置所有电机零点范围为 0~2π
            >>> robot.set_zero_range_all(zero_sta=0)
        """
        for arm in self.arms:
            if motor_ids:
                for motor_id in motor_ids:
                    if motor_id in arm.motor_ids:
                        arm.set_zero_range(motor_id=motor_id, zero_sta=zero_sta)
                    time.sleep(0.01)
            else:
                # 设置该臂的所有电机
                arm.set_zero_range(motor_id=None, zero_sta=zero_sta)

    def set_zero_range_left(self, zero_sta: int = 1, motor_ids: Optional[List[int]] = None):
        """
        设置左臂的零点表示范围

        参数:
            zero_sta (int): 0=范围 0~2π, 1=范围 -π~π，默认为1
            motor_ids (List[int], optional): 指定电机ID列表，默认为左臂所有电机

        示例:
            >>> robot.set_zero_range_left(zero_sta=1)
        """
        if motor_ids:
            for motor_id in motor_ids:
                if motor_id in self.left_arm.motor_ids:
                    self.left_arm.set_zero_range(motor_id=motor_id, zero_sta=zero_sta)
                time.sleep(0.01)
        else:
            # 设置左臂所有电机
            self.left_arm.set_zero_range(motor_id=None, zero_sta=zero_sta)

    def set_zero_range_right(self, zero_sta: int = 1, motor_ids: Optional[List[int]] = None):
        """
        设置右臂的零点表示范围

        参数:
            zero_sta (int): 0=范围 0~2π, 1=范围 -π~π，默认为1
            motor_ids (List[int], optional): 指定电机ID列表，默认为右臂所有电机

        示例:
            >>> robot.set_zero_range_right(zero_sta=1)
        """
        if motor_ids:
            for motor_id in motor_ids:
                if motor_id in self.right_arm.motor_ids:
                    self.right_arm.set_zero_range(motor_id=motor_id, zero_sta=zero_sta)
                time.sleep(0.01)
        else:
            # 设置右臂所有电机
            self.right_arm.set_zero_range(motor_id=None, zero_sta=zero_sta)
    

    def move_all_to_zero(self, kp: Union[float, List[float]] = 5.0,
                            kd: Union[float, List[float]] = 0.5,
                            motor_ids: Optional[List[int]] = None,
                            verbose: bool = False,
                            progress_callback=None):
        """
        所有机械臂回到零位 (MIT模式)

        参数:
            kp (float or List[float]): 位置增益，可以是单个值（所有电机使用相同值）或列表（每个电机使用对应值）
            kd (float or List[float]): 速度增益，可以是单个值（所有电机使用相同值）或列表（每个电机使用对应值）
            motor_ids (List[int], optional): 指定电机ID列表
            verbose (bool): 是否打印详细信息
            progress_callback (callable, optional): 进度回调函数

        返回:
            dict: 详细结果字典（格式同 enable_all）

        示例:
            >>> # 所有电机使用相同的kp和kd值
            >>> results = robot.move_all_to_zero(kp=5.0, kd=0.5)
            >>>
            >>> # 每个电机使用不同的kp和kd值（每条臂8个电机）
            >>> results = robot.move_all_to_zero(
            >>>     kp=[5.0, 6.0, 7.0, 8.0, 5.0, 5.0, 5.0, 5.0],
            >>>     kd=[0.5, 0.6, 0.7, 0.8, 0.5, 0.5, 0.5, 0.5]
            >>> )
            >>>
            >>> # 使用回调函数实时监控
            >>> def callback(arm, mid, success, error, time):
            >>>     print(f"{arm} - Motor {mid}: {'✓' if success else '✗'}")
            >>> results = robot.move_all_to_zero(progress_callback=callback)
        """
        import time as time_module

        results = {
            'summary': {'total': 0, 'success': 0, 'failed': 0, 'total_time': 0},
            'details': {'right': {}, 'left': {}}
        }

        start_total = time_module.time()

        for arm, arm_name in zip(self.arms, ['right', 'left']):
            ids = motor_ids if motor_ids is not None else arm.motor_ids

            for i, motor_id in enumerate(ids):
                results['summary']['total'] += 1
                start_time = time_module.time()
                success = False
                error_msg = None

                try:
                    # 获取对应的kp和kd值
                    kp_val = kp[i] if isinstance(kp, list) else kp
                    kd_val = kd[i] if isinstance(kd, list) else kd

                    # 调用home_joint归零
                    state = arm.home_joint(motor_id, kp=kp_val, kd=kd_val, verbose=verbose)
                    success = (state == 0)
                    if not success:
                        error_msg = f"Home joint returned state {state}"
                except Exception as e:
                    success = False
                    error_msg = f"Exception: {str(e)}"

                exec_time = time_module.time() - start_time

                results['details'][arm_name][motor_id] = {
                    'success': success,
                    'error': error_msg,
                    'time': exec_time
                }

                if success:
                    results['summary']['success'] += 1
                else:
                    results['summary']['failed'] += 1

                if progress_callback:
                    try:
                        progress_callback(arm_name, motor_id, success, error_msg, exec_time)
                    except Exception as e:
                        log_output(f"Callback error: {e}", "WARNING", self.log)
                time.sleep(0.01)

        results['summary']['total_time'] = time_module.time() - start_total
        return results