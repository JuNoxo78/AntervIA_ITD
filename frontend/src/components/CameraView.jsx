import React, { useState } from 'react'; // 1. Importa useState
import './CameraView.css';
// 2. Importa los nuevos iconos para los controles de vista
import { FaArrowLeft, FaArrowRight } from 'react-icons/fa';
import { BsLayoutSplit, BsFillGrid3X3GapFill } from 'react-icons/bs';
import { LuCameraOff } from "react-icons/lu"; // Icono para "cámara no disponible"

function CameraView({ selectedCamera, cameraImage }) {
  // 3. Crea el estado para el layout
  const [layout, setLayout] = useState('single'); // 'single' o 'grid'

  return (
    // 4. Añade una clase dinámica al contenedor principal
    <main className={`camera-view ${layout === 'grid' ? 'grid-mode' : 'single-mode'}`}>
      
      {/* 5. Contenedor para el contenido (que será flexible) */}
      <div className="camera-content-area">
        
        {/* --- RENDERIZADO CONDICIONAL --- */}
        {layout === 'single' ? (
          
          // --- VISTA INDIVIDUAL (El código que ya tenías) ---
          <div className="camera-view-container">
            <div className="camera-view-header-main">
              {selectedCamera}
            </div>
            <div className="video-feed">
              <img src={cameraImage} alt={`Feed de ${selectedCamera}`} />
              <div className="timestamp">
                15-06-2024 17:35:08
              </div>
            </div>
          </div>

        ) : (

          // --- VISTA DE CUADRÍCULA (El nuevo diseño 2x2) ---
          <div className="camera-grid-container">
            {/* Cámara 1 */}
            <div className="grid-item">
              <img src={cameraImage} alt="Feed 1" className="grid-item-video" />
              <div className="grid-item-timestamp">15-06-2024 17:35:08</div>
            </div>
            {/* Cámara 2 */}
            <div className="grid-item">
              {/* Esta es la otra imagen de tu ejemplo */}
              <img src="/image_c2daa8.jpg" alt="Feed 2" className="grid-item-video" />
              <div className="grid-item-timestamp">12-11-2020 23:18:47</div>
            </div>
            {/* Cámara 3 (No disponible) */}
            <div className="grid-item empty-grid-item">
              <LuCameraOff size={50} />
              <p>Cámaras no disponibles</p>
              <span>Agregue una cámara</span>
            </div>
            {/* Cámara 4 (No disponible) */}
            <div className="grid-item empty-grid-item">
              <LuCameraOff size={50} />
              <p>Cámaras no disponibles</p>
              <span>Agregue una cámara</span>
            </div>
          </div>

        )}
      </div>

      {/* 6. BARRA DE CONTROLES DE VISTA (Siempre visible) */}
      <div className="view-controls">
        <button className="control-button">
          <FaArrowLeft size={18} />
        </button>
        <button 
          className={`control-button ${layout === 'single' ? 'active' : ''}`}
          onClick={() => setLayout('single')}
        >
          <BsLayoutSplit size={20} />
        </button>
        <button 
          className={`control-button ${layout === 'grid' ? 'active' : ''}`}
          onClick={() => setLayout('grid')}
        >
          <BsFillGrid3X3GapFill size={18} />
        </button>
        <button className="control-button">
          <FaArrowRight size={18} />
        </button>
      </div>
    </main>
  );
}

export default CameraView;