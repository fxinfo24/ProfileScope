#!/bin/bash
# File: scripts/cleanup.sh
# Created: 2024-04-15 18:30:00
# ProfileScope Cleanup Script - Handles logs, caches and temporary files

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
set -e  # Exit on error
SCRIPT_VERSION="1.0.0"
START_TIME=$(date +%s)

# Directory structure
BASE_DIR=$(dirname "$(dirname "$0")")
LOG_DIR="${BASE_DIR}/logs"
ARCHIVE_DIR="${LOG_DIR}/archive"
BACKUP_DIR="${BASE_DIR}/data/backups"
REPORT_DIR="${LOG_DIR}/reports"
ERROR_DIR="${LOG_DIR}/error_reports"
RETENTION_DAYS=7

# Create required directories
for dir in "$LOG_DIR" "$ARCHIVE_DIR" "$BACKUP_DIR" "$REPORT_DIR" "$ERROR_DIR"; do
    mkdir -p "$dir"
done

# Current log file
LOG_FILE="${LOG_DIR}/cleanup_$(date +%Y%m%d_%H%M%S).log"

# Function to log messages with timestamp and color
log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$timestamp [$level] $message" >> "$LOG_FILE"

    case $level in
        "INFO")    echo -e "${BLUE}➜${NC} $message" ;;
        "SUCCESS") echo -e "${GREEN}✓${NC} $message" ;;
        "WARNING") echo -e "${YELLOW}⚠${NC} $message" ;;
        "ERROR")   echo -e "${RED}✗${NC} $message" ;;
    esac
}

# Function to handle errors
handle_error() {
    local exit_code=$?
    local line_number=$1
    local command=$2

    log_message "ERROR" "Error occurred at line $line_number"
    log_message "ERROR" "Command: $command"
    log_message "ERROR" "Exit code: $exit_code"

    # Create error report
    local error_report="${ERROR_DIR}/cleanup_error_$(date +%Y%m%d_%H%M%S).txt"
    {
        echo "Error Report - $(date)"
        echo "=================="
        echo "Script Version: $SCRIPT_VERSION"
        echo "Error Line: $line_number"
        echo "Command: $command"
        echo "Exit Code: $exit_code"
        echo "Environment:"
        env
    } > "$error_report"

    exit $exit_code
}

# Register error handler
trap 'handle_error ${LINENO} "${BASH_COMMAND}"' ERR

# Define directories and files to clean for ProfileScope
DIRS_TO_CLEAN=(
    "data/logs"
    "data/cache"
    "data/temp"
    "output"
    "test_results"
    "tests/temp"
    "app/web/static/temp"
    "app/desktop/cache"
    "examples/output"
    "venv/__pycache__"
)

FILES_TO_CLEAN=(
    "*.pyc"
    "*.pyo"
    "*.pyd"
    "__pycache__"
    ".pytest_cache"
    ".coverage"
    "htmlcov"
    ".mypy_cache"
    "*.log"
    "*.tmp"
    "*.bak"
    ".DS_Store"
    "Thumbs.db"
    "test_*.log"
    "test_analyzer.log"
    "profilescope_web.log"
    "test_log.log"
    "pytest_*.xml"
)

# Function to safely clean directories with backup and verification
clean_directory() {
    local dir=$1
    local full_dir="${BASE_DIR}/${dir}"
    
    if [ -d "$full_dir" ]; then
        log_message "INFO" "Cleaning directory: $dir"

        # Create backup if directory is not empty
        if [ -n "$(ls -A "$full_dir" 2>/dev/null)" ]; then
            local backup_name="$(basename "$dir")_$(date +%Y%m%d_%H%M%S).tar.gz"
            local backup_path="$BACKUP_DIR/$backup_name"

            if tar -czf "$backup_path" -C "$(dirname "$full_dir")" "$(basename "$full_dir")" 2>/dev/null; then
                if tar -tzf "$backup_path" >/dev/null 2>&1; then
                    log_message "SUCCESS" "Created and verified backup: $backup_name"
                else
                    log_message "ERROR" "Backup verification failed: $backup_name"
                    return 1
                fi
            else
                log_message "ERROR" "Backup creation failed: $dir"
                return 1
            fi
        fi

        # Clean directory with progress tracking
        local file_count=$(find "$full_dir" -type f | wc -l)
        if [ "$file_count" -gt 0 ]; then
            log_message "INFO" "Removing $file_count files from $dir"
            find "$full_dir" -type f -delete 2>/dev/null || true
        fi

        log_message "SUCCESS" "Cleaned $dir"
    else
        log_message "WARNING" "Directory not found: $dir (skipping)"
    fi
}

