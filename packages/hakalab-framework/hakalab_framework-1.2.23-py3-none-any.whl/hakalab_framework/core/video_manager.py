#!/usr/bin/env python3
"""
Gestor de videos para el framework Hakalab
Maneja automáticamente la grabación y guardado de videos según configuración
"""
import os
import shutil
import time
from pathlib import Path
from typing import Optional


def clean_filename(filename: str) -> str:
    """Limpia un nombre de archivo para que sea válido en Windows y otros sistemas"""
    # Caracteres no permitidos en nombres de archivo
    invalid_chars = '<>:"/\\|?*'
    
    # Reemplazar caracteres inválidos
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Reemplazar espacios múltiples con uno solo
    filename = ' '.join(filename.split())
    
    # Limitar longitud
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename.strip()


def generate_video_name(feature_name: str, scenario_name: str, status: str = "") -> str:
    """Genera un nombre de video basado en feature y scenario"""
    # Limpiar nombres
    clean_feature = clean_filename(feature_name)
    clean_scenario = clean_filename(scenario_name)
    
    # Crear nombre base
    if status:
        video_name = f"{status}_{clean_feature}_{clean_scenario}"
    else:
        video_name = f"{clean_feature}_{clean_scenario}"
    
    # Agregar timestamp para evitar conflictos
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    video_name = f"{video_name}_{timestamp}"
    
    return video_name


def save_video_on_scenario_end(context, scenario):
    """
    Guarda el video al final del scenario según la configuración
    Esta función se llama automáticamente desde after_scenario
    """
    try:
        # Verificar si hay página y video habilitado
        if not (hasattr(context, 'page') and context.page and context.page.video):
            return
        
        # Obtener configuración de video
        video_mode = os.getenv('VIDEO_MODE', 'retain-on-failure')
        video_dir = os.getenv('VIDEO_DIR', 'videos')
        
        # Crear directorio si no existe
        os.makedirs(video_dir, exist_ok=True)
        
        # Determinar si guardar el video
        should_save = False
        status_prefix = ""
        
        if video_mode == 'on':
            # Guardar siempre
            should_save = True
            status_prefix = "PASSED" if scenario.status == 'passed' else "FAILED"
        elif video_mode == 'retain-on-failure' and scenario.status == 'failed':
            # Guardar solo si falló
            should_save = True
            status_prefix = "FAILED"
        
        if should_save:
            # Obtener ruta del video temporal
            video_path = context.page.video.path()
            
            if video_path and os.path.exists(video_path):
                # Generar nombre final del video
                feature_name = scenario.feature.name if hasattr(scenario, 'feature') else "Unknown_Feature"
                scenario_name = scenario.name
                
                final_video_name = generate_video_name(feature_name, scenario_name, status_prefix)
                final_video_path = os.path.join(video_dir, f"{final_video_name}.webm")
                
                # Copiar video a ubicación final
                shutil.copy2(video_path, final_video_path)
                
                # Mensaje informativo
                if scenario.status == 'failed':
                    print(f"📹 Video de fallo guardado: {final_video_path}")
                else:
                    print(f"📹 Video guardado: {final_video_path}")
                
                # Guardar ruta en contexto para referencia
                if not hasattr(context, 'saved_videos'):
                    context.saved_videos = []
                context.saved_videos.append(final_video_path)
        
        else:
            # Video no se guarda según configuración
            if video_mode == 'retain-on-failure' and scenario.status == 'passed':
                print("📹 Video no guardado (scenario exitoso, modo retain-on-failure)")
    
    except Exception as e:
        print(f"⚠️ Error guardando video: {e}")


