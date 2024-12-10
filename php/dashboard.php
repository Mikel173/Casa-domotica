<?php
// /php/dashboard.php
session_start();
if (!isset($_SESSION['usuario_id'])) {
    header('Location: login.php');
    exit();
}
?>
<!DOCTYPE html>
<html>

<head>
    <title>Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f0f2f5;
            margin: 0;
            padding: 20px;
        }

        iframe {
            border: none;
            width: 100%;
            height: 800px;
        }

        /* Opcional: Estilo para el botón de cierre de sesión */
        .logout-button {
            position: absolute;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            background-color: #e74c3c;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
    </style>
</head>

<body>
    <!-- Botón de cierre de sesión -->
    <button class="logout-button" onclick="window.location.href='logout.php'">Cerrar Sesión</button>

    <h1>Bienvenido al Dashboard</h1>
    <iframe src="http://<?php echo $_SERVER['SERVER_ADDR']; ?>:8050/"></iframe>
</body>

</html>