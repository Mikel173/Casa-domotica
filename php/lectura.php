<?php
// /php/lectura.php
include_once 'conexion.php';

try {
    $stmt = $conexion->query("SELECT dd.id_dato, d.nombre AS dispositivo_nombre, d.tipo AS dispositivo_tipo, dd.tipo_dispositivo, dd.valor, dd.fecha_hora, u.nombre AS usuario_nombre
                              FROM datos_dispositivos dd
                              JOIN dispositivos d ON dd.dispositivo_id = d.id_dispositivo
                              LEFT JOIN usuarios u ON dd.usuario_id = u.id_usuario
                              ORDER BY dd.fecha_hora DESC");
    $datos = $stmt->fetchAll(PDO::FETCH_ASSOC);
    header('Content-Type: application/json');
    echo json_encode($datos);
} catch (PDOException $e) {
    echo "Error al leer datos: " . $e->getMessage();
}
