#!/bin/bash

APP_NAME="api"

RUNTIME_DIR="runtime"

PID_DIR="${RUNTIME_DIR}/pids"
PID_FILE="${PID_DIR}/${APP_NAME}.pid"

LOG_DIR="${RUNTIME_DIR}/logs"
LOG_FILE="${LOG_DIR}/${APP_NAME}.error.log"

CONSOLE_LOG_FILE=${LOG_DIR}/${APP_NAME}.console.log

CONFIG_DIR="${RUNTIME_DIR}/configs"

DEFAULT_TAIL_LINES=20

DATA_DIR="${RUNTIME_DIR}/data"

build_env() {
    echo "Building environment for ${APP_NAME}..."

    echo "Creating runtime directories..."
    mkdir -pv "${RUNTIME_DIR}"

    echo "- Creating config directory..."
    mkdir -pv "${CONFIG_DIR}"

    echo "- Creating pid directory..."
    mkdir -pv "${PID_DIR}"

    echo "- Creating log directory..."
    mkdir -pv "${LOG_DIR}"

    echo "- Creating data directory..."
    mkdir -pv "${DATA_DIR}"

    echo "Environment for ${APP_NAME} built successfully"
}

start() {
    if [ -f "${PID_FILE}" ]; then
        local pid=$(cat "${PID_FILE}")
        if [ -n "$(ps -p ${pid} -o pid=)" ]; then
            echo "${APP_NAME} is already running with PID ${pid}"
            return 1
        fi
    fi

    mkdir -p "${LOG_DIR}"
    mkdir -p "${PID_DIR}"

    nohup python -m app.main > ${CONSOLE_LOG_FILE}  2>&1 &

    local pid=$!
    # TODO: Check if the server is started successfully...
    local exit_status=$?
    if [ $exit_status -eq 0 ]; then
        echo "${APP_NAME} started with PID ${pid}"
        echo "You can check the log file at ${LOG_FILE}"
        echo -e "Or you can run \e[31m$0 taillog\e[0m to tail the log file"

        echo "${pid}" > "${PID_FILE}"
    else
        echo "Failed to start ${APP_NAME}"
        if [ -f "${LOG_FILE}" ]; then
            local num_lines=${LOG_LINES:-10}
            tail -n ${num_lines} "${LOG_FILE}"
        fi
    fi
}

stop() {
    if [ -f "${PID_FILE}" ]; then
        local pid=$(cat "${PID_FILE}")
        if [ -n "$(ps -p ${pid} -o pid=)" ]; then
            kill -9 "${pid}"
            echo "Stopping ${APP_NAME}..."
            sleep 2
            if [ -n "$(ps -p ${pid} -o pid=)" ]; then
                echo "Failed to stop ${APP_NAME}"
                return
            fi
        fi
        rm "${PID_FILE}"
        echo "Stopped ${APP_NAME}"
    else
        echo "${APP_NAME} is not running"
    fi
}


check_config() {
    python -c "from app.common.core.config import ApiConfig"
    local exit_status=$?
    if [ $exit_status -ne 0 ]; then
        echo "Config check failed"
        exit $exit_status
    else
        echo "Config check ok"
    fi
}

taillog() {
    local num_lines=${1:-$DEFAULT_TAIL_LINES}
    if [ -f "${LOG_FILE}" ]; then
        tail -n "${num_lines}" -f "${LOG_FILE}"
    else
        echo "No log file found for ${APP_NAME} ${LOG_FILE}"
    fi
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "daphne 正在运行，进程 ID 为 $PID"
        else
            echo "daphne 未运行，但 PID 文件存在，已删除 PID 文件"
            rm "$PID_FILE"
        fi
    else
        echo "daphne 未运行"
    fi
}


case "$1" in
    build_env)
        build_env
        ;;
    start)
        check_config
        start
        ;;
    stop)
        stop
        ;;
    restart)
        check_config
        stop
        sleep 3
        start
        sleep 10
        ;;
    taillog)
        shift
        taillog "$@"
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac