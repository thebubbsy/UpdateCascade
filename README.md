# UpdateCascade

> **Autonomous Multi-Pass Windows Update & Driver Engine with Bulletproof Reboot Persistence**

[![UpdateCascade CI](https://github.com/thebubbsy/UpdateCascade/actions/workflows/ci.yml/badge.svg)](https://github.com/thebubbsy/UpdateCascade/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: Windows 10 / 11 / Server / OOBE](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011%20%7C%20Server%20%7C%20OOBE-0078D4.svg)](https://github.com/thebubbsy/UpdateCascade)

**UpdateCascade** is a standalone, single-file Windows Update and Driver cascade utility engineered specifically for field technicians, sysadmins, and automated provisioning pipelines. It solves the number-one frustration with Windows Update automation: **reboot survivability and relaunch persistence across reboots in all Windows lifecycle phases (OOBE Shift+F10, pre-logon lock screen, and desktop).**

---

## 1. Quick Start (1-Click Web Bootstrap)

Open PowerShell as Administrator (or press `Shift + F10` during Windows Setup / OOBE) and execute:

```powershell
irm https://onyachamp.com/cascade | iex
```

*Or via raw GitHub URL:*

```powershell
irm https://raw.githubusercontent.com/thebubbsy/UpdateCascade/main/cascade.ps1 | iex
```

Hit **Start Autonomous Cascade** once. UpdateCascade handles scanning, downloading, installing, countdown rebooting, persistent relaunching across reboots, repeating passes until zero updates remain, and clean unregistration on completion.

---

## 2. Core Capabilities

- **1-Click Multi-Pass Cascade**: Loops autonomously (Pass 1 -> Reboot -> Pass 2 -> Reboot ...) until zero pending updates remain or `-MaxPasses` is reached.
- **17-Tier Relaunch Persistence**: Relaunches reliably across reboots regardless of whether Windows is in OOBE (`defaultuser0` / Winlogon setup desktop), sitting at the lock screen without a logged-in user, or running under standard desktop logon.
- **4-Tier Bulletproof Reboot Engine**: Ensures restart physically occurs across all Windows contexts without getting stuck on hanging processes.
- **Native COM Engine (`Microsoft.Update.Session`)**: Zero external PowerShell module dependencies (`PSWindowsUpdate` does not exist on fresh Windows or in OOBE).
- **Microsoft Update Catalog Integration**: Opts into the Microsoft Update catalog to include hardware device drivers (Intel, AMD, Nvidia, Realtek, Dell, HP, Lenovo) and firmware updates alongside core OS security updates.
- **Win11 Cyber-Dark WPF GUI & Headless CLI**: Beautiful, lightweight dark-themed GUI with progress bars, pass counters, real-time log, cancel/abort buttons, and full headless CLI parameter support.
- **Systematic Clean Teardown**: Automatically disarms and cleans all 17 persistence mechanisms and state files once the cascade finishes or when cancelled.

---

## 3. The 17-Tier Relaunch Persistence Architecture

Why do standard reboot scripts fail to resume? Because Windows boots through radically different security contexts depending on lifecycle phase:
1. In **Windows Setup (OOBE)**, `explorer.exe` does not run, Winlogon bypasses standard `Run`/`RunOnce` keys, and `SetupComplete.cmd` only fires at the end of setup.
2. At the **Lock Screen / Pre-Logon**, standard user logon triggers (`AtLogOn`, `RunOnce`, Startup folder) never fire until an operator manually types a password.

UpdateCascade deploys an exhaustive 17-vector persistence grid to guarantee autonomous execution across every scenario:

| Tier | Persistence Mechanism | Execution Context & Lifecycle Role |
| :--- | :--- | :--- |
| **1** | `HKLM RunOnce` (`*UpdateCascade`) | Winlogon elevated logon hook (`*` prefix forces priority processing even in Safe Mode). |
| **2** | `HKLM Run` (`UpdateCascade`) | Persistent machine-wide logon hook. |
| **3** | `HKCU RunOnce` & `HKCU Run` | Interactive logged-on user session execution. |
| **4** | `Default User Hive` (`NTUSER.DAT`) | Injects RunOnce into default user profile so newly provisioned accounts (`defaultuser0`) inherit it. |
| **5** | Scheduled Task: `AtLogOn` | Interactive task for `BUILTIN\Administrators` and `BUILTIN\Users` (`/IT` interactive desktop flag). |
| **6** | Scheduled Task: `AtStartup` | System boot trigger running as `NT AUTHORITY\SYSTEM` before any user logs in. |
| **7** | Winlogon `Userinit` Key Hook | Appended to `userinit.exe` so Winlogon executes launcher immediately before shell initialization. |
| **8** | Winlogon `AppSetup` Key Hook | Low-level Winlogon setup hook executed during session preparation. |
| **9** | Active Setup Component | Handled by userinit/explorer for all existing and newly logged-in accounts. |
| **10** | `SetupComplete.cmd` Hook | Windows Setup specialization and post-OOBE desktop transition fallback. |
| **11** | `ErrorHandler.cmd` Hook | Windows Setup error handler fallback in `%windir%\Setup\Scripts\`. |
| **12** | All Users Startup Folder | `%ProgramData%\Microsoft\Windows\Start Menu\Programs\StartUp\UpdateCascade.cmd`. |
| **13** | Default User Startup Folder | `C:\Users\Default\AppData\Roaming\...\StartUp\UpdateCascade.cmd` inherited by new users. |
| **14** | `RunOnceEx` Registry Key | Low-level installer execution hook in `HKLM:\...\RunOnceEx\900`. |
| **15** | Ephemeral Windows Service | `UpdateCascadeSvc` configured to auto-start at boot and trigger cascade resumption. |
| **16** | Local Group Policy Startup Script | `%windir%\System32\GroupPolicy\Machine\Scripts\Startup\UpdateCascade_GP.cmd`. |
| **17** | Silent VBScript & CMD Launchers | Dedicated `resume.cmd`, `resume.vbs`, and `launch.cmd` in `%ProgramData%\UpdateCascade\`. |

*When all passes complete or when `-Unregister` is called, UpdateCascade systematically removes and disarms all 17 vectors, leaving zero residual hooks.*

---

## 4. 4-Tier Bulletproof Reboot Engine

When an update installation signals that a restart is required, UpdateCascade engages a multi-tiered reboot sequence:

1. **Tier 1 (`shutdown.exe`)**: Dispatches `shutdown.exe /r /t <delay> /f /c "<reason>"`. Falls back immediately to un-commented syntax if comment parsing fails.
2. **Tier 2 (Win32 P/Invoke)**: Calls native Win32 `InitiateSystemShutdownEx` and `ExitWindowsEx` with `SHTDN_REASON_FLAG_PLANNED` and `EWX_REBOOT | EWX_FORCE`.
3. **Tier 3 (PowerShell Native)**: Invokes `Restart-Computer -Force`.
4. **Tier 4 (WMI / CIM)**: Calls `(Get-CimInstance Win32_OperatingSystem).Win32Shutdown(6)` (Reboot + Force).

---

## 5. Command-Line Reference

UpdateCascade can be run interactively or completely unattended in automated scripts:

```powershell
# 1. Unattended autonomous 5-pass cascade including drivers
powershell.exe -ExecutionPolicy Bypass -File .\cascade.ps1 -Autonomous -MaxPasses 5 -IncludeDrivers

# 2. Software patches only (exclude hardware device drivers)
powershell.exe -ExecutionPolicy Bypass -File .\cascade.ps1 -Autonomous -IncludeDrivers:$false

# 3. Query pending updates and drivers without installing (Scan Only)
powershell.exe -ExecutionPolicy Bypass -File .\cascade.ps1 -ScanOnly

# 4. Install updates but suppress automatic reboot
powershell.exe -ExecutionPolicy Bypass -File .\cascade.ps1 -Autonomous -NoReboot

# 5. Check active cascade state (JSON)
powershell.exe -ExecutionPolicy Bypass -File .\cascade.ps1 -Status

# 6. Disarm and unregister all persistence vectors (Emergency cleanup)
powershell.exe -ExecutionPolicy Bypass -File .\cascade.ps1 -Unregister
```

### Parameter Reference

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `-Autonomous` | Switch | `$false` | Runs headless in console mode without displaying WPF GUI. |
| `-MaxPasses` | Int | `5` | Maximum number of update-reboot iterations before concluding. |
| `-IncludeDrivers` | Bool | `$true` | Registers Microsoft Update catalog to include hardware device drivers. |
| `-RebootDelay` | Int | `5` | Countdown timer in seconds before rebooting. |
| `-NoReboot` | Switch | `$false` | Disables automatic restart after updates are installed. |
| `-ScanOnly` | Switch | `$false` | Scans and lists pending updates and drivers without installing. |
| `-ResumeFromRestart` | Switch | `$false` | Triggered internally by persistence mechanisms to resume active pass. |
| `-Status` | Switch | `$false` | Outputs the current cascade state as clean JSON. |
| `-Unregister` | Switch | `$false` | Completely cleans and removes all persistence mechanisms and exits. |

---

## 6. OOBE (Out-Of-Box Experience) Usage Guide

1. Boot device to the Windows Setup / OOBE screen ("Let's connect you to a network" or region selection).
2. Press `Shift + F10` to open an administrative command prompt.
3. If internet is required, connect ethernet or run `control netconnections` / `ms-settings:network-wifi`.
4. Run:
   ```cmd
   powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://onyachamp.com/cascade | iex"
   ```
5. Click **Start Autonomous Cascade** (or supply `-Autonomous` for headless).
6. Walk away. The device will install firmware and drivers, reboot repeatedly through setup, and resume autonomously until 100% updated.

---

## 7. Development & Verification

UpdateCascade includes comprehensive automated testing:

```powershell
# Run the complete Python governance and verification suite
python tests/test_cascade.py

# Run Pester unit and integration tests
pwsh -NoProfile -Command "Invoke-Pester -Path tests/UpdateCascade.Tests.ps1 -Output Detailed"

# Build and sync to onyachamp distribution endpoint
python build.py --sync-onyachamp
```

---

## Author & License

- **Author**: Matthew Bubb `<matt@onyachamp.com>`
- **Repository**: [https://github.com/thebubbsy/UpdateCascade](https://github.com/thebubbsy/UpdateCascade)
- **Website Endpoint**: [https://onyachamp.com/cascade](https://onyachamp.com/cascade)
- **License**: MIT License
