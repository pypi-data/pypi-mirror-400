#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例：如何使用 fast2common.actions 模块

这个示例展示了如何在 node_service.py 中集成新的 actions 模块
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

from fast2common.actions import (
    ActionExecutor,
    ActionContext,
    ActionResult,
)


async def example_send_log(task_id: str, message: str, log_type: str = "stdout"):
    """示例日志回调函数"""
    print(f"[{log_type}] {message}")


async def example_basic_usage():
    """示例 1: 基本使用方式"""
    print("\n" + "="*70)
    print("示例 1: 基本使用方式")
    print("="*70)

    # 创建执行上下文
    context = ActionContext(
        device_id="emulator-5554",
        package_name="com.example.app",
        main_activity=".MainActivity",
        task_id="test_task_001",
        screenshot_dir="screenshots"
    )

    # 示例 1: 执行等待操作
    print("\n--- 执行等待操作 ---")
    result = await ActionExecutor.execute(
        action_type="wait",
        action_data={"duration": 1},
        context=context,
        send_log_callback=example_send_log
    )
    print(f"结果: success={result.success}, message={result.message}")

    # 示例 2: 执行返回键操作（需要设备，这里仅展示）
    print("\n--- 返回键操作（示例） ---")
    print("注意: 实际执行需要连接设备")
    # result = await ActionExecutor.execute(
    #     action_type="press_back",
    #     action_data={},
    #     context=context,
    #     send_log_callback=example_send_log
    # )


async def example_execute_test_steps():
    """示例 2: 执行完整的测试步骤"""
    print("\n" + "="*70)
    print("示例 2: 执行测试步骤流程")
    print("="*70)

    context = ActionContext(
        device_id="emulator-5554",
        package_name="com.example.app",
        main_activity=".MainActivity",
        task_id="test_task_002"
    )

    # 测试步骤
    test_steps = [
        {
            "sequence": 1,
            "action_type": "wait",
            "action_data": {"duration": 0.5},
            "description": "等待0.5秒"
        },
        {
            "sequence": 2,
            "action_type": "wait",
            "action_data": {"duration": 0.5},
            "description": "再等待0.5秒"
        }
    ]

    print(f"\n执行 {len(test_steps)} 个测试步骤...")

    for step in test_steps:
        print(f"\n步骤 {step['sequence']}: {step['description']}")
        result = await ActionExecutor.execute(
            action_type=step["action_type"],
            action_data=step["action_data"],
            context=context,
            send_log_callback=example_send_log
        )

        if result.success:
            print(f"✅ 成功: {result.message} (耗时: {result.execution_time:.2f}s)")
        else:
            print(f"❌ 失败: {result.error}")
            break


async def example_check_supported_actions():
    """示例 3: 查看支持的操作类型"""
    print("\n" + "="*70)
    print("示例 3: 支持的操作类型")
    print("="*70)

    supported = ActionExecutor.get_supported_actions()
    print(f"\n支持 {len(supported)} 种操作类型:")
    for action_type in sorted(supported):
        print(f"  - {action_type}")


async def example_custom_action():
    """示例 4: 创建自定义操作"""
    print("\n" + "="*70)
    print("示例 4: 创建自定义操作")
    print("="*70)

    from fast2common.actions.base import BaseAction, ActionContext, ActionResult
    from typing import Dict, Any, Optional
    import time

    class CustomAction(BaseAction):
        """自定义操作示例"""
        action_type = "custom_greet"
        description = "自定义问候操作"

        async def execute(
            self,
            action_data: Dict[str, Any],
            context: ActionContext,
            send_log_callback: Optional[callable] = None
        ) -> ActionResult:
            start_time = time.time()

            name = action_data.get("name", "World")

            await self.send_log(
                context.task_id,
                f"👋 Hello, {name}!",
                "stdout",
                send_log_callback
            )

            return ActionResult(
                success=True,
                message=f"Greeted {name}",
                data={"name": name},
                execution_time=time.time() - start_time
            )

    # 注册自定义操作
    ActionExecutor.register_action("custom_greet", CustomAction)
    print("\n已注册自定义操作: custom_greet")

    # 使用自定义操作
    context = ActionContext(
        device_id="test_device",
        task_id="custom_test"
    )

    result = await ActionExecutor.execute(
        action_type="custom_greet",
        action_data={"name": "Claude"},
        context=context,
        send_log_callback=example_send_log
    )

    print(f"结果: {result.message}")


async def main():
    """主函数"""
    print("\n" + "="*70)
    print("fast2common.actions 使用示例")
    print("="*70)

    try:
        # 示例 1: 基本使用
        await example_basic_usage()

        # 示例 2: 执行测试步骤
        await example_execute_test_steps()

        # 示例 3: 查看支持的操作
        await example_check_supported_actions()

        # 示例 4: 自定义操作
        await example_custom_action()

        print("\n" + "="*70)
        print("所有示例执行完成！")
        print("="*70)

    except Exception as e:
        print(f"\n❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
