: <<'BATCH_EOF'
@echo off
setlocal enabledelayedexpansion
set "SCRIPT_DIR=%~dp0"
set "HOOK_NAME=%~1"
if "%HOOK_NAME%"=="" set "HOOK_NAME=session-start"

for %%B in (
  "C:\Program Files\Git\bin\bash.exe"
  "C:\Program Files (x86)\Git\bin\bash.exe"
  "%LOCALAPPDATA%\Programs\Git\bin\bash.exe"
) do (
  if exist %%B (
    %%B "%SCRIPT_DIR%%HOOK_NAME%"
    exit /b !ERRORLEVEL!
  )
)
where bash >nul 2>&1
if !ERRORLEVEL! equ 0 (
  bash "%SCRIPT_DIR%%HOOK_NAME%"
  exit /b !ERRORLEVEL!
)
exit /b 0
BATCH_EOF
#!/usr/bin/env bash
# Intent-Driven Coding — cross-platform hook launcher
# Adapted from Superpowers hooks/run-hook.cmd (MIT License)
PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK_NAME="${1:-session-start}"
exec bash "${PLUGIN_ROOT}/hooks/${HOOK_NAME}"
