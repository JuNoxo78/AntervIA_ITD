/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.antervia.apiAlerta.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;



/**
 *
 * @author michel
 *
 * Entidad que representa una alerta de seguridad.
 * Mapea el JSON externo (snake_case) a propiedades Java (camelCase).
 */
@Entity
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Alert {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Mapea "camera_id" del JSON a "cameraId"
    @JsonProperty("camera_id")
    private Integer cameraId;

    // Recibe el timestamp como String (ISO 8601)
    private String timestamp;

    // Mapea "event_type" del JSON a "eventType"
    @JsonProperty("event_type")
    private String eventType;

    private String details;

    // Mapea "clip_path" del JSON a "clipPath"
    @JsonProperty("clip_path")
    private String clipPath;
}