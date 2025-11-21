from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import asyncio
from typing import Dict, Optional
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Streaming Service API", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diccionario para almacenar los procesos activos
active_streams: Dict[str, subprocess.Popen] = {}

# Tarea de monitoreo
monitor_task: Optional[asyncio.Task] = None


class StreamConfig(BaseModel):
    stream_name: str
    rtsp_url: str
    username: Optional[str] = None
    password: Optional[str] = None


class StreamResponse(BaseModel):
    stream_name: str
    status: str
    message: str
    mediamtx_url: Optional[str] = None


async def monitor_streams():
    """
    Tarea en segundo plano que monitorea el estado de los streams
    y limpia automáticamente los que han fallado
    """
    while True:
        try:
            # Revisar cada 5 segundos
            await asyncio.sleep(5)
            
            # Lista de streams que han terminado
            dead_streams = []
            
            for stream_name, process in active_streams.items():
                # Verificar si el proceso sigue corriendo
                if process.poll() is not None:
                    # El proceso terminó
                    dead_streams.append(stream_name)
                    
                    # Leer el error de stderr si existe
                    try:
                        stderr = process.stderr.read().decode('utf-8', errors='ignore')
                        if stderr:
                            logger.error(f"Stream '{stream_name}' terminó con error: {stderr[-500:]}")
                        else:
                            logger.warning(f"Stream '{stream_name}' terminó inesperadamente")
                    except:
                        logger.warning(f"Stream '{stream_name}' terminó")
            
            # Limpiar los streams muertos
            for stream_name in dead_streams:
                del active_streams[stream_name]
                logger.info(f"Stream '{stream_name}' removido automáticamente (cámara no disponible)")
        
        except asyncio.CancelledError:
            # Tarea cancelada, salir del loop
            break
        except Exception as e:
            logger.error(f"Error en monitor de streams: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Iniciar el monitoreo de streams al arrancar la aplicación"""
    global monitor_task
    monitor_task = asyncio.create_task(monitor_streams())
    logger.info("Monitor de streams iniciado")


@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    return {
        "service": "Streaming Service API",
        "version": "1.0.0",
        "active_streams": len(active_streams)
    }


@app.get("/streams")
async def list_streams():
    """Listar todos los streams activos"""
    streams = []
    for stream_name, process in active_streams.items():
        is_running = process.poll() is None
        streams.append({
            "stream_name": stream_name,
            "status": "running" if is_running else "stopped",
            "pid": process.pid if is_running else None
        })
    
    return {
        "total": len(streams),
        "streams": streams
    }


@app.post("/stream/start", response_model=StreamResponse)
async def start_stream(config: StreamConfig):
    """
    Iniciar un stream RTSP hacia MediaMTX
    
    Args:
        config: Configuración del stream con nombre, URL RTSP y credenciales opcionales
    
    Returns:
        Información del stream iniciado
    """
    stream_name = config.stream_name
    
    # Verificar si el stream ya existe
    if stream_name in active_streams:
        process = active_streams[stream_name]
        if process.poll() is None:  # El proceso sigue corriendo
            raise HTTPException(
                status_code=400,
                detail=f"Stream '{stream_name}' ya está activo"
            )
        else:
            # El proceso murió, removerlo
            del active_streams[stream_name]
    
    # Construir la URL RTSP de entrada
    rtsp_input = config.rtsp_url
    if config.username and config.password:
        # Insertar credenciales en la URL
        if "://" in rtsp_input:
            protocol, rest = rtsp_input.split("://", 1)
            rtsp_input = f"{protocol}://{config.username}:{config.password}@{rest}"
    
    # URL de salida hacia MediaMTX
    mediamtx_url = f"rtsp://localhost:8554/{stream_name}"
    
    # Construir comando ffmpeg con opciones mejoradas para estabilidad
    ffmpeg_command = [
        "ffmpeg",
        "-rtsp_transport", "tcp",  # Usar TCP para la entrada
        "-i", rtsp_input,
        "-c", "copy",  # Copiar sin recodificar
        "-f", "rtsp",
        "-rtsp_transport", "tcp",  # Usar TCP para la salida
        "-rtsp_flags", "prefer_tcp",
        mediamtx_url
    ]
    
    try:
        # Iniciar el proceso ffmpeg
        process = subprocess.Popen(
            ffmpeg_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        
        # Esperar un momento para verificar que el proceso no falle inmediatamente
        await asyncio.sleep(1)
        
        if process.poll() is not None:
            # El proceso terminó inmediatamente, algo salió mal
            stderr = process.stderr.read().decode('utf-8', errors='ignore')
            raise HTTPException(
                status_code=500,
                detail=f"Error al iniciar el stream: {stderr[:500]}"
            )
        
        # Guardar el proceso
        active_streams[stream_name] = process
        
        logger.info(f"Stream '{stream_name}' iniciado exitosamente (PID: {process.pid})")
        
        return StreamResponse(
            stream_name=stream_name,
            status="started",
            message="Stream iniciado exitosamente",
            mediamtx_url=mediamtx_url
        )
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="FFmpeg no está instalado o no se encuentra en el PATH del sistema"
        )
    except Exception as e:
        logger.error(f"Error al iniciar stream '{stream_name}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al iniciar el stream: {str(e)}"
        )


@app.post("/stream/stop/{stream_name}", response_model=StreamResponse)
async def stop_stream(stream_name: str):
    """
    Detener un stream activo
    
    Args:
        stream_name: Nombre del stream a detener
    
    Returns:
        Información del stream detenido
    """
    if stream_name not in active_streams:
        raise HTTPException(
            status_code=404,
            detail=f"Stream '{stream_name}' no existe o no está activo"
        )
    
    process = active_streams[stream_name]
    
    try:
        # Intentar terminar el proceso de forma limpia
        process.terminate()
        
        # Esperar hasta 5 segundos para que termine
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # Si no termina, forzar la terminación
            process.kill()
            process.wait()
        
        # Remover del diccionario
        del active_streams[stream_name]
        
        logger.info(f"Stream '{stream_name}' detenido exitosamente")
        
        return StreamResponse(
            stream_name=stream_name,
            status="stopped",
            message="Stream detenido exitosamente"
        )
        
    except Exception as e:
        logger.error(f"Error al detener stream '{stream_name}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al detener el stream: {str(e)}"
        )


@app.delete("/stream/{stream_name}", response_model=StreamResponse)
async def delete_stream(stream_name: str):
    """
    Alias para detener un stream (usando DELETE method)
    
    Args:
        stream_name: Nombre del stream a eliminar
    
    Returns:
        Información del stream eliminado
    """
    return await stop_stream(stream_name)


@app.on_event("shutdown")
async def shutdown_event():
    """Limpiar todos los streams al apagar el servicio"""
    global monitor_task
    
    # Cancelar la tarea de monitoreo
    if monitor_task:
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
    
    logger.info("Deteniendo todos los streams activos...")
    
    for stream_name, process in list(active_streams.items()):
        try:
            process.terminate()
            process.wait(timeout=3)
        except Exception as e:
            logger.error(f"Error al detener stream '{stream_name}': {str(e)}")
            try:
                process.kill()
            except:
                pass
    
    active_streams.clear()
    logger.info("Todos los streams han sido detenidos")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
