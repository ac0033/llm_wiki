"""CLI 文本调用：独立上下文、显式权限、完整结果校验；不做静默模型回退。"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import hashlib
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path


class AgentError(RuntimeError):
    pass


@dataclass
class AgentReply:
    text: str
    requested_model: str
    actual_model: str
    session_id: str = ""


def command_for(provider: str) -> list[str]:
    """JSON 数组覆盖支持 node + 脚本路径，不经 shell 解释。"""
    key = provider.upper() + "_COMMAND_JSON"
    if os.getenv(key):
        value = json.loads(os.environ[key])
        if not isinstance(value, list) or not value or not all(isinstance(x, str) and x for x in value):
            raise AgentError(f"{key} 必须是非空字符串数组")
        return value
    executable = {"claude": "claude", "codex": "codex", "codebuddy": "codebuddy"}[provider]
    found = shutil.which(executable)
    if found:
        return [found]
    if provider == "codebuddy":
        # 优先显式路径，其次查询安装登记；不读取或复制 WorkBuddy 凭据。
        roots = [os.getenv("WORKBUDDY_INSTALL_DIR", "")]
        if os.name == "nt":
            import winreg
            for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
                try:
                    with winreg.OpenKey(hive, r"Software\Microsoft\Windows\CurrentVersion\Uninstall") as parent:
                        for i in range(winreg.QueryInfoKey(parent)[0]):
                            with winreg.OpenKey(parent, winreg.EnumKey(parent, i)) as child:
                                try:
                                    name = winreg.QueryValueEx(child, "DisplayName")[0]
                                    icon = winreg.QueryValueEx(child, "DisplayIcon")[0]
                                    if name.startswith("WorkBuddy"):
                                        roots.append(str(Path(icon.rsplit(",", 1)[0].strip('"')).parent))
                                except OSError:
                                    continue
                except OSError:
                    continue
        for root in filter(None, roots):
            entry = Path(root) / "resources/app.asar.unpacked/cli/bin/codebuddy"
            node = shutil.which("node")
            if entry.is_file() and node:
                return [node, str(entry)]
    raise AgentError(f"找不到 {provider}；请安装 CLI 或设置 {key}")


def parse_output(provider: str, output: str, requested: str) -> AgentReply:
    """兼容 Claude 单对象、CodeBuddy 数组和 Codex JSONL；中间文本不是成功结果。"""
    try:
        value = json.loads(output)
        events = value if isinstance(value, list) else [value]
    except ValueError:
        try:
            events = [json.loads(line) for line in output.splitlines() if line.strip()]
        except ValueError as exc:
            raise AgentError(f"{provider} 输出不是完整 JSON") from exc
    answer, actual, session, complete = "", "", "", False
    for event in events:
        if not isinstance(event, dict):
            raise AgentError(f"{provider} 事件格式无效")
        kind = event.get("type")
        if kind in {"error", "turn.failed"} or event.get("is_error"):
            raise AgentError(f"{provider} 返回失败事件；没有有效最终结果")
        metadata = event.get("providerData") or {}
        actual = metadata.get("model") or event.get("model") or actual
        session = event.get("session_id") or event.get("thread_id") or session
        if provider == "codex":
            item = event.get("item") or {}
            if kind == "item.completed" and item.get("type") == "agent_message":
                answer = item.get("text", "")
            if kind == "turn.completed":
                complete = True
        elif kind == "result":
            if event.get("subtype") != "success":
                raise AgentError(f"{provider} 未成功完成：{event.get('subtype')}")
            if event.get("permission_denials"):
                raise AgentError(f"{provider} 存在被拒绝的工具操作，请检查权限后重试")
            answer = event.get("result", "")
            complete = True
            models = event.get("modelUsage", {})
            if len(models) == 1 and not actual:
                actual = next(iter(models))
    if not complete or not isinstance(answer, str) or not answer.strip():
        raise AgentError(f"{provider} 没有完整、非空的最终结果")
    return AgentReply(answer, requested, actual or "未报告", session)


def invoke(provider: str, model: str, prompt: str, *, timeout: int = 900,
           cwd: Path | None = None, file_tools: bool = False,
           writable: tuple[str, ...] = (), runner=None,
           environment: dict[str, str] | None = None,
           mcp_config: Path | None = None,
           mcp_tools: tuple[str, ...] = ()) -> AgentReply:
    """默认不开放工具。wiki 仅开放读和指定路径的写；绝不开放 shell。"""
    if provider not in {"claude", "codex", "codebuddy"}:
        raise AgentError(f"不支持的 CLI：{provider}")
    if mcp_config and provider != "claude":
        raise AgentError("记忆 MCP 目前仅验证了 Claude 入口，不向其他入口静默套用配置")
    # Windows CLI 的短生命周期子进程可能暂时持有 cwd 句柄；清理失败不能吞掉已完成结果。
    with tempfile.TemporaryDirectory(prefix="llm-cli-", ignore_cleanup_errors=True) as scratch:
        cmd = command_for(provider)
        if provider == "codex":
            if writable:
                raise AgentError("Codex 在此适配器中只用于只读核验")
            cmd += ["exec", "--json", "--ephemeral", "--skip-git-repo-check",
                    "--sandbox", "read-only", "--ignore-user-config", "-"]
            if model:
                cmd += ["--model", model]
        else:
            cmd += ["-p", "--output-format", "json", "--no-session-persistence",
                    "--strict-mcp-config", "--permission-mode", "dontAsk",
                    "--setting-sources", "", "--settings", '{"disableAllHooks":true,"autoMemoryEnabled":false}']
            if model:
                cmd += ["--model", model]
            if provider == "claude":
                cmd[cmd.index("--output-format") + 1] = "stream-json"
                cmd += ["--verbose"]
                cmd += ["--permission-prompts", "none"]
            names = ["Read", "Glob", "Grep"] if file_tools else []
            rules = list(names)
            if mcp_config:
                cmd += ["--mcp-config", str(mcp_config.resolve())]
                rules += list(mcp_tools)
            if writable:
                names += ["Edit", "Write"]
                for path in writable:
                    rules += [f"Edit({path})", f"Write({path})"]
                cmd += ["--disallowedTools", "Edit(./wiki/index.md),Write(./wiki/index.md)"]
            cmd += ["--tools", ",".join(names)]
            if rules:
                cmd += ["--allowedTools", ",".join(rules)]
        env = dict(os.environ if environment is None else environment)
        env["DISABLE_AUTOUPDATER"] = "1"
        env["CODEBUDDY_DISABLE_COMPILE_CACHE"] = "1"
        # 嵌套调用是新的一次独立任务，不向 CLI 传递父会话标识。
        env.pop("CLAUDECODE", None)
        try:
            proc = (runner or subprocess.run)(cmd, input=prompt, cwd=cwd or scratch,
                capture_output=True, text=True, encoding="utf-8", errors="strict",
                timeout=timeout, env=env)
        except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
            raise AgentError(f"{provider} 调用失败：{type(exc).__name__}") from exc
        if proc.returncode:
            # 不把可能含账户信息的原始 stderr 放进用户日志。
            raise AgentError(f"{provider} 退出码 {proc.returncode}；检查认证、额度、模型与 CLI 配置")
        reply = parse_output(provider, proc.stdout, model)
        trace_dir = env.get("LLM_CLI_TRACE_DIR")
        if trace_dir:
            # 留调用证据，不保存提示词、工具参数、召回内容或模型 thinking。
            try:
                events = json.loads(proc.stdout)
                events = events if isinstance(events, list) else [events]
            except ValueError:
                events = [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
            calls, results = [], []
            for event in events:
                for block in (event.get("message") or {}).get("content", []):
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "tool_use":
                        calls.append({"id": block.get("id"), "name": block.get("name")})
                    elif block.get("type") == "tool_result":
                        results.append({"id": block.get("tool_use_id"), "is_error": bool(block.get("is_error"))})
            record = {"at": datetime.now(timezone.utc).isoformat(), "provider": provider,
                      "requested_model": model, "actual_model": reply.actual_model,
                      "session_id": reply.session_id, "tools": calls, "tool_results": results,
                      "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                      "result_sha256": hashlib.sha256(reply.text.encode()).hexdigest()}
            folder = Path(trace_dir)
            folder.mkdir(parents=True, exist_ok=True)
            (folder / (uuid.uuid4().hex + ".json")).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        return reply