# Function to clean all specified directories
clean_directories() {
    log_message "INFO" "Starting directory cleanup"
    for dir in "${DIRS_TO_CLEAN[@]}"; do
        clean_directory "$dir"
    done
    log_message "SUCCESS" "Directory cleanup completed"
}

# Function to clean files matching patterns
clean_files() {
    log_message "INFO" "Removing temporary files"
    for pattern in "${FILES_TO_CLEAN[@]}"; do
        local count=$(find "${BASE_DIR}" -type f -name "$pattern" | wc -l)
        if [ "$count" -gt 0 ]; then
            log_message "INFO" "Removing $count files matching pattern: $pattern"
            find "${BASE_DIR}" -type f -name "$pattern" -delete 2>/dev/null || true
        fi
    done
    log_message "SUCCESS" "Temporary files cleanup completed"
}

# Function to archive logs with compression and verification
archive_logs() {
    log_message "INFO" "Archiving logs older than $RETENTION_DAYS days"

    if [ ! -d "${BASE_DIR}/data/logs" ]; then
        log_message "WARNING" "Logs directory not found (skipping archival)"
        return 0
    fi

    # Create archive directory
    mkdir -p "$ARCHIVE_DIR"
    local archived_count=0
    local failed_count=0

    while IFS= read -r log_file; do
        if [ -f "$log_file" ]; then
            local archive_name="$(basename "${log_file%.*}")_$(date +%Y%m%d_%H%M%S).gz"
            if gzip -c "$log_file" > "$ARCHIVE_DIR/$archive_name"; then
                if gzip -t "$ARCHIVE_DIR/$archive_name" 2>/dev/null; then
                    rm "$log_file"
                    ((archived_count++))
                    log_message "SUCCESS" "Archived: $log_file -> $archive_name"
                else
                    ((failed_count++))
                    log_message "ERROR" "Archive verification failed: $archive_name"
                    rm "$ARCHIVE_DIR/$archive_name"
                fi
            else
                ((failed_count++))
                log_message "ERROR" "Failed to archive: $log_file"
            fi
        fi
    done < <(find "${BASE_DIR}/data/logs" -type f -name "*.log" -mtime +$RETENTION_DAYS 2>/dev/null)

    log_message "INFO" "Archive summary: $archived_count archived, $failed_count failed"
}

# Function to clean Python-specific artifacts
clean_python_artifacts() {
    log_message "INFO" "Cleaning Python artifacts"
    
    # Clean Python cache files
    find "${BASE_DIR}" -type d -name "__pycache__" -exec rm -rf {} +  2>/dev/null || true
    find "${BASE_DIR}" -type f -name "*.pyc" -delete 2>/dev/null || true
    find "${BASE_DIR}" -type f -name "*.pyo" -delete 2>/dev/null || true
    find "${BASE_DIR}" -type f -name "*.pyd" -delete 2>/dev/null || true
    
    # Clean test caches
    find "${BASE_DIR}" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find "${BASE_DIR}" -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
    find "${BASE_DIR}" -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
    find "${BASE_DIR}" -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
    
    log_message "SUCCESS" "Python artifacts cleaned"
}

# Function to delete old test results
clean_test_results() {
    log_message "INFO" "Cleaning old test results"
    
    # Test results older than 7 days
    find "${BASE_DIR}/test_results" -type f -name "pytest_*.html" -mtime +7 -delete 2>/dev/null || true
    find "${BASE_DIR}/test_results" -type f -name "test_*.xml" -mtime +7 -delete 2>/dev/null || true
    
    log_message "SUCCESS" "Old test results cleaned"
}

