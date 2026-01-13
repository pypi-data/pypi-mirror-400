"""
WebSocket机器人使用封装 - 同步版本
基于websocket-client的同步WebSocket机器人使用封装实现
"""

import random
from typing import Optional, List, Union
from .ws_robot_manager import WebSocketRobotManager
from .ws_robot_instance import WebSocketRobotInstance
from .robot_api_body import RobotAPIBody


class WebSocketRobotUse:
    """WebSocket版本的机器人使用封装类 - 同步版本"""
    
    def __init__(self, robot_manager: WebSocketRobotManager, vos: Optional[str] = None):
        """
        初始化使用封装类

        Args:
            robot_manager: 机器人管理器（必须已经设置了 user）
            vos: VOS配置
        """
        self.robot_manager = robot_manager
        self.client = robot_manager.client
        self.api_body = RobotAPIBody()
        self.user = robot_manager.user  # 从 robot_manager 获取 user
        
        if vos is None or vos.strip() == "":
            self.default_param = []
        else:
            # 使用vos直连
            self.default_param = ['{"rtc.vos_list":["112.24.105.212:4063"]}']
    
    def add_base_robot(self, cname: str, appId: str, uid: Optional[int] = None, 
                      activeTime: int = 120, url: str = "http://114.236.93.153:8080/download/video/agora.mov",
                      channelKey: Optional[str] = None, clientRole: int = 1, 
                      muteVideo= False, muteAudio= False,
                      width: int = 640, height: int = 360, fps: int = 30, 
                      bitrate: int = 800, codecType: int = 2) -> WebSocketRobotInstance:
        """
        添加基础机器人
        
        Args:
            cname: 频道名
            appId: 应用ID
            uid: 用户ID（可选，自动生成）
            activeTime: 活跃时间（秒）
            url: 视频URL
            channelKey: 频道密钥（可选）
            clientRole: 客户端角色
            muteVideo: 静音视频（可选）
            muteAudio: 静音音频（可选）
            width: 视频宽度
            height: 视频高度
            fps: 帧率
            bitrate: 码率
            codecType: 编解码类型
            
        Returns:
            WebSocketRobotInstance: 机器人实例
        """
        if uid is None:
            uid = random.randint(10000, 99999)
        
        robot_data = self.api_body.gen_create_data(
            appId=appId,
            cname=cname,
            url=url,
            uid=uid,
            width=width,
            height=height,
            channelKey=channelKey,
            fps=fps,
            bitrate=bitrate,
            activeTime=activeTime,
            repeatTime=-1,
            muteVideo=muteVideo,
            codecType=codecType,
            clientRole=clientRole,
            live=1,
            muteAudio=muteAudio,
            privateParams=self.default_param,
            user=self.user
        )
        
        return self.robot_manager.add_robot(robot_data)
    
    def add_string_robot(self, cname: str, appId: str, userAccount: str,
                        activeTime: int = 60, url: str = "http://114.236.93.153:8080/download/video/agora.mov",
                        channelKey: Optional[str] = None, clientRole: int = 1,
                        width: int = 640, height: int = 360, fps: int = 30, 
                        bitrate: int = 800, codecType: int = 2) -> WebSocketRobotInstance:
        """
        添加字符串机器人
        
        Args:
            cname: 频道名
            appId: 应用ID
            userAccount: 用户账户
            activeTime: 活跃时间（秒）
            url: 视频URL
            channelKey: 频道密钥（可选）
            clientRole: 客户端角色
            width: 视频宽度
            height: 视频高度
            fps: 帧率
            bitrate: 码率
            codecType: 编解码类型
            
        Returns:
            WebSocketRobotInstance: 机器人实例
        """
        robot_data = self.api_body.gen_create_data(
            appId=appId,
            cname=cname,
            url=url,
            userAccount=userAccount,
            width=width,
            height=height,
            channelKey=channelKey,
            fps=fps,
            bitrate=bitrate,
            activeTime=activeTime,
            repeatTime=-1,
            muteVideo=False,
            codecType=codecType,
            clientRole=clientRole,
            live=1,
            muteAudio=False,
            privateParams=self.default_param,
            user=self.user
        )
        
        return self.robot_manager.add_robot(robot_data)
    
    def add_encryption_robot(self, cname: str, appId: str, encryptionMode: str, 
                            encryptionKey: str, encryptionKdfSalt: str,
                            datastreamEncryptionEnabled: bool, clientRole: int = 1, 
                            activeTime: int = 60, width: int = 640, height: int = 360,
                            fps: int = 30, bitrate: int = 800, codecType: int = 2) -> WebSocketRobotInstance:
        """
        添加加密机器人
        
        Args:
            cname: 频道名
            appId: 应用ID
            encryptionMode: 加密模式
            encryptionKey: 加密密钥
            encryptionKdfSalt: 加密KDF盐
            datastreamEncryptionEnabled: 数据流加密是否启用
            clientRole: 客户端角色
            activeTime: 活跃时间（秒）
            width: 视频宽度
            height: 视频高度
            fps: 帧率
            bitrate: 码率
            codecType: 编解码类型
            
        Returns:
            WebSocketRobotInstance: 机器人实例
        """
        uid = random.randint(10000, 99999)
        config = self.api_body.gen_encryption_config(
            encryptionMode=encryptionMode,
            encryptionKey=encryptionKey,
            encryptionKdfSalt=encryptionKdfSalt,
            datastreamEncryptionEnabled=datastreamEncryptionEnabled
        )
        
        robot_data = self.api_body.gen_create_data(
            appId=appId,
            cname=cname,
            url="http://114.236.93.153:8080/download/video/agora.mov",
            uid=uid,
            width=width,
            height=height,
            fps=fps,
            bitrate=bitrate,
            activeTime=activeTime,
            repeatTime=-1,
            muteVideo=False,
            codecType=codecType,
            clientRole=clientRole,
            live=1,
            muteAudio=False,
            encryptionConfig=config,
            privateParams=self.default_param,
            user=self.user
        )
        
        return self.robot_manager.add_robot(robot_data)
    
    def add_fix_robot(self, cname: str, appId: str, num: int, activeTime: int = 600) -> List[WebSocketRobotInstance]:
        """
        添加固定机器人
        
        Args:
            cname: 频道名
            appId: 应用ID
            num: 机器人数量（1-3）
            activeTime: 活跃时间（秒）
            
        Returns:
            List[WebSocketRobotInstance]: 机器人实例列表
        """
        robots = []
        
        if num >= 1:
            robot = self.add_base_robot(
                cname=cname, 
                appId=appId, 
                activeTime=activeTime, 
                uid=100,
                url="http://114.236.93.153:8080/download/video/stt/tranlation_04_quiet.mov",
                muteVideo=True
            )
            robots.append(robot)
        
        if num >= 2:
            robot = self.add_base_robot(
                cname=cname, 
                appId=appId, 
                activeTime=activeTime, 
                uid=200,
                url="http://114.236.93.153:8080/download/video/lx.flv",
                muteVideo=True
            )
            robots.append(robot)
        
        if num >= 3:
            robot = self.add_base_robot(
                cname=cname, 
                appId=appId, 
                activeTime=activeTime, 
                uid=300,
                url="http://114.236.93.153:8080/download/video/stt/es.flv",
                muteVideo=True
            )
            robots.append(robot)
        
        return robots
    
    def add_fix_lesson_robot(self, cname: str, appId: str, num: int, activeTime: int = 600) -> List[WebSocketRobotInstance]:
        """
        添加固定课程机器人
        
        Args:
            cname: 频道名
            appId: 应用ID
            num: 机器人数量
            activeTime: 活跃时间（秒）
            
        Returns:
            List[WebSocketRobotInstance]: 机器人实例列表
        """
        robots = []
        for i in range(num):
            url = f"http://114.236.93.153:8080/download/video/stt/lesson{i + 1}.mov"
            uid = (i + 1) * 100
            robot = self.add_base_robot(
                cname=cname, 
                appId=appId, 
                activeTime=activeTime, 
                uid=uid, 
                url=url
            )
            robots.append(robot)
        return robots
    
    def add_multi_language_robot(self, cname: str, appId: str, activeTime: int = 61,
                                url: str = "http://114.236.93.153:8080/download/video/stt/all_greetings.mp3") -> WebSocketRobotInstance:
        """
        添加多语言机器人
        
        Args:
            cname: 频道名
            appId: 应用ID
            activeTime: 活跃时间（秒）
            url: 视频URL
            
        Returns:
            WebSocketRobotInstance: 机器人实例
        """
        return self.add_base_robot(
            cname=cname, 
            appId=appId, 
            url=url, 
            activeTime=activeTime
        )
    
    def add_fix_ch_en_robot(self, cname: str, appId: str, num: int, activeTime: int = 600) -> List[WebSocketRobotInstance]:
        """
        添加固定中英机器人
        
        Args:
            cname: 频道名
            appId: 应用ID
            num: 机器人数量
            activeTime: 活跃时间（秒）
            
        Returns:
            List[WebSocketRobotInstance]: 机器人实例列表
        """
        robots = []
        for i in range(num):
            url = "http://114.236.93.153:8080/download/video/stt/chs%26eng.mp4"
            uid = (i + 1) * 100
            robot = self.add_base_robot(
                cname=cname, 
                appId=appId, 
                activeTime=activeTime, 
                uid=uid, 
                url=url
            )
            robots.append(robot)
        return robots
    
    # ========== 统计信息 ==========
    
    def get_robot_count(self) -> int:
        """获取机器人数量"""
        return self.robot_manager.get_robot_count()
    
    def get_robot_ids(self) -> List[str]:
        """获取所有机器人ID"""
        return self.robot_manager.get_robot_ids()
    
    def is_empty(self) -> bool:
        """检查是否为空"""
        return self.robot_manager.is_empty()
    
    def __str__(self) -> str:
        return f"WebSocketRobotUse(robots={self.get_robot_count()})"
    
    def __repr__(self) -> str:
        return self.__str__()