def setup_video_name_for_scenario(context, scenario):
    """
    Configura el nombre del video para el scenario actual
    Esta función se llama automáticamente desde before_scenario
    """
    try:
        # Solo si video está habilitado
        if os.getenv('RECORD_VIDEO', 'false').lower() != 'true':
            return
        
        # Generar nombre base para el video
        feature_name = scenario.feature.name if hasattr(scenario, 'feature') else "Unknown_Feature"
        scenario_name = scenario.name
        
        video_name = generate_video_name(feature_name, scenario_name)
        context.video_name = video_name
        
        # Mensaje informativo (solo en modo debug)
        if os.getenv('HAKALAB_DEBUG', 'false').lower() == 'true':
            print(f"📹 Grabación de video iniciada: {video_name}")
    
    except Exception as e:
        print(f"⚠️ Error configurando nombre de video: {e}")


def get_video_summary(context) -> dict:
    """
    Obtiene un resumen de los videos generados
    """
    try:
        video_dir = os.getenv('VIDEO_DIR', 'videos')
        
        summary = {
            'total_videos': 0,
            'failed_videos': 0,
            'passed_videos': 0,
            'video_directory': video_dir,
            'videos_saved': []
        }
        
        # Contar videos guardados en esta ejecución
        if hasattr(context, 'saved_videos'):
            summary['videos_saved'] = context.saved_videos
            summary['total_videos'] = len(context.saved_videos)
            
            for video_path in context.saved_videos:
                if 'FAILED_' in os.path.basename(video_path):
                    summary['failed_videos'] += 1
                else:
                    summary['passed_videos'] += 1
        
        # Contar todos los videos en el directorio
        if os.path.exists(video_dir):
            all_videos = list(Path(video_dir).glob('*.webm'))
            summary['total_videos_in_directory'] = len(all_videos)
        else:
            summary['total_videos_in_directory'] = 0
        
        return summary
    
    except Exception as e:
        print(f"⚠️ Error obteniendo resumen de videos: {e}")
        return {
            'total_videos': 0,
            'failed_videos': 0,
            'passed_videos': 0,
            'video_directory': video_dir,
            'videos_saved': [],
            'error': str(e)
        }


def cleanup_old_videos(video_dir: str = None, max_age_hours: int = None):
    """
    Limpia videos antiguos del directorio especificado
    """
    try:
        if video_dir is None:
            video_dir = os.getenv('VIDEO_DIR', 'videos')
        
        if max_age_hours is None:
            max_age_hours = int(os.getenv('VIDEO_MAX_AGE_HOURS', '168'))  # 7 días por defecto
        
        if not os.path.exists(video_dir):
            return
        
        max_age_seconds = max_age_hours * 3600
        current_time = time.time()
        
        video_path = Path(video_dir)
        deleted_count = 0
        
        for video_file in video_path.glob('*.webm'):
            try:
                file_age = current_time - video_file.stat().st_mtime
                if file_age > max_age_seconds:
                    video_file.unlink()
                    deleted_count += 1
            except Exception as e:
                print(f"⚠️ No se pudo eliminar video antiguo {video_file}: {e}")
        
        if deleted_count > 0:
            print(f"🧹 Videos antiguos eliminados: {deleted_count} archivos (más de {max_age_hours} horas)")
    
    except Exception as e:
        print(f"⚠️ Error limpiando videos antiguos: {e}")


def is_video_recording_enabled() -> bool:
    """
    Verifica si la grabación de video está habilitada
    """
    return os.getenv('RECORD_VIDEO', 'false').lower() == 'true'


def get_video_config() -> dict:
    """
    Obtiene la configuración actual de video
    """
    return {
        'enabled': is_video_recording_enabled(),
        'directory': os.getenv('VIDEO_DIR', 'videos'),
        'size': os.getenv('VIDEO_SIZE', '1280x720'),
        'mode': os.getenv('VIDEO_MODE', 'retain-on-failure'),
        'cleanup_enabled': os.getenv('CLEANUP_OLD_VIDEOS', 'true').lower() == 'true',
        'max_age_hours': int(os.getenv('VIDEO_MAX_AGE_HOURS', '168'))
    }