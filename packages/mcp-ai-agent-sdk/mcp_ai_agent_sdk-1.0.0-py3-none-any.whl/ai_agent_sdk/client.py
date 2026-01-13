"""
AI Agent SDK 客户端（API 模式）
包含完整的 AI 处理和数据库操作
"""
import requests
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, date
from decimal import Decimal
from .exceptions import AIAgentError, AuthenticationError, RateLimitError


class DatabaseAdapter:
    """内置数据库适配器 - 支持 MySQL"""
    
    def __init__(self, config: dict):
        self.config = config
        self._connection = None
    
    def _get_connection(self):
        import pymysql
        # 检查连接是否有效，无效则重新连接
        if self._connection is not None:
            try:
                self._connection.ping(reconnect=True)
            except:
                self._connection = None
        
        if self._connection is None:
            self._connection = pymysql.connect(
                host=self.config.get("host", "localhost"),
                port=self.config.get("port", 3306),
                user=self.config.get("user", "root"),
                password=self.config.get("password", ""),
                database=self.config.get("database", ""),
                charset=self.config.get("charset", "utf8mb4"),
                cursorclass=pymysql.cursors.DictCursor
            )
        return self._connection
    
    def list(self, entity: str, where: dict = None, limit: int = 1000, offset: int = 0) -> tuple:
        conn = self._get_connection()
        cursor = conn.cursor()
        sql = f"SELECT * FROM `{entity}`"
        params = []
        if where:
            conditions = [f"`{k}` = %s" for k in where.keys()]
            sql += " WHERE " + " AND ".join(conditions)
            params = list(where.values())
        sql += f" LIMIT {limit} OFFSET {offset}"
        cursor.execute(sql, params)
        records = cursor.fetchall()
        cursor.close()
        return list(records), len(records)
    
    def create(self, entity: str, data: dict) -> dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        fields = ", ".join([f"`{k}`" for k in data.keys()])
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO `{entity}` ({fields}) VALUES ({placeholders})"
        cursor.execute(sql, list(data.values()))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        return {"id": new_id, **data}
    
    def update(self, entity: str, id: Any, data: dict) -> dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        set_clause = ", ".join([f"`{k}` = %s" for k in data.keys()])
        sql = f"UPDATE `{entity}` SET {set_clause} WHERE id = %s"
        cursor.execute(sql, list(data.values()) + [id])
        conn.commit()
        cursor.close()
        return {"id": id, **data}
    
    def delete(self, entity: str, id: Any) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        sql = f"DELETE FROM `{entity}` WHERE id = %s"
        cursor.execute(sql, [id])
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected > 0
    
    def execute(self, sql: str, params: list = None) -> list:
        """执行原始 SQL 查询"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params or [])
        if sql.strip().upper().startswith("SELECT") or sql.strip().upper().startswith("SHOW"):
            result = cursor.fetchall()
        else:
            conn.commit()
            result = [{"affected_rows": cursor.rowcount}]
        cursor.close()
        return list(result)
    
    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None


class AIAgentClient:
    """
    AI Agent 客户端
    
    用于连接 AI Agent 服务，通过自然语言操作后台系统
    
    Example:
        >>> from ai_agent_sdk import AIAgentClient
        >>> client = AIAgentClient("your_api_key")
        >>> client.register_schema(
        ...     api_base_url="http://your-backend.com/api",
        ...     entities=[{"name": "user", "fields": [...]}]
        ... )
        >>> result = client.chat("查询所有用户")
        >>> print(result)
    """
    
    def __init__(
        self, 
        api_key: str, 
        base_url: str = "https://wangyunge.top",
        timeout: int = 30,
        db_config: dict = None,
        db_adapter: Any = None,
        auto_schema: bool = True
    ):
        """
        初始化客户端
        
        Args:
            api_key: API Key，从 AI Agent 平台获取
            base_url: API 服务地址，默认为官方地址
            timeout: 请求超时时间（秒）
            db_config: 数据库配置（自动创建 MySQL 适配器）
            db_adapter: 自定义数据库适配器（需实现 list/create/update/delete 方法）
            auto_schema: 是否自动从数据库生成 Schema（默认 True）
        
        Example:
            # 方式1：使用内置 MySQL 适配器
            client = AIAgentClient("ak_xxx", db_config={
                "host": "localhost",
                "user": "root",
                "password": "xxx",
                "database": "mydb"
            })
            
            # 方式2：使用自定义适配器
            client = AIAgentClient("ak_xxx", db_adapter=my_db)
        """
        if not api_key:
            raise ValueError("api_key 不能为空")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json",
            "User-Agent": "AI-Agent-SDK/1.0.0 Python"
        })
        
        # 数据库适配器
        if db_adapter:
            self._db = db_adapter
        elif db_config:
            self._db = DatabaseAdapter(db_config)
        else:
            self._db = None
        
        # Schema 状态
        self._schema_registered = False
        self._entities = []
        self._cached_schema = None  # 缓存的 Schema
        self._schema_file = None  # Schema 文件路径
        self._conversation_id = None
        self._history = []
        
        # 自动从数据库生成 Schema（如果有数据库连接）
        if self._db and auto_schema:
            try:
                self.generate_schema_from_db(use_ai=False)
                print("[SDK] 已自动从数据库生成 Schema")
            except Exception as e:
                print(f"[SDK] 自动生成 Schema 失败: {e}")
    
    def _request(
        self, 
        method: str, 
        path: str, 
        data: dict = None,
        params: dict = None
    ) -> dict:
        """发送 HTTP 请求"""
        url = f"{self.base_url}{path}"
        
        try:
            resp = self._session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )
        except requests.exceptions.Timeout:
            raise AIAgentError("请求超时，请检查网络连接")
        except requests.exceptions.ConnectionError:
            raise AIAgentError("无法连接到服务器，请检查网络或服务地址")
        
        # 处理错误响应
        if resp.status_code == 401:
            raise AuthenticationError("API Key 无效或已过期", status_code=401)
        elif resp.status_code == 429:
            raise RateLimitError("请求频率超限，请稍后重试", status_code=429)
        elif resp.status_code >= 400:
            try:
                error_data = resp.json()
                message = error_data.get("detail", resp.text)
            except:
                message = resp.text
            raise AIAgentError(message, status_code=resp.status_code)
        
        return resp.json()
    
    # ============ Schema 注册 ============
    
    def register_schema(
        self,
        entities: List[Dict[str, Any]],
        system_name: str = None,
        system_description: str = None,
        api_base_url: str = None
    ) -> Dict[str, Any]:
        """
        注册后台系统的 Schema
        
        告诉 AI Agent 你的后台系统有哪些实体和操作
        
        Args:
            entities: 实体列表，每个实体包含 name, fields, operations
            system_name: 系统名称，如 "学生管理系统"
            system_description: 系统描述
            api_base_url: 后台 API 基础地址（可选），如 "http://your-backend.com/api"
        
        Returns:
            dict: 注册结果
            
        Example:
            >>> client.register_schema(
            ...     api_base_url="http://my-shop.com/api",
            ...     system_name="电商管理系统",
            ...     entities=[
            ...         {
            ...             "name": "order",
            ...             "description": "订单",
            ...             "fields": [
            ...                 {"name": "id", "type": "number"},
            ...                 {"name": "customer", "type": "string"},
            ...                 {"name": "amount", "type": "number"}
            ...             ],
            ...             "operations": ["list", "get", "create", "update", "delete"]
            ...         }
            ...     ]
            ... )
            {'success': True, 'entities': ['order']}
        """
        data = {
            "api_base_url": api_base_url or "",
            "entities": entities
        }
        if system_name:
            data["system_name"] = system_name
        if system_description:
            data["system_description"] = system_description
        
        # 缓存 Schema（不再发送到 api_server）
        self._cached_schema = data
        self._schema_registered = True
        self._entities = [e["name"] if isinstance(e, dict) else e for e in entities]
        return {"success": True, "message": "Schema 已缓存"}
    
    def set_schema_file(self, file_path: str):
        """
        设置 Schema 文件路径，自动加载和保存
        
        Args:
            file_path: Schema 文件路径
        """
        import json
        from pathlib import Path
        self._schema_file = Path(file_path)
        
        # 自动加载
        if self._schema_file.exists():
            with open(self._schema_file, "r", encoding="utf-8") as f:
                schema = json.load(f)
                if schema and schema.get("entities"):
                    self.register_schema(
                        entities=schema["entities"],
                        system_name=schema.get("system_name"),
                        system_description=schema.get("system_description")
                    )
    
    def save_schema_to_file(self):
        """保存当前 Schema 到文件"""
        import json
        if self._schema_file and self._cached_schema:
            with open(self._schema_file, "w", encoding="utf-8") as f:
                json.dump(self._cached_schema, f, ensure_ascii=False, indent=2)
    
    def save_and_register_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        保存并注册 Schema（保存到文件 + 注册到内存）
        
        Args:
            schema: Schema 配置，包含 entities, system_name 等
        
        Returns:
            dict: {"success": True, "message": "..."}
        """
        import json
        
        # 1. 注册到内存
        if schema.get("entities"):
            self.register_schema(
                entities=schema["entities"],
                system_name=schema.get("system_name"),
                system_description=schema.get("system_description")
            )
        
        # 2. 保存到文件
        if self._schema_file:
            with open(self._schema_file, "w", encoding="utf-8") as f:
                json.dump(schema, f, ensure_ascii=False, indent=2)
            print(f"[SDK] Schema 已保存到 {self._schema_file}")
        
        return {"success": True, "message": "Schema 保存并注册成功"}
    
    def check_schema_completeness(self) -> Dict[str, Any]:
        """
        检查 Schema 完整性（字段是否都有描述）
        
        Returns:
            dict: {
                "complete": bool,  # 是否完整
                "missing_descriptions": list,  # 缺少描述的字段列表
                "message": str  # 提示信息
            }
        """
        schema = self.get_schema(auto_generate=False)
        if not schema or not schema.get("entities"):
            return {
                "complete": False,
                "missing_descriptions": [],
                "message": "Schema 未配置，请先在「表结构管理」中配置数据表"
            }
        
        missing = []
        for entity in schema.get("entities", []):
            entity_name = entity.get("name", "unknown")
            for field in entity.get("fields", []):
                field_name = field.get("name", "unknown")
                description = field.get("description", "")
                if not description or description.strip() == "":
                    missing.append(f"{entity_name}.{field_name}")
        
        if missing:
            return {
                "complete": False,
                "missing_descriptions": missing,
                "message": f"以下字段缺少描述，建议先完善：{', '.join(missing[:5])}{'...' if len(missing) > 5 else ''}"
            }
        
        return {
            "complete": True,
            "missing_descriptions": [],
            "message": "Schema 配置完整"
        }
    
    def get_schema(self, auto_generate: bool = True) -> Dict[str, Any]:
        """
        获取 Schema（优先级：SDK内存 > 本地文件 > 自动生成）
        
        Args:
            auto_generate: 如果内存和文件都没有，是否自动从数据库生成
        
        Returns:
            dict: Schema 信息
        """
        import json
        
        # 1. 优先从内存获取
        if self._cached_schema and self._cached_schema.get("entities"):
            return self._cached_schema
        
        # 2. 从本地文件获取
        if self._schema_file and self._schema_file.exists():
            try:
                with open(self._schema_file, "r", encoding="utf-8") as f:
                    schema = json.load(f)
                    if schema and schema.get("entities"):
                        # 加载到内存
                        self.register_schema(
                            entities=schema["entities"],
                            system_name=schema.get("system_name"),
                            system_description=schema.get("system_description")
                        )
                        print("[SDK] Schema 从本地文件加载")
                        return self._cached_schema
            except Exception as e:
                print(f"[SDK] 读取 Schema 文件失败: {e}")
        
        # 3. 自动从数据库生成
        if auto_generate and self._db:
            try:
                result = self.generate_schema_from_db(use_ai=False)
                if result.get("success"):
                    # 保存到文件
                    if self._schema_file:
                        self.save_schema_to_file()
                    print("[SDK] Schema 从数据库自动生成")
                    return self._cached_schema
            except Exception as e:
                print(f"[SDK] 自动生成 Schema 失败: {e}")
        
        return self._cached_schema
    
    def generate_schema_from_db(self, use_ai: bool = False) -> Dict[str, Any]:
        """
        从数据库自动生成 Schema
        
        根据数据库表结构自动生成 Schema 配置
        
        Args:
            use_ai: 是否使用 AI 智能分析（更准确但较慢）
        
        Returns:
            dict: {
                "success": bool,
                "entities": list,  # 生成的实体列表
                "relations": list  # 表关联关系（AI 模式）
            }
        
        Example:
            >>> result = client.generate_schema_from_db(use_ai=True)
            >>> client.register_schema(entities=result["entities"])
        """
        if not self._db:
            raise AIAgentError("未配置数据库，请在初始化时传入 db_config")
        
        # 获取数据库表结构
        tables_info = self._get_tables_info(use_ai)
        
        if use_ai:
            # 调用 AI 分析
            result = self._request("POST", "/api/v1/schema/analyze", {
                "tables_info": tables_info
            })
            return {
                "success": True,
                "entities": result.get("entities", []),
                "relations": result.get("relations", [])
            }
        else:
            # 规则推断
            entities = self._infer_schema(tables_info)
            return {"success": True, "entities": entities}
    
    def _get_tables_info(self, include_sample: bool = False) -> List[Dict]:
        """获取数据库表结构信息"""
        from decimal import Decimal
        
        tables_info = []
        
        # 获取所有表
        tables = self._db.execute("SHOW TABLES")
        if not tables:
            return []
        
        # 获取数据库名
        db_result = self._db.execute("SELECT DATABASE()")
        database = db_result[0].get("DATABASE()") if db_result else ""
        
        for table_row in tables:
            table_name = list(table_row.values())[0]
            
            # 获取表注释
            table_info = self._db.execute(f"""
                SELECT TABLE_COMMENT FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = '{database}' AND TABLE_NAME = '{table_name}'
            """)
            table_comment = table_info[0].get("TABLE_COMMENT", "") if table_info else ""
            
            # 获取字段信息
            columns_info = self._db.execute(f"""
                SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_COMMENT
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = '{database}' AND TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
            """)
            
            columns = []
            for col in columns_info:
                col_type = col.get("COLUMN_TYPE", "").lower()
                field_type = "string"
                if "int" in col_type:
                    field_type = "integer"
                elif "decimal" in col_type or "float" in col_type or "double" in col_type:
                    field_type = "decimal"
                elif "datetime" in col_type or "timestamp" in col_type:
                    field_type = "datetime"
                elif "date" in col_type:
                    field_type = "date"
                elif "text" in col_type:
                    field_type = "text"
                elif "bool" in col_type or "tinyint(1)" in col_type:
                    field_type = "boolean"
                
                columns.append({
                    "name": col.get("COLUMN_NAME"),
                    "type": field_type,
                    "comment": col.get("COLUMN_COMMENT", ""),
                    "required": col.get("IS_NULLABLE") == "NO"
                })
            
            # 获取采样数据（用于 AI 分析）
            sample_data = []
            if include_sample:
                try:
                    rows = self._db.execute(f"SELECT * FROM `{table_name}` LIMIT 3")
                    for row in rows:
                        converted_row = {}
                        for k, v in row.items():
                            if hasattr(v, 'isoformat'):
                                converted_row[k] = v.isoformat()
                            elif isinstance(v, (bytes, bytearray)):
                                converted_row[k] = v.decode('utf-8', errors='ignore')
                            elif isinstance(v, Decimal):
                                converted_row[k] = float(v)
                            else:
                                converted_row[k] = v
                        sample_data.append(converted_row)
                except:
                    pass
            
            tables_info.append({
                "name": table_name,
                "table_comment": table_comment,
                "columns": columns,
                "sample_data": sample_data
            })
        
        return tables_info
    
    def _infer_schema(self, tables_info: List[Dict]) -> List[Dict]:
        """使用规则推断 Schema"""
        entities = []
        
        # 表名中文映射
        table_cn_map = {
            "student": "学生", "students": "学生",
            "class": "班级", "classes": "班级",
            "course": "课程", "courses": "课程",
            "score": "成绩", "scores": "成绩",
            "user": "用户", "users": "用户",
            "order": "订单", "orders": "订单",
            "product": "商品", "products": "商品",
            "teacher": "教师", "teachers": "教师",
        }
        
        # 字段名中文映射
        field_cn_map = {
            "id": "ID", "name": "名称", "title": "标题",
            "age": "年龄", "gender": "性别", "phone": "电话",
            "email": "邮箱", "address": "地址", "status": "状态",
            "created_at": "创建时间", "updated_at": "更新时间",
            "price": "价格", "amount": "数量", "total": "总计",
            "description": "描述", "remark": "备注",
        }
        
        for table in tables_info:
            fields = []
            for col in table["columns"]:
                # 优先使用数据库注释
                if col.get("comment") and col["comment"].strip():
                    description = col["comment"].strip()
                else:
                    # 使用映射或字段名
                    description = field_cn_map.get(col["name"].lower(), col["name"])
                
                fields.append({
                    "name": col["name"],
                    "type": col["type"],
                    "description": description,
                    "required": col.get("required", False)
                })
            
            # 表中文名
            table_comment = table.get("table_comment", "")
            if table_comment and table_comment.strip():
                chinese_name = table_comment.strip()
                table_desc = table_comment.strip()
            else:
                chinese_name = table_cn_map.get(table["name"].lower(), table["name"])
                table_desc = f"{table['name']} 表"
            
            entities.append({
                "name": table["name"],
                "chinese_name": chinese_name,
                "description": table_desc,
                "fields": fields
            })
        
        return entities
    
    def _check_schema(self):
        """检查是否已注册 Schema"""
        if not self._schema_registered:
            raise AIAgentError("请先调用 register_schema() 注册后台 Schema")
    
    # ============ 自然语言对话 ============
    
    def chat(self, message: str, conversation_id: str = None) -> Dict[str, Any]:
        """
        与 AI Agent 对话
        
        发送自然语言指令，AI 会理解并返回建议的操作
        
        Args:
            message: 自然语言指令，如 "查询所有订单"
            conversation_id: 对话 ID（多轮对话时使用）
        
        Returns:
            dict: 包含 conversation_id, message, actions
            
        Example:
            >>> result = client.chat("查询所有订单")
            >>> print(result['message'])
            '我理解您想查询数据。以下是建议的操作：'
            >>> print(result['actions'])
            [{'id': 'action_xxx', 'type': 'list', 'entity': 'order', ...}]
        """
        self._check_schema()
        
        if not message or not message.strip():
            raise ValueError("message 不能为空")
        
        data = {"message": message.strip()}
        if conversation_id:
            data["conversation_id"] = conversation_id
        elif self._conversation_id:
            data["conversation_id"] = self._conversation_id
        
        result = self._request("POST", "/api/v1/chat", data)
        
        # 保存对话 ID 用于多轮对话
        self._conversation_id = result.get("conversation_id")
        
        return result
    
    def ask(self, question: str) -> str:
        """
        简化版对话，直接返回 AI 回复文本
        
        Args:
            question: 问题
        
        Returns:
            str: AI 回复
            
        Example:
            >>> answer = client.ask("查询所有订单")
            >>> print(answer)
        """
        result = self.chat(question)
        return result.get("message", "")
    
    # ============ 执行操作 ============
    
    def execute(
        self, 
        action_id: str, 
        conversation_id: str = None,
        confirmed: bool = False
    ) -> Dict[str, Any]:
        """
        执行 AI 建议的操作
        
        Args:
            action_id: 操作 ID（从 chat 返回的 actions 中获取）
            conversation_id: 对话 ID
            confirmed: 是否已确认（增删改操作需要设为 True）
        
        Returns:
            dict: 执行结果
            
        Example:
            >>> # 查询操作，直接执行
            >>> result = client.execute(action_id)
            
            >>> # 增删改操作，需要确认
            >>> result = client.execute(action_id, confirmed=True)
        """
        conv_id = conversation_id or self._conversation_id
        if not conv_id:
            raise AIAgentError("请先调用 chat() 获取操作建议")
        
        return self._request("POST", "/api/v1/execute", {
            "conversation_id": conv_id,
            "action_id": action_id,
            "confirmed": confirmed
        })
    
    def get_conversation(self, conversation_id: str = None) -> Dict[str, Any]:
        """
        获取对话历史
        
        Args:
            conversation_id: 对话 ID
        
        Returns:
            dict: 对话历史
        """
        conv_id = conversation_id or self._conversation_id
        if not conv_id:
            raise AIAgentError("没有活跃的对话")
        
        return self._request("GET", f"/api/v1/conversations/{conv_id}")
    
    # ============ 便捷方法 ============
    
    def new_conversation(self):
        """开始新对话"""
        self._conversation_id = None
        self._history = []
    
    # ============ 一键执行（核心方法） ============
    
    def ask_and_execute(self, message: str, history: List[Dict] = None) -> Dict[str, Any]:
        """
        一键完成：AI 理解 → 数据库执行 → 结果总结
        
        客户只需调用此方法，即可完成所有操作
        
        Args:
            message: 自然语言指令，如 "查询王五的成绩"
            history: 对话历史（可选），格式 [{"role": "user", "content": "..."}, ...]
        
        Returns:
            dict: {
                "success": bool,
                "message": str,      # AI 总结的回复
                "data": list/dict,   # 查询结果（如有）
                "steps": list        # 执行的步骤
            }
        
        Example:
            >>> result = client.ask_and_execute("查询王五的成绩")
            >>> print(result["message"])
            '王五同学的成绩如下：语文 95 分，数学 98 分'
        """
        self._check_schema()
        
        if not self._db:
            raise AIAgentError("未配置数据库，请在初始化时传入 db_config 或 db_adapter")
        
        # 合并历史
        combined_history = (history or []) + self._history[-20:]
        
        # 1. 调用 AI 处理（意图理解 + 规划）
        process_result = self._request("POST", "/api/v1/process", {
            "message": message,
            "conversation_id": self._conversation_id,
            "history": combined_history[-20:],  # 最近20条历史
            "schema": self._cached_schema  # 附带 Schema
        })
        
        self._conversation_id = process_result.get("conversation_id")
        steps = process_result.get("steps", [])
        intent = process_result.get("understood_message", message)
        
        # 保存历史
        self._history.append({"role": "user", "content": message})
        
        if not steps:
            # 普通对话，无需执行
            response = process_result.get("response", "你好！有什么可以帮你的吗？")
            self._history.append({"role": "assistant", "content": response})
            return {"success": True, "message": response, "data": None, "steps": []}
        
        # 2. 执行数据库操作
        step_results = {}
        for idx, step in enumerate(steps, 1):
            resolved_step = self._resolve_step_references(step, step_results)
            result = self._execute_query(resolved_step)
            step_results[idx] = result
        
        # 3. 调用 AI 总结结果
        serialized_results = self._serialize(step_results)
        summary_result = self._request("POST", "/api/v1/summarize", {
            "question": intent,
            "results": serialized_results,
            "conversation_id": self._conversation_id
        })
        
        summary = summary_result.get("message", "操作完成")
        self._history.append({"role": "assistant", "content": summary})
        
        # 获取最后一步的数据
        last_result = step_results.get(len(steps), {})
        
        return {
            "success": True,
            "message": summary,
            "data": last_result.get("data"),
            "steps": steps,
            "step_results": step_results,
            "intent": intent if intent != message else None
        }
    
    def chat_and_execute(self, message: str, history: List[Dict] = None) -> Dict[str, Any]:
        """ask_and_execute 的别名，保持兼容性"""
        return self.ask_and_execute(message, history)
    
    def parse_intent(self, message: str, history: List[Dict] = None) -> Dict[str, Any]:
        """
        解析用户意图，返回操作步骤（不执行）
        
        Args:
            message: 用户消息
            history: 对话历史
        
        Returns:
            dict: {"intent": str, "steps": list}
        """
        self._check_schema()
        
        combined_history = (history or []) + self._history[-20:]
        
        process_result = self._request("POST", "/api/v1/process", {
            "message": message,
            "conversation_id": self._conversation_id,
            "history": combined_history[-20:],
            "schema": self._cached_schema
        })
        
        self._conversation_id = process_result.get("conversation_id")
        
        return {
            "intent": process_result.get("understood_message", message),
            "steps": process_result.get("steps", []),
            "response": process_result.get("response", "")
        }
    
    def process_chat_stream(self, message: str, history: List[Dict] = None):
        """
        流式处理对话请求，生成 SSE 事件
        
        Args:
            message: 用户消息
            history: 对话历史
        
        Yields:
            str: SSE 格式的事件字符串
        
        Example:
            for event in client.process_chat_stream("查询学生"):
                yield event  # 直接用于 StreamingResponse
        """
        import json
        
        def send(type: str, **data):
            return f"data: {json.dumps({'type': type, **data}, ensure_ascii=False)}\n\n"
        
        def serialize(obj):
            from decimal import Decimal
            if isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize(i) for i in obj]
            elif hasattr(obj, 'strftime'):
                return obj.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(obj, Decimal):
                return float(obj)
            return obj
        
        try:
            yield send("thinking", icon="🤖", text="正在分析...")
            
            # 检查 Schema 完整性
            schema_check = self.check_schema_completeness()
            if not schema_check.get("complete"):
                yield send("thinking", icon="⚠️", text=schema_check.get("message"))
                yield send("done", message=schema_check.get("message"), schema_incomplete=True)
                return
            
            # 解析意图
            parse_result = self.parse_intent(message, history)
            intent = parse_result.get("intent")
            steps = parse_result.get("steps", [])
            
            if intent:
                yield send("thinking", icon="🧠", text=f'理解意图: "{message}" → "{intent}"')
            
            # 检查是否有危险操作
            dangerous_actions = ["delete", "update", "create"]
            has_dangerous = any(step.get("action") in dangerous_actions for step in steps)
            
            if has_dangerous and steps:
                # 生成预览信息
                action_map = {"query": "查询", "create": "创建", "update": "更新", "delete": "删除", "aggregate": "统计"}
                preview = "即将执行以下操作：\n"
                for idx, step in enumerate(steps, 1):
                    action_name = action_map.get(step.get("action"), step.get("action"))
                    preview += f"\n{idx}. **{action_name}** `{step.get('entity', '')}`"
                    if step.get("where"):
                        preview += f"\n   条件: {json.dumps(step['where'], ensure_ascii=False)}"
                    if step.get("data"):
                        preview += f"\n   数据: {json.dumps(step['data'], ensure_ascii=False)}"
                
                yield send("thinking", icon="⚠️", text="检测到数据修改操作，需要确认")
                yield send("confirm", message=preview, intent=intent, steps=steps, original_message=message)
                return
            
            # 执行查询操作
            if steps:
                yield send("thinking", icon="⚡", text=f"执行 {len(steps)} 个操作步骤...")
            
            result = self.execute_steps(steps, message)
            yield send("thinking", icon="✅", text="完成")
            yield send("done", message=result.get("message", ""), intent=intent, steps=steps, step_results=serialize(result.get("step_results", {})))
            
        except Exception as e:
            yield send("error", message=f"处理失败: {str(e)}")
    
    def process_chat(self, message: str, history: List[Dict] = None) -> Dict[str, Any]:
        """
        处理对话请求（用于流式接口）
        
        返回处理结果，包含是否需要确认、操作步骤等信息
        
        Args:
            message: 用户消息
            history: 对话历史
        
        Returns:
            dict: {
                "need_confirm": bool,  # 是否需要确认（危险操作）
                "intent": str,         # 理解后的意图
                "steps": list,         # 操作步骤
                "preview": str,        # 操作预览（需确认时）
                "result": dict,        # 执行结果（不需确认时）
                "schema_error": str    # Schema 错误信息（如有）
            }
        """
        # 检查 Schema 完整性
        schema_check = self.check_schema_completeness()
        if not schema_check.get("complete"):
            return {"schema_error": schema_check.get("message")}
        
        # 解析意图
        parse_result = self.parse_intent(message, history)
        intent = parse_result.get("intent")
        steps = parse_result.get("steps", [])
        
        # 检查是否有危险操作
        dangerous_actions = ["delete", "update", "create"]
        has_dangerous = any(step.get("action") in dangerous_actions for step in steps)
        
        if has_dangerous and steps:
            # 生成预览信息
            action_map = {"query": "查询", "create": "创建", "update": "更新", "delete": "删除", "aggregate": "统计"}
            preview = "即将执行以下操作：\n"
            for idx, step in enumerate(steps, 1):
                action_name = action_map.get(step.get("action"), step.get("action"))
                preview += f"\n{idx}. **{action_name}** `{step.get('entity', '')}`"
                if step.get("where"):
                    import json
                    preview += f"\n   条件: {json.dumps(step['where'], ensure_ascii=False)}"
                if step.get("data"):
                    import json
                    preview += f"\n   数据: {json.dumps(step['data'], ensure_ascii=False)}"
            
            return {
                "need_confirm": True,
                "intent": intent,
                "steps": steps,
                "preview": preview,
                "original_message": message
            }
        
        # 直接执行查询操作
        result = self.execute_steps(steps, message)
        return {
            "need_confirm": False,
            "intent": intent,
            "steps": steps,
            "result": result
        }
    
    def execute_steps(self, steps: List[Dict], original_message: str = "") -> Dict[str, Any]:
        """
        执行操作步骤
        
        Args:
            steps: 操作步骤列表
            original_message: 原始用户消息（用于总结）
        
        Returns:
            dict: {"success": bool, "message": str, "step_results": dict}
        """
        if not self._db:
            raise AIAgentError("未配置数据库")
        
        if not steps:
            return {"success": True, "message": "无需执行操作", "step_results": {}}
        
        # 执行数据库操作
        step_results = {}
        for idx, step in enumerate(steps, 1):
            resolved_step = self._resolve_step_references(step, step_results)
            result = self._execute_query(resolved_step)
            step_results[idx] = result
            # 如果操作失败，直接返回错误
            if not result.get("success"):
                return {
                    "success": False,
                    "message": result.get("error", "操作失败"),
                    "step_results": step_results
                }
        
        # 调用 AI 总结结果
        serialized_results = self._serialize(step_results)
        summary_result = self._request("POST", "/api/v1/summarize", {
            "question": original_message,
            "results": serialized_results,
            "conversation_id": self._conversation_id
        })
        
        summary = summary_result.get("message", "操作完成")
        self._history.append({"role": "user", "content": original_message})
        self._history.append({"role": "assistant", "content": summary})
        
        return {
            "success": True,
            "message": summary,
            "step_results": step_results
        }
    
    def _execute_query(self, query: dict) -> dict:
        """执行 AI 生成的查询指令"""
        import re
        
        action = query.get("action")
        entity = query.get("entity")
        where = query.get("where") or {}
        if not isinstance(where, dict):
            where = {}
        order_by = query.get("orderBy")
        order = query.get("order", "asc")
        limit = query.get("limit", 20)
        data = query.get("data") or {}
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        if not isinstance(data, dict):
            data = {}
        
        if not entity:
            return {"success": False, "error": "缺少实体名"}
        
        try:
            # 处理子查询条件
            resolved_where = {}
            for key, value in where.items():
                if isinstance(value, dict) and "subquery" in value:
                    sub_entity = value.get("subquery")
                    sub_field = value.get("field", "id")
                    sub_condition = value.get("condition", {})
                    sub_records, _ = self._db.list(sub_entity, sub_condition, limit=1000)
                    sub_ids = [r.get(sub_field) for r in sub_records if r.get(sub_field) is not None]
                    resolved_where[key] = sub_ids if sub_ids else None
                else:
                    resolved_where[key] = value
            
            # 查询数据
            records, _ = self._db.list(entity, {}, limit=1000)
            
            # 条件过滤
            for key, value in resolved_where.items():
                if value is not None:
                    if isinstance(value, list):
                        records = [r for r in records if r.get(key) in value]
                    else:
                        records = [r for r in records if r.get(key) == value]
            
            if action == "query":
                if order_by:
                    reverse = order == "desc"
                    records = sorted(records, key=lambda x: x.get(order_by, 0), reverse=reverse)
                records = records[:limit]
                return {"success": True, "action": action, "entity": entity, "data": records, "total": len(records)}
            
            elif action == "create":
                record = self._db.create(entity, data)
                return {"success": True, "action": action, "entity": entity, "data": record, "message": "创建成功"}
            
            elif action == "update":
                record_id = where.get("id")
                if record_id:
                    # 按 id 更新
                    record = self._db.update(entity, record_id, data)
                    return {"success": True, "action": action, "entity": entity, "data": record, "message": "更新成功"}
                elif records:
                    # 按条件更新
                    if len(records) == 1:
                        # 只有一条匹配，直接更新
                        result = self._db.update(entity, records[0].get("id"), data)
                        return {"success": True, "action": action, "entity": entity, "data": result, "message": "更新成功"}
                    else:
                        # 多条匹配，提示用户
                        return {"success": False, "error": f"找到 {len(records)} 条匹配记录，请指定更精确的条件或使用 id"}
                return {"success": False, "error": "未找到符合条件的记录"}
            
            elif action == "delete":
                record_id = where.get("id")
                if record_id:
                    if self._db.delete(entity, record_id):
                        return {"success": True, "action": action, "entity": entity, "message": "删除成功", "count": 1}
                    return {"success": False, "error": "记录不存在"}
                elif where:
                    deleted_count = 0
                    for record in records:
                        if self._db.delete(entity, record.get("id")):
                            deleted_count += 1
                    return {"success": True, "action": action, "entity": entity, "message": "批量删除成功", "count": deleted_count}
                return {"success": False, "error": "删除需要指定条件"}
            
            elif action == "aggregate" or action == "count":
                return {"success": True, "action": "aggregate", "type": "count", "entity": entity, "total": len(records)}
            
            return {"success": False, "error": f"不支持的操作: {action}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _resolve_step_references(self, step: dict, step_results: dict) -> dict:
        """解析步骤中的引用（如 $1.id）"""
        import re
        resolved = step.copy()
        if "where" in resolved and isinstance(resolved["where"], dict):
            new_where = {}
            for k, v in resolved["where"].items():
                if isinstance(v, str) and v.startswith("$"):
                    match = re.match(r'\$(\d+)\.(\w+)', v)
                    if match:
                        ref = step_results.get(int(match.group(1)), {}).get("data", [])
                        new_where[k] = ref[0].get(match.group(2)) if ref else None
                    else:
                        new_where[k] = v
                else:
                    new_where[k] = v
            resolved["where"] = new_where
        return resolved
    
    def _serialize(self, obj):
        """序列化对象，处理 datetime 等类型"""
        if isinstance(obj, dict):
            return {k: self._serialize(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize(i) for i in obj]
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, bytes):
            return obj.decode('utf-8', errors='ignore')
        return obj
    
    # ============ 上下文管理器 ============
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """关闭连接"""
        self._session.close()
    
    @property
    def is_registered(self) -> bool:
        """是否已注册 Schema"""
        return self._schema_registered
    
    @property
    def entities(self) -> List[str]:
        """已注册的实体列表"""
        return self._entities
    
    @property
    def conversation_id(self) -> Optional[str]:
        """当前对话 ID"""
        return self._conversation_id
    
    # ============ 内置 HTTP 服务器 ============
    
    def run_server(self, host: str = "0.0.0.0", port: int = 8000, cors_origins: List[str] = None):
        """
        启动内置 HTTP 服务器
        
        Args:
            host: 监听地址，默认 0.0.0.0
            port: 端口，默认 8000
            cors_origins: 允许的跨域来源，默认 ["*"]
        
        Example:
            client = AIAgentClient(api_key="...", db_config={...})
            client.run_server(port=8000)
        """
        try:
            from fastapi import FastAPI, Request
            from fastapi.responses import StreamingResponse, JSONResponse
            from fastapi.middleware.cors import CORSMiddleware
            from pydantic import BaseModel
            import uvicorn
        except ImportError:
            raise ImportError("请安装 fastapi 和 uvicorn: pip install fastapi uvicorn")
        
        app = FastAPI(title="AI Agent API", version="1.0.0")
        
        # CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins or ["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 请求模型
        class ChatRequest(BaseModel):
            message: str
            history: List[Dict] = []
        
        class ConfirmRequest(BaseModel):
            steps: List[Dict]
            original_message: str
        
        class SchemaRequest(BaseModel):
            system_name: str = ""
            entities: List[Dict] = []
        
        class GenerateRequest(BaseModel):
            use_ai: bool = False
        
        # 流式对话
        @app.post("/api/chat/stream")
        async def chat_stream(request: ChatRequest):
            def generate():
                for event in self.process_chat_stream(request.message, request.history):
                    yield event
            return StreamingResponse(generate(), media_type="text/event-stream")
        
        # 确认执行
        @app.post("/api/chat/confirm")
        async def chat_confirm(request: ConfirmRequest):
            result = self.execute_steps(request.steps, request.original_message)
            return {"success": True, "message": result.get("message", "")}
        
        # 普通对话
        @app.post("/api/chat")
        async def chat(request: ChatRequest):
            result = self.ask_and_execute(request.message, request.history)
            return result
        
        # 获取 Schema
        @app.get("/api/schema")
        async def get_schema():
            return {"schema": self.get_schema()}
        
        # 注册 Schema
        @app.post("/api/schema/register")
        async def register_schema_api(request: SchemaRequest):
            self.register_schema(request.entities, system_name=request.system_name)
            return {"success": True, "message": "Schema 注册成功"}
        
        # 生成 Schema
        @app.post("/api/schema/generate")
        async def generate_schema(request: GenerateRequest):
            result = self.generate_schema_from_db(use_ai=request.use_ai)
            return {"entities": result.get("entities", [])}
        
        # 检查 Schema 完整性
        @app.get("/api/schema/check")
        async def check_schema():
            return self.check_schema_completeness()
        
        print(f"🚀 AI Agent 服务已启动: http://{host}:{port}")
        print(f"📖 API 文档: http://{host}:{port}/docs")
        uvicorn.run(app, host=host, port=port)
