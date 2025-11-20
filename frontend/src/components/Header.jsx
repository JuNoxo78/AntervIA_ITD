import React from 'react';
import './Header.css';

// Ya no recibimos 'isDarkMode' como prop
function Header({ selectedCamera }) {
  
  // Ruta directa a la única imagen del logo
  // (Esto asume que 'Logo.png' está en tu carpeta 'public/')
  const logoSrc = '/LogoLight.png'; 

  return (
    <header className="header">
      <div className="logo">
        <img src={logoSrc} alt="AnterVIA Logo" className="logo-img" />
        <span className="logo-text">AntervIA</span>
      </div>
      
      <div className="header-right-content">
        {/* Espacio para contenido futuro */}
      </div>
    </header>
  );
}

export default Header;