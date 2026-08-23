# weekly_compile.ps1 - Weekly compile pipeline (Windows)
#
# Usage:
#   powershell -File scripts/weekly_compile.ps1 -DryRun
#   powershell -File scripts/weekly_compile.ps1
#
# DryRun: fetch candidates with --dry-run, score with weekly_update.py --dry-run,
#         run lint, and check `kimi --version`. It does not write registry, digest,
#         review queue, wiki pages, or weekly LLM logs.
# Full run: fetch_candidates.py -> weekly_update.py -> lint_wiki.py ->
#           agent-memory MCP preflight ->
#           kimi -p prompts/weekly_compile.md --output-format stream-json ->
#           compile_index.py -> lint_wiki.py.
#
# The kimi invocation runs with the repo root as cwd, so it picks up the
# project-level .kimi-code/mcp.json (agent-memory MCP server) and the
# .kimi-code/skills/agent-memory skill. The memory server must be running
# at http://127.0.0.1:8765 before this script is run; the preflight check
# below aborts early if it is unreachable.

param(
    [switch]$DryRun,
    [int]$Limit = 20
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$DateStr = Get-Date -Format "yyyy-MM-dd"
$LogDir = Join-Path $Root "data/logs/weekly"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

Write-Host "[1/5] fetch_candidates.py (arXiv / OpenAlex / Semantic Scholar)"
$FetchArgs = @("--limit", "$Limit")
if ($DryRun) { $FetchArgs += "--dry-run" }
uv run python scripts/fetch_candidates.py @FetchArgs
if ($LASTEXITCODE -ne 0) { Write-Error "fetch_candidates.py failed"; exit 1 }

Write-Host "[2/5] weekly_update.py (dedupe, scoring, review queue + digest)"
$UpdateArgs = @("--date", "$DateStr", "--limit", "$Limit")
if ($DryRun) { $UpdateArgs += "--dry-run" }
uv run python scripts/weekly_update.py @UpdateArgs
if ($LASTEXITCODE -ne 0) { Write-Error "weekly_update.py failed"; exit 1 }

Write-Host "[3/5] lint_wiki.py (pre-compile check)"
uv run python scripts/lint_wiki.py
$PreLintExit = $LASTEXITCODE

if ($DryRun) {
    Write-Host "[dry-run] checking kimi CLI availability"
    kimi --version
    Write-Host "[dry-run] checking agent-memory MCP server availability"
    try {
        $null = Invoke-WebRequest -Uri "http://127.0.0.1:8765/bootstrap" -UseBasicParsing -TimeoutSec 5
        Write-Host "[dry-run] agent-memory MCP server reachable"
    } catch {
        Write-Error "[dry-run] agent-memory MCP server is NOT reachable at http://127.0.0.1:8765"
        exit 1
    }
    Write-Host "[dry-run] LLM compile step skipped. lint exit code: $PreLintExit"
    exit 0
}

if ($PreLintExit -ne 0) {
    Write-Error "lint_wiki.py reported errors before compile; aborting LLM step."
    exit $PreLintExit
}

Write-Host "[4/5] kimi editorial pass with prompts/weekly_compile.md"

# Preflight: the agent-memory MCP server must be up, otherwise the kimi
# session would run without memory tools. Abort early with a clear message.
try {
    $null = Invoke-WebRequest -Uri "http://127.0.0.1:8765/bootstrap" -UseBasicParsing -TimeoutSec 5
} catch {
    Write-Error "agent-memory MCP server is not reachable at http://127.0.0.1:8765. Start the memory service first, then re-run this script."
    exit 1
}

$LogFile = Join-Path $LogDir "weekly-$DateStr.jsonl"
$ErrFile = Join-Path $LogDir "weekly-$DateStr.stderr.log"
$PromptFile = Join-Path $Root "prompts/weekly_compile.md"
$Prompt = Get-Content -Raw -Encoding UTF8 $PromptFile
# PowerShell wraps every native-command stderr line in an error record even
# when stderr is redirected to a file, and $ErrorActionPreference = "Stop"
# then aborts the script. Run kimi in a nested scope with Continue instead.
& {
    $ErrorActionPreference = "Continue"
    kimi -p $Prompt --output-format stream-json 2>$ErrFile | Tee-Object -FilePath $LogFile
}
$KimiExit = $LASTEXITCODE
if ($KimiExit -ne 0) { Write-Error "kimi invocation failed (log: $LogFile, stderr: $ErrFile)"; exit $KimiExit }

Write-Host "[5/5] compile_index.py + lint_wiki.py (post-compile check)"
uv run python scripts/compile_index.py
if ($LASTEXITCODE -ne 0) { Write-Error "compile_index.py failed"; exit 1 }
uv run python scripts/lint_wiki.py
$PostLintExit = $LASTEXITCODE
if ($PostLintExit -ne 0) { Write-Error "lint_wiki.py failed after compile"; exit $PostLintExit }

Write-Host "[done] weekly compile finished, log: $LogFile"
