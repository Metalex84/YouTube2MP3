#!/usr/bin/env bash

# YouTube2MP3 Web Application - Docker Wrapper Script
# This script builds and runs the web application in a Docker container

set -e

# Configuration
IMAGE_NAME="youtube2mp3-web"
CONTAINER_NAME="youtube2mp3-web"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOWNLOADS_DIR="${SCRIPT_DIR}/downloads"
LOGS_DIR="${SCRIPT_DIR}/logs"
PORT=5000

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}  YouTube2MP3 Web Application - Docker${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        print_info "Please install Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        print_info "Please start Docker and try again"
        exit 1
    fi
}

# Check if container exists
container_exists() {
    docker ps -a --filter "name=^${CONTAINER_NAME}$" --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"
}

# Check if container is running
container_running() {
    docker ps --filter "name=^${CONTAINER_NAME}$" --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"
}

# Check if image exists
image_exists() {
    docker images -q "${IMAGE_NAME}" 2> /dev/null | grep -q .
}

# Stop and remove container
stop_container() {
    print_info "Stopping container..."
    
    if container_running; then
        docker stop "${CONTAINER_NAME}" > /dev/null
        print_success "Container stopped"
    fi
    
    if container_exists; then
        docker rm "${CONTAINER_NAME}" > /dev/null
        print_success "Container removed"
    fi
}

# Build Docker image
build_image() {
    print_info "Building Docker image..."
    
    cd "${SCRIPT_DIR}"
    
    if docker build -t "${IMAGE_NAME}" .; then
        print_success "Image built successfully"
        return 0
    else
        print_error "Failed to build image"
        return 1
    fi
}

# Create directories if they don't exist
initialize_directories() {
    if [[ ! -d "${DOWNLOADS_DIR}" ]]; then
        mkdir -p "${DOWNLOADS_DIR}"
        print_info "Created downloads directory"
    fi
    
    if [[ ! -d "${LOGS_DIR}" ]]; then
        mkdir -p "${LOGS_DIR}"
        print_info "Created logs directory"
    fi
}

# Run container
start_container() {
    print_info "Starting container on port ${PORT}..."
    
    if docker run -d \
        --name "${CONTAINER_NAME}" \
        -p "${PORT}:5000" \
        -v "${DOWNLOADS_DIR}:/app/downloads" \
        -v "${LOGS_DIR}:/app/logs" \
        -e PYTHONUNBUFFERED=1 \
        -e PYTHONIOENCODING=utf-8 \
        -e DOWNLOAD_DIR=/app/downloads \
        -e LOGS_DIR=/app/logs \
        --restart unless-stopped \
        "${IMAGE_NAME}" > /dev/null; then
        
        print_success "Container started successfully"
        print_info "Web application available at: http://localhost:${PORT}"
        return 0
    else
        print_error "Failed to start container"
        return 1
    fi
}

# Show logs
show_logs() {
    print_info "Showing container logs (Ctrl+C to exit)..."
    docker logs -f "${CONTAINER_NAME}"
}

# Clean everything
clean_everything() {
    print_warning "This will remove the container and image completely."
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cancelled"
        return
    fi
    
    stop_container
    
    if image_exists; then
        print_info "Removing image..."
        docker rmi "${IMAGE_NAME}" > /dev/null
        print_success "Image removed"
    fi
}

# Show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    -b, --build     Force rebuild of the Docker image
    -s, --stop      Stop and remove the running container
    -l, --logs      Show logs from the running container
    -c, --clean     Remove container and image completely
    -p, --port PORT Port to expose the web application (default: 5000)
    -h, --help      Show this help message

Examples:
    $0                  Start the web application (builds if needed)
    $0 --build          Force rebuild and start the application
    $0 --stop           Stop the running container
    $0 --logs           Show container logs
    $0 --port 8080      Run on port 8080 instead of 5000

EOF
}

# Parse command line arguments
BUILD=false
STOP=false
LOGS=false
CLEAN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--build)
            BUILD=true
            shift
            ;;
        -s|--stop)
            STOP=true
            shift
            ;;
        -l|--logs)
            LOGS=true
            shift
            ;;
        -c|--clean)
            CLEAN=true
            shift
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main script
print_header

# Check Docker installation
check_docker

# Handle different operations
if [[ "$CLEAN" == true ]]; then
    clean_everything
    exit 0
fi

if [[ "$STOP" == true ]]; then
    stop_container
    exit 0
fi

if [[ "$LOGS" == true ]]; then
    if ! container_running; then
        print_error "Container is not running"
        exit 1
    fi
    show_logs
    exit 0
fi

# Main flow: Build and Run
initialize_directories

# Check if image exists or force rebuild
if [[ "$BUILD" == true ]] || ! image_exists; then
    if ! build_image; then
        exit 1
    fi
fi

# Stop existing container if running
if container_running; then
    print_info "Container already running, stopping it first..."
    stop_container
fi

# Remove existing container if exists
if container_exists; then
    docker rm "${CONTAINER_NAME}" > /dev/null 2>&1 || true
fi

# Start the container
if start_container; then
    echo ""
    print_success "Application is ready!"
    echo ""
    print_info "Access the web interface at: http://localhost:${PORT}"
    print_info "View logs with: ./run-web.sh --logs"
    print_info "Stop with: ./run-web.sh --stop"
    echo ""
else
    print_error "Failed to start application"
    exit 1
fi
