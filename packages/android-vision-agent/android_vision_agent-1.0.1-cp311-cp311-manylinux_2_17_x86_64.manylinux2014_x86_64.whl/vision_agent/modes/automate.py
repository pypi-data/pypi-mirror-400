"""Automate mode - Multi-step automation with embedded prompts."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from vision_agent.utils.action_executor import ActionHandler, parse_action
import vision_agent.device.adb as adb
from vision_agent.modes.llmclient import LlmClient
from vision_agent.utils.image import base64_to_image_bytes


# System prompts embedded in this mode
def _get_system_prompt(lang: str = "cn") -> str:
    """Get system prompt by language."""
    today = datetime.today()

    if lang == "en":
        formatted_date = today.strftime("%Y-%m-%d, %A")
        return (
            "The current date: "
            + formatted_date
            + """
You are an Android operation assistant. Observe screenshots and execute tasks.

Output format:
1. Brief explanation of what you see and why you do this
2. do(action="...", ...) or finish(message="...")

Available actions:
- do(action="Tap", element=[x,y])
- do(action="Type", text="text")
- do(action="Swipe", start=[x1,y1], end=[x2,y2])
- do(action="Back")
- do(action="Home")
- do(action="Long Press", element=[x,y])
- do(action="Wait", duration="x seconds")
- finish(message="completion message")

Important:
1. Carefully observe screenshots, decide based on actual visible elements
2. If action fails, immediately try different method (tap coordinates/search/swipe)
3. Check screen changes after each action
"""
        )

    # Chinese prompt
    weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday = weekday_names[today.weekday()]
    formatted_date = today.strftime("%Y年%m月%d日") + " " + weekday

    return (
        "今天的日期是: "
        + formatted_date
        + """

# 你的身份和任务
你正在远程操作一台真实的 Android 设备（可能是手机、平板、车机）。
你通过观察设备的实时屏幕截图来执行用户的任务。

# 设备特性理解
1. **物理限制**：这是真实设备，操作需要时间响应，界面加载需要等待
2. **触摸交互**：所有操作都是模拟手指触摸，坐标必须精确
3. **屏幕尺寸**：设备有固定的屏幕分辨率，列表内容可能超出可见区域
4. **应用状态**：应用可能卡顿、崩溃、加载缓慢，需要灵活应对
5. **系统行为**：Android系统有返回键、主屏幕键等标准导航方式

# 系统导航栏识别（重要）
屏幕顶部或底部通常有系统导航栏，你必须学会识别这些标准图标：
- **房子图标** → 主屏幕/桌面
- **四宫格/九宫格** → 应用列表/所有应用
- **左箭头/三角形** → 返回上一级
- **正方形/双矩形** → 最近任务/多任务切换
- **齿轮图标** → 系统设置
- **三条横线/汉堡菜单** → 侧边栏菜单
- **三个点** → 更多选项/溢出菜单

当你需要进入某个系统功能时：
1. 先观察屏幕上下边缘的导航栏图标
2. 识别每个图标的含义
3. 通过点击对应图标进入目标功能
4. 如果当前应用全屏，尝试 Home 操作回到主屏幕

# 输出格式
1. 简短说明你看到什么，为什么这样做
2. do(action="操作", ...) 或 finish(message="...")

# 可用操作
- do(action="Tap", element=[x,y])  # 坐标范围 0-999
- do(action="Type", text="文本")
- do(action="Swipe", start=[x1,y1], end=[x2,y2])  # 滑动手势
- do(action="Back")
- do(action="Home")
- do(action="Long Press", element=[x,y])
- do(action="Wait", duration="x seconds")
- finish(message="完成信息")

# 核心策略

1. **视觉分析优先**
   - 仔细观察截图中的所有可见元素（按钮、图标、文字、列表项, 弹窗, 界面滑动控件）
   - 识别界面类型：主屏幕/应用列表/设置页面/输入框/列表/弹窗
   - 注意滚动条、下拉箭头等提示有更多内容的标志

2. **列表和滚动处理**
   - Android列表通常很长，内容超出屏幕可见区域
   - 看到列表时，先检查目标是否在可见区域
   - 如果目标不可见（如"中文"在语言列表中），必须滑动查看

   **滚动控件识别**（优先级最高）：
   - 首先检查列表旁边是否有滚动控制按钮（上箭头▲、下箭头▼、滚动条等）
   - 如果有这些控件，优先点击它们来滚动，比Swipe更可靠
   - 车机界面经常使用按钮控制滚动而非手势滑动

   **滑动手势**（当没有滚动控件时使用）：
   - 向下滑动查看下方内容：do(action="Swipe", start=[500,700], end=[500,300])
   - 向上滑动查看上方内容：do(action="Swipe", start=[500,300], end=[500,700])
   - 左右滑动切换页面：do(action="Swipe", start=[800,500], end=[200,500])

   **单向持续滑动策略**（关键）：
   - 选定一个方向后，必须持续向该方向滑动，直到：(1)找到目标 或 (2)确认到达边界
   - **禁止来回切换方向**：不要滑动几次就换方向，这样会在同一区域反复徘徊
   - 判断到达边界的方法：连续2次滑动后界面内容完全相同
   - 正确做法：先持续向下滑动到底部，如果没找到，再持续向上滑动到顶部
   - 错误做法：向下滑2次→向上滑1次→向下滑1次（来回切换）
   - 如果整个列表都滑动完毕仍未找到，尝试使用搜索功能

