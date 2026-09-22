# chat.ps1 - 主动唤起 llm_wiki 知识库的 Claude Code 交互会话
#
# 用法：
#   .\chat.ps1              # 新开一个交互会话
#   .\chat.ps1 -Continue    # 接着本仓库最近一次会话继续聊
#   .\chat.ps1 -Pick        # 打开会话选择器，从本仓库历史会话里挑一个
#
# 会话记录由 Claude Code CLI 持久化，不迁移旧 Kimi 会话。
# 在本仓库根目录发起的所有会话都能通过 -Continue / -Pick 找回。
# 明确传入 AGENTS.md；不声称继承 .kimi-code 的 MCP 和 skills。

param(
    [switch]$Continue,
    [switch]$Pick
)

$Root = Split-Path -Parent $PSCommandPath
Set-Location $Root

Write-Host '[info] Claude session; agent-memory MCP and skill are explicitly loaded; review decisions still require the user.'

if ($Continue) {
    uv run python -m service.agent_runner chat --continue
} elseif ($Pick) {
    uv run python -m service.agent_runner chat --pick
} else {
    uv run python -m service.agent_runner chat
}
