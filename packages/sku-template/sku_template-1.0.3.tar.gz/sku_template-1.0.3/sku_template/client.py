"""
AppID客户端SDK
提供AppID的获取和释放功能，支持轮询等待
"""
import time
import requests
from typing import Tuple, Optional, Dict, List, Any
from .sku_query_framework import SkuQueryFactory
from pathlib import Path


class AppIdClient:
    """AppID客户端"""
    
    def __init__(self, base_url: str, auth_token: str, product_name: Optional[str] = None, timeout: int = 5):
        """
        初始化AppID客户端
        
        Args:
            base_url: 服务端地址（必填）
            auth_token: 认证token（必填）
            product_name: 产品名称，如果指定则在调用时自动使用（可选）
            timeout: 请求超时时间（秒），默认5秒
        """
        if not base_url or not auth_token:
            raise ValueError("base_url and auth_token are required")
        
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.auth_token = auth_token
        self.product_name = product_name  # 保存默认的产品名称
                # 检查产品配置是否存在，不存在则初始化
        if product_name:
            result = self.get_status(product_name)
            if result is None or result.get("total") == 0:
                print("初始化产品配置...")
                # 从配置文件加载AppID配置
                appids = SkuQueryFactory.get_appids(business=product_name)
                if not appids:
                    raise ValueError("无法从配置文件加载AppID配置，请检查配置文件")
                print("appids================", appids)
                self.init_product(appIds=appids)
                print(f"产品 '{product_name}' 初始化完成，共 {len(appids)} 个AppID")
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头（包含认证信息）"""
        headers = {}
        if self.auth_token:
            # 使用 X-API-Key header
            headers['X-API-Key'] = self.auth_token
        return headers
    
    def acquire_appid(self, product_name: Optional[str] = None, max_retries: int = 61, retry_interval: int = 60, force_acquire: bool = False) -> Tuple[str, int, int, str]:
        """
        获取可用的AppID，支持轮询等待
        
        Args:
            product_name: 产品名称，用于隔离不同业务的AppID（可选）
                        如果未指定，使用初始化时的 product_name
            max_retries: 最大重试次数
            retry_interval: 重试间隔（秒）
            force_acquire: 是否强制获取（忽略小时内使用检查），默认为False
                         如果为True，即使AppID在当前小时内使用过，也可以直接获取
                         但starttime和stoptime依旧要填
            
        Returns:
            (appid, vid, starttime, productName): AppID、VID、开始时间和产品名称
            
        Raises:
            Exception: 获取失败或超时
        """
        # 使用传入的 product_name 或初始化时的默认值
        product_name = product_name or self.product_name
        if not product_name:
            raise ValueError("product_name is required (either in __init__ or as parameter)")
            
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/api/appid/acquire",
                    json={"productName": product_name, "forceAcquire": force_acquire},
                    headers=self._get_headers(),
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    # 成功获取
                    data = response.json()
                    return data["appid"], data["vid"], data["starttime"], data["productName"]
                
                elif response.status_code == 202:
                    # 需要等待
                    data = response.json()
                    error = data.get("error")
                    retry_after = data.get("retry_after", retry_interval)
                    message = data.get("message", "Waiting for available appid")
                    
                    print(f"[Attempt {attempt + 1}/{max_retries}] {message}")
                    
                    if error == "no_available":
                        # 所有AppID都不可用，等待到下个小时
                        print(f"All appids for product '{product_name}' are in use for current hour, waiting {retry_after}s...")
                        time.sleep(retry_after)
                    elif error == "waiting":
                        # 服务端正在等待，客户端也等待
                        print(f"All appids for product '{product_name}' are in use, retrying in {retry_after}s...")
                        time.sleep(retry_after)
                    else:
                        print(f"Unknown error: {error}, retrying in {retry_after}s...")
                        time.sleep(retry_after)
                
                elif response.status_code == 401:
                    # 认证失败
                    data = response.json()
                    error_msg = data.get("message", "Authentication failed")
                    raise Exception(f"Authentication failed: {error_msg}")
                
                else:
                    # 其他错误
                    print(f"HTTP {response.status_code}: {response.text}")
                    time.sleep(retry_interval)
            
            except requests.exceptions.Timeout:
                print(f"[Attempt {attempt + 1}/{max_retries}] Request timeout, retrying in {retry_interval}s...")
                time.sleep(retry_interval)
            
            except requests.exceptions.ConnectionError as e:
                print(f"[Attempt {attempt + 1}/{max_retries}] Connection error, retrying in {retry_interval}s...")
                time.sleep(retry_interval)
            
            except Exception as e:
                print(f"[Attempt {attempt + 1}/{max_retries}] Unexpected error: {e}, retrying in {retry_interval}s...")
                time.sleep(retry_interval)
        
        raise Exception(f"Failed to acquire appid after {max_retries} attempts")
    
    def release_appid(self, appid: str, product_name: Optional[str] = None) -> bool:
        """
        释放AppID
        
        Args:
            appid: 要释放的AppID
            product_name: 产品名称，用于验证AppID归属（可选）
                        如果未指定，使用初始化时的 product_name
            
        Returns:
            bool: 是否成功释放
            
        Raises:
            Exception: 释放失败
        """
        # 使用传入的 product_name 或初始化时的默认值
        product_name = product_name or self.product_name
        if not product_name:
            raise ValueError("product_name is required (either in __init__ or as parameter)")
            
        try:
            response = requests.post(
                f"{self.base_url}/api/appid/release",
                json={"appid": appid, "productName": product_name},
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"AppID {appid} for product '{product_name}' released successfully at {data.get('stoptime')}")
                return True
            else:
                data = response.json()
                error_msg = data.get('message', 'Unknown error')
                print(f"Failed to release AppID {appid} for product '{product_name}': {error_msg}")
                raise Exception(f"Release failed: {error_msg}")
        
        except requests.exceptions.Timeout:
            raise Exception("Request timeout while releasing AppID")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection error while releasing AppID")
        except Exception as e:
            raise Exception(f"Unexpected error while releasing AppID: {e}")
    
    def get_status(self, product_name: Optional[str] = None) -> Optional[dict]:
        """
        获取AppID状态统计
        
        Args:
            product_name: 产品名称，如果指定则只统计该产品的AppID（可选）
                        如果未指定且初始化时设置了 product_name，则使用默认值
                        如果为 None，则获取所有产品的状态
            
        Returns:
            dict: 状态信息，失败时返回None
        """
        try:
            params = {}
            # 如果传入了 product_name，使用传入的值
            # 如果未传入但初始化时设置了 product_name，使用默认值
            # 如果都为 None，则不传参数（获取所有产品状态）
            if product_name:
                params['productName'] = product_name
            elif self.product_name:
                params['productName'] = self.product_name
            
            response = requests.get(
                f"{self.base_url}/api/appid/status",
                params=params,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get status: HTTP {response.status_code}")
                return None
        
        except requests.exceptions.Timeout:
            print("Request timeout while getting status")
            return None
        except requests.exceptions.ConnectionError:
            print("Connection error while getting status")
            return None
        except Exception as e:
            print(f"Error getting status: {e}")
            return None
    
    def init_product(self, product_name: Optional[str] = None, appIds: Optional[Dict[str, str]] = None) -> bool:
        """
        初始化或重置产品AppID配置
        
        Args:
            product_name: 产品名称（可选）
                        如果未指定，使用初始化时的 product_name
            appIds: AppID配置 {appid: vid}（可选）
                   如果未指定且初始化时设置了 product_name，则不传此参数
            
        Returns:
            bool: 是否成功初始化
            
        Raises:
            Exception: 初始化失败
        """
        # 使用传入的 product_name 或初始化时的默认值
        product_name = product_name or self.product_name
        if not product_name:
            raise ValueError("product_name is required (either in __init__ or as parameter)")
        
        if appIds is None:
            raise ValueError("appids is required")
        try:
            response = requests.post(
                f"{self.base_url}/api/appid/init",
                json={"productName": product_name, "appids": appIds},
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Product '{product_name}' initialized successfully: {data.get('message')}")
                return True
            else:
                data = response.json()
                error_msg = data.get('message', 'Unknown error')
                error_code = data.get('error', 'unknown_error')
                print(f"Failed to initialize product '{product_name}': {error_msg} (error: {error_code})")
                print(f"Request payload: productName={product_name}, appids count={len(appIds) if appIds else 0}")
                raise Exception(f"Initialization failed: {error_msg}")
                
        except requests.exceptions.Timeout:
            raise Exception("Request timeout while initializing product")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection error while initializing product")
        except Exception as e:
            raise Exception(f"Unexpected error while initializing product: {e}")

    def _convert_decimal_to_float(self, obj: Any) -> Any:
        """
        递归地将 Decimal 类型转换为 float，以便 JSON 序列化
        
        Args:
            obj: 需要转换的对象
            
        Returns:
            转换后的对象
        """
        from decimal import Decimal
        
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {key: self._convert_decimal_to_float(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._convert_decimal_to_float(item) for item in obj]
        else:
            return obj
    
    def store_test_result(self, product_name: str, session_id: str, test_data: Dict[str, Any]) -> bool:
        """
        存储测试用例执行数据
        
        Args:
            product_name: 产品名称（业务类型）
            session_id: 测试会话ID（用于区分不同的测试会话，如pytest worker进程）
            test_data: 测试用例数据字典
            
        Returns:
            bool: 是否成功存储
        """
        try:
            # 转换 Decimal 类型为 float，以便 JSON 序列化
            serializable_test_data = self._convert_decimal_to_float(test_data)
            
            response = requests.post(
                f"{self.base_url}/api/test/result",
                json={
                    "product_name": product_name,
                    "session_id": session_id,
                    "test_data": serializable_test_data
                },
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True
            else:
                data = response.json()
                error_msg = data.get('message', 'Unknown error')
                print(f"Failed to store test result: {error_msg}")
                return False
        except Exception as e:
            print(f"Error storing test result: {e}")
            return False
    
    def get_test_results(self, product_name: Optional[str] = None, session_id: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """
        获取测试用例执行数据
        
        Args:
            product_name: 产品名称（可选）
                        如果未指定，使用初始化时的 product_name
                        如果为 None，则获取所有产品的测试结果
            session_id: 测试会话ID（可选）
                       如果为 None，则获取该产品的所有会话的测试结果
            
        Returns:
            list: 测试结果数据列表，失败时返回None
        """
        try:
            params = {}
            # 如果传入了 product_name，使用传入的值
            # 如果未传入但初始化时设置了 product_name，使用默认值
            # 如果都为 None，则不传参数（获取所有产品状态）
            if product_name:
                params['product_name'] = product_name
            elif self.product_name:
                params['product_name'] = self.product_name
            
            if session_id:
                params['session_id'] = session_id
            
            response = requests.get(
                f"{self.base_url}/api/test/results",
                params=params,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                # 如果返回的是字典，提取 results 字段
                if isinstance(data, dict) and "results" in data:
                    return data["results"]
                # 如果返回的是列表，直接返回
                elif isinstance(data, list):
                    return data
                else:
                    print(f"⚠️  警告: get_test_results 返回了意外的格式: {type(data)}")
                    return []
            else:
                print(f"Failed to get test results: HTTP {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            print("Request timeout while getting test results")
            return None
        except requests.exceptions.ConnectionError:
            print("Connection error while getting test results")
            return None
        except Exception as e:
            print(f"Error getting test results: {e}")
            return None
    
    def clear_test_results(self, product_name: Optional[str] = None, session_id: Optional[str] = None) -> bool:
        """
        清除测试用例执行数据
        
        Args:
            product_name: 产品名称（可选）
                        如果未指定，使用初始化时的 product_name
                        如果为 None，则清除所有产品的测试结果
            session_id: 测试会话ID（可选）
                       如果为 None，则清除该产品的所有会话的测试结果
            
        Returns:
            bool: 是否成功清除
        """
        try:
            # 使用传入的 product_name 或初始化时的默认值
            product_name = product_name or self.product_name
            
            json_data = {}
            if product_name:
                json_data['product_name'] = product_name
            if session_id:
                json_data['session_id'] = session_id
            
            response = requests.post(
                f"{self.base_url}/api/test/results/clear",
                json=json_data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True
            else:
                data = response.json()
                error_msg = data.get('message', 'Unknown error')
                print(f"Failed to clear test results: {error_msg}")
                return False
        except requests.exceptions.Timeout:
            print("Request timeout while clearing test results")
            return False
        except requests.exceptions.ConnectionError:
            print("Connection error while clearing test results")
            return False
        except Exception as e:
            print(f"Error clearing test results: {e}")
            return False
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: 服务是否健康
        """
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            return response.status_code == 200
        except:
            return False

