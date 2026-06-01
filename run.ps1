<#
.SYNOPSIS
  Run the full Open Cognitive Bench pipeline (run_bench -> judge -> stats).
.EXAMPLE
  .\run.ps1                                   # mock smoke test on the dev set
  .\run.ps1 -Provider anthropic -Model claude-sonnet-4-5
  .\run.ps1 -Provider openai -Model gpt-4o -Tasks bench\tasks\heldout -Seeds 5
#>
param(
  [string]$Provider = "mock",
  [string]$Model = "",
  [string]$LensModel = "",
  [string]$Tasks = "bench\tasks\dev",
  [int]$Seeds = 5,
  [string]$Arms = "B C D S W"
)
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

$py = $null
foreach ($c in @("python", "py")) {
  if (Get-Command $c -ErrorAction SilentlyContinue) { $py = $c; break }
}
if (-not $py) {
  Write-Error "Python not found on PATH. Install Python 3.11+ from python.org (tick 'Add to PATH')."
  exit 1
}

$args = @("$root\bench\run_bench.py", "--tasks", (Join-Path $root $Tasks),
          "--arms") + ($Arms -split '\s+') + @("--seeds", $Seeds, "--provider", $Provider)
if ($Model)     { $args += @("--model", $Model) }
if ($LensModel) { $args += @("--lens-model", $LensModel) }

& $py @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $py "$root\bench\judge.py" --run "$root\results\latest"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $py "$root\bench\stats.py" --run "$root\results\latest"
