"""
AppID管理HTTP服务
提供AppID的获取、释放和状态查询功能
支持并发获取，解决AppID资源管理问题
支持定时任务监控和报告生成
"""
import time
import threading
import os
import secrets
import string
import json
import uuid
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, Optional, List
from pathlib import Path
from flask import Flask, request, jsonify, send_file
import argparse


class AppIdManager:
    """AppID管理器"""
    
    def __init__(self):
        """
        初始化AppID管理器
        """
        self.appid_config = {}
        self.appid_status = {}
        self.test_results = {}  # 存储测试用例执行数据 {product_name: {session_id: [test_results]}}
        self.lock = threading.Lock()
    
    def init_product(self, product_name: str, appids: Dict[str, str]) -> Tuple[bool, Dict[str, Any]]:
        """
        初始化或重置产品AppID配置
        
        Args:
            product_name: 产品名称
            appids: AppID配置 {appid: vid}
            
        Returns:
            (success, data): 成功标志和数据
        """
        with self.lock:
            # 更新配置
            self.appid_config[product_name] = appids
            
            # 移除该产品下所有现有的AppID状态
            removed_count = 0
            appids_to_remove = []
            for appid, status in self.appid_status.items():
                if status.get("productName") == product_name:
                    appids_to_remove.append(appid)
                    removed_count += 1
            
            for appid in appids_to_remove:
                del self.appid_status[appid]
            
            # 添加新的AppID状态
            added_count = 0
            for appid, vid in appids.items():
                self.appid_status[appid] = {
                    "starttime": None,
                    "stoptime": None,
                    "productName": product_name,
                    "vid": int(vid)
                }
                added_count += 1
            
            return True, {
                "success": True,
                "productName": product_name,
                "removed_count": removed_count,
                "added_count": added_count,
                "message": f"Product '{product_name}' initialized: removed {removed_count}, added {added_count} appids"
            }
    
    def _is_available(self, appid: str, status: Dict[str, Any]) -> bool:
        """
        判断AppID是否可用
        
        判断规则：
        - starttime=null, stoptime=null → 可用
        - starttime=null, stoptime≠null → 错误状态（不应该存在）
        - starttime≠null, stoptime=null → 使用中，不可用
        - starttime≠null, stoptime≠null → 检查stoptime是否在当前小时内
        """
        starttime = status.get("starttime")
        stoptime = status.get("stoptime")
        
        # 未使用过
        if starttime is None and stoptime is None:
            return True
        
        # 错误状态
        if starttime is None and stoptime is not None:
            return False
        
        # 使用中
        if starttime is not None and stoptime is None:
            return False
        
        # 使用结束，检查是否在当前小时内
        if starttime is not None and stoptime is not None:
            current_hour = self._get_current_hour()
            stoptime_hour = self._get_hour_of_timestamp(stoptime)
            # 严格按小时判断：stoptime所在小时 < 当前小时 → 可用
            # 即：stoptime在之前的小时，现在进入新小时，可以再次使用
            # 如果stoptime所在小时 == 当前小时，说明在当前小时内使用过，不可重复使用
            is_available = stoptime_hour < current_hour
            return is_available
        
        # 理论上不会到达这里，但为了类型检查，返回False
        return False
    
    def _get_current_hour(self) -> int:
        """获取当前小时（时间戳，毫秒）"""
        now = datetime.now()
        # 获取当前小时的开始时间
        hour_start = now.replace(minute=0, second=0, microsecond=0)
        return int(hour_start.timestamp() * 1000)
    
    def _get_hour_of_timestamp(self, timestamp: int) -> int:
        """获取时间戳所在的小时（时间戳，毫秒）"""
        dt = datetime.fromtimestamp(timestamp / 1000)
        hour_start = dt.replace(minute=0, second=0, microsecond=0)
        return int(hour_start.timestamp() * 1000)
    
    def _get_next_hour_start(self) -> int:
        """获取下一个小时的开始时间（时间戳，毫秒）"""
        now = datetime.now()
        next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        return int(next_hour.timestamp() * 1000)
    
    def acquire_appid(self, product_name: str = "default", force_acquire: bool = False) -> Tuple[bool, Dict[str, Any]]:
        """
        获取可用的AppID
        
        Args:
            product_name: 产品名称，用于隔离不同业务的AppID
            force_acquire: 是否强制获取（忽略小时内使用检查），默认为False
                         如果为True，即使AppID在当前小时内使用过，也可以直接获取
                         但starttime和stoptime依旧要填
            
        Returns:
            (success, data): 成功标志和数据
        """
        with self.lock:
            # 遍历找可用AppID（只查找指定产品的AppID）
            for appid, status in self.appid_status.items():
                if status.get("productName") == product_name:
                    # 如果 force_acquire=True，只要AppID不在使用中（stoptime != None），就可以获取
                    # 如果 force_acquire=False，需要检查是否可用（包括小时内使用检查）
                    if force_acquire:
                        # 强制获取：只要不在使用中（stoptime != None），就可以获取
                        # 即使在当前小时内使用过，也可以直接获取
                        if status.get("stoptime") is not None:
                            # 已释放，可以获取（忽略小时内使用检查）
                            current_time = int(time.time() * 1000)
                            vid = status.get("vid")  # 保留vid字段
                            self.appid_status[appid] = {
                                "starttime": current_time,
                                "stoptime": None,
                                "productName": product_name,
                                "vid": vid  # 保留vid字段
                            }
                            
                            return True, {
                                "appid": appid,
                                "vid": vid,
                                "productName": product_name,
                                "starttime": current_time
                            }
                    else:
                        # 正常获取：需要检查是否可用（包括小时内使用检查）
                        if self._is_available(appid, status):
                            # 立即标记为使用中（保留vid字段）
                            current_time = int(time.time() * 1000)
                            vid = status.get("vid")  # 保留vid字段
                            self.appid_status[appid] = {
                                "starttime": current_time,
                                "stoptime": None,
                                "productName": product_name,
                                "vid": vid  # 保留vid字段
                            }
                            
                            return True, {
                                "appid": appid,
                                "vid": vid,
                                "productName": product_name,
                                "starttime": current_time
                            }
            
            # 所有AppID都不可用，检查是否需要等待（只检查指定产品的AppID）
            # 如果 force_acquire=True，但所有AppID都在使用中，返回等待
            current_hour = self._get_current_hour()
            all_in_current_hour = True
            has_released_appid = False  # 是否有已释放的AppID
            
            for status in self.appid_status.values():
                if status.get("productName") == product_name:
                    stoptime = status.get("stoptime")
                    if stoptime is not None:
                        # 有已释放的AppID
                        has_released_appid = True
                        stoptime_hour = self._get_hour_of_timestamp(stoptime)
                        if stoptime_hour < current_hour:
                            # 有AppID的stoptime在之前的小时，应该可用
                            # 但遍历时没找到，可能是判断逻辑有问题，返回waiting让其重试
                            all_in_current_hour = False
                            break
                    elif status.get("starttime") is not None:
                        # 正在使用中的AppID
                        pass
            
            if all_in_current_hour and has_released_appid:
                # 所有已释放AppID的stoptime都在当前小时内，需要等待到下个小时
                next_hour_start = self._get_next_hour_start()
                current_time = int(time.time() * 1000)
                wait_seconds = (next_hour_start - current_time) / 1000
                
                return False, {
                    "error": "no_available",
                    "retry_after": min(int(wait_seconds), 300),  # 最多等待5分钟
                    "message": f"All appids for product '{product_name}' are in use for current hour, wait {wait_seconds:.0f}s until next hour"
                }
            else:
                # 其他情况，短时间重试
                # 包括：1) 所有AppID都在使用中 2) 有AppID应该可用但判断可能有问题
                return False, {
                    "error": "waiting",
                    "retry_after": 60,
                    "message": f"All appids for product '{product_name}' are in use, retry in 60s"
                }
    
    def release_appid(self, appid: str, product_name: str = "default") -> Tuple[bool, Dict[str, Any]]:
        """
        释放AppID
        
        Args:
            appid: 要释放的AppID
            product_name: 产品名称，用于验证AppID归属
            
        Returns:
            (success, data): 成功标志和数据
        """
        with self.lock:
            if appid not in self.appid_status:
                return False, {"error": "appid_not_found", "message": f"AppID {appid} not found"}
            
            status = self.appid_status[appid]
            if status.get("productName") != product_name:
                return False, {"error": "product_mismatch", "message": f"AppID {appid} belongs to product '{status.get('productName')}', not '{product_name}'"}
            
            if status.get("stoptime") is not None:
                return False, {"error": "already_released", "message": f"AppID {appid} already released"}
            
            # 标记为已释放（保留vid字段）
            current_time = int(time.time() * 1000)
            vid = status.get("vid")  # 保留vid字段
            self.appid_status[appid] = {
                "starttime": status.get("starttime"),
                "stoptime": current_time,
                "productName": product_name,
                "vid": vid  # 保留vid字段
            }
            
            return True, {
                "success": True,
                "stoptime": current_time,
                "productName": product_name,
                "message": f"AppID {appid} released successfully"
            }
    
    def get_status(self, product_name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取AppID状态统计和详细信息
        
        Args:
            product_name: 产品名称，如果指定则只统计该产品的AppID
            
        Returns:
            状态统计信息和每个AppID的详细信息
        """
        with self.lock:
            total = 0
            available = 0
            in_use = 0
            appid_details = []  # 存储每个AppID的详细信息
            
            # 获取当前小时，用于判断可用性
            current_hour = self._get_current_hour()
            
            for appid, status in self.appid_status.items():
                # 如果指定了产品名称，只统计该产品的AppID
                if product_name and status.get("productName") != product_name:
                    continue
                
                total += 1
                
                # 判断状态
                is_available = self._is_available(appid, status)
                starttime = status.get("starttime")
                stoptime = status.get("stoptime")
                
                # 计算stoptime所在的小时（如果存在）
                stoptime_hour = None
                if stoptime is not None:
                    stoptime_hour = self._get_hour_of_timestamp(stoptime)
                
                if is_available:
                    status_str = "available"
                    available += 1
                elif stoptime is None:
                    status_str = "in_use"
                    in_use += 1
                else:
                    # 有stoptime，判断是否在当前小时内
                    if stoptime_hour == current_hour:
                        # 在当前小时内使用过，被视为"在当前小时内已使用"
                        status_str = "used_in_current_hour"
                        in_use += 1  # 统计上也算作使用中
                    else:
                        # 在之前的小时使用过，已释放
                        status_str = "released"
                
                # 构建AppID详细信息
                appid_info = {
                    "appid": appid,
                    "vid": status.get("vid"),
                    "productName": status.get("productName"),
                    "starttime": starttime,
                    "stoptime": stoptime,
                    "status": status_str,
                    "is_available": is_available,
                    "stoptime_hour": stoptime_hour,  # stoptime所在的小时（时间戳，毫秒）
                    "current_hour": current_hour  # 当前小时（时间戳，毫秒）
                }
                appid_details.append(appid_info)
            
            result = {
                "total": total,
                "available": available,
                "in_use": in_use,
                "released": total - available - in_use,
                "appids": appid_details  # 所有AppID的详细信息
            }
            
            if product_name:
                result["productName"] = product_name
            
            return result
    
    def store_test_result(self, product_name: str, session_id: str, test_data: Dict[str, Any]) -> None:
        """
        存储测试用例执行数据
        
        Args:
            product_name: 产品名称（业务类型）
            session_id: 测试会话ID（用于区分不同的测试会话，如pytest worker进程）
            test_data: 测试用例数据字典
        """
        with self.lock:
            # 按业务类型组织数据
            if product_name not in self.test_results:
                self.test_results[product_name] = {}
            
            if session_id not in self.test_results[product_name]:
                self.test_results[product_name][session_id] = []
            
            # 添加时间戳（如果test_data中没有）
            if "_stored_at" not in test_data:
                test_data["_stored_at"] = int(time.time() * 1000)  # 毫秒时间戳
            
            self.test_results[product_name][session_id].append(test_data)
    
    def get_test_results(self, product_name: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取测试用例执行数据
        
        Args:
            product_name: 产品名称（业务类型），如果指定则只返回该业务的数据，否则返回所有业务的数据
            session_id: 测试会话ID，如果指定则只返回该会话的数据，否则返回所有会话的数据
            
        Returns:
            测试结果数据字典
        """
        with self.lock:
            if product_name:
                # 返回指定业务的数据
                business_results = self.test_results.get(product_name, {})
                
                if session_id:
                    # 返回指定业务和会话的数据
                    results = business_results.get(session_id, [])
                    return {
                        "product_name": product_name,
                        "session_id": session_id,
                        "results": results
                    }
                else:
                    # 返回指定业务的所有会话数据
                    all_results = []
                    for results in business_results.values():
                        all_results.extend(results)
                    
                    return {
                        "product_name": product_name,
                        "results": all_results
                    }
            else:
                # 返回所有业务的数据
                all_results = []
                for business_results in self.test_results.values():
                    for results in business_results.values():
                        all_results.extend(results)
                
                return {
                    "results": all_results
                }
    
    def clear_test_results(self, product_name: Optional[str] = None, session_id: Optional[str] = None) -> None:
        """
        清除测试用例执行数据
        
        Args:
            product_name: 产品名称（业务类型），如果指定则只清除该业务的数据，否则清除所有业务的数据
            session_id: 测试会话ID，如果指定则只清除该会话的数据，否则清除所有会话的数据
        """
        with self.lock:
            if product_name:
                if product_name not in self.test_results:
                    return
                
                business_results = self.test_results[product_name]
                
                if session_id:
                    # 清除指定业务和会话的数据
                    if session_id in business_results:
                        del business_results[session_id]
                    
                    # 如果该业务下没有会话了，删除业务
                    if not business_results:
                        del self.test_results[product_name]
                else:
                    # 清除指定业务的所有会话数据
                    del self.test_results[product_name]
            else:
                # 清除所有业务的数据
                self.test_results.clear()
    
    def clear_old_test_results(self, days: int = 14) -> Dict[str, Any]:
        """
        清除指定天数前的测试用例执行数据
        
        Args:
            days: 保留最近N天的数据，默认14天（2周）
            
        Returns:
            清理统计信息
        """
        from datetime import datetime, timedelta
        
        with self.lock:
            cutoff_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)  # 毫秒时间戳
            total_removed = 0
            total_kept = 0
            removed_by_product = {}
            
            # 遍历所有业务
            products_to_remove = []
            for product_name, business_results in list(self.test_results.items()):
                sessions_to_remove = []
                product_removed = 0
                product_kept = 0
                
                # 遍历所有会话
                for session_id, results in list(business_results.items()):
                    # 过滤出需要保留的数据（时间戳 >= cutoff_time）
                    kept_results = []
                    for result in results:
                        stored_at = result.get("_stored_at", 0)
                        if stored_at >= cutoff_time:
                            kept_results.append(result)
                            product_kept += 1
                        else:
                            product_removed += 1
                    
                    # 如果该会话还有数据，更新；否则标记为删除
                    if kept_results:
                        business_results[session_id] = kept_results
                    else:
                        sessions_to_remove.append(session_id)
                
                # 删除空的会话
                for session_id in sessions_to_remove:
                    del business_results[session_id]
                
                # 如果该业务下没有会话了，标记为删除
                if not business_results:
                    products_to_remove.append(product_name)
                
                total_removed += product_removed
                total_kept += product_kept
                if product_removed > 0:
                    removed_by_product[product_name] = product_removed
            
            # 删除空的业务
            for product_name in products_to_remove:
                del self.test_results[product_name]
            
            return {
                "cutoff_time": cutoff_time,
                "cutoff_date": datetime.fromtimestamp(cutoff_time / 1000).isoformat(),
                "days": days,
                "total_removed": total_removed,
                "total_kept": total_kept,
                "removed_by_product": removed_by_product
            }
    


