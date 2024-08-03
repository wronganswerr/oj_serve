#!/bin/bash

APP_NAME="api"

RUNTIME_DIR="runtime"

PID_DIR="${RUNTIME_DIR}/pids"
PID_FILE="${PID_DIR}/${APP_NAME}.pid"

LOG_DIR="${RUNTIME_DIR}/logs"
LOG_FILE="${LOG_DIR}/error.log"

CONSOLE_LOG_FILE=${LOG_DIR}/${APP_NAME}.console.log

CONFIG_DIR="${RUNTIME_DIR}/configs"



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

    nohup python -m app.main >> ${CONSOLE_LOG_FILE}  2>&1 &

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
    python -c "from app.command.core.config import ApiConfig"
    local exit_status=$?
    if [ $exit_status -ne 0 ]; then
        echo "Config check failed"
        exit $exit_status
    else
        echo "Config check ok"
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
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac