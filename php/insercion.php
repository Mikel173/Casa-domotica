<?php
// /php/insercion.php
include_once 'conexion.php';

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // Obtener los datos JSON
    $json = file_get_contents('php://input');
    $data = json_decode($json, true);

    if (isset($data['datos']) && is_array($data['datos'])) {
        try {
            // Preparar la declaración una vez
            $stmt = $conexion->prepare("INSERT INTO datos_dispositivos (dispositivo_id, tipo_dispositivo, valor, usuario_id) VALUES (?, ?, ?, ?)");

            // Iniciar una transacción para mayor eficiencia
            $conexion->beginTransaction();

            foreach ($data['datos'] as $dato) {
                if (isset($dato['dispositivo_id'], $dato['tipo_dispositivo'], $dato['valor'], $dato['usuario_id'])) {
                    $stmt->execute([
                        $dato['dispositivo_id'],
                        $dato['tipo_dispositivo'],
                        $dato['valor'],
                        $dato['usuario_id']
                    ]);
                }
            }

            // Confirmar la transacción
            $conexion->commit();
            echo "Datos insertados correctamente";
        } catch (PDOException $e) {
            // Revertir la transacción en caso de error
            $conexion->rollBack();
            echo "Error al insertar datos: " . $e->getMessage();
        }
    } else {
        echo "Datos inválidos en la solicitud POST";
    }
} else {
    echo "Solicitud inválida";
}
