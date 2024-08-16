param (
    [string]$action
)

# Define variables
$APP_NAME = "api"
$RUNTIME_DIR = "runtime"
$PID_DIR = "${RUNTIME_DIR}\pids"
$PID_FILE = "${PID_DIR}\${APP_NAME}.AppPid"
$LOG_DIR = "${RUNTIME_DIR}\logs"
$LOG_FILE = "${LOG_DIR}\error.log"
$CONSOLE_LOG_FILE = "${LOG_DIR}\${APP_NAME}.console.log"
$OUTPUT_LOG_FILE = "${LOG_DIR}\${APP_NAME}.output.log"

$CONFIG_DIR = "${RUNTIME_DIR}\configs"

function New-Env {
    Write-Host "Building environment for $APP_NAME..."

    Write-Host "Creating runtime directories..."
    New-Item -Path $RUNTIME_DIR -ItemType Directory -Force

    Write-Host "- Creating config directory..."
    New-Item -Path $CONFIG_DIR -ItemType Directory -Force

    Write-Host "- Creating AppPid directory..."
    New-Item -Path $PID_DIR -ItemType Directory -Force

    Write-Host "- Creating log directory..."
    New-Item -Path $LOG_DIR -ItemType Directory -Force

    Write-Host "Environment for $APP_NAME built successfully"
}

function Start-App {
    if (Test-Path $PID_FILE) {
        $AppPid = Get-Content $PID_FILE
        if (Get-Process -Id $AppPid -ErrorAction SilentlyContinue) {
            Write-Host "$APP_NAME is already running with PID $AppPid"
            return 1
        }
    }

    New-Item -Path $LOG_DIR -ItemType Directory -Force
    New-Item -Path $PID_DIR -ItemType Directory -Force

    Start-Process -FilePath "python" -ArgumentList "-m app.main" -RedirectStandardOutput $OUTPUT_LOG_FILE -RedirectStandardError $CONSOLE_LOG_FILE -NoNewWindow -PassThru | ForEach-Object {
        $AppPid = $_.Id
        Write-Host "$APP_NAME started with PID $AppPid"
        Write-Host "You can check the log file at $LOG_FILE"
        Write-Host "Or you can run `e[31m\$0 taillog`e[0m to tail the log file"
        Set-Content -Path $PID_FILE -Value $AppPid
    }
}

function Stop-App {
    if (Test-Path $PID_FILE) {
        $AppPid = Get-Content $PID_FILE
        if (Get-Process -Id $AppPid -ErrorAction SilentlyContinue) {
            Stop-Process -Id $AppPid -Force
            Write-Host "Stopping $APP_NAME..."
            Start-Sleep -Seconds 2
            if (Get-Process -Id $AppPid -ErrorAction SilentlyContinue) {
                Write-Host "Failed to stop $APP_NAME"
                return
            }
        }
        Remove-Item $PID_FILE
        Write-Host "Stopped $APP_NAME"
    } else {
        Write-Host "$APP_NAME is not running"
    }
}

function Test-Config {
    try {
        python -c "from app.common.core.config import ApiConfig"
        Write-Host "Config check ok"
    } catch {
        Write-Host "Config check failed"
        exit 1
    }
}

switch ($action) {
    "build_env" {
        New-Env
        break
    }
    "start" {
        Test-Config
        Start-App
        break
    }
    "stop" {
        Stop-App
        break
    }
    "restart" {
        Tset-Config
        Stop-App
        Start-Sleep -Seconds 3
        Start-App
        Start-Sleep -Seconds 10
        break
    }
    default {
        Write-Host "Usage: $($MyInvocation.MyCommand.Name) {start|stop|restart|build_env}"
        exit 1
    }
}
