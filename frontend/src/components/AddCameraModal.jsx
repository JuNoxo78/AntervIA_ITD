import React, { useState } from 'react'; // 1. Importa useState
import './AddCameraModal.css';
import { IoCloseCircleOutline } from "react-icons/io5";

// Datos de ejemplo para las sugerencias
const suggestionData = [
  { id: 1, name: 'IP_Camera (BUILD_123)', url: 'http://ip:port/onvif/device_service' },
  { id: 2, name: 'IP_Camera (BUILD_123)', url: 'http://ip:port/onvif/device_service' },
];

function AddCameraModal({ onClose }) {
  // 2. Estado para la sugerencia seleccionada
  const [selectedSuggestionId, setSelectedSuggestionId] = useState(null); // null por defecto, ninguna seleccionada

  // Función para manejar el clic en una sugerencia
  const handleSuggestionClick = (id, url) => {
    setSelectedSuggestionId(id);
    // Aquí podrías también rellenar el campo 'URL del servicio' con la 'url'
    // Por ahora, solo cambiaremos el estilo.
    console.log(`Sugerencia ${id} seleccionada: ${url}`);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content add-camera-modal" onClick={(e) => e.stopPropagation()}>
        
        {/* Cabecera con Gradiente */}
        <div className="modal-header-gradient">
          <h2>Agregar Cámara IP (ONVIF)</h2>
          <p>Ingrese las credenciales correspondientes, para agregar su cámara IP a AntervIA.</p>
          {/* Botón de cerrar aquí para que esté en la cabecera del gradiente */}
          <IoCloseCircleOutline size={24} className="close-button" onClick={onClose} />
        </div>

        {/* Cuerpo del Formulario */}
        <form className="modal-form-body">
          {/* Columna Izquierda */}
          <div className="form-column-left">
            <div className="form-group">
              <label htmlFor="cam-nombre">Nombre</label>
              <input type="text" id="cam-nombre" defaultValue="Camera 01" />
            </div>
            <div className="form-group">
              <label htmlFor="cam-notas">Notas</label>
              <textarea id="cam-notas" rows="10"></textarea>
            </div>
          </div>

          {/* Columna Derecha */}
          <div className="form-column-right">
            <div className="form-group">
              <label>Datos ONVIF/RTSP</label>
            </div>
            <div className="form-group">
              <label htmlFor="cam-user">Nombre de usuario</label>
              <input type="text" id="cam-user" placeholder="Usuario configurado para seguridad en ONVIF" />
            </div>
            <div className="form-group">
              <label htmlFor="cam-pass">Contraseña</label>
              <input type="password" id="cam-pass" placeholder="Contraseña configurada para seguridad en ONVIF" />
            </div>
            <div className="form-group">
              <label htmlFor="cam-url">URL del servicio</label>
              <input type="text" id="cam-url" defaultValue="http://ip:port/onvif/device_service" />
            </div>
            
            <div className="suggestion-box">
              <label>Disponible (haga clic para seleccionar):</label>
              <div className="suggestion-items">
                {suggestionData.map((sug) => (
                  <div
                    key={sug.id}
                    // 3. Clase condicional 'selected'
                    className={`suggestion-item ${selectedSuggestionId === sug.id ? 'selected' : ''}`}
                    // 4. Maneja el clic
                    onClick={() => handleSuggestionClick(sug.id, sug.url)}
                  >
                    <span>{sug.name}</span>
                    <span>{sug.url}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="form-group discover-group">
              <label>Descubrir</label>
              <button type="button" className="btn-discover">Recibir las URL de vídeo</button>
            </div>
            <div className="form-group">
              <label htmlFor="cam-rtsp">URL RTSP en vivo</label>
              <input type="text" id="cam-rtsp" defaultValue="rtsp://ip:puerto/h264_ulaw.sdp" />
            </div>
          </div>
        </form>

        {/* Pie de Página del Modal (Botones) */}
        <div className="modal-footer">
          <button type="button" className="btn-cancel" onClick={onClose}>Cancelar</button>
          <button type="submit" className="btn-submit">Agregar</button> {/* Cambiado a type="submit" */}
        </div>

      </div>
    </div>
  );
}

export default AddCameraModal;