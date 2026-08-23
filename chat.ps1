# chat.ps1 - 主动唤起 llm_wiki 知识库的 Kimi Code 交互会话
#
# 用法：
#   .\chat.ps1              # 新开一个交互会话
#   .\chat.ps1 -Continue    # 接着本仓库最近一次会话继续聊
#   .\chat.ps1 -Pick        # 打开会话选择器，从本仓库历史会话里挑一个
#
# 会话记录由 Kimi Code CLI 自动持久化（~/.kimi-code/sessions/ 下按工作目录分组），
# 在本仓库根目录发起的所有会话都能通过 -Continue / -Pick 找回。
# 会话从仓库根目录启动，自动加载项目级 .kimi-code/mcp.json（agent-memory 记忆服务）
# 和 .kimi-code/skills/agent-memory 使用规范。

param(
    [switch]$Continue,
    [switch]$Pick
)

$Root = Split-Path -Parent $PSCommandPath
Set-Location $Root

# 记忆服务预检：交互场景下只警告不中断，MCP 工具不可用时仍可普通对话。
try {
    $null = Invoke-WebRequest -Uri "http://127.0.0.1:8765/bootstrap" -UseBasicParsing -TimeoutSec 5
} catch {
    Write-Host "[warn] agent-memory 记忆服务（http://127.0.0.1:8765）当前不可达，本次会话将没有 memory 工具。请先启动记忆服务再运行本脚本。" -ForegroundColor Yellow
}

if ($Continue) {
    kimi --continue
} elseif ($Pick) {
    kimi --session
} else {
    kimi
}
