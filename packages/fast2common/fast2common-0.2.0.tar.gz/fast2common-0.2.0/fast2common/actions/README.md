# Test Case Actions 使用指南

## 概述

`fast2common.actions` 模块提供了一套可扩展的测试用例步骤操作实现，将各种操作类型解耦到独立的文件中，便于维护和扩展。

## 目录结构

```
fast2common_dist/fast2common/actions/
├── __init__.py                 # 模块入口
├── base.py                     # 基础类和数据结构
├── executor.py                 # 统一执行器
├── tap_action.py              # 点击操作
├── swipe_action.py            # 滑动操作
├── launch_app_action.py       # 启动应用
├── close_app_action.py        # 关闭应用
├── input_action.py            # 输入文本
├── wait_action.py             # 等待
├── press_back_action.py       # 返回键
└── screenshot_action.py       # 截图
```

## 核心组件

### 1. BaseAction（基类）

所有操作的基础类，定义了操作的基本接口：

```python
class BaseAction(ABC):
    action_type: str = ""        # 操作类型标识
    description: str = ""        # 操作描述

    async def execute(
        self,
        action_data: Dict[str, Any],
        context: ActionContext,
        send_log_callback: Optional[callable] = None
    ) -> ActionResult:
        """执行操作"""
        pass
```

### 2. ActionContext（执行上下文）

包含执行操作所需的上下文信息：

```python
@dataclass
class ActionContext:
    device_id: str                      # 设备 ID
    package_name: Optional[str]         # 应用包名
    main_activity: Optional[str]        # 主 Activity
    task_id: str = ""                   # 任务 ID
    screenshot_dir: str = "screenshots" # 截图目录
    execution_id: str = ""              # 执行 ID
    test_case_id: str = ""              # 测试用例 ID
    metadata: Dict[str, Any]            # 额外元数据
```

### 3. ActionResult（执行结果）

返回操作执行的结果：

```python
@dataclass
class ActionResult:
    success: bool                        # 是否成功
    message: str = ""                    # 结果消息
    data: Dict[str, Any]                 # 结果数据
    error: Optional[str] = None          # 错误信息
    execution_time: float = 0.0          # 执行时间（秒）
```

### 4. ActionExecutor（执行器）

统一的操作执行入口，根据类型路由到具体实现：

```python
# 方式 1: 使用类方法
result = await ActionExecutor.execute(
    action_type="tap",
    action_data={"x": 100, "y": 200},
    context=context
)

# 方式 2: 使用便捷函数
from fast2common.actions import execute_action

result = await execute_action(
    action_type="swipe",
    action_data={"start_x": 100, "start_y": 200, "end_x": 300, "end_y": 400},
    context=context
)
```

## 在 node_service.py 中的使用方式

### 原来的实现（需要重构）

```python
# node_service.py 旧代码（2541-2696行）
if action_type == "tap":
    x, y = await self._resolve_tap_coordinates(action_data, device_id, task_id)
    if x is not None and y is not None:
        result = await self._execute_adb_command_internal(
            device_id,
            ["shell", "input", "tap", str(x), str(y)],
            task_id
        )
        step_success = result.get("success", False)
elif action_type == "swipe":
    x1 = action_data.get("start_x")
    y1 = action_data.get("start_y")
    x2 = action_data.get("end_x")
    y2 = action_data.get("end_y")
    duration = action_data.get("duration_ms", 300)
    # ... 执行逻辑
elif action_type == "launch_app":
    # ... 启动应用逻辑
# ... 更多操作类型
```

### 新的实现方式（推荐）

```python
# node_service.py 新代码
from fast2common.actions import ActionExecutor, ActionContext

async def _execute_test_case(self, args: Dict[str, Any], task_id: str) -> Dict[str, Any]:
    """执行测试用例"""

    # 准备执行上下文
    context = ActionContext(
        device_id=args.get("device_id"),
        package_name=args.get("app", {}).get("package_name"),
        main_activity=args.get("app", {}).get("main_activity"),
        task_id=task_id,
        screenshot_dir=args.get("screenshot_dir", "screenshots"),
        execution_id=args.get("execution_id", ""),
        test_case_id=args.get("test_case_id", "")
    )

    steps = args.get("steps", [])

    for idx, step in enumerate(steps):
        action_type = step.get("action_type")
        action_data = step.get("action_data", {})

        # 使用 ActionExecutor 执行操作
        result = await ActionExecutor.execute(
            action_type=action_type,
            action_data=action_data,
            context=context,
            send_log_callback=self.send_log  # 传递日志回调
        )

        if result.success:
            print(f"✅ {action_type} 成功: {result.message}")
            # 处理结果数据
            if result.data:
                print(f"   数据: {result.data}")
        else:
            print(f"❌ {action_type} 失败: {result.error}")
            # 处理错误
            break
```

