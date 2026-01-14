"""词汇审查插件核心模块。

提供基于关键词列表和正则表达式的消息拦截功能，
支持通过指令动态管理黑名单。
"""

import json
import re
from pathlib import Path

from nonebot import get_driver, logger, on_command
from nonebot.adapters import Bot, Message
from nonebot.exception import MockApiException
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot_plugin_localstore import get_plugin_data_file

from .config import Config, plugin_config

# --- 插件元数据 ---
__plugin_meta__ = PluginMetadata(
    name="词汇黑名单审查",
    description="拦截包含黑名单词汇或匹配正则表达式的机器人发送消息",
    usage="指令：word blacklist add/del/list/refresh/help (支持 regex)",
    type="application",
    homepage="https://github.com/ChlorophyTeio/nonebot-plugin-word-censor",
    config=Config,
    extra={"priority": plugin_config.send_word_priority},
)

_driver = get_driver()

_BLACKLIST_WORDS: list[str] = []
_BLACKLIST_REGEX_STRS: list[str] = []
_COMPILED_REGEX: list[re.Pattern] = []


# 工具函数
def _get_file_path() -> Path:
    """获取黑名单文件的绝对路径。

    Returns:
        解析后的 Path 对象。
    """
    return get_plugin_data_file("send_word_blacklist.json")


def _compile_regex_list() -> None:
    """编译正则表达式字符串列表。

    将 _BLACKLIST_REGEX_STRS 中的字符串编译为正则对象，
    存入 _COMPILED_REGEX 中。如果编译失败，会记录错误日志。
    """
    global _COMPILED_REGEX  # noqa: PLW0603

    _COMPILED_REGEX = []
    for pattern_str in _BLACKLIST_REGEX_STRS:
        try:
            # re.IGNORECASE: 忽略大小写
            pattern = re.compile(pattern_str, re.IGNORECASE)
            _COMPILED_REGEX.append(pattern)
        except re.error as e:
            logger.error(f"正则规则【{pattern_str}】编译失败，已忽略。错误信息: {e}")


def _load_blacklist() -> None:
    """从文件加载黑名单数据。

    读取 JSON 配置文件，更新内存中的关键词列表和正则列表。
    如果文件不存在，会自动创建默认模板。
    """
    global _BLACKLIST_WORDS, _BLACKLIST_REGEX_STRS  # noqa: PLW0603

    file_path = _get_file_path()
    default_data = {"blacklist": [], "regex_blacklist": []}

    # 文件不存在时尝试创建
    if not file_path.exists():
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            logger.error(f"无法创建黑名单文件: {e}")
            return

    # 读取文件
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            _BLACKLIST_WORDS = data.get("blacklist", [])
            _BLACKLIST_REGEX_STRS = data.get("regex_blacklist", [])

            _compile_regex_list()

            logger.info(
                f"黑名单加载完毕: 普通词汇 {len(_BLACKLIST_WORDS)} 个, "
                f"正则规则 {len(_COMPILED_REGEX)} 个"
            )
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"加载黑名单文件失败: {e}")


def _save_blacklist_to_file() -> bool:
    """将内存中的黑名单数据保存到文件。

    Returns:
        bool: 保存成功返回 True，失败返回 False。
    """
    try:
        data = {
            "blacklist": _BLACKLIST_WORDS,
            "regex_blacklist": _BLACKLIST_REGEX_STRS,
        }
        with _get_file_path().open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except OSError as e:
        logger.error(f"保存黑名单失败: {e}")
        return False


def _mask_word(word: str) -> str:
    """对敏感词进行脱敏处理。

    保留首字符，其余字符替换为星号，防止机器人回复时再次触发拦截。

    Args:
        word: 需要脱敏的原始字符串。

    Returns:
        脱敏后的字符串。
    """
    if len(word) <= 1:
        return word + "*"
    return f"{word[0]}{'*' * (len(word) - 1)}"


@_driver.on_startup
async def _init_plugin() -> None:
    """插件启动时的初始化钩子。"""
    _load_blacklist()


# 指令
wb_add = on_command("word blacklist add", permission=SUPERUSER, priority=5, block=True)


@wb_add.handle()
async def _handle_add(args: Message = CommandArg()) -> None:
    """处理添加黑名单指令。"""
    text = args.extract_plain_text().strip()
    if not text:
        await wb_add.finish(r"❌ 请输入内容。例如：/word blacklist add 笨蛋 或 regex \d+")

    # 处理正则添加
    if text.startswith("regex "):
        pattern = text[6:].strip()
        if not pattern:
            await wb_add.finish("❌ 请输入正则表达式。")

        # 预检查正则合法性
        try:
            re.compile(pattern)
        except re.error as e:
            await wb_add.finish(f"❌ 正则表达式语法错误: {e}")

        if pattern in _BLACKLIST_REGEX_STRS:
            await wb_add.finish(f"⚠️ 正则规则【{pattern}】已存在。")

        _BLACKLIST_REGEX_STRS.append(pattern)
        if _save_blacklist_to_file():
            _compile_regex_list()
            await wb_add.finish(f"✅ 已添加正则规则: {pattern}")
        else:
            _BLACKLIST_REGEX_STRS.remove(pattern)
            await wb_add.finish("❌ 保存文件失败，请检查日志。")

    # 处理普通词汇添加
    else:
        word = text
        if word in _BLACKLIST_WORDS:
            await wb_add.finish(f"⚠️ 词汇【{_mask_word(word)}】已存在。")

        _BLACKLIST_WORDS.append(word)
        if _save_blacklist_to_file():
            await wb_add.finish(f"✅ 已添加普通词汇: {_mask_word(word)}")
        else:
            _BLACKLIST_WORDS.remove(word)
            await wb_add.finish("❌ 保存文件失败，请检查日志。")


