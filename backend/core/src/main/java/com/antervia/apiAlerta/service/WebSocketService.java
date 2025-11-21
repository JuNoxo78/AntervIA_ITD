/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.antervia.apiAlerta.service;

import com.antervia.apiAlerta.model.Alert;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;
/**
 *
 * @author michel
 */
@Service
public class WebSocketService {

    private final SimpMessagingTemplate template;

    public WebSocketService(SimpMessagingTemplate template) {
        this.template = template;
    }

    /**
     * Envía la alerta al tópico público para que el frontend la reciba.
     */
    public void notifyFrontend(Alert alert) {
        System.out.println("Enviando alerta WS: " + alert.getEventType());
        // El destino debe coincidir con lo que el cliente JS suscribe (/topic/alerts)
        template.convertAndSend("/topic/alerts", alert);
    }
}