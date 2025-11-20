import React from 'react';
import './AlertModal.css';
import { FaPlay, FaPause, FaRedo, FaForward, FaVideo } from 'react-icons/fa'; // Iconos para el reproductor
import { IoCloseCircleOutline } from "react-icons/io5"; // Icono de cerrar

function AlertModal({ alert, onClose, cameraImage }) {
  if (!alert) return null; // No renderizar si no hay datos de alerta

  // Función de ejemplo para "Ver cámara en vivo"
  const handleViewLive = () => {
    alert('Simulando ver cámara en vivo...');
    onClose(); // Cerrar el modal al ver en vivo
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}> {/* Evita cerrar al clickear dentro */}
        
        {/* Cabecera del Modal (Riesgo Alto) */}
        <div className={`modal-header alert-${alert.type}`}>
          <div className="modal-title">{alert.title}</div>
          <IoCloseCircleOutline size={24} className="close-button" onClick={onClose} /> {/* Botón de cerrar */}
        </div>

        {/* Cuerpo del Modal */}
        <div className="modal-body">
          <p className="modal-description">Visualiza el clip en donde se generó la alerta</p>
          
          {/* Aquí iría el reproductor de video */}
          <div className="video-player-container">
            {/* Usamos la imagen de la cámara actual como placeholder para el video */}
            <img src={cameraImage} alt="Video de Alerta" className="alert-video-placeholder" />

            {/* Este sería un video real si tuvieras una URL, por ejemplo: */}
            {/* <video controls src={alert.videoUrl} className="alert-video"></video> */}
            
            {/* Overlay del tiempo y controles */}
            <div className="video-controls-overlay">
              <div className="video-timeline">
                <span className="current-time">{alert.time}</span> {/* Tiempo del clip */}
                <input type="range" className="timeline-slider" value="50" readOnly /> {/* Slider de ejemplo */}
                <span className="total-time">00:00:00</span> {/* Tiempo total del video */}
              </div>

              <div className="playback-controls">
                <FaRedo size={20} className="control-icon" />
                <FaPlay size={24} className="control-icon play-pause" /> {/* O FaPause */}
                <FaForward size={20} className="control-icon" />
                
                <button className="live-button" onClick={handleViewLive}>
                  Ver cámara en vivo <FaVideo size={14} style={{ marginLeft: '5px' }} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AlertModal;