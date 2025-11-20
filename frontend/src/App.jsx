import React, { useState } from 'react';
import './App.css';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import CameraView from './components/CameraView';
import AlertModal from './components/AlertModal'; // 1. Importa los modales
import AddCameraModal from './components/AddCameraModal';

// --- DATOS MOVIDOS DE SIDEBAR -> APP ---
const initialCameras = [
  { 
    id: 1, // 2. Agrega IDs
    name: 'Camera 01',
    thumbnail: '/image_c1e7a5.jpg', // Esta es la imagen del preview
    feedImage: '/image_e9700c.png'  // Esta es la imagen del feed principal
  },
  { 
    id: 2,
    name: 'Camera 02',
    thumbnail: 'https://via.placeholder.com/150/EEEEEE/808080?text=Cam+02',
    feedImage: 'https://via.placeholder.com/1280x720.png?text=Feed+Cam+2'
  }
];

const initialAlerts = [
  { 
    id: 1, 
    type: 'high', 
    title: 'Riesgo Alto', 
    description: 'Cámara 01 - Actos violentos',
    camera: 'Camera 01',
    time: '12h 34m 45s',
    videoUrl: 'https://www.w3schools.com/html/mov_bbb.mp4'
  },
  // ... (tus otras alertas)
];
// --- FIN DE LOS DATOS ---

function App() {
  // --- ESTADOS PRINCIPALES ---
  const [cameras, setCameras] = useState(initialCameras);
  const [alerts, setAlerts] = useState(initialAlerts);
  
  // Guardamos el OBJETO completo de la cámara seleccionada
  const [selectedCamera, setSelectedCamera] = useState(initialCameras[0]);
  
  // 3. Estados para manejar los modales
  const [selectedAlert, setSelectedAlert] = useState(null); // (null = cerrado, objeto = abierto)
  const [isAddCameraModalOpen, setIsAddCameraModalOpen] = useState(false);
  
  const [isDarkMode, setIsDarkMode] = useState(false); 

  // --- MANEJADORES DE EVENTOS ---
  const handleCameraSelect = (camera) => {
    console.log("Cámara seleccionada:", camera.name);
    setSelectedCamera(camera); // Guardamos el objeto completo
  };

  const handleOpenAlertModal = (alert) => {
    setSelectedAlert(alert);
  };
  
  const handleCloseAlertModal = () => {
    setSelectedAlert(null);
  };

  const handleOpenAddCameraModal = () => {
    setIsAddCameraModalOpen(true);
  };

  const handleCloseAddCameraModal = () => {
    setIsAddCameraModalOpen(false);
  };

  return (
    <div className="app-container">
      {/* 4. Pasamos los props correctos a cada componente */}
      <Header 
        selectedCamera={selectedCamera.name} // Header solo necesita el nombre
        isDarkMode={isDarkMode} 
      />
      <div className="main-content">
        <Sidebar 
          // Pasamos los datos
          cameras={cameras} 
          alerts={alerts}
          
          // Pasamos el estado y la función para cambiarlo
          selectedCamera={selectedCamera} // Pasamos el objeto
          onSelectCamera={handleCameraSelect} // 5. EL NOMBRE COINCIDE: onSelectCamera
          
          // Pasamos las funciones para abrir los modales
          onOpenAlertModal={handleOpenAlertModal}
          onOpenAddCameraModal={handleOpenAddCameraModal}
        />
        <CameraView 
          // 6. CameraView recibe los props que espera
          selectedCamera={selectedCamera.name} 
          cameraImage={selectedCamera.feedImage}
        />
      </div>

      {/* 7. Los modales se renderizan aquí, en App.jsx */}
      {selectedAlert && (
        <AlertModal 
          alert={selectedAlert} 
          onClose={handleCloseAlertModal} 
          // Pasamos la imagen del feed de la cámara seleccionada
          cameraImage={selectedCamera.feedImage}
        />
      )}
      {isAddCameraModalOpen && (
        <AddCameraModal 
          onClose={handleCloseAddCameraModal}
        />
      )}
    </div>
  );
}

export default App;