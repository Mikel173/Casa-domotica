<?php
// /php/registro.php
include_once 'conexion.php';

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['nombre']) && isset($_POST['correo']) && isset($_POST['password'])) {
        $nombre = $_POST['nombre'];
        $correo = $_POST['correo'];
        $password = password_hash($_POST['password'], PASSWORD_BCRYPT);

        try {
            $stmt = $conexion->prepare("INSERT INTO usuarios (nombre, correo, password) VALUES (?, ?, ?)");
            $stmt->execute([$nombre, $correo, $password]);
            $mensaje = "Usuario registrado correctamente";
        } catch (PDOException $e) {
            // Manejar errores de duplicación de correo electrónico u otros
            if ($e->getCode() == 23000) { // Código de error para violación de integridad
                $error = "El correo electrónico ya está registrado.";
            } else {
                $error = "Error al registrar usuario: " . $e->getMessage();
            }
        }
    } else {
        $error = "Faltan datos en el formulario";
    }
}
?>
<!DOCTYPE html>
<html>

<head>
    <title>Registro</title>
    <style>
        /* Estilos básicos para el formulario */
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f2f5;
            padding: 50px;
        }

        .form-container {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            max-width: 400px;
            margin: auto;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }

        input[type="text"],
        input[type="email"],
        input[type="password"] {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 4px;
        }

        input[type="submit"] {
            width: 100%;
            padding: 10px;
            background-color: #2ecc71;
            border: none;
            border-radius: 4px;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }

        .error {
            color: red;
        }

        .success {
            color: green;
        }

        /* Estilo para el enlace de inicio de sesión */
        .form-container p a {
            color: #2ecc71;
            text-decoration: none;
        }

        .form-container p a:hover {
            text-decoration: underline;
        }
    </style>
</head>

<body>
    <div class="form-container">
        <h2>Registro de Usuario</h2>
        <?php if (isset($error)): ?>
            <p class="error"><?php echo htmlspecialchars($error); ?></p>
        <?php endif; ?>
        <?php if (isset($mensaje)): ?>
            <p class="success"><?php echo htmlspecialchars($mensaje); ?></p>
        <?php endif; ?>
        <form method="POST" action="registro.php">
            <label for="nombre">Nombre:</label>
            <input type="text" id="nombre" name="nombre" required>

            <label for="correo">Correo:</label>
            <input type="email" id="correo" name="correo" required>

            <label for="password">Contraseña:</label>
            <input type="password" id="password" name="password" required>

            <input type="submit" value="Registrar">
        </form>
        <p>¿Ya tienes una cuenta? <a href="login.php">Inicia sesión aquí</a>.</p>
    </div>
</body>

</html>