# ==================== 定时任务相关类 ====================

class TaskConfigLoader:
    """任务配置加载器"""
    
    @staticmethod
    def load_tasks_from_jsonl(file_path: Path) -> List[Dict[str, Any]]:
        """
        从JSONL文件加载任务配置
        
        Args:
            file_path: JSONL文件路径
            
        Returns:
            任务配置列表
        """
        tasks = []
        if not file_path.exists():
            return tasks
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        task_config = json.loads(line)
                        tasks.append(task_config)
                    except json.JSONDecodeError as e:
                        print(f"⚠️  警告: 任务配置文件第 {line_num} 行JSON解析失败: {e}")
        except Exception as e:
            print(f"⚠️  警告: 加载任务配置文件失败: {e}")
        
        return tasks
    
    @staticmethod
    def validate_task_config(task_config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        校验任务配置
        
        Args:
            task_config: 任务配置字典
            
        Returns:
            (是否有效, 错误信息)
        """
        required_fields = ["business", "environment", "start_delay_minutes"]
        
        for field in required_fields:
            if field not in task_config:
                return False, f"缺少必需字段: {field}"
        
        # 校验业务配置是否已初始化
        try:
            from .sku_query_framework import SkuQueryFactory
            configs = SkuQueryFactory._get_business_configs()
            business = task_config.get("business")
            if business not in configs:
                return False, f"业务 '{business}' 未在配置中初始化，可用业务: {list(configs.keys())}"
        except Exception as e:
            return False, f"校验业务配置失败: {e}"
        
        return True, ""
    
    @staticmethod
    def load_expected_values_from_jsonl(file_path: Path) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        从JSONL文件加载预期值（每行一个用例的预期值）
        
        Args:
            file_path: JSONL文件路径
            
        Returns:
            (预期值列表, 错误信息)，如果成功则错误信息为None
        """
        expected_values_list = []
        if not file_path.exists():
            return [], "预期值文件不存在"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        expected_values = json.loads(line)
                        if not isinstance(expected_values, dict):
                            return [], f"第 {line_num} 行不是字典格式"
                        
                        # 校验tolerance字段（可选）
                        # tolerance 字段是可选的，如果不提供则在使用时默认为0
                        # 如果提供了tolerance，必须是字典类型（可以为空字典）
                        if "tolerance" in expected_values:
                            tolerance = expected_values.get("tolerance")
                            if not isinstance(tolerance, dict):
                                return [], f"第 {line_num} 行的tolerance必须是字典类型"
                        
                        expected_values_list.append(expected_values)
                    except json.JSONDecodeError as e:
                        return [], f"第 {line_num} 行JSON解析失败: {e}"
        except Exception as e:
            return [], f"加载预期值文件失败: {e}"
        
        if len(expected_values_list) == 0:
            return [], "预期值文件为空"
        
        return expected_values_list, None
    
    @staticmethod
    def append_task_to_jsonl(file_path: Path, task_config: Dict[str, Any]) -> bool:
        """
        追加任务到JSONL文件
        
        Args:
            file_path: JSONL文件路径
            task_config: 任务配置字典
            
        Returns:
            是否成功
        """
        try:
            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 追加到文件
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(task_config, ensure_ascii=False) + '\n')
            return True
        except Exception as e:
            print(f"⚠️  错误: 追加任务到配置文件失败: {e}")
            return False
    
    @staticmethod
    def remove_task_from_jsonl(file_path: Path, task_id: str) -> bool:
        """
        从JSONL文件中删除任务
        
        Args:
            file_path: JSONL文件路径
            task_id: 任务ID
            
        Returns:
            是否成功
        """
        if not file_path.exists():
            return False
        
        try:
            # 读取所有任务
            tasks = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        task_config = json.loads(line)
                        if task_config.get("task_id") != task_id:
                            tasks.append(line)
                    except json.JSONDecodeError:
                        continue
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                for task_line in tasks:
                    f.write(task_line + '\n')
            return True
        except Exception as e:
            print(f"⚠️  错误: 从配置文件删除任务失败: {e}")
            return False


