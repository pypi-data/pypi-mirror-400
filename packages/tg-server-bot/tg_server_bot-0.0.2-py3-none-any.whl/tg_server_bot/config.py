# -*- coding: utf-8 -*-
import configparser
import os
import shutil
import threading
import time
from typing import Optional, List, Dict, Set
from .utils import singleton, logger, get_file_modify_time, get_package_file_path
from .const import DEF_CONFIG_FILE_NAME, DEF_LOG_FILE, DEF_ALLOW_USER_FILE


@singleton
class Config:
    def __init__(self) -> None:
        self.get_cmds: Dict[str, str] = {}
        self.run_cmds: Dict[str, str] = {}
        self.runtime_keys: Set[str] = set()
        self.token: Optional[str] = None
        self.proxy: Optional[str] = None
        self.log_file: Optional[str] = None
        self.config_path: str = DEF_CONFIG_FILE_NAME
        self.pwd: str = os.getcwd()

    def load(self, path=None):
        if path:
            self.config_path = path
        if not os.path.exists(self.config_path):
            logger.error(f"配置文件不存在: {self.config_path}")
            return
        p = configparser.ConfigParser()
        p.read(self.config_path, 'utf-8')
        if p.has_section('common'):
            self.token = p.get('common', 'token', fallback=None)
            self.proxy = p.get('common', 'proxy', fallback=None)
            self.log_file = p.get('common', 'log_file', fallback=None)
            self.pwd = p.get('common', 'pwd', fallback=os.getcwd())
        if p.has_section('get'):
            self.get_cmds = dict(p.items('get'))
        if p.has_section('run_cmds'):
            self.run_cmds = dict(p.items('run_cmds'))

    def save_cmd(self, section: str, cmd: str, value: str):
        """保存新指令到配置文件"""
        if section == 'get':
            self.get_cmds[cmd] = value
        else:
            self.run_cmds[cmd] = value
        parser = configparser.ConfigParser()
        parser.read(self.config_path, 'utf-8')
        if not parser.has_section(section):
            parser.add_section(section)
        parser.set(section, cmd, value)
        try:
            if os.path.exists(self.config_path):
                shutil.copy2(self.config_path, self.config_path + ".bak")
        except Exception as e:
            logger.error(f"配置文件备份失败: {e}")
        with open(self.config_path, 'w', encoding='utf-8') as f:
            parser.write(f)

    def add_runtime_cmd(self, section: str, cmd: str, value: str):
        if section == 'get':
            self.get_cmds[cmd] = value
        else:
            self.run_cmds[cmd] = value
        self.runtime_keys.add(cmd)

    def clear_runtime_cmds(self):
        for cmd in list(self.runtime_keys):
            if cmd in self.get_cmds:
                del self.get_cmds[cmd]
            if cmd in self.run_cmds:
                del self.run_cmds[cmd]
        count = len(self.runtime_keys)
        self.runtime_keys.clear()
        return count

    def is_config_cmd(self, cmd: str) -> bool:
        return (
            cmd in self.get_cmds or cmd in self.run_cmds) and cmd not in self.runtime_keys


@singleton
class PermissionHelper:
    def __init__(self) -> None:
        self.allow_user_file = get_package_file_path(DEF_ALLOW_USER_FILE)
        self.allow_user_ids: List[str] = []
        self.last_modify_time: float = 0
        self._running = True
        self.__update_allow_users()
        self.__watch_config()

    def __watch_config(self):
        self.last_modify_time = get_file_modify_time(self.allow_user_file)
        watcher = threading.Thread(
            target=self.__watch_file_change, daemon=True)
        watcher.start()

    def __update_allow_users(self):
        new_allow_ids = []
        if not os.path.exists(self.allow_user_file):
            self.allow_user_ids = []
            return
        try:
            with open(self.allow_user_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    new_allow_ids.append(line)
            self.allow_user_ids = new_allow_ids
            logger.info(f"已更新授权用户列表: {len(self.allow_user_ids)} 个用户")
        except Exception as e:
            logger.error(f"读取鉴权文件失败: {e}")

    def __watch_file_change(self):
        while self._running:
            try:
                current_time = get_file_modify_time(self.allow_user_file)
                if current_time > self.last_modify_time:
                    self.last_modify_time = current_time
                    logger.info('鉴权文件检测到更新，正在重新加载...')
                    self.__update_allow_users()
            except Exception as e:
                logger.error(f"监听鉴权文件出错: {e}")
            time.sleep(3)

    def is_allowed(self, user_id: str) -> bool:
        return str(user_id) in self.allow_user_ids
