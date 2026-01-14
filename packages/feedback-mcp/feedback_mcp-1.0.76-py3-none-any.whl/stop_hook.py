#!/usr/bin/env python3
"""
Stop Hook处理脚本
智能处理stop事件，通过检查AI消息中的停止标记来决定是否允许停止
"""
import sys
import json
import os
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from context_formatter import format_for_stop_hook

# 停止标记常量
STOP_MARKER = "<用户已明确告知停止工作>"


def check_stop_marker_in_transcript(transcript_path: str) -> bool:
    """检查 transcript 中最后一条 AI 消息是否包含停止标记

    Args:
        transcript_path: 对话记录文件路径 (JSONL格式)

    Returns:
        如果最后一条 AI 消息包含停止标记则返回 True
    """
    try:
        if not transcript_path:
            return False

        path = Path(transcript_path)
        if not path.exists():
            return False

        # 读取 JSONL 文件，找最后一条 assistant 消息
        last_assistant_msg = None
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get('type') == 'assistant':
                        last_assistant_msg = entry
                except json.JSONDecodeError:
                    continue

        if not last_assistant_msg:
            return False

        # 检查消息内容是否包含停止标记
        message = last_assistant_msg.get('message', {})
        content = message.get('content', [])

        for item in content:
            if isinstance(item, dict) and item.get('type') == 'text':
                text = item.get('text', '')
                if STOP_MARKER in text:
                    return True
            elif isinstance(item, str):
                if STOP_MARKER in item:
                    return True

        return False
    except Exception:
        return False


def main():
    """主函数"""
    try:
        # 从stdin读取JSON输入
        input_data = json.load(sys.stdin)

        # 提取关键信息
        session_id = input_data.get('session_id', '')
        transcript_path = input_data.get('transcript_path', '')

        # 获取项目路径
        project_path = os.getcwd()

        # 检查 transcript 中是否有停止标记
        if check_stop_marker_in_transcript(transcript_path):
            # AI 已声明停止，允许停止
            return 0

        # 默认行为：阻止停止并提示使用feedback工具
        if session_id:
            reason_text = format_for_stop_hook(session_id, project_path)
        else:
            reason_text = "请你调用 feedback mcp tool 向用户反馈/请示。示例：使用 mcp__feedback__feedback 工具向用户汇报当前工作进度、完成状态或请求下一步指示。"

        result = {
            "decision": "block",
            "reason": reason_text
        }
        print(json.dumps(result, ensure_ascii=False))
        return 0

    except Exception as e:
        # 发生错误时，默认允许停止（避免卡死）
        error_result = {
            "decision": "approve",
            "reason": f"Hook处理出错: {str(e)}"
        }
        print(json.dumps(error_result, ensure_ascii=False), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
