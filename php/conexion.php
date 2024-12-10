<?php
// conexion.php
try {
    $conexion = new PDO('mysql:host=localhost;dbname=bd_csdomotica', 'root', '');
    $conexion->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    // Conexión exitosa
} catch (PDOException $e) {
    echo "Error de conexión: " . $e->getMessage();
    exit();
}
