import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from pathlib import Path
import ServexTools.Tools as Tools

# Configuración centralizada
LOG_DIR = None
LOG_MAX_BYTES = 100 * 1024 * 1024  # 100MB
LOG_BACKUP_COUNT = 5  # Mantener 5 archivos rotados
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%d/%m/%Y %I:%M %p'


def _get_log_directory():
    """Obtiene y crea el directorio de logs si no existe"""
    global LOG_DIR
    if LOG_DIR is None:
        LOG_DIR = os.path.join(Tools.OptenerRutaApp(), "Log")
        Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
    return LOG_DIR


def _get_logger(name, filename):
    """Crea o retorna un logger configurado con RotatingFileHandler"""
    logger = logging.getLogger(name)
    
    # Si ya está configurado, retornarlo
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    log_path = os.path.join(_get_log_directory(), filename)
    
    # RotatingFileHandler: rotación automática por tamaño
    handler = RotatingFileHandler(
        log_path,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    
    formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def EscribirLog(texto, tipo="Error"):
    """
    Escribe log de errores o éxitos.
    Append-only, sin leer archivo completo.
    
    Args:
        texto (str): Mensaje a escribir en el log
        tipo (str): "Error" o "Success"
    """
    try:
        filename = "Success.log" if tipo != "Error" else "Error.log"
        logger = _get_logger(f"servex_{tipo.lower()}", filename)
        
        if tipo == "Error":
            logger.error(texto)
        else:
            logger.info(texto)
            
        # También imprimir en consola
        print(f"{datetime.now().strftime(LOG_DATE_FORMAT)}: {texto}")
        
    except Exception as e:
        print(f"Error escribiendo log: {str(e)}")


def EscribirConsola(texto):
    """
    Escribe log de consola. Append-only.
    
    Args:
        texto (str): Mensaje a escribir en el log de consola
    """
    try:
        logger = _get_logger("servex_consola", "Consola.log")
        logger.info(texto)
        print(f"{datetime.now().strftime(LOG_DATE_FORMAT)}: {texto}")
    except Exception as e:
        print(f"Error escribiendo consola: {str(e)}")


def EscribirProcesos(texto):
    """
    Escribe log de procesos. Append-only.
    
    Args:
        texto (str): Mensaje a escribir en el log de procesos
    """
    try:
        logger = _get_logger("servex_procesos", "Procesos.log")
        logger.info(texto)
    except Exception as e:
        print(f"Error escribiendo procesos: {str(e)}")


def EscribirUpdate(texto):
    """
    Escribe log de updates y emite por socket. Append-only.
    
    Args:
        texto (str): Mensaje a escribir en el log de updates
    """
    try:
        from app import socketio as io
        
        logger = _get_logger("servex_update", "Update.log")
        logger.info(texto)
        
        # Emitir por socket
        mensaje = f"{datetime.now().strftime(LOG_DATE_FORMAT)}: {texto}"
        io.emit("EscribirEnConsola", mensaje)
        
        # También escribir en consola
        EscribirConsola(texto)
        
    except Exception as e:
        print(f"Error escribiendo update: {str(e)}")


def LimpiarLogsAntiguos(dias=30):
    """
    Limpia archivos de log más antiguos que X días.
    Llamar periódicamente desde un cron job o al inicio de la app.
    
    Args:
        dias (int): Número de días. Archivos más antiguos serán eliminados.
    """
    try:
        from ServexTools.GetTime import CalDias
        log_dir = _get_log_directory()
        
        for filename in os.listdir(log_dir):
            if filename.endswith('.log') or '.log.' in filename:
                filepath = os.path.join(log_dir, filename)
                if os.path.isfile(filepath):
                    fecha_creacion = Tools.OptenerFechaArchivo(filepath)
                    if CalDias(fechaInicial=fecha_creacion) >= dias:
                        os.remove(filepath)
                        print(f"Log antiguo eliminado: {filename}")
                        
    except Exception as e:
        print(f"Error limpiando logs antiguos: {str(e)}")


# Mantener función legacy por compatibilidad
def GetDirectorio():
    """Función legacy - mantener por compatibilidad"""
    return Tools.OptenerRutaApp()