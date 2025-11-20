import React, { useState } from 'react';
import './Sidebar.css';
import { FaVideo, FaBell, FaPlus } from 'react-icons/fa';

// --- ¡HEMOS BORRADO LAS CONSTANTES 'cameras' Y 'alerts' DE AQUÍ! ---
// Los datos ahora vienen de App.jsx

// 1. Recibimos los props correctos de App.jsx
function Sidebar({ 
  cameras, 
  alerts, 
  selectedCamera, 
  onSelectCamera, // 2. El nombre coincide: onSelectCamera
  onOpenAlertModal, 
  onOpenAddCameraModal 
}) {
  const [activeView, setActiveView] = useState('cameras'); // Estado interno (esto está bien)

  return (
    <aside className="sidebar">
      <div className="top-icons">
        <div 
          className={`icon-wrapper ${activeView === 'cameras' ? 'active' : ''}`}
          onClick={() => setActiveView('cameras')}
        >
          <FaVideo size={20} />
        </div>
        <div 
          className={`icon-wrapper ${activeView === 'alerts' ? 'active' : ''}`}
          onClick={() => setActiveView('alerts')}
        >
          <FaBell size={20} />
        </div>
      </div>

      <div className="sidebar-main-content">
        {activeView === 'cameras' ? (
          <>
            <div className="sidebar-title">
              Mis Cámaras
            </div>
            <div className="camera-list">
              {/* 3. Mapeamos las 'cameras' recibidas como prop */}
              {cameras.map((camera) => (
                <div
                  // 4. Comparamos por ID (más seguro que por nombre)
                  className={`camera-preview ${selectedCamera.id === camera.id ? 'selected' : ''}`}
                  key={camera.id} // Usar ID para el key
                  // 5. ¡AQUÍ ESTÁ LA MAGIA!
                  // Llamamos a la función 'onSelectCamera' que nos pasó App.jsx
                  // y le pasamos el objeto 'camera' completo.
                  onClick={() => onSelectCamera(camera)}
                >
                  <img 
                    src={camera.thumbnail} 
                    alt={`Preview ${camera.name}`} 
                  />
                  <div className="camera-label">{camera.name}</div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <>
            <div className="sidebar-title">
              Alertas
            </div>
            <div className="alerts-list">
              {/* 6. Mapeamos las 'alerts' recibidas como prop */}
              {alerts.map((alert) => (
                <div 
                  key={alert.id}
                  className={`alert-item alert-${alert.type}`}
                  onClick={() => onOpenAlertModal(alert)} // Esto ya estaba bien
                >
                  <div className="alert-title">{alert.title}</div>
                  <div className="alert-description">{alert.description}</div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
      
      {/* 7. Botón de "Agregar Cámara" (esto ya estaba bien) */}
      {activeView === 'cameras' && (
        <button className="add-camera-button" onClick={onOpenAddCameraModal}>
          <FaPlus size={14} />Agregar Cámara
        </button>
      )}
    </aside>
  );
}

export default Sidebar;