# Function to generate cleanup report
generate_cleanup_report() {
    local duration=$(($(date +%s) - START_TIME))
    local report_path="${REPORT_DIR}/cleanup_report_$(date +%Y%m%d_%H%M%S).txt"

    mkdir -p "${REPORT_DIR}"

    {
        echo "ProfileScope Cleanup Report - $(date)"
        echo "=================================="
        echo "Script Version: $SCRIPT_VERSION"
        echo "Duration: ${duration}s"
        echo ""
        echo "Statistics:"
        echo "-----------"
        echo "Directories Cleaned: ${#DIRS_TO_CLEAN[@]}"
        echo "File Patterns Cleaned: ${#FILES_TO_CLEAN[@]}"
        echo ""
        echo "Disk Space After Cleanup:"
        df -h "$(dirname "${BASE_DIR}")" | grep -v "Filesystem"
    } > "$report_path"

    log_message "SUCCESS" "Generated cleanup report: $report_path"
}

# Function to collect performance metrics
collect_performance_metrics() {
    local metrics_file="${REPORT_DIR}/performance_metrics_$(date +%Y%m%d_%H%M%S).json"

    # Get memory usage based on OS
    local memory_usage
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS memory usage
        memory_usage=$(vm_stat | perl -ne '/page size of (\d+)/ and $size=$1; /Pages active: (\d+)/ and printf("%.0f\n", $1 * $size / 1048576);')
    else
        # Linux memory usage
        memory_usage=$(free -m | awk '/Mem:/ {print $3}')
    fi

    # Get disk usage without percentage sign
    local disk_usage=$(df -h "$(dirname "${BASE_DIR}")" | awk 'NR==2 {print $5}' | tr -d '%')

    # Generate JSON
    {
        echo "{"
        echo "  \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\","
        echo "  \"memory_usage_mb\": ${memory_usage:-0},"
        echo "  \"disk_usage_percent\": ${disk_usage:-0},"
        echo "  \"cleanup_duration_seconds\": $(($(date +%s) - START_TIME))"
        echo "}"
    } > "$metrics_file"

    log_message "SUCCESS" "Generated performance metrics: $metrics_file"
}

# Final cleanup and statistics
perform_final_cleanup() {
    local stats_file="${REPORT_DIR}/cleanup_stats_$(date +%Y%m%d_%H%M%S).json"
    mkdir -p "${REPORT_DIR}"

    # Define stats data
    local -a keys=("timestamp" "directories_cleaned" "files_removed" "duration_seconds")
    local -a values=(
        "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
        "${#DIRS_TO_CLEAN[@]}"
        "$(find "${BASE_DIR}" -type f -name "*.log" 2>/dev/null | wc -l)"
        "$(($(date +%s) - START_TIME))"
    )

    # Generate JSON without sed dependency
    {
        echo "{"
        for i in "${!keys[@]}"; do
            if [ $i -eq $((${#keys[@]} - 1)) ]; then
                echo "  \"${keys[$i]}\": \"${values[$i]}\""
            else
                echo "  \"${keys[$i]}\": \"${values[$i]}\","
            fi
        done
        echo "}"
    } > "$stats_file"

    log_message "SUCCESS" "Generated cleanup statistics: $stats_file"
}

# Main execution flow
main() {
    log_message "INFO" "Starting ProfileScope cleanup process (v$SCRIPT_VERSION)"

    # Create required directories
    mkdir -p "${LOG_DIR}" "${REPORT_DIR}" "${BACKUP_DIR}"

    # Run cleanup tasks
    clean_directories
    clean_files
    archive_logs
    clean_python_artifacts
    clean_test_results

    # Generate reports
    generate_cleanup_report
    collect_performance_metrics
    perform_final_cleanup

    log_message "SUCCESS" "ProfileScope cleanup completed successfully"
}

# Execute main function
main

# Cleanup on exit
trap 'log_message "INFO" "Script execution completed, cleaning up..."; perform_final_cleanup' EXIT