3. **失败后的应对**
   - 如果操作无效（界面未变化），立即分析原因：
     * 是否点击位置不对？重新观察截图找准坐标
     * 是否目标在屏幕外？尝试滑动
     * 是否列表已到底部？尝试反向滑动或使用搜索
     * 是否需要先展开菜单？点击下拉箭头或三点图标
     * 是否应用未响应？尝试 Back 返回或 Home 回到主屏幕
   - 不要重复相同操作超过2次

4. **多路径思维**
   - 方法A失败后，立即尝试方法B、C：
     * 从主屏幕点击图标打开应用
     * 点击按钮 vs 使用搜索功能
     * 逐级导航 vs 直接跳转
   - 优先选择最直接的路径

5. **搜索功能利用**
   - 看到搜索图标（放大镜）时，优先使用搜索
   - 在设置中搜索功能名称比逐级点击更快
   - 在应用列表中搜索应用名比滚动查找更准确

6. **界面状态判断**
   - 每次操作后对比前后截图，确认变化
   - 如果current_app未变但界面变了，说明在同一应用内导航
   - 如果界面完全相同，说明操作未生效，必须立即换方法

7. **坐标精确度**
   - 点击按钮时瞄准中心位置
   - 避免点击边缘或文字外的空白区域
   - 小图标需要更精确的坐标

8. **特殊场景处理**
   - 弹窗/对话框：先处理弹窗再继续主任务
   - 权限请求：根据任务需要选择允许/拒绝
   - 加载中：使用 Wait 等待界面加载完成
   - 键盘遮挡：输入完成后可能需要 Back 关闭键盘