class ReportManager:
    """报告管理器"""
    
    def __init__(self, base_dir: Path):
        """
        初始化报告管理器
        
        Args:
            base_dir: 报告存储基础目录
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = self.base_dir / "task_reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def save_report(self, task_id: str, execution_id: str, html_content: str) -> Path:
        """
        保存HTML报告
        
        Args:
            task_id: 任务ID
            execution_id: 执行ID
            html_content: HTML内容
            
        Returns:
            报告文件路径
        """
        task_dir = self.reports_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = task_dir / f"{execution_id}.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_file
    
    def get_report_path(self, task_id: str, execution_id: str) -> Optional[Path]:
        """
        获取报告文件路径
        
        Args:
            task_id: 任务ID
            execution_id: 执行ID
            
        Returns:
            报告文件路径，如果不存在返回None
        """
        report_file = self.reports_dir / task_id / f"{execution_id}.html"
        if report_file.exists():
            return report_file
        return None
    
    def cleanup_old_reports(self, days: int = 7) -> Dict[str, Any]:
        """
        清理旧报告
        
        Args:
            days: 保留天数，默认7天
            
        Returns:
            清理统计信息
        """
        cutoff_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        removed_count = 0
        kept_count = 0
        
        try:
            task_dirs = [d for d in self.reports_dir.iterdir() if d.is_dir()]
            for task_dir in task_dirs:
                
                for report_file in task_dir.iterdir():
                    if not report_file.is_file() or not report_file.suffix == '.html':
                        continue
                    
                    # 从文件名提取时间戳（execution_id格式：exec_{timestamp}）
                    file_stem = report_file.stem
                    if file_stem.startswith('exec_'):
                        try:
                            timestamp = int(file_stem.split('_')[1])
                            if timestamp < cutoff_time:
                                report_file.unlink()
                                removed_count += 1
                            else:
                                kept_count += 1
                        except (ValueError, IndexError):
                            # 文件名格式不正确，保留
                            kept_count += 1
                    else:
                        # 文件名格式不正确，保留
                        kept_count += 1
                
                # 如果任务目录为空，删除目录
                if task_dir.exists() and not any(task_dir.iterdir()):
                    task_dir.rmdir()
        except Exception as e:
            print(f"⚠️  清理报告时出错: {e}")
        
        return {
            "removed_count": removed_count,
            "kept_count": kept_count,
            "cutoff_time": cutoff_time
        }
    
    def list_reports(self, task_id: Optional[str] = None, days: int = 7) -> List[Dict[str, Any]]:
        """
        列出报告
        
        Args:
            task_id: 任务ID，如果指定则只列出该任务的报告
            days: 只列出最近N天的报告
            
        Returns:
            报告列表
        """
        cutoff_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        reports = []
        
        try:
            if task_id:
                task_dirs = [self.reports_dir / task_id] if (self.reports_dir / task_id).is_dir() else []
            else:
                task_dirs = [d for d in self.reports_dir.iterdir() if d.is_dir()]
            
            for task_dir in task_dirs:
                
                current_task_id = task_dir.name
                
                for report_file in task_dir.iterdir():
                    if not report_file.is_file() or not report_file.suffix == '.html':
                        continue
                    
                    file_stem = report_file.stem
                    if file_stem.startswith('exec_'):
                        try:
                            timestamp = int(file_stem.split('_')[1])
                            if timestamp >= cutoff_time:
                                reports.append({
                                    "task_id": current_task_id,
                                    "execution_id": file_stem,
                                    "timestamp": timestamp,
                                    "file_path": str(report_file),
                                    "file_name": report_file.name
                                })
                        except (ValueError, IndexError):
                            pass
        except Exception as e:
            print(f"⚠️  列出报告时出错: {e}")
        
        # 按时间戳倒序排序
        reports.sort(key=lambda x: x["timestamp"], reverse=True)
        return reports


class EmailNotifier:
    """邮件通知服务 - 通过 Jenkins Job 发送邮件"""
    
    # Jenkins 配置（Hard coded）
    JENKINS_URL = "https://jenkins-api.bj2.agoralab.co/job/QAE/job/ACCS/job/ass_email_notification/buildWithParameters?delay=0sec"
    JENKINS_USER = "ouyangrunli@agora.io"
    JENKINS_TOKEN = "119cb0debb083f1a7fd54f1b5c213edc51"
    
    @staticmethod
    def send_email(subject: str, content: str, to_emails: List[str], 
                   cc_emails: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        通过 Jenkins Job 发送邮件通知
        
        Args:
            subject: 邮件主题
            content: 邮件内容（支持HTML和Markdown）
            to_emails: 收件人邮箱列表
            cc_emails: 抄送人邮箱列表（可选）
            
        Returns:
            (是否成功, 错误信息)
        """
        if not to_emails:
            return False, "收件人列表为空"
        
        try:
            # 使用 Hard coded 的 Jenkins 配置
            jenkins_url = EmailNotifier.JENKINS_URL
            jenkins_user = EmailNotifier.JENKINS_USER
            jenkins_token = EmailNotifier.JENKINS_TOKEN
            
            # 将 Markdown 内容转换为 HTML（保留原有的转换逻辑）
            import re
            # 转换标题
            html_content = re.sub(r'^### (.*)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
            html_content = re.sub(r'^## (.*)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'^# (.*)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
            # 转换加粗
            html_content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html_content)
            # 转换代码块
            html_content = re.sub(r'```([^`]+)```', r'<pre><code>\1</code></pre>', html_content, flags=re.DOTALL)
            html_content = re.sub(r'`([^`]+)`', r'<code>\1</code>', html_content)
            # 转换链接
            html_content = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html_content)
            # 转换列表
            html_content = re.sub(r'^- (.*)$', r'<li>\1</li>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html_content, flags=re.DOTALL)
            # 转换换行
            html_content = html_content.replace('\n', '<br>\n')
            
            # 构建 Jenkins Job 参数
            params = {
                "email_subject": subject,
                "email_content": html_content,
                "send_email_to_somebody": ", ".join(to_emails),
                "cc_email_to_somebody": ", ".join(cc_emails) if cc_emails else ""
            }
            
            # 打印日志
            print(f"📧 通过 Jenkins 发送邮件通知到: {', '.join(to_emails)}")
            if cc_emails:
                print(f"📧 抄送到: {', '.join(cc_emails)}")
            print(f"📝 邮件主题: {subject}")
            print(f"🔗 Jenkins Job URL: {jenkins_url}")
            
            # 调用 Jenkins API 触发构建
            response = requests.post(
                jenkins_url,
                params=params,
                auth=(jenkins_user, jenkins_token),
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ 邮件发送任务已成功提交到 Jenkins")
                return True, "邮件发送任务已提交到 Jenkins"
            else:
                error_msg = f"Jenkins API 返回错误: {response.status_code}"
                if response.text:
                    error_msg += f" - {response.text[:200]}"
                print(f"⚠️  {error_msg}")
                return False, error_msg
                
        except requests.RequestException as e:
            error_msg = f"调用 Jenkins API 失败: {str(e)}"
            print(f"⚠️  {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"发送邮件失败: {str(e)}"
            print(f"⚠️  {error_msg}")
            return False, error_msg


class TaskExecutor:
    """任务执行器"""
    
    def __init__(self, report_manager: ReportManager):
        """
        初始化任务执行器
        
        Args:
            report_manager: 报告管理器
        """
        self.report_manager = report_manager
        self.email_notifier = EmailNotifier()
    
    def execute_task(self, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务
        
        Args:
            task_config: 任务配置
            
        Returns:
            执行结果
        """
        execution_id = f"exec_{int(time.time() * 1000)}"
        task_id = task_config.get("task_id")
        if not task_id:
            raise ValueError("task_id 不能为空")
        
        task_name = task_config.get("task_name", "")
        business = task_config.get("business")
        if not business:
            raise ValueError("business 不能为空")
        
        environment = task_config.get("environment", "staging")
        
        start_time = int(time.time() * 1000)
        
        try:
            # 导入必要的模块
            from .sku_query_framework import SkuQueryFactory
            
            # 从JSONL文件加载预期值（每行一个用例的预期值）
            expected_values_file = task_config.get("expected_values_file")
            if not expected_values_file:
                raise ValueError("expected_values_file 不能为空")
            
            expected_values_list, error_msg = TaskConfigLoader.load_expected_values_from_jsonl(Path(expected_values_file))
            if error_msg:
                raise ValueError(f"预期值文件校验失败: {error_msg}")
            if not expected_values_list:
                raise ValueError(f"预期值文件为空: {expected_values_file}")
            
            # 为每个用例构建billing_data
            billing_datas = []
            for idx, expected_values in enumerate(expected_values_list):
                try:
                    # 从预期值中提取tolerance（必须存在，已在加载时校验）
                    tolerance = expected_values.pop("tolerance", {})
                    
                    # 提取真正的expected字段（JSONL文件中expected字段包含真正的预期值）
                    # 如果JSONL文件中没有expected字段，则使用整个expected_values（兼容旧格式）
                    expected_dict = expected_values.pop("expected", expected_values)
                    
                    # 提取其他元数据字段（不放入expected中）
                    case_name = expected_values.pop("case", f"用例 {idx + 1}")
                    # 提取vid、startTime、stopTime等字段用于查询（这些都是必需字段）
                    vid_from_data = expected_values.pop("vid", None)
                    start_time_from_data = expected_values.pop("startTime", None)
                    stop_time_from_data = expected_values.pop("stopTime", None)
                    
                    # 校验必需字段
                    missing_fields = []
                    if vid_from_data is None:
                        missing_fields.append("vid")
                    if start_time_from_data is None:
                        missing_fields.append("startTime")
                    if stop_time_from_data is None:
                        missing_fields.append("stopTime")
                    
                    # 如果缺少必需字段，记录错误但不中断任务
                    if missing_fields:
                        error_msg = f"缺少必需字段: {', '.join(missing_fields)}"
                        print(f"⚠️  用例 '{case_name}' {error_msg}，将标记为失败")
                        # 创建一个带有错误信息的billing_data
                        billing_data = {
                            "vid": vid_from_data or 0,
                            "startTime": start_time_from_data or 0,
                            "stopTime": stop_time_from_data or 0,
                            "case": case_name,
                            "expected": expected_dict,
                            "actual": {},
                            "tolerance": tolerance,
                            "error": error_msg,  # 标记错误信息
                            "_skip_query": True  # 标记跳过查询
                        }
                        billing_data.update(expected_values)
                        billing_datas.append(billing_data)
                        continue
                    
                    use_vid = vid_from_data
                    use_start_time = start_time_from_data
                    use_end_time = stop_time_from_data
                    
                    billing_data = {
                        "vid": use_vid,
                        "startTime": use_start_time,
                        "stopTime": use_end_time,
                        "case": case_name,
                        "expected": expected_dict,
                        "actual": {},
                        "tolerance": tolerance
                    }
                    # 将其他元数据字段也保存到billing_data中（如appId、cname、sql等）
                    billing_data.update(expected_values)
                    billing_datas.append(billing_data)
                    
                except Exception as e:
                    # 捕获其他可能的异常
                    case_name = expected_values.get("case", f"用例 {idx + 1}")
                    error_msg = f"处理用例数据时出错: {str(e)}"
                    print(f"⚠️  用例 '{case_name}' {error_msg}，将标记为失败")
                    billing_data = {
                        "vid": 0,
                        "startTime": 0,
                        "stopTime": 0,
                        "case": case_name,
                        "expected": {},
                        "actual": {},
                        "tolerance": {},
                        "error": error_msg,
                        "_skip_query": True
                    }
                    billing_datas.append(billing_data)
                    continue
            
            # 查询数据
            from .html_report_generator import load_report_config_from_business, HTMLReportGenerator
            from .sku_query_framework import QueryLogger
            
            # 创建查询日志记录器
            query_logger = QueryLogger()
            
            client = SkuQueryFactory.get_client(business, environment=environment, query_logger=query_logger)
            
            # 查询Detail数据（如果有detail字段）
            detail_fields_to_aggregate = []
            try:
                report_config = load_report_config_from_business(business)
                detail_fields_to_aggregate = report_config.get("detail_fields", [])
            except Exception as e:
                print(f"⚠️  从配置文件加载报告配置失败: {e}，将不处理 detail 字段")
            
            # 为每个用例查询数据（因为每个用例可能有不同的vid和时间范围）
            for billing_data in billing_datas:
                # 跳过标记为需要跳过查询的用例（有错误的用例）
                if billing_data.get("_skip_query"):
                    case_name = billing_data.get("case", "未知用例")
                    print(f"⚠️  跳过查询用例 '{case_name}'（数据错误）")
                    continue
                
                case_vid = billing_data.get("vid")
                case_start_time = billing_data.get("startTime")
                case_end_time = billing_data.get("stopTime")
                
                # 如果缺少必要参数，跳过
                if case_vid is None or case_start_time is None or case_end_time is None:
                    case_name = billing_data.get("case", "未知用例")
                    print(f"⚠️  警告: 用例 '{case_name}' 缺少必要参数 (vid, startTime, stopTime)，跳过查询")
                    continue
                
                # 查询SKU数据（添加错误处理，防止单个用例失败影响其他用例）
                case_name = billing_data.get("case", "未知用例")
                try:
                    aggregated_results, hourly_details = client.query_sku_across_hours(
                        vid=case_vid,
                        start_time=case_start_time,
                        end_time=case_end_time,
                        sku_ids=SkuQueryFactory.get_sku_ids(business),
                    )
                    
                    # 查询Detail数据（如果需要）
                    detail_aggregated = {}
                    if detail_fields_to_aggregate:
                        detail_aggregated = client.aggregate_detail_fields_across_hours(
                            vid=case_vid,
                            start_time=case_start_time,
                            end_time=case_end_time,
                            detail_fields=detail_fields_to_aggregate
                        )
                    
                    # 填充实际值
                    actual_dict = billing_data.setdefault("actual", {})
                    actual_dict.update(aggregated_results)
                    actual_dict.update(detail_aggregated)
                    
                    # 确保所有expected字段都在actual中存在（即使值为None）
                    # 这样报告中就会显示所有字段，而不是只显示有数据的字段
                    expected_dict = billing_data.get("expected", {})
                    for key in expected_dict.keys():
                        if key not in actual_dict:
                            actual_dict[key] = None
                    
                    print(f"✅  用例 '{case_name}' 查询成功")
                    
                except Exception as e:
                    # 查询失败，记录错误但继续处理其他用例
                    error_msg = f"查询数据失败: {str(e)}"
                    print(f"❌  用例 '{case_name}' {error_msg}")
                    billing_data["error"] = error_msg
                    # actual 保持为空字典，表示查询失败
                    continue
            
            # 生成HTML报告
            try:
                report_config = load_report_config_from_business(business)
                comparison_config = report_config.get("comparison_config")
                custom_columns = report_config.get("custom_columns")
            except Exception as e:
                print(f"⚠️  从配置文件加载报告配置失败: {e}，使用默认配置")
                comparison_config = None
                custom_columns = None
            
            html_generator = HTMLReportGenerator(
                comparison_config=comparison_config,
                custom_columns=custom_columns,
                output_dir=str(self.report_manager.base_dir)
            )
            
            # 生成报告内容
            html_content = html_generator._build_table_html(billing_datas)
            
            # 保存报告
            report_path = self.report_manager.save_report(task_id, execution_id, html_content)
            
            # 导出查询数据为jsonl文件
            jsonl_file_path = self._export_billing_data_to_jsonl(task_id, execution_id, billing_datas)
            
            # 保存查询日志文件
            log_file_path = self._save_query_logs(task_id, execution_id, query_logger)
            
            # 计算摘要（所有用例的汇总）
            summary = self._calculate_summary_all_cases(billing_datas, html_generator)
            
            # 发送邮件通知 - 从业务配置中读取收件人列表
            # 获取业务配置
            from .sku_query_framework import SkuQueryFactory
            configs = SkuQueryFactory._get_business_configs()
            business_config = configs.get(business, {})
            
            # 从业务配置中获取 email_config
            email_config = business_config.get("email_config", {})
            email_list = email_config.get("recipients", [])
            cc_list = email_config.get("cc", [])
            
            # 如果业务配置中没有配置收件人，尝试从 task_config 中获取（兼容旧方式）
            if not email_list:
                email_list = task_config.get("email_list", [])
            
            if email_list:
                notification_content = self._build_notification_content(
                    task_config.get("task_name", ""), task_id, execution_id, summary, 
                    report_path, task_config.get("_base_url", ""),
                    query_logs=query_logger.get_logs() if query_logger else None,
                    jsonl_file_path=jsonl_file_path,
                    log_file_path=log_file_path
                )
                subject = f"【{task_config.get('task_name', '定时任务')}】执行报告"
                success, error_msg = self.email_notifier.send_email(
                    subject, notification_content, email_list, cc_list
                )
                if not success:
                    print(f"⚠️  邮件通知发送失败: {error_msg}")
                else:
                    print(f"✅ 邮件通知已发送到: {', '.join(email_list)}")
                    if cc_list:
                        print(f"📧 抄送到: {', '.join(cc_list)}")
            else:
                print(f"⚠️  未配置收件人，跳过邮件通知")
            
            return {
                "execution_id": execution_id,
                "status": "success",
                "timestamp": start_time,
                "report_path": str(report_path),
                "jsonl_file_path": str(jsonl_file_path) if jsonl_file_path else None,
                "log_file_path": str(log_file_path) if log_file_path else None,
                "summary": summary,
                "error": None
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"⚠️  任务执行失败: {error_msg}")
            
            # 发送错误邮件通知 - 从业务配置中读取收件人列表
            try:
                from .sku_query_framework import SkuQueryFactory
                configs = SkuQueryFactory._get_business_configs()
                business_config = configs.get(business, {})
                
                # 从业务配置中获取 email_config
                email_config = business_config.get("email_config", {})
                email_list = email_config.get("recipients", [])
                cc_list = email_config.get("cc", [])
                
                # 如果业务配置中没有配置收件人，尝试从 task_config 中获取（兼容旧方式）
                if not email_list:
                    email_list = task_config.get("email_list", [])
                
                if email_list:
                    error_content = f"""## ❌ 任务执行失败

**任务名称**: {task_config.get('task_name', '')}
**任务ID**: {task_id}
**执行时间**: {datetime.fromtimestamp(start_time / 1000).strftime('%Y-%m-%d %H:%M:%S')}

**错误信息**: {error_msg}
"""
                    subject = f"【{task_config.get('task_name', '定时任务')}】执行失败"
                    self.email_notifier.send_email(
                        subject, error_content, email_list, cc_list
                    )
            except Exception as email_error:
                print(f"⚠️  发送失败邮件通知时出错: {email_error}")
            
            return {
                "execution_id": execution_id,
                "status": "failed",
                "timestamp": start_time,
                "report_path": None,
                "summary": None,
                "error": error_msg
            }
    
    def _calculate_summary_all_cases(self, billing_datas: List[Dict[str, Any]], 
                                     html_generator: Any) -> Dict[str, Any]:
        """
        计算所有用例的数据摘要
        
        Args:
            billing_datas: 计费数据列表
            html_generator: HTML报告生成器
            
        Returns:
            摘要信息
        """
        total_cases = len(billing_datas)
        passed_cases = 0
        failed_cases = 0
        
        for data in billing_datas:
            if html_generator._has_differences(data):
                failed_cases += 1
            else:
                passed_cases += 1
        
        pass_rate = (passed_cases / total_cases * 100) if total_cases > 0 else 0
        
        return {
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "failed_cases": failed_cases,
            "pass_rate": round(pass_rate, 1)
        }
    
    def _export_billing_data_to_jsonl(self, task_id: str, execution_id: str, 
                                     billing_datas: List[Dict[str, Any]]) -> Optional[Path]:
        """
        将查询数据导出为jsonl文件
        
        Args:
            task_id: 任务ID
            execution_id: 执行ID
            billing_datas: 计费数据列表
            
        Returns:
            jsonl文件路径，如果失败返回None
        """
        try:
            # 在报告目录下创建jsonl文件（使用reports_dir，与API查找路径一致）
            jsonl_dir = self.report_manager.reports_dir / task_id
            jsonl_dir.mkdir(parents=True, exist_ok=True)
            jsonl_file = jsonl_dir / f"{execution_id}_data.jsonl"
            
            with open(jsonl_file, 'w', encoding='utf-8') as f:
                for data in billing_datas:
                    # 转换为可序列化的格式
                    json.dump(data, f, ensure_ascii=False)
                    f.write('\n')
            
            print(f"✅ 查询数据已导出到: {jsonl_file}")
            return jsonl_file
        except Exception as e:
            print(f"⚠️  导出jsonl文件失败: {e}")
            return None
    
    def _save_query_logs(self, task_id: str, execution_id: str, 
                        query_logger: Any) -> Optional[Path]:
        """
        保存查询日志文件
        
        Args:
            task_id: 任务ID
            execution_id: 执行ID
            query_logger: 查询日志记录器
            
        Returns:
            日志文件路径，如果失败返回None
        """
        try:
            # 在报告目录下创建日志文件（使用reports_dir，与API查找路径一致）
            log_dir = self.report_manager.reports_dir / task_id
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"{execution_id}_query_logs.log"
            
            # 保存为可读的日志格式
            with open(log_file, 'w', encoding='utf-8') as f:
                for log in query_logger.get_logs():
                    timestamp = log.get("timestamp", "N/A")
                    query_type = log.get("query_type", "Unknown")
                    status = log.get("response_status", "N/A")
                    duration = log.get("duration_ms", 0)
                    error = log.get("error")
                    curl_cmd = log.get("curl_command", "")
                    response_text = log.get("response_text", "")
                    
                    # 写入时间戳和查询类型
                    f.write(f"[{timestamp}] {query_type} Query\n")
                    f.write(f"  Status: {status}\n")
                    f.write(f"  Duration: {duration:.2f}ms\n")
                    
                    if error:
                        f.write(f"  Error: {error}\n")
                    else:
                        summary = log.get("response_summary", {})
                        if isinstance(summary, dict) and "data_count" in summary:
                            count = summary.get("data_count", 0)
                            f.write(f"  Data Count: {count}\n")
                    
                    # 写入curl命令（单行）
                    f.write(f"  Curl Command: {curl_cmd}\n")
                    
                    # 写入curl返回结果
                    if response_text:
                        f.write(f"  Curl Response: {response_text}\n")
                    elif error:
                        f.write(f"  Curl Response: (Error occurred)\n")
                    else:
                        f.write(f"  Curl Response: (No response)\n")
                    
                    f.write("\n")
            
            print(f"✅ 查询日志已保存到: {log_file}")
            return log_file
        except Exception as e:
            print(f"⚠️  保存查询日志失败: {e}")
            return None
    
    def _build_notification_content(self, task_name: str, task_id: str, 
                                   execution_id: str, summary: Dict[str, Any],
                                   report_path: Path, base_url: str = "",
                                   query_logs: Optional[List[Dict[str, Any]]] = None,
                                   jsonl_file_path: Optional[Path] = None,
                                   log_file_path: Optional[Path] = None) -> str:
        """
        构建通知内容（邮件通知）- 紧凑版本
        
        Args:
            task_name: 任务名称
            task_id: 任务ID
            execution_id: 执行ID
            summary: 摘要信息
            report_path: 报告路径
            base_url: 服务基础URL，用于生成下载链接
            query_logs: 查询日志列表（可选）
            jsonl_file_path: jsonl文件路径（可选）
            log_file_path: 日志文件路径（可选）
            
        Returns:
            Markdown格式的通知内容
        """
        execution_time = datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')
        
        status_emoji = "✅" if summary["failed_cases"] == 0 else "⚠️"
        
        # 生成下载方式（URL或curl命令）
        if base_url:
            download_url = f"{base_url.rstrip('/')}/api/report/{execution_id}"
            download_info = f"**下载链接**: {download_url}"
        else:
            download_info = f"**执行ID**: `{execution_id}`"
        
        # 紧凑的邮件内容（减少空行和间距）
        content = f"""## {status_emoji} {task_name} 执行报告
**执行时间**: {execution_time} | **任务ID**: {task_id}
**数据摘要**: 总用例: {summary['total_cases']} | 通过: {summary['passed_cases']} | 失败: {summary['failed_cases']} | 通过率: {summary['pass_rate']}%
**报告下载**: {download_info}
"""
        
        # 添加文件下载链接
        if base_url:
            if jsonl_file_path and jsonl_file_path.exists():
                data_download_url = f"{base_url.rstrip('/')}/api/report/{execution_id}/data"
                content += f"**数据文件**: [下载 {jsonl_file_path.name}]({data_download_url})\n"
            
            if log_file_path and log_file_path.exists():
                log_download_url = f"{base_url.rstrip('/')}/api/report/{execution_id}/logs"
                content += f"**日志文件**: [下载 {log_file_path.name}]({log_download_url})\n"
        else:
            # 如果没有base_url，只显示文件名
            if jsonl_file_path and jsonl_file_path.exists():
                content += f"**数据文件**: `{jsonl_file_path.name}`\n"
            if log_file_path and log_file_path.exists():
                content += f"**日志文件**: `{log_file_path.name}`\n"
        
        return content


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, task_executor: TaskExecutor, report_manager: ReportManager):
        """
        初始化任务调度器
        
        Args:
            task_executor: 任务执行器
            report_manager: 报告管理器
        """
        self.task_executor = task_executor
        self.report_manager = report_manager
        self.tasks: Dict[str, Dict[str, Any]] = {}  # {task_id: {config, timer, ...}}
        self.execution_history: Dict[str, List[Dict[str, Any]]] = {}  # {task_id: [execution_results]}
        self.lock = threading.Lock()
    
    def add_task(self, task_config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        添加任务
        
        Args:
            task_config: 任务配置
            
        Returns:
            (是否成功, 错误信息)
        """
        task_id = task_config.get("task_id")
        if not task_id:
            return False, "task_id 不能为空"
        
        # 校验配置
        is_valid, error_msg = TaskConfigLoader.validate_task_config(task_config)
        if not is_valid:
            return False, error_msg
        
        with self.lock:
            if task_id in self.tasks:
                return False, f"任务 {task_id} 已存在"
            
            # 计算首次执行时间
            start_delay_minutes = task_config.get("start_delay_minutes", 30)
            
            # 创建一次性执行函数
            def execute_once():
                # 执行任务
                result = self.task_executor.execute_task(task_config)
                
                # 记录执行历史
                self._add_execution_history(task_id, result)
                
                # 清理旧历史（保留7天）
                self._cleanup_old_history()
                
                # 清理旧报告（保留7天）
                self.report_manager.cleanup_old_reports(days=7)
                
                # 任务执行完成后，从任务列表中移除（但保留在历史中）
                with self.lock:
                    if task_id in self.tasks:
                        del self.tasks[task_id]
            
            # 启动一次性执行定时器
            timer = threading.Timer(start_delay_minutes * 60, execute_once)
            timer.daemon = True
            
            self.tasks[task_id] = {
                "config": task_config,
                "timer": timer,
                "last_execution": None,
                "execution_count": 0
            }
            
            timer.start()
            
            return True, f"任务 {task_id} 已添加，将在 {start_delay_minutes} 分钟后执行一次"
    
    def remove_task(self, task_id: str) -> Tuple[bool, str]:
        """
        移除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            (是否成功, 错误信息)
        """
        with self.lock:
            if task_id not in self.tasks:
                return False, f"任务 {task_id} 不存在"
            
            # 停止定时器
            timer = self.tasks[task_id].get("timer")
            if timer:
                timer.cancel()
            
            # 删除任务
            del self.tasks[task_id]
            
            return True, f"任务 {task_id} 已移除"
    
    def run_task_manually(self, task_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        手动执行任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            (是否成功, 执行结果)
        """
        with self.lock:
            if task_id not in self.tasks:
                return False, {"error": f"任务 {task_id} 不存在"}
            
            task_config = self.tasks[task_id]["config"]
        
        # 执行任务
        result = self.task_executor.execute_task(task_config)
        
        # 记录执行历史
        self._add_execution_history(task_id, result)
        
        return True, result
    
    def _add_execution_history(self, task_id: str, result: Dict[str, Any]):
        """添加执行历史"""
        with self.lock:
            if task_id not in self.execution_history:
                self.execution_history[task_id] = []
            
            self.execution_history[task_id].append(result)
            self.tasks[task_id]["last_execution"] = result.get("timestamp")
            self.tasks[task_id]["execution_count"] += 1
    
    def _cleanup_old_history(self):
        """清理旧历史（保留7天）"""
        cutoff_time = int((datetime.now() - timedelta(days=7)).timestamp() * 1000)
        
        with self.lock:
            for task_id in list(self.execution_history.keys()):
                history = self.execution_history[task_id]
                # 过滤出7天内的记录
                self.execution_history[task_id] = [
                    h for h in history 
                    if h.get("timestamp", 0) >= cutoff_time
                ]
                
                # 如果历史为空，删除key
                if not self.execution_history[task_id]:
                    del self.execution_history[task_id]
    
    def get_task_list(self) -> List[Dict[str, Any]]:
        """获取任务列表"""
        with self.lock:
            result = []
            for task_id, task_info in self.tasks.items():
                result.append({
                    "task_id": task_id,
                    "task_name": task_info["config"].get("task_name"),
                    "business": task_info["config"].get("business"),
                    "environment": task_info["config"].get("environment"),
                    "interval_minutes": task_info["config"].get("interval_minutes"),
                    "last_execution": task_info.get("last_execution"),
                    "execution_count": task_info.get("execution_count", 0)
                })
            return result
    
    def get_task_history(self, task_id: str) -> List[Dict[str, Any]]:
        """获取任务执行历史"""
        with self.lock:
            return self.execution_history.get(task_id, [])


# Flask应用
app = Flask(__name__)

# 全局AppID管理器实例
appid_manager = None

# 全局认证Token
AUTH_TOKEN = "npYXxclHVCN2wvRWJeW57fTsCXz0r2GnFvxdS5ve5eJxrqFYTCQw03uFKwC-T7n0"

# 定时清理任务
cleanup_thread = None
cleanup_running = False

# 定时任务相关
task_scheduler = None
task_executor = None
report_manager = None


def generate_auth_token(length: int = 64) -> str:
    """
    生成安全的认证token
    
    Args:
        length: token长度（默认64字符，推荐32-128）
        
    Returns:
        随机生成的token字符串
    """
    # 使用大小写字母、数字和部分特殊字符
    alphabet = string.ascii_letters + string.digits + "-_"
    token = ''.join(secrets.choice(alphabet) for _ in range(length))
    return token


def cleanup_old_test_results():
    """清理2周前的测试结果数据"""
    global appid_manager
    if appid_manager is None:
        return
    
    try:
        result = appid_manager.clear_old_test_results(days=14)
        if result["total_removed"] > 0:
            print(f"[Cleanup] 清理了 {result['total_removed']} 条2周前的测试数据，保留了 {result['total_kept']} 条")
            if result["removed_by_product"]:
                for product, count in result["removed_by_product"].items():
                    print(f"  - {product}: {count} 条")
    except Exception as e:
        print(f"[Cleanup Error] 清理测试数据时出错: {str(e)}")


def cleanup_task_worker():
    """定时清理任务的工作线程"""
    global cleanup_running
    while cleanup_running:
        try:
            # 每天凌晨2点执行清理（避免影响正常使用）
            # 这里简化为每24小时执行一次
            time.sleep(24 * 3600)  # 24小时
            if cleanup_running:
                cleanup_old_test_results()
        except Exception as e:
            print(f"[Cleanup Task Error] {str(e)}")
            # 出错后等待1小时再重试
            time.sleep(3600)


def start_cleanup_task():
    """启动定时清理任务"""
    global cleanup_thread, cleanup_running
    
    if cleanup_thread is not None and cleanup_thread.is_alive():
        return  # 任务已在运行
    
    cleanup_running = True
    cleanup_thread = threading.Thread(target=cleanup_task_worker, daemon=True)
    cleanup_thread.start()
    print("✓ 定时清理任务已启动（每24小时清理一次2周前的测试数据）")


def stop_cleanup_task():
    """停止定时清理任务"""
    global cleanup_running, cleanup_thread
    
    cleanup_running = False
    if cleanup_thread is not None:
        cleanup_thread.join(timeout=5)
    print("定时清理任务已停止")


def init_appid_manager():
    """初始化AppID管理器"""
    global appid_manager
    
    appid_manager = AppIdManager()
    print("AppID Manager initialized (empty)")
    
    # 启动定时清理任务
    start_cleanup_task()


def init_task_scheduler():
    """初始化任务调度器"""
    global task_scheduler, task_executor, report_manager
    
    try:
        # 尝试相对导入（作为包的一部分）
        try:
            from .config_init import get_config_dir, get_config_locations
        except ImportError:
            # 如果相对导入失败，尝试绝对导入（直接运行或作为模块运行）
            from sku_template.config_init import get_config_dir, get_config_locations
        
        # 打印配置查找信息（用于调试）
        locations = get_config_locations()
        print(f"🔍 配置目录查找路径: {[str(loc) for loc in locations]}")
        
        config_dir = get_config_dir()
        
        if config_dir is None:
            print("⚠️  未找到配置目录，任务调度器未初始化")
            print("   提示: 配置目录必须包含 common.json 文件")
            print("   检查的路径:")
            for loc in locations:
                common_file = loc / "common.json"
                exists = "✓" if common_file.exists() else "✗"
                print(f"     {exists} {loc}/common.json")
            return
        
        print(f"✓ 使用配置目录: {config_dir}")
        
        # 确定报告目录（使用数据目录）
        data_dir = os.environ.get('SKU_DATA_DIR')
        if data_dir:
            reports_base_dir = Path(data_dir) / "reports"
        else:
            # 如果没有设置数据目录，使用配置目录的父目录下的 data/reports
            reports_base_dir = config_dir.parent / "data" / "reports"
        
        reports_base_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ 报告目录: {reports_base_dir}")
        
        # 初始化报告管理器
        report_manager = ReportManager(reports_base_dir)
        
        # 初始化任务执行器
        task_executor = TaskExecutor(report_manager)
        
        # 初始化任务调度器
        task_scheduler = TaskScheduler(task_executor, report_manager)
        
        # 加载任务配置
        tasks_file = config_dir / "tasks.jsonl"
        if tasks_file.exists():
            tasks = TaskConfigLoader.load_tasks_from_jsonl(tasks_file)
            loaded_count = 0
            failed_count = 0
            
            for task_config in tasks:
                is_valid, error_msg = TaskConfigLoader.validate_task_config(task_config)
                if is_valid:
                    success, message = task_scheduler.add_task(task_config)
                    if success:
                        loaded_count += 1
                        print(f"✓ 任务已加载: {task_config.get('task_id')} - {task_config.get('task_name')}")
                    else:
                        failed_count += 1
                        print(f"⚠️  任务加载失败: {task_config.get('task_id')} - {message}")
                else:
                    failed_count += 1
                    print(f"⚠️  任务配置无效: {task_config.get('task_id', 'unknown')} - {error_msg}")
            
            print(f"✓ 任务调度器已初始化: 成功加载 {loaded_count} 个任务，失败 {failed_count} 个")
        else:
            print("✓ 任务调度器已初始化（无任务配置）")
    except Exception as e:
        print(f"⚠️  初始化任务调度器失败: {e}")
        import traceback
        traceback.print_exc()


def verify_auth():
    """
    验证请求的认证信息
    支持两种方式：
    1. Authorization: Bearer <token>
    2. X-API-Key: <token>
    
    Returns:
        None if auth valid, Response object if auth invalid
    """
    if AUTH_TOKEN is None:
        # 如果没有配置token，不需要认证
        return None
    
    # 从请求头获取token
    auth_header = request.headers.get('Authorization', '')
    api_key = request.headers.get('X-API-Key', '')
    
    token = None
    
    # 尝试从 Authorization header 获取 Bearer token
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]  # 去掉 'Bearer ' 前缀
    
    # 或者从 X-API-Key header 获取
    if not token and api_key:
        token = api_key
    
    # 验证token
    if not token:
        return jsonify({
            "error": "unauthorized",
            "message": "Authentication required. Please provide token via 'Authorization: Bearer <token>' or 'X-API-Key: <token>' header"
        }), 401
    
    if token != AUTH_TOKEN:
        return jsonify({
            "error": "unauthorized",
            "message": "Invalid authentication token"
        }), 401
    
    return None


@app.before_request
def check_auth():
    """请求前检查认证（health接口除外）"""
    # health接口不需要认证
    if request.path == '/health':
        return None
    
    # 其他所有接口都需要认证
    return verify_auth()


@app.route('/api/appid/acquire', methods=['POST'])
def acquire_appid():
    """获取可用的AppID"""
    if appid_manager is None:
        return jsonify({"error": "service_unavailable", "message": "AppID Manager not initialized"}), 500
    
    try:
        data = request.get_json() or {}
        product_name = data.get('productName')
        force_acquire = data.get('forceAcquire', False)  # 默认为False，保持向后兼容
        
        if not product_name:
            return jsonify({"error": "missing_product_name", "message": "productName is required"}), 400
        
        success, result = appid_manager.acquire_appid(product_name, force_acquire=force_acquire)
        if success:
            return jsonify(result), 200
        else:
            return jsonify(result), 202  # Accepted but waiting
    except Exception as e:
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route('/api/appid/release', methods=['POST'])
def release_appid():
    """释放AppID"""
    if appid_manager is None:
        return jsonify({"error": "service_unavailable", "message": "AppID Manager not initialized"}), 500
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "missing_data", "message": "Request body is required"}), 400
        
        appid = data.get('appid')
        product_name = data.get('productName')
        
        if not appid:
            return jsonify({"error": "missing_appid", "message": "appid is required"}), 400
        
        if not product_name:
            return jsonify({"error": "missing_product_name", "message": "productName is required"}), 400
        
        success, result = appid_manager.release_appid(appid, product_name)
        
        if success:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route('/api/appid/status', methods=['GET'])
def get_status():
    """获取AppID状态统计"""
    if appid_manager is None:
        return jsonify({"error": "service_unavailable", "message": "AppID Manager not initialized"}), 500
    
    try:
        product_name = request.args.get('productName')
        status = appid_manager.get_status(product_name)
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route('/api/appid/init', methods=['POST'])
def init_product():
    """初始化或重置产品AppID配置"""
    if appid_manager is None:
        return jsonify({"error": "service_unavailable", "message": "AppID Manager not initialized"}), 500
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "missing_data", "message": "Request body is required"}), 400
        
        product_name = data.get('productName')
        appids = data.get('appids')
        
        if not product_name:
            return jsonify({"error": "missing_product_name", "message": "productName is required"}), 400
        
        if not appids:
            return jsonify({"error": "missing_appids", "message": "appids is required"}), 400
        
        success, result = appid_manager.init_product(product_name, appids)
        if success:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route('/api/test/result', methods=['POST'])
def store_test_result():
    """存储测试用例执行数据"""
    if appid_manager is None:
        return jsonify({"error": "service_unavailable"}), 500
    
    data = request.get_json() or {}
    product_name = data.get('product_name') or data.get('productName')
    session_id = data.get('session_id')
    test_data = data.get('test_data')
    
    if not product_name or not session_id or test_data is None:
        return jsonify({"error": "missing_required_fields"}), 400
    
    appid_manager.store_test_result(product_name, session_id, test_data)
    return jsonify({"success": True}), 200


@app.route('/api/test/results', methods=['GET'])
def get_test_results():
    """获取测试用例执行数据"""
    if appid_manager is None:
        return jsonify({"error": "service_unavailable"}), 500
    
    product_name = request.args.get('product_name') or request.args.get('productName')
    session_id = request.args.get('session_id')
    results = appid_manager.get_test_results(product_name, session_id)
    return jsonify(results), 200


@app.route('/api/test/results/clear', methods=['POST'])
def clear_test_results():
    """清除测试用例执行数据"""
    if appid_manager is None:
        return jsonify({"error": "service_unavailable"}), 500
    
    data = request.get_json() or {}
    product_name = data.get('product_name') or data.get('productName')
    session_id = data.get('session_id')
    
    appid_manager.clear_test_results(product_name, session_id)
    return jsonify({"success": True}), 200


@app.route('/api/test/results/cleanup', methods=['POST'])
def cleanup_old_results():
    """手动触发清理2周前的测试数据"""
    if appid_manager is None:
        return jsonify({"error": "service_unavailable"}), 500
    
    try:
        data = request.get_json() or {}
        days = data.get('days', 14)  # 默认14天（2周）
        
        result = appid_manager.clear_old_test_results(days=days)
        return jsonify({
            "success": True,
            "result": result
        }), 200
    except Exception as e:
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({"status": "healthy", "timestamp": int(time.time() * 1000)}), 200


# ==================== 定时任务API接口 ====================

@app.route('/api/task/init', methods=['POST'])
def init_task_scheduler_api():
    """
    通过API初始化任务调度器（类似 /api/appid/init）
    
    这是一个全新的功能，通过API动态初始化任务调度器，支持上传配置文件。
    
    接收参数（multipart/form-data）：
    - business_name: 业务名称（必填）
    - business_config_file: 业务配置文件（可选，如果上传则保存到配置目录）
    - common_config_file: common.json 配置文件（可选，如果上传则保存到配置目录）
    - data_dir: 数据目录路径（可选，默认使用当前目录下的 data）
    
    说明：
    - 服务器上使用当前工作目录下的 `sku-config` 作为配置目录
    - 如果上传了配置文件，保存到配置目录
    - 如果配置文件已存在于配置目录，直接使用
    - 如果既没有上传文件也没有已存在的文件，返回错误
    - 只清除指定业务的缓存，不影响其他业务
    - 初始化成功后，任务调度器就可以使用了
    """
    global task_scheduler, task_executor, report_manager
    
    try:
        # 获取参数
        business_name = request.form.get('business_name')
        data_dir_path = request.form.get('data_dir')
        
        # 获取上传的文件
        business_config_file = request.files.get('business_config_file')
        common_config_file = request.files.get('common_config_file')
        
        # 校验必需参数
        if not business_name:
            return jsonify({"error": "missing_parameter", "message": "business_name 参数是必填的"}), 400
        
        # 服务器上使用当前工作目录下的 sku-config 作为配置目录
        config_path = Path.cwd() / "sku-config"
        config_path.mkdir(parents=True, exist_ok=True)
        
        # 处理 common.json 文件
        common_config_path = config_path / "common.json"
        if common_config_file and common_config_file.filename:
            # 如果上传了 common.json，保存它
            file_content = common_config_file.read().decode('utf-8')
            try:
                # 验证JSON格式
                json.loads(file_content)
                with open(common_config_path, 'w', encoding='utf-8') as f:
                    f.write(file_content)
            except json.JSONDecodeError as e:
                return jsonify({"error": "invalid_json", "message": f"common.json 格式错误: {e}"}), 400
        elif not common_config_path.exists():
            # 如果不存在且没有上传，创建空的 common.json
            with open(common_config_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=2)
        
        # 处理业务配置文件
        businesses_dir = config_path / "businesses"
        businesses_dir.mkdir(parents=True, exist_ok=True)
        business_config_path = businesses_dir / f"{business_name}.json"
        
        if business_config_file and business_config_file.filename:
            # 如果上传了业务配置文件，保存它
            file_content = business_config_file.read().decode('utf-8')
            try:
                # 验证JSON格式
                business_config = json.loads(file_content)
                with open(business_config_path, 'w', encoding='utf-8') as f:
                    json.dump(business_config, f, indent=2, ensure_ascii=False)
            except json.JSONDecodeError as e:
                return jsonify({"error": "invalid_json", "message": f"业务配置文件JSON格式错误: {e}"}), 400
        elif not business_config_path.exists():
            # 如果没有上传且文件不存在，返回错误
            return jsonify({
                "error": "business_config_not_found",
                "message": f"业务配置文件不存在: {business_config_path}",
                "hint": f"请确保配置文件存在于: {business_config_path}，或者上传 business_config_file 参数"
            }), 400
        
        # 设置配置目录
        try:
            from .config_init import set_config_dir
        except ImportError:
            from sku_template.config_init import set_config_dir
        set_config_dir(config_path)
        
        # 导入 SkuQueryFactory（用于加载和清除业务配置）
        from .sku_query_framework import SkuQueryFactory
        
        # 验证业务配置文件格式（再次验证，确保文件有效）
        try:
            with open(business_config_path, 'r', encoding='utf-8') as f:
                json.load(f)  # 验证JSON格式
        except json.JSONDecodeError as e:
            return jsonify({"error": "invalid_json", "message": f"业务配置文件JSON格式错误: {e}"}), 400
        
        # 只清除该业务的缓存，不影响其他业务
        if business_name in SkuQueryFactory._BUSINESS_CONFIGS:
            del SkuQueryFactory._BUSINESS_CONFIGS[business_name]
        
        # 验证业务配置是否可以加载
        try:
            configs = SkuQueryFactory._get_business_configs()
            if business_name not in configs:
                return jsonify({
                    "error": "business_config_load_failed",
                    "message": f"业务配置加载失败: {business_name}",
                    "hint": "请检查业务配置文件格式是否正确"
                }), 400
        except Exception as e:
            return jsonify({
                "error": "business_config_load_failed",
                "message": f"业务配置加载失败: {str(e)}"
            }), 400
        
        # 设置数据目录
        if data_dir_path:
            data_path = Path(data_dir_path)
            data_path.mkdir(parents=True, exist_ok=True)
            os.environ['SKU_DATA_DIR'] = str(data_path)
        else:
            # 默认数据目录：当前工作目录下的 data
            data_path = Path.cwd() / "data"
            data_path.mkdir(parents=True, exist_ok=True)
            os.environ['SKU_DATA_DIR'] = str(data_path)
        
        # 确定报告目录
        reports_base_dir = Path(os.environ.get('SKU_DATA_DIR')) / "reports"
        reports_base_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化报告管理器
        report_manager = ReportManager(reports_base_dir)
        
        # 初始化任务执行器
        task_executor = TaskExecutor(report_manager)
        
        # 初始化任务调度器
        task_scheduler = TaskScheduler(task_executor, report_manager)
        
        result = {
            "success": True,
            "message": "任务调度器初始化成功",
            "config_dir": str(config_path),
            "data_dir": str(data_path),
            "reports_dir": str(reports_base_dir),
            "business_name": business_name,
            "business_config_file": str(business_config_path)
        }
        
        # 如果上传了文件，添加到响应中
        if business_config_file and business_config_file.filename:
            result["business_config_uploaded"] = True
        if common_config_file and common_config_file.filename:
            result["common_config_uploaded"] = True
        
        return jsonify(result), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route('/api/task/add', methods=['POST'])
def add_task():
    """添加一次性任务
    
    接收参数：
    - business: 业务名称（必填）
    - environment: 环境（必填，staging/prod）
    - start_delay_minutes: 执行延迟（分钟，必填），任务将在延迟后执行一次
    - expected_values_file: 上传的JSONL文件（必填），包含用例的预期值
    
    说明：
    - 任务是一次性的，执行完成后自动结束，不会重复执行
    - 查询时间范围固定为过去24小时
    - 邮件收件人配置在业务配置文件的 email_config 中（recipients 和 cc 字段）
    - Jenkins 邮件发送凭证已在代码中配置
    """
    global task_scheduler
    
    if task_scheduler is None:
        return jsonify({"error": "service_unavailable", "message": "Task scheduler not initialized"}), 500
    
    try:
        # 获取参数
        business = request.form.get('business')
        environment = request.form.get('environment')
        start_delay_minutes = request.form.get('start_delay_minutes')
        
        # 获取上传的文件
        if 'expected_values_file' not in request.files:
            return jsonify({"error": "missing_file", "message": "expected_values_file is required"}), 400
        
        file = request.files['expected_values_file']
        if file.filename == '':
            return jsonify({"error": "missing_file", "message": "expected_values_file is required"}), 400
        
        # 校验必需参数
        if not business:
            return jsonify({"error": "missing_parameter", "message": "business is required"}), 400
        if not environment:
            return jsonify({"error": "missing_parameter", "message": "environment is required"}), 400
        if not start_delay_minutes:
            return jsonify({"error": "missing_parameter", "message": "start_delay_minutes is required"}), 400
        
        # 解析参数
        try:
            start_delay_minutes = int(start_delay_minutes)
        except (ValueError, json.JSONDecodeError) as e:
            return jsonify({"error": "invalid_parameter", "message": f"参数格式错误: {e}"}), 400
        
        # 读取上传的文件内容
        file_content = file.read().decode('utf-8')
        
        # 先校验文件内容（临时保存到内存中校验）
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = Path(tmp_file.name)
        
        try:
            # 加载并校验预期值
            expected_values_list, error_msg = TaskConfigLoader.load_expected_values_from_jsonl(tmp_file_path)
            if error_msg:
                return jsonify({"error": "invalid_expected_values", "message": error_msg}), 400
        finally:
            # 删除临时文件
            tmp_file_path.unlink()
        
        # 获取配置目录（用于验证业务配置）
        try:
            from .config_init import get_config_dir
        except ImportError:
            from sku_template.config_init import get_config_dir
        config_dir = get_config_dir()
        if not config_dir:
            return jsonify({"error": "config_not_found", "message": "配置目录未找到"}), 500
        
        # 获取数据目录（用于保存预期值文件和报告）
        data_dir = os.environ.get('SKU_DATA_DIR')
        if not data_dir:
            # 如果没有设置数据目录，使用配置目录的父目录下的 data 目录
            data_dir = str(config_dir.parent / "data")
        data_dir_path = Path(data_dir)
        data_dir_path.mkdir(parents=True, exist_ok=True)
        
        # 生成task_id（business_UUID格式）
        task_id = f"{business}_{uuid.uuid4().hex[:8]}"
        
        # 保存预期值文件到数据目录
        expected_values_dir = data_dir_path / "task_expected_values"
        expected_values_dir.mkdir(parents=True, exist_ok=True)
        expected_values_file = expected_values_dir / f"{task_id}.jsonl"
        with open(expected_values_file, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        # 验证业务配置是否存在
        from .sku_query_framework import SkuQueryFactory
        configs = SkuQueryFactory._get_business_configs()
        if business not in configs:
            return jsonify({"error": "business_not_found", "message": f"业务 '{business}' 未在配置中初始化"}), 400
        
        # 构建任务配置（一次性任务）
        # 邮件收件人将从业务配置的 email_config 中读取
        task_config = {
            "task_id": task_id,
            "task_name": f"{business}监控任务",
            "business": business,
            "environment": environment,
            "start_delay_minutes": start_delay_minutes,
            "expected_values_file": str(expected_values_file),
            "_base_url": request.host_url.rstrip('/')  # 保存base_url用于生成下载链接
        }
        
        # 校验配置
        is_valid, error_msg = TaskConfigLoader.validate_task_config(task_config)
        if not is_valid:
            return jsonify({"error": "invalid_config", "message": error_msg}), 400
        
        # 添加到调度器
        success, message = task_scheduler.add_task(task_config)
        if success:
            return jsonify({
                "success": True,
                "task_id": task_id,
                "message": message
            }), 200
        else:
            return jsonify({"error": "add_failed", "message": message}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route('/api/task/list', methods=['GET'])
def list_tasks():
    """获取任务列表"""
    global task_scheduler
    
    if task_scheduler is None:
        return jsonify({"error": "service_unavailable", "message": "Task scheduler not initialized"}), 500
    
    try:
        tasks = task_scheduler.get_task_list()
        return jsonify({"tasks": tasks}), 200
    except Exception as e:
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route('/api/task/<task_id>', methods=['DELETE'])
def remove_task(task_id):
    """删除任务"""
    global task_scheduler
    
    if task_scheduler is None:
        return jsonify({"error": "service_unavailable", "message": "Task scheduler not initialized"}), 500
    
    try:
        success, message = task_scheduler.remove_task(task_id)
        if success:
            # 从配置文件删除
            try:
                from .config_init import get_config_dir
            except ImportError:
                from sku_template.config_init import get_config_dir
            config_dir = get_config_dir()
            if config_dir:
                tasks_file = config_dir / "tasks.jsonl"
                TaskConfigLoader.remove_task_from_jsonl(tasks_file, task_id)
            
            return jsonify({"success": True, "message": message}), 200
        else:
            return jsonify({"error": "remove_failed", "message": message}), 400
    except Exception as e:
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route('/api/task/<task_id>/run', methods=['POST'])
def run_task(task_id):
    """手动触发执行任务"""
    global task_scheduler
    
    if task_scheduler is None:
        return jsonify({"error": "service_unavailable", "message": "Task scheduler not initialized"}), 500
    
    try:
        success, result = task_scheduler.run_task_manually(task_id)
        if success:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route('/api/task/<task_id>/history', methods=['GET'])
def get_task_history(task_id):
    """获取任务执行历史"""
    global task_scheduler
    
    if task_scheduler is None:
        return jsonify({"error": "service_unavailable", "message": "Task scheduler not initialized"}), 500
    
    try:
        history = task_scheduler.get_task_history(task_id)
        return jsonify({"task_id": task_id, "history": history}), 200
    except Exception as e:
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route('/api/report/<execution_id>', methods=['GET'])
def download_report(execution_id):
    """下载HTML报告"""
    global report_manager
    
    if report_manager is None:
        return jsonify({"error": "service_unavailable", "message": "Report manager not initialized"}), 500
    
    try:
        # 从execution_id提取task_id（格式：exec_{timestamp}）
        # 需要遍历所有任务目录查找
        reports = report_manager.list_reports(days=7)
        
        for report in reports:
            if report["execution_id"] == execution_id:
                report_path = Path(report["file_path"])
                if report_path.exists():
                    return send_file(str(report_path), mimetype='text/html', 
                                   as_attachment=True, download_name=report["file_name"])
        
        return jsonify({"error": "not_found", "message": f"报告 {execution_id} 不存在"}), 404
    except Exception as e:
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route('/api/report/<execution_id>/data', methods=['GET'])
def download_report_data(execution_id):
    """下载数据文件（jsonl）"""
    global report_manager
    
    if report_manager is None:
        return jsonify({"error": "service_unavailable", "message": "Report manager not initialized"}), 500
    
    try:
        # 从execution_id提取task_id（格式：exec_{timestamp}）
        # 需要遍历所有任务目录查找
        reports = report_manager.list_reports(days=7)
        
        for report in reports:
            if report["execution_id"] == execution_id:
                task_id = report["task_id"]
                # 查找jsonl文件
                data_file = report_manager.reports_dir / task_id / f"{execution_id}_data.jsonl"
                if data_file.exists():
                    return send_file(str(data_file), mimetype='application/jsonl', 
                                   as_attachment=True, download_name=f"{execution_id}_data.jsonl")
        
        return jsonify({"error": "not_found", "message": f"数据文件 {execution_id}_data.jsonl 不存在"}), 404
    except Exception as e:
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route('/api/report/<execution_id>/logs', methods=['GET'])
def download_report_logs(execution_id):
    """下载日志文件（log）"""
    global report_manager
    
    if report_manager is None:
        return jsonify({"error": "service_unavailable", "message": "Report manager not initialized"}), 500
    
    try:
        # 从execution_id提取task_id（格式：exec_{timestamp}）
        # 需要遍历所有任务目录查找
        reports = report_manager.list_reports(days=7)
        
        for report in reports:
            if report["execution_id"] == execution_id:
                task_id = report["task_id"]
                # 查找log文件
                log_file = report_manager.reports_dir / task_id / f"{execution_id}_query_logs.log"
                if log_file.exists():
                    return send_file(str(log_file), mimetype='text/plain', 
                                   as_attachment=True, download_name=f"{execution_id}_query_logs.log")
        
        return jsonify({"error": "not_found", "message": f"日志文件 {execution_id}_query_logs.log 不存在"}), 404
    except Exception as e:
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route('/api/report/list', methods=['GET'])
def list_reports():
    """获取报告列表"""
    global report_manager
    
    if report_manager is None:
        return jsonify({"error": "service_unavailable", "message": "Report manager not initialized"}), 500
    
    try:
        task_id = request.args.get('task_id')
        days = int(request.args.get('days', 7))
        
        reports = report_manager.list_reports(task_id=task_id, days=days)
        return jsonify({"reports": reports}), 200
    except Exception as e:
        return jsonify({"error": "internal_error", "message": str(e)}), 500


def main():
    """主函数"""
    global AUTH_TOKEN
    
    parser = argparse.ArgumentParser(description='AppID Manager Service')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0 for external access, use 127.0.0.1 for localhost only)')
    parser.add_argument('--port', type=int, default=8888, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--auth-token', default=None, 
                       help='Authentication token (or set APPID_AUTH_TOKEN env var). If not set, authentication is disabled.')
    parser.add_argument('--generate-token', action='store_true',
                       help='Generate a secure authentication token and exit')
    parser.add_argument('--token-length', type=int, default=64,
                       help='Token length when using --generate-token (default: 64, recommended: 32-128)')
    parser.add_argument('--config-dir', default=None, type=str,
                       help='Configuration directory path (or set SKU_CONFIG_DIR env var). Priority: command line > env var > system defaults')
    parser.add_argument('--data-dir', default=None, type=str,
                       help='Data directory path for storing uploaded task files, reports, and logs (or set SKU_DATA_DIR env var). Default: <config_dir>/../data or ./data. Optional if default location is acceptable.')
    
    args = parser.parse_args()
    
    # 如果只是生成token，生成后退出
    if args.generate_token:
        token = generate_auth_token(args.token_length)
        print("\n" + "="*70)
        print("Generated Authentication Token:")
        print("="*70)
        print(token)
        print("="*70)
        print("\nUsage examples:")
        print(f"  # Start service with this token:")
        print(f"  python3.11 appid_manager_service.py --auth-token \"{token}\"")
        print(f"\n  # Or set environment variable:")
        print(f"  export APPID_AUTH_TOKEN=\"{token}\"")
        print(f"  python3.11 appid_manager_service.py")
        print("\n" + "="*70)
        return
    
    # 设置认证token（优先使用命令行参数，其次使用环境变量）
    AUTH_TOKEN = args.auth_token or os.environ.get('APPID_AUTH_TOKEN')
    
    # 设置配置目录（优先级：命令行参数 > 环境变量 > 自动查找）
    if args.config_dir:
        config_dir_path = Path(args.config_dir)
        if not config_dir_path.exists():
            print(f"⚠️  警告: 指定的配置目录不存在: {config_dir_path}")
            print(f"   将使用自动查找的配置目录")
        else:
            try:
                from .config_init import set_config_dir
            except ImportError:
                from sku_template.config_init import set_config_dir
            set_config_dir(config_dir_path)
            print(f"✓ 使用指定的配置目录: {config_dir_path}")
    elif os.environ.get('SKU_CONFIG_DIR'):
        config_dir_path = Path(os.environ.get('SKU_CONFIG_DIR'))
        if config_dir_path.exists():
            try:
                from .config_init import set_config_dir
            except ImportError:
                from sku_template.config_init import set_config_dir
            set_config_dir(config_dir_path)
            print(f"✓ 使用环境变量配置目录: {config_dir_path}")
    
    # 设置数据目录（优先级：命令行参数 > 环境变量 > 默认值）
    # 数据目录用于保存：
    # 1. 上传的预期值文件（通过 /api/task/add 上传，需要持久化因为任务可能延迟执行）
    # 2. 任务执行后生成的HTML报告
    # 3. 查询日志文件
    # 注意：即使不指定 --data-dir，系统也会使用默认位置自动创建数据目录
    if args.data_dir:
        data_dir_path = Path(args.data_dir)
        data_dir_path.mkdir(parents=True, exist_ok=True)
        os.environ['SKU_DATA_DIR'] = str(data_dir_path)
        print(f"✓ 使用指定的数据目录: {data_dir_path}")
    elif os.environ.get('SKU_DATA_DIR'):
        data_dir_path = Path(os.environ.get('SKU_DATA_DIR'))
        data_dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ 使用环境变量数据目录: {data_dir_path}")
    else:
        # 默认数据目录：配置目录的父目录下的 data 目录，或当前目录下的 data
        # 系统会自动创建，用户无需手动指定（除非需要自定义位置）
        try:
            from .config_init import get_config_dir
            config_dir = get_config_dir()
            if config_dir:
                data_dir_path = config_dir.parent / "data"
            else:
                data_dir_path = Path.cwd() / "data"
            data_dir_path.mkdir(parents=True, exist_ok=True)
            os.environ['SKU_DATA_DIR'] = str(data_dir_path)
            print(f"✓ 使用默认数据目录: {data_dir_path} (上传的文件和报告将保存在此目录)")
        except Exception as e:
            print(f"⚠️  设置数据目录失败: {e}")
    
    # 初始化AppID管理器
    init_appid_manager()
    
    # 初始化任务调度器
    init_task_scheduler()
    
    print(f"Starting AppID Manager Service on {args.host}:{args.port}")
    
    if AUTH_TOKEN:
        print(f"✓ Authentication enabled (token configured)")
        print("  All API requests require authentication via:")
        print("    - Authorization: Bearer <token>")
        print("    - or X-API-Key: <token>")
    else:
        print("⚠ Authentication disabled (no token configured)")
        print("  WARNING: Service is accessible without authentication!")
    
    print("\nAvailable endpoints:")
    print("  【AppID管理接口】")
    print("  POST /api/appid/acquire - Get available appid (requires auth)")
    print("  POST /api/appid/release - Release appid (requires auth)")
    print("  GET  /api/appid/status  - Get status (requires auth)")
    print("  POST /api/appid/init    - Initialize product (requires auth)")
    print("  【测试结果存储接口】")
    print("  POST /api/test/result   - Store test result (requires auth)")
    print("  GET  /api/test/results   - Get test results (JSON, requires auth)")
    print("  POST /api/test/results/clear - Clear test results (requires auth)")
    print("  【定时任务接口】")
    print("  POST /api/task/add - Add task (requires auth)")
    print("  GET  /api/task/list - List all tasks (requires auth)")
    print("  DELETE /api/task/<task_id> - Remove task (requires auth)")
    print("  POST /api/task/<task_id>/run - Manually run task (requires auth)")
    print("  GET  /api/task/<task_id>/history - Get task execution history (requires auth)")
    print("  GET  /api/report/<execution_id> - Download report (requires auth)")
    print("  GET  /api/report/list - List reports (requires auth)")
    print("  【通用接口】")
    print("  GET  /health            - Health check (no auth required)")
    
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
