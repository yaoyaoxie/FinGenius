#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国稀土阶梯分析Agent调用脚本
使用说明：在命令行输入【阶梯分析启动】即可调用完整分析
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数 - 响应【阶梯分析启动】指令"""
    
    # 检查是否是通过【阶梯分析启动】调用
    if len(sys.argv) > 1 and sys.argv[1] == "【阶梯分析启动】":
        print("🎯 中国稀土阶梯分析系统启动中...")
        print("=" * 60)
        
        try:
            # 导入并运行Agent
            from china_rare_earth_agent import china_rare_earth_agent
            
            # 获取完整分析报告
            report = china_rare_earth_agent.generate_investment_report()
            print(report)
            
            print("\n" + "=" * 60)
            print("✅ 分析完成！")
            print("💡 核心建议：当前56.47元偏高，等待36-42元区间布局")
            
        except Exception as e:
            print(f"❌ 分析系统启动失败: {e}")
            print("💡 请确保china_rare_earth_agent.py文件存在")
            
    else:
        print("💡 使用说明：")
        print("在命令行输入：python call_agent.py 【阶梯分析启动】")
        print("或直接运行：python china_rare_earth_agent.py")

if __name__ == "__main__":
    main()