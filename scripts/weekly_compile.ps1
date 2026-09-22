# weekly_compile.ps1 - Weekly compile pipeline (Windows)
#
# Usage:
#   powershell -File scripts/weekly_compile.ps1 -DryRun
#   powershell -File scripts/weekly_compile.ps1
#
# DryRun: fetch candidates with --dry-run, score with weekly_update.py --dry-run,
#         run lint, and check CLI discovery. It does not write registry, digest,
#         review queue, wiki pages, or weekly LLM logs.
# Full run: fetch_candidates.py -> weekly_update.py -> lint_wiki.py ->
#           Claude selection -> scripted ingest -> Claude compile -> Codex audit ->
#           compile_index.py -> lint_wiki.py.
#
# CLI sessions do not inherit Kimi sessions or its memory configuration.

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
if (-not $DryRun) { New-Item -ItemType Directory -Force -Path $LogDir | Out-Null }

Write-Host "[1/5] fetch_candidates.py (arXiv / OpenAlex / Semantic Scholar)"
$FetchArgs = @("--limit", "$Limit")
if ($DryRun) { $FetchArgs += "--dry-run" }
uv run python scripts/fetch_candidates.py @FetchArgs
if ($LASTEXITCODE -ne 0) { Write-Error "fetch_candidates.py failed"; exit 1 }

Write-Host "[2/5] weekly_update.py (dedupe, scoring, review queue + digest)"
$QueuesBefore = @(Get-ChildItem (Join-Path $Root 'data/review_queue') -Filter 'weekly-*.md' -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
$UpdateArgs = @("--date", "$DateStr", "--limit", "$Limit")
if ($DryRun) { $UpdateArgs += "--dry-run" }
uv run python scripts/weekly_update.py @UpdateArgs
if ($LASTEXITCODE -ne 0) { Write-Error "weekly_update.py failed"; exit 1 }
if (-not $DryRun) {
    $NewQueues = @(Get-ChildItem (Join-Path $Root 'data/review_queue') -Filter 'weekly-*.md' | Where-Object { $_.FullName -notin $QueuesBefore })
    if ($NewQueues.Count -eq 0) { Write-Host '[done] no new review batch; skipped LLM calls'; exit 0 }
    if ($NewQueues.Count -ne 1) { throw 'Multiple new batches detected; select a review queue explicitly.' }
    $ReviewQueue = $NewQueues[0].FullName
}

Write-Host "[3/5] lint_wiki.py (pre-compile check)"
uv run python scripts/lint_wiki.py
$PreLintExit = $LASTEXITCODE

if ($DryRun) {
    Write-Host "[dry-run] checking configured CLI availability"
    uv run python -m service.agent_runner weekly --check
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host '[dry-run] Claude memory config is explicitly loaded on real runs; dry-run does not connect'
    Write-Host "[dry-run] LLM compile step skipped. lint exit code: $PreLintExit"
    exit $PreLintExit
}

if ($PreLintExit -ne 0) {
    Write-Error "lint_wiki.py reported errors before compile; aborting LLM step."
    exit $PreLintExit
}

Write-Host "[4/5] Claude editorial pass + Codex independent audit"

Write-Host 'Claude explicitly loads agent-memory MCP; pending review gates are preserved.'

$RunStamp = Get-Date -Format 'yyyy-MM-dd-HHmmss-fff'
$LogFile = Join-Path $LogDir "weekly-$RunStamp.log"
$ErrFile = Join-Path $LogDir "weekly-$RunStamp.stderr.log"
$PromptFile = Join-Path $Root "prompts/weekly_compile.md"
# PowerShell wraps every native-command stderr line in an error record even
# when stderr is redirected to a file, and $ErrorActionPreference = "Stop"
# then aborts the script. Run the CLI adapter in a nested scope instead.
& {
    $ErrorActionPreference = "Continue"
    uv run python -m service.agent_runner weekly --prompt-file $PromptFile --review-queue $ReviewQueue 2>$ErrFile | Tee-Object -FilePath $LogFile
}
$AgentExit = $LASTEXITCODE
if ($AgentExit -ne 0) { Write-Error "LLM generation or audit failed (log: $LogFile, stderr: $ErrFile)"; exit $AgentExit }

Write-Host "[5/5] compile_index.py + lint_wiki.py (post-compile check)"
uv run python scripts/compile_index.py
if ($LASTEXITCODE -ne 0) { Write-Error "compile_index.py failed"; exit 1 }
uv run python scripts/lint_wiki.py
$PostLintExit = $LASTEXITCODE
if ($PostLintExit -ne 0) { Write-Error "lint_wiki.py failed after compile"; exit $PostLintExit }

Write-Host "[done] weekly compile finished, log: $LogFile"
