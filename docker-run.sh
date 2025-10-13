#!/bin/bash
# YouTube to MP3 Downloader - Docker Runner Script

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de utilidad
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Función de ayuda
show_help() {
    echo "YouTube to MP3 Downloader - Docker Runner"
    echo "=========================================="
    echo ""
    echo "Uso: $0 [opción] [argumentos...]"
    echo ""
    echo "Opciones:"
    echo "  build                    Construir la imagen Docker"
    echo "  run [args]               Ejecutar el contenedor con argumentos"
    echo "  shell                    Abrir shell interactiva en el contenedor"
    echo "  logs                     Mostrar logs del contenedor"
    echo "  clean                    Limpiar contenedores e imágenes"
    echo "  help                     Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 build"
    echo "  $0 run --version"
    echo "  $0 run \"https://youtube.com/watch?v=...\""
    echo "  $0 run --csv-file urls.csv --max-concurrent 3"
    echo ""
}

# Crear directorios necesarios
create_directories() {
    print_info "Creando directorios necesarios..."
    mkdir -p downloads logs
    print_success "Directorios creados: ./downloads y ./logs"
}

# Construir imagen
build_image() {
    print_info "Construyendo imagen Docker..."
    if docker build -t youtube-mp3-downloader .; then
        print_success "Imagen construida exitosamente"
    else
        print_error "Error construyendo la imagen"
        exit 1
    fi
}

# Ejecutar contenedor
run_container() {
    create_directories
    
    print_info "Ejecutando contenedor con argumentos: $@"
    
    docker run --rm \
        -v "$(pwd)/downloads:/app/downloads" \
        -v "$(pwd)/logs:/app/logs" \
        $([ -f "urls.csv" ] && echo "-v $(pwd)/urls.csv:/app/urls.csv:ro") \
        youtube-mp3-downloader -o downloads "$@"
}

# Shell interactiva
run_shell() {
    create_directories
    
    print_info "Abriendo shell interactiva..."
    docker run --rm -it \
        -v "$(pwd)/downloads:/app/downloads" \
        -v "$(pwd)/logs:/app/logs" \
        --entrypoint /bin/bash \
        youtube-mp3-downloader
}

# Mostrar logs
show_logs() {
    if [ -f "logs/youtube_downloader.log" ]; then
        print_info "Mostrando logs recientes..."
        tail -f logs/youtube_downloader.log
    else
        print_warning "No se encontraron logs"
    fi
}

# Limpiar contenedores e imágenes
clean_docker() {
    print_warning "Limpiando contenedores e imágenes..."
    docker container prune -f
    docker image rm youtube-mp3-downloader 2>/dev/null || true
    print_success "Limpieza completada"
}

# Verificar que Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado o no está en el PATH"
        exit 1
    fi
}

# Función principal
main() {
    check_docker
    
    case "${1:-help}" in
        build)
            build_image
            ;;
        run)
            shift
            run_container "$@"
            ;;
        shell)
            run_shell
            ;;
        logs)
            show_logs
            ;;
        clean)
            clean_docker
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Opción desconocida: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"