## 支持的操作类型

| 操作类型 | 说明 | action_data 格式 |
|---------|------|-----------------|
| `tap` | 点击屏幕 | `{"x": 100, "y": 200}` 或 `{"icon_description": "..."}` |
| `swipe` | 滑动手势 | `{"start_x": 100, "start_y": 200, "end_x": 300, "end_y": 400, "duration_ms": 300}` |
| `launch_app` | 启动应用 | `{"package_name": "com.example.app", "main_activity": ".MainActivity"}` |
| `close_app` | 关闭应用 | `{"package_name": "com.example.app"}` |
| `输入` / `input` | 输入文本 | `{"text": "Hello World"}` |
| `wait` | 等待 | `{"duration": 2}` |
| `press_back` | 返回键 | `{}` (无需参数) |
| `screenshot` | 截图 | `{}` (标记操作) |

## 扩展新的操作类型

### 1. 创建新的 Action 类

```python
# long_press_action.py
from .base import BaseAction, ActionContext, ActionResult

class LongPressAction(BaseAction):
    """长按操作"""

    action_type = "long_press"
    description = "Long press on screen"

    async def execute(
        self,
        action_data: Dict[str, Any],
        context: ActionContext,
        send_log_callback: Optional[callable] = None
    ) -> ActionResult:
        """执行长按操作"""
        # 实现长按逻辑
        x = action_data.get("x")
        y = action_data.get("y")
        duration = action_data.get("duration_ms", 1000)

        # 执行 ADB 长按命令
        # ...

        return ActionResult(
            success=True,
            message=f"Long pressed at ({x}, {y}) for {duration}ms",
            data={"x": x, "y": y, "duration": duration}
        )
```

### 2. 注册新操作

```python
# 在 executor.py 中注册
from .long_press_action import LongPressAction

class ActionExecutor:
    ACTION_REGISTRY: Dict[str, Type[BaseAction]] = {
        # ... 现有操作
        "long_press": LongPressAction,  # 新增
    }
```

### 3. 或动态注册

```python
# 在运行时注册
from fast2common.actions import ActionExecutor, LongPressAction

ActionExecutor.register_action("long_press", LongPressAction)
```

## 优势

1. **解耦**: 每个操作类型独立文件，互不影响
2. **可扩展**: 轻松添加新操作类型
3. **可维护**: 代码结构清晰，易于定位和修改
4. **可测试**: 每个操作可独立测试
5. **统一接口**: 所有操作使用相同的调用方式
6. **灵活复用**: 可在不同场景复用操作实现

## 迁移计划

1. ✅ 创建 actions 模块结构
2. ✅ 实现基础操作类型
3. ✅ 创建 ActionExecutor
4. ⏳ 在 node_service.py 中逐步替换现有实现
5. ⏳ 添加单元测试
6. ⏳ 性能优化和错误处理增强

## 注意事项

1. **向后兼容**: 保留了 "输入" (中文) 和 "input" (英文) 两种写法
2. **错误处理**: 每个操作都有完善的错误处理和日志记录
3. **异步支持**: 所有操作都是异步的，适合高并发场景
4. **日志回调**: 支持传入日志回调函数，实时推送执行日志

## 示例：完整测试用例

```python
# 测试用例示例
test_case = {
    "test_case_id": "login_001",
    "execution_id": "exec_001",
    "device_id": "emulator-5554",
    "app": {
        "package_name": "com.example.app",
        "main_activity": ".MainActivity"
    },
    "steps": [
        {
            "id": "step1",
            "sequence": 1,
            "action_type": "launch_app",
            "action_data": {},
            "description": "启动应用"
        },
        {
            "id": "step2",
            "sequence": 2,
            "action_type": "tap",
            "action_data": {
                "icon_description": "登录按钮"
            },
            "description": "点击登录按钮"
        },
        {
            "id": "step3",
            "sequence": 3,
            "action_type": "输入",
            "action_data": {
                "text": "test_user"
            },
            "description": "输入用户名"
        },
        {
            "id": "step4",
            "sequence": 4,
            "action_type": "wait",
            "action_data": {
                "duration": 2
            },
            "description": "等待2秒"
        },
        {
            "id": "step5",
            "sequence": 5,
            "action_type": "press_back",
            "action_data": {},
            "description": "返回"
        }
    ]
}

# 执行测试用例
context = ActionContext(
    device_id=test_case["device_id"],
    package_name=test_case["app"]["package_name"],
    main_activity=test_case["app"]["main_activity"],
    task_id="task_001"
)

for step in test_case["steps"]:
    result = await ActionExecutor.execute(
        action_type=step["action_type"],
        action_data=step["action_data"],
        context=context
    )

    if not result.success:
        print(f"步骤 {step['sequence']} 失败: {result.error}")
        break
```
