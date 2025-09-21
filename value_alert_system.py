#!/usr/bin/env python3
"""
股票价值分析预警系统
提供多渠道的价值偏离预警通知
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from stock_value_analysis_system import StockValueAnalysisSystem
import schedule
import threading
import os
from dataclasses import dataclass
import requests
import hashlib
import yaml

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AlertConfig:
    """预警配置数据类"""
    symbol: str
    alert_type: str  # 'overvalued', 'undervalued', 'deviation'
    threshold: float
    enabled: bool = True
    email_enabled: bool = False
    webhook_enabled: bool = False
    sms_enabled: bool = False
    cooldown_hours: int = 24
    last_triggered: Optional[datetime] = None

class ValueAlertSystem:
    """价值预警系统主类"""
    
    def __init__(self, config_file: str = "alert_config.yaml"):
        self.config_file = config_file
        self.system = StockValueAnalysisSystem()
        self.db_path = "value_alerts.db"
        self._init_database()
        self.config = self._load_config()
        self.running = False
        self.scheduler_thread = None
    
    def _init_database(self):
        """初始化预警数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 预警配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                threshold REAL NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                email_enabled BOOLEAN DEFAULT 0,
                webhook_enabled BOOLEAN DEFAULT 0,
                sms_enabled BOOLEAN DEFAULT 0,
                cooldown_hours INTEGER DEFAULT 24,
                last_triggered DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 预警历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                current_price REAL NOT NULL,
                fair_value_low REAL NOT NULL,
                fair_value_high REAL NOT NULL,
                deviation REAL NOT NULL,
                alert_message TEXT,
                email_sent BOOLEAN DEFAULT 0,
                webhook_sent BOOLEAN DEFAULT 0,
                sms_sent BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 系统配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        default_config = {
            'email': {
                'enabled': False,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'from_email': '',
                'to_emails': []
            },
            'webhook': {
                'enabled': False,
                'urls': [],
                'secret': ''
            },
            'sms': {
                'enabled': False,
                'api_key': '',
                'api_secret': '',
                'phone_numbers': []
            },
            'scheduler': {
                'enabled': True,
                'check_interval_minutes': 60,
                'market_hours_only': True
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    if user_config:
                        # 合并配置
                        for key in default_config:
                            if key in user_config:
                                default_config[key].update(user_config[key])
            except Exception as e:
                logger.error(f"加载配置文件失败：{e}")
        
        return default_config
    
    def add_alert_config(self, config: AlertConfig) -> bool:
        """添加预警配置"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alert_configs (symbol, alert_type, threshold, enabled, 
                                         email_enabled, webhook_enabled, sms_enabled, 
                                         cooldown_hours, last_triggered)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                config.symbol, config.alert_type, config.threshold, config.enabled,
                config.email_enabled, config.webhook_enabled, config.sms_enabled,
                config.cooldown_hours, config.last_triggered
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"添加预警配置成功：{config.symbol} - {config.alert_type}")
            return True
            
        except Exception as e:
            logger.error(f"添加预警配置失败：{e}")
            return False
    
    def get_alert_configs(self, symbol: str = None, enabled_only: bool = True) -> List[AlertConfig]:
        """获取预警配置"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM alert_configs WHERE 1=1"
            params = []
            
            if symbol:
                query += " AND symbol = ?"
                params.append(symbol)
            
            if enabled_only:
                query += " AND enabled = 1"
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            configs = []
            for row in rows:
                config = AlertConfig(
                    symbol=row[1],
                    alert_type=row[2],
                    threshold=row[3],
                    enabled=bool(row[4]),
                    email_enabled=bool(row[5]),
                    webhook_enabled=bool(row[6]),
                    sms_enabled=bool(row[7]),
                    cooldown_hours=row[8],
                    last_triggered=row[9]
                )
                configs.append(config)
            
            conn.close()
            return configs
            
        except Exception as e:
            logger.error(f"获取预警配置失败：{e}")
            return []
    
    def check_alerts(self, symbol: str) -> List[Dict]:
        """检查预警条件"""
        try:
            # 获取股票分析结果
            analysis_result = self.system.run_comprehensive_analysis(symbol)
            
            if not analysis_result:
                return []
            
            # 获取预警配置
            alert_configs = self.get_alert_configs(symbol)
            
            triggered_alerts = []
            
            for config in alert_configs:
                if not config.enabled:
                    continue
                
                # 检查冷却时间
                if config.last_triggered and \
                   (datetime.now() - config.last_triggered).total_seconds() / 3600 < config.cooldown_hours:
                    continue
                
                # 检查预警条件
                value_trend = analysis_result['value_trend']
                deviation = value_trend['deviation']
                current_price = analysis_result['current_price']
                fair_value_range = value_trend['fair_value_range']
                
                should_trigger = False
                alert_message = ""
                
                if config.alert_type == 'overvalued':
                    if deviation > config.threshold:
                        should_trigger = True
                        alert_message = f"{symbol} 出现高估风险，当前价格高于合理价值 {deviation:.1%}"
                
                elif config.alert_type == 'undervalued':
                    if deviation < -config.threshold:
                        should_trigger = True
                        alert_message = f"{symbol} 出现低估机会，当前价格低于合理价值 {abs(deviation):.1%}"
                
                elif config.alert_type == 'deviation':
                    if abs(deviation) > config.threshold:
                        should_trigger = True
                        direction = "高估" if deviation > 0 else "低估"
                        alert_message = f"{symbol} 出现价值偏离，当前价格{direction} {abs(deviation):.1%}"
                
                if should_trigger:
                    alert_info = {
                        'symbol': symbol,
                        'alert_type': config.alert_type,
                        'current_price': current_price,
                        'fair_value_low': fair_value_range[0],
                        'fair_value_high': fair_value_range[1],
                        'deviation': deviation,
                        'alert_message': alert_message,
                        'config': config
                    }
                    triggered_alerts.append(alert_info)
                    
                    # 保存预警历史
                    self._save_alert_history(alert_info)
                    
                    # 更新最后触发时间
                    self._update_last_triggered(symbol, config.alert_type)
            
            return triggered_alerts
            
        except Exception as e:
            logger.error(f"检查预警失败：{e}")
            return []
    
    def _save_alert_history(self, alert_info: Dict):
        """保存预警历史"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alert_history (symbol, alert_type, current_price, 
                                         fair_value_low, fair_value_high, deviation, 
                                         alert_message, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert_info['symbol'],
                alert_info['alert_type'],
                alert_info['current_price'],
                alert_info['fair_value_low'],
                alert_info['fair_value_high'],
                alert_info['deviation'],
                alert_info['alert_message'],
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"保存预警历史失败：{e}")
    
    def _update_last_triggered(self, symbol: str, alert_type: str):
        """更新最后触发时间"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE alert_configs 
                SET last_triggered = ? 
                WHERE symbol = ? AND alert_type = ?
            ''', (datetime.now(), symbol, alert_type))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"更新最后触发时间失败：{e}")
    
    def send_alert_notifications(self, alerts: List[Dict]) -> bool:
        """发送预警通知"""
        success_count = 0
        
        for alert in alerts:
            config = alert['config']
            
            # 邮件通知
            if config.email_enabled and self.config['email']['enabled']:
                if self._send_email_alert(alert):
                    alert['email_sent'] = True
                    success_count += 1
            
            # Webhook通知
            if config.webhook_enabled and self.config['webhook']['enabled']:
                if self._send_webhook_alert(alert):
                    alert['webhook_sent'] = True
                    success_count += 1
            
            # 短信通知
            if config.sms_enabled and self.config['sms']['enabled']:
                if self._send_sms_alert(alert):
                    alert['sms_sent'] = True
                    success_count += 1
        
        logger.info(f"预警通知发送完成，成功发送 {success_count} 条")
        return success_count > 0
    
    def _send_email_alert(self, alert: Dict) -> bool:
        """发送邮件预警"""
        try:
            email_config = self.config['email']
            
            msg = MIMEMultipart()
            msg['From'] = email_config['from_email']
            msg['To'] = ', '.join(email_config['to_emails'])
            msg['Subject'] = f"股票价值预警 - {alert['symbol']}"
            
            body = f"""
股票代码：{alert['symbol']}
预警类型：{alert['alert_type']}
当前价格：¥{alert['current_price']:.2f}
合理价值区间：¥{alert['fair_value_low']:.2f} - ¥{alert['fair_value_high']:.2f}
偏离度：{alert['deviation']:.1%}

{alert['alert_message']}

分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # 连接SMTP服务器并发送
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['username'], email_config['password'])
                server.send_message(msg)
            
            logger.info(f"邮件预警发送成功：{alert['symbol']}")
            return True
            
        except Exception as e:
            logger.error(f"邮件预警发送失败：{e}")
            return False
    
    def _send_webhook_alert(self, alert: Dict) -> bool:
        """发送Webhook预警"""
        try:
            webhook_config = self.config['webhook']
            
            payload = {
                'symbol': alert['symbol'],
                'alert_type': alert['alert_type'],
                'current_price': alert['current_price'],
                'fair_value_low': alert['fair_value_low'],
                'fair_value_high': alert['fair_value_high'],
                'deviation': alert['deviation'],
                'message': alert['alert_message'],
                'timestamp': datetime.now().isoformat()
            }
            
            success_count = 0
            for webhook_url in webhook_config['urls']:
                try:
                    headers = {'Content-Type': 'application/json'}
                    
                    # 如果配置了secret，添加签名
                    if webhook_config.get('secret'):
                        signature = self._generate_webhook_signature(payload, webhook_config['secret'])
                        headers['X-Signature'] = signature
                    
                    response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        success_count += 1
                        logger.info(f"Webhook预警发送成功：{webhook_url}")
                    else:
                        logger.warning(f"Webhook预警发送失败：{response.status_code}")
                        
                except Exception as e:
                    logger.error(f"Webhook发送失败：{webhook_url} - {e}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Webhook预警发送失败：{e}")
            return False
    
    def _generate_webhook_signature(self, payload: Dict, secret: str) -> str:
        """生成Webhook签名"""
        import hashlib
        import hmac
        
        message = json.dumps(payload, sort_keys=True)
        signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
        return signature
    
    def _send_sms_alert(self, alert: Dict) -> bool:
        """发送短信预警（需要第三方SMS服务）"""
        try:
            # 这里需要集成具体的短信服务API
            # 例如阿里云短信、腾讯云短信等
            
            sms_config = self.config['sms']
            
            # 简化实现，实际使用时需要集成具体的SMS服务
            sms_content = f"股票{alert['symbol']}价值预警：{alert['alert_message']}"
            
            logger.info(f"SMS预警内容：{sms_content}")
            
            # 这里应该调用具体的SMS API
            # 由于需要具体的SMS服务配置，这里仅作示例
            
            return True  # 模拟成功
            
        except Exception as e:
            logger.error(f"短信预警发送失败：{e}")
            return False
    
    def get_alert_history(self, symbol: str = None, days: int = 30, limit: int = 100) -> List[Dict]:
        """获取预警历史"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = ""
            params = []
            
            if symbol:
                query = '''
                    SELECT * FROM alert_history 
                    WHERE symbol = ? AND created_at >= datetime('now', '-' || ? || ' days')
                    ORDER BY created_at DESC LIMIT ?
                '''
                params = [symbol, days, limit]
            else:
                query = '''
                    SELECT * FROM alert_history 
                    WHERE created_at >= datetime('now', '-' || ? || ' days')
                    ORDER BY created_at DESC LIMIT ?
                '''
                params = [days, limit]
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                history.append({
                    'id': row[0],
                    'symbol': row[1],
                    'alert_type': row[2],
                    'current_price': row[3],
                    'fair_value_low': row[4],
                    'fair_value_high': row[5],
                    'deviation': row[6],
                    'alert_message': row[7],
                    'email_sent': bool(row[8]),
                    'webhook_sent': bool(row[9]),
                    'sms_sent': bool(row[10]),
                    'created_at': row[11]
                })
            
            conn.close()
            return history
            
        except Exception as e:
            logger.error(f"获取预警历史失败：{e}")
            return []
    
    def run_scheduler(self):
        """运行调度器"""
        if self.running:
            logger.warning("调度器已经在运行中")
            return
        
        self.running = True
        
        # 获取所有启用的预警配置
        alert_configs = self.get_alert_configs(enabled_only=True)
        
        if not alert_configs:
            logger.info("没有启用的预警配置，调度器不启动")
            self.running = False
            return
        
        logger.info(f"启动价值预警调度器，监控 {len(alert_configs)} 个预警")
        
        # 定义检查函数
        def check_all_alerts():
            if not self.running:
                return
            
            logger.info("开始检查所有股票预警")
            
            # 获取所有需要监控的股票
            symbols = list(set(config.symbol for config in alert_configs))
            
            for symbol in symbols:
                try:
                    logger.info(f"检查股票 {symbol} 的预警")
                    
                    # 检查预警
                    alerts = self.check_alerts(symbol)
                    
                    if alerts:
                        logger.info(f"{symbol} 触发 {len(alerts)} 个预警")
                        
                        # 发送通知
                        self.send_alert_notifications(alerts)
                        
                        # 记录日志
                        for alert in alerts:
                            logger.info(f"预警触发：{alert['alert_message']}")
                    
                except Exception as e:
                    logger.error(f"检查股票 {symbol} 预警失败：{e}")
            
            logger.info("完成所有股票预警检查")
        
        # 设置定时任务
        check_interval = self.config.get('scheduler', {}).get('check_interval_minutes', 60)
        schedule.every(check_interval).minutes.do(check_all_alerts)
        
        # 运行调度器
        logger.info(f"调度器启动成功，每{check_interval}分钟检查一次")
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
        
        logger.info("调度器已停止")
    
    def start_scheduler(self):
        """启动调度器线程"""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            logger.warning("调度器线程已在运行中")
            return
        
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("调度器线程启动成功")
    
    def stop_scheduler(self):
        """停止调度器"""
        self.running = False
        schedule.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        logger.info("调度器已停止")

def main():
    """主函数 - 演示预警系统功能"""
    print("=" * 60)
    print("股票价值分析预警系统")
    print("=" * 60)
    
    # 创建预警系统实例
    alert_system = ValueAlertSystem()
    
    # 添加一些示例预警配置
    configs = [
        AlertConfig(symbol="601899", alert_type="undervalued", threshold=0.30),
        AlertConfig(symbol="000001", alert_type="overvalued", threshold=0.25),
        AlertConfig(symbol="600519", alert_type="deviation", threshold=0.20)
    ]
    
    for config in configs:
        alert_system.add_alert_config(config)
    
    print(f"已添加 {len(configs)} 个预警配置")
    
    # 手动检查一次预警
    print("\n手动检查预警...")
    for config in configs:
        alerts = alert_system.check_alerts(config.symbol)
        if alerts:
            print(f"{config.symbol} 触发 {len(alerts)} 个预警")
            alert_system.send_alert_notifications(alerts)
        else:
            print(f"{config.symbol} 未触发预警")
    
    # 获取预警历史
    print("\n获取最近预警历史...")
    history = alert_system.get_alert_history(days=7)
    print(f"最近7天有 {len(history)} 条预警记录")
    
    print("\n" + "=" * 60)
    print("预警系统演示完成")
    print("=" * 60)

if __name__ == "__main__":
    main()