wb_del = on_command("word blacklist del", permission=SUPERUSER, priority=5, block=True)


@wb_del.handle()
async def _handle_del(args: Message = CommandArg()) -> None:
    """处理删除黑名单指令。"""
    text = args.extract_plain_text().strip()

    # 处理正则删除
    if text.startswith("regex "):
        pattern = text[6:].strip()
        if pattern not in _BLACKLIST_REGEX_STRS:
            await wb_del.finish(f"⚠️ 未找到正则规则: {pattern}")

        _BLACKLIST_REGEX_STRS.remove(pattern)
        if _save_blacklist_to_file():
            _compile_regex_list()
            await wb_del.finish(f"✅ 已删除正则规则: {pattern}")
        else:
            _BLACKLIST_REGEX_STRS.append(pattern)
            await wb_del.finish("❌ 保存文件失败。")

    # 处理普通词汇删除
    else:
        word = text
        if word not in _BLACKLIST_WORDS:
            await wb_del.finish(f"⚠️ 未找到普通词汇: {_mask_word(word)}")

        _BLACKLIST_WORDS.remove(word)
        if _save_blacklist_to_file():
            await wb_del.finish(f"✅ 已删除普通词汇: {_mask_word(word)}")
        else:
            _BLACKLIST_WORDS.append(word)
            await wb_del.finish("❌ 保存文件失败。")


wb_list = on_command("word blacklist list", permission=SUPERUSER, priority=5, block=True)


@wb_list.handle()
async def _handle_list() -> None:
    """处理查看黑名单列表指令。"""
    msg_lines = ["📋 当前黑名单配置:"]

    if _BLACKLIST_WORDS:
        masked_words = [_mask_word(w) for w in _BLACKLIST_WORDS]
        msg_lines.append(f"🔹 普通词汇 ({len(masked_words)}): " + " | ".join(masked_words))
    else:
        msg_lines.append("🔹 普通词汇: (空)")

    if _BLACKLIST_REGEX_STRS:
        msg_lines.append(f"🔹 正则规则 ({len(_BLACKLIST_REGEX_STRS)}):")
        for idx, r in enumerate(_BLACKLIST_REGEX_STRS, 1):
            msg_lines.append(f"  {idx}. {r}")
    else:
        msg_lines.append("🔹 正则规则: (空)")

    await wb_list.finish("\n".join(msg_lines))


wb_refresh = on_command(
    "word blacklist refresh", permission=SUPERUSER, priority=5, block=True
)


@wb_refresh.handle()
async def _handle_refresh() -> None:
    """处理手动刷新指令。"""
    _load_blacklist()
    await wb_refresh.finish(
        f"✅ 刷新成功\n普通词: {len(_BLACKLIST_WORDS)}\n正则: {len(_COMPILED_REGEX)}"
    )


wb_help = on_command("word blacklist help", priority=5, block=True)


@wb_help.handle()
async def _handle_help() -> None:
    """处理帮助指令。"""
    await wb_help.finish(
        "🛡️ 黑名单管理指令:\n"
        "1. 普通词汇:\n"
        "   add <词> | del <词>\n"
        "2. 正则表达式:\n"
        "   add regex <表达式>\n"
        "   del regex <表达式>\n"
        "3. 其他:\n"
        "   list | refresh"
    )


# API
async def _check_black_list(bot: Bot, api: str, data: dict) -> None:
    """API 调用钩子函数。

    在机器人调用发送消息 API 之前拦截，检查内容是否包含黑名单词汇。

    Args:
        bot: Bot 实例。
        api: 调用的 API 名称。
        data: API 参数字典。

    Raises:
        MockApiException: 当检测到敏感词时抛出，用于阻断 API 调用。
    """
    sending_apis = {"send_msg", "send_group_msg", "send_private_msg"}
    if api not in sending_apis:
        return

    # 强制转为字符串，确保处理 Message 对象等
    raw_message = str(data.get("message", ""))

    # 1. 检查普通词汇 (性能较高，优先检查)
    for word in _BLACKLIST_WORDS:
        if word in raw_message:
            raise MockApiException(result={"message": "Blocked by word blacklist"})

    # 2. 检查正则 (性能相对较低)
    for pattern in _COMPILED_REGEX:
        if pattern.search(raw_message):
            raise MockApiException(result={"message": "Blocked by regex blacklist"})


# 注册全局 API 钩子
Bot.on_calling_api(_check_black_list)
