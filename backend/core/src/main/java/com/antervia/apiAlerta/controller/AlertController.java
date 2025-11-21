/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.antervia.apiAlerta.controller;

import com.antervia.apiAlerta.model.Alert;
import com.antervia.apiAlerta.repository.AlertRepository;
import com.antervia.apiAlerta.service.WebSocketService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 *
 * @author michel
 */
@RestController
@RequestMapping("/api")
// Permite peticiones CORS desde cualquier origen (útil para desarrollo)
@CrossOrigin(origins = "*") 
public class AlertController {

    private final AlertRepository alertRepository;
    private final WebSocketService webSocketService;

    public AlertController(AlertRepository alertRepository, WebSocketService webSocketService) {
        this.alertRepository = alertRepository;
        this.webSocketService = webSocketService;
    }

    /**
     * Recibe la alerta desde Python (POST).
     * El JSON snake_case se convierte automáticamente a objeto Alert gracias a @JsonProperty.
     */
    // Endpoint para el script de Python (POST)
    @PostMapping("/internal/alerts")
    public ResponseEntity<Alert> createAlert(@RequestBody Alert alert) {
        System.out.println("Alerta recibida (REST): " + alert.getEventType());

        // 1. Guardar en base de datos
        Alert savedAlert = alertRepository.save(alert);
        
        // 2. Notificar a WebSocket
        webSocketService.notifyFrontend(savedAlert);

        return new ResponseEntity<>(savedAlert, HttpStatus.CREATED);
    }

    /**
     * Devuelve el historial de alertas (GET).
     */
    // Endpoint para el historial (GET)
    @GetMapping("/alerts")
    public List<Alert> getAllAlerts() {
        return alertRepository.findTop50ByOrderByIdDesc();
    }
}