# 关键原则
- 你操作的是真实设备，不是模拟器，每个操作都会产生真实效果
- 观察截图是你唯一的信息来源，必须仔细分析
- 界面未变化 = 操作失败，必须立即调整策略
- 不要假设，不要猜测，基于实际看到的内容决策
"""
    )


def _build_user_message(text: str, image_base64: str) -> dict[str, Any]:
    return {
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
            {"type": "text", "text": text},
        ],
    }


def _strip_images(message: dict[str, Any]) -> None:
    content = message.get("content")
    if isinstance(content, list):
        message["content"] = [item for item in content if item.get("type") == "text"]


def _parse_response(content: str) -> tuple[str, str]:
    """Parse response: split thinking from action."""
    if "finish(message=" in content:
        parts = content.split("finish(message=", 1)
        return parts[0].strip(), "finish(message=" + parts[1]
    if "do(action=" in content:
        parts = content.split("do(action=", 1)
        return parts[0].strip(), "do(action=" + parts[1]
    return "", content.strip()


class AutoRunner:
    """Run multi-step automation using the project action format."""

    def __init__(
        self,
        llm: LlmClient,
        device_id: str | None,
        max_steps: int,
        lang: str = "cn",
        output_dir: str | None = None,
        display_id: int | None = None,
    ):
        self.llm = llm
        self.device_id = device_id
        self.max_steps = max_steps
        self.system_prompt = _get_system_prompt(lang)
        self.output_dir = output_dir
        self.display_id = display_id
        self.action_handler = ActionHandler(device_id=device_id, display_id=display_id)

    def _save_step_screenshot(self, base64_data: str, run_id: str, step: int) -> str | None:
        if not self.output_dir:
            return None
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        suffix = f"_d{self.display_id}" if self.display_id is not None else ""
        path = Path(self.output_dir) / f"{run_id}_step{step:03d}{suffix}.png"
        path.write_bytes(base64_to_image_bytes(base64_data))
        return str(path)

    def run(self, task: str) -> dict[str, Any]:
        context: list[dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt}
        ]

        run_id = time.strftime("%Y%m%d_%H%M%S_automate")
        last_action_text = ""
        last_screenshot_hash = ""
        repeat_count = 0
        no_change_count = 0

        for step in range(self.max_steps):
            screenshot = adb.get_screenshot(self.device_id, display_id=self.display_id)
            current_app = adb.get_current_app(
                self.device_id, display_id=self.display_id
            )
            screenshot_path = self._save_step_screenshot(
                screenshot.base64_data, run_id, step + 1
            )
            if screenshot_path:
                print(f"[DEBUG] Screenshot saved: {screenshot_path}")

            current_screenshot_hash = hashlib.md5(screenshot.base64_data.encode()).hexdigest()

            display_id_for_log = self.display_id if self.display_id is not None else 0
            screen_info = json.dumps(
                {"current_app": current_app, "display_id": display_id_for_log},
                ensure_ascii=False,
            )
            if step == 0:
                text = f"{task}\n\n{screen_info}"
            else:
                text = f"Screen Info:\n{screen_info}"

            context.append(_build_user_message(text, screenshot.base64_data))

            print(f"\n[DEBUG] Step {step + 1} - Sending request with {len(context)} messages")
            print(f"[DEBUG] Screen info: {screen_info}")

            response = self.llm.chat(messages=context, temperature=0.1)

            content = response.choices[0].message.content or ""
            print(f"\n[DEBUG] Model response content:\n{repr(content)}\n")
            thinking, action_text = _parse_response(content)

            # Detect repeated actions
            if action_text == last_action_text:
                repeat_count += 1
                print(f"[WARNING] Repeated action detected ({repeat_count} times): {action_text}")
                if repeat_count >= 2:
                    feedback_text = (
                        f"【最高优先级反馈｜必须严格遵守】\n"
                        f"你刚才的操作 '{action_text}' 已连续执行{repeat_count}次，但界面/截图没有任何可见变化（当前应用：{current_app}）。\n\n"
                        "这不是让你继续'再试一次'的信号；这说明你的界面理解、目标定位或动作前提很可能存在错误。\n"
                        "请立刻停止机械重复，并在下一次回复中进行一次深度复盘（必须写在思考部分）：\n"
                        "1) 重新基于当前截图提取关键信息：页面标题/当前焦点/是否有弹窗或遮罩/是否出现键盘或加载状态/哪些元素明确可点击；\n"
                        "2) 明确解释'为什么界面没变'的最可能原因，并给出截图证据支撑（不要凭空猜测截图里不存在的控件/状态）；\n"
                        "3) 重新制定新的动作规划：下一步必须选择与刚才不同、且能最大化验证你假设的动作，并写清楚你期望看到的界面变化。\n\n"
                        "强制要求：不要重复同一动作；不要沿用旧计划不加验证；本条反馈优先级高于你先前的任何假设。"
                    )
                    context.append(_build_user_message(feedback_text, screenshot.base64_data))
                    repeat_count = 0
                    last_action_text = ""
                    continue
            else:
                repeat_count = 0
                last_action_text = action_text

            try:
                action = parse_action(action_text)
            except ValueError as e:
                error_feedback = (
                    f"解析失败：{e}\n"
                    f"你的输出：{action_text}\n"
                    f"请检查格式，使用正确的等号（=）而非冒号或引号。\n"
                    f"正确示例：do(action=\"Tap\", element=[x,y])"
                )
                context.append(_build_user_message(error_feedback, screenshot.base64_data))
                continue

            _strip_images(context[-1])

            assistant_content = f"{thinking}\n{action_text}" if thinking else action_text
            context.append({"role": "assistant", "content": assistant_content})

            result = self.action_handler.execute(
                action, screenshot.width, screenshot.height
            )

            # Check if screen changed
            if step > 0 and current_screenshot_hash == last_screenshot_hash:
                no_change_count += 1
                print(f"[WARNING] Screen unchanged after action ({no_change_count} times)")

                if no_change_count >= 2:
                    feedback_text = (
                        f"【严重反馈｜必须立即停下并深度思考】\n"
                        f"检测到当前截图与上一轮一致：连续{no_change_count}轮动作后界面仍然完全未变化（当前应用：{current_app}）。\n"
                        f"最近动作：{action_text}\n\n"
                        "这表明你的动作没有生效，或你对当前界面的理解已经偏离。\n"
                        "请把本条反馈当作最高优先级约束：下一次回复必须先重新深度理解当前截图，再输出新的动作规划。\n"
                        "具体要求（必须写在思考部分）：\n"
                        "1) 用一句话重述当前子目标（与任务相关），并说明你认为自己处于哪个页面/状态；\n"
                        "2) 从截图中重新核对可交互对象与状态，指出你之前判断可能错在哪里；\n"
                        "3) 提出至少2个'界面不变'的原因假设，并为每个假设给出一个可验证的判断依据；\n"
                        "4) 选择一个与前两轮不同、信息增益最大的下一步动作来验证假设，并写明预期结果与后续分支。\n\n"
                        "强制要求：不要继续尝试相同模式的操作；不要跳过截图复核；忽略本反馈将被视为失败。"
                    )
                    context.append(_build_user_message(feedback_text, screenshot.base64_data))
                    no_change_count = 0
                    last_screenshot_hash = current_screenshot_hash
                    continue
            else:
                no_change_count = 0

            last_screenshot_hash = current_screenshot_hash

            finished = action.get("_metadata") == "finish" or result.should_finish
            if finished:
                return {
                    "mode": "automate",
                    "status": "finished",
                    "message": result.message or action.get("message", ""),
                    "steps": step + 1,
                }

        return {
            "mode": "automate",
            "status": "max_steps",
            "message": "Max steps reached",
            "steps": self.max_steps,
        }


def run(
    llm: LlmClient,
    prompt: str,
    device_id: str | None = None,
    display_id: int | None = None,
    output_dir: str = "outputs",
    max_steps: int = 50,
    lang: str = "cn",
    **kwargs,
) -> dict[str, Any]:
    """Run multi-step automation."""
    runner = AutoRunner(
        llm, device_id=device_id, max_steps=max_steps, lang=lang,
        output_dir=output_dir, display_id=display_id
    )
    return runner.run(prompt)
