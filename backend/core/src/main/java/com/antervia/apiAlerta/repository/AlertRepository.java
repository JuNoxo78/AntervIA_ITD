/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.antervia.apiAlerta.repository;

import com.antervia.apiAlerta.model.Alert;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
/**
 *
 * @author michel
 */
@Repository
public interface AlertRepository extends JpaRepository<Alert, Long> {
    
    // Método para obtener las últimas 50 alertas ordenadas por ID descendente
    // Esto asegura que en el frontend se vean primero las más recientes.
    List<Alert> findTop50ByOrderByIdDesc();
}