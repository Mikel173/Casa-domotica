<?php
// /php/login.php
session_start();
include_once 'conexion.php'; // Asegúrate de tener tu archivo de conexión PDO

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['correo']) && isset($_POST['password'])) {
        $correo = $_POST['correo'];
        $password = $_POST['password'];

        try {
            $stmt = $conexion->prepare("SELECT id_usuario, password FROM usuarios WHERE correo = ?");
            $stmt->execute([$correo]);
            $usuario = $stmt->fetch(PDO::FETCH_ASSOC);

            if ($usuario && password_verify($password, $usuario['password'])) {
                // Autenticación exitosa
                $_SESSION['usuario_id'] = $usuario['id_usuario'];
                header('Location: dashboard.php');
                exit();
            } else {
                $error = "Correo o contraseña incorrectos";
            }
        } catch (PDOException $e) {
            $error = "Error al iniciar sesión: " . $e->getMessage();
        }
    } else {
        $error = "Faltan datos en el formulario";
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
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
            background-color: #3498db;
            border: none;
            border-radius: 4px;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }
        .error {
            color: red;
        }
        .form-container p a {
            color: #3498db;
            text-decoration: none;
        }
        .form-container p a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>Iniciar Sesión</h2>
        <?php if (isset($error)): ?>
            <p class="error"><?php echo htmlspecialchars($error); ?></p>
        <?php endif; ?>
        <form method="POST" action="login.php">
            <label for="correo">Correo:</label>
            <input type="email" id="correo" name="correo" required>
            <label for="password">Contraseña:</label>
            <input type="password" id="password" name="password" required>
            <input type="submit" value="Iniciar Sesión">
        </form>
        <p>¿No tienes una cuenta? <a href="registro.php">Regístrate aquí</a>.</p>
    </div>
</body>
</html>
