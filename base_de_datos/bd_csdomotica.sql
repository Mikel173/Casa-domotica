-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 09-12-2024 a las 21:17:53
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `bd_csdomotica`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `datos_dispositivos`
--

CREATE TABLE `datos_dispositivos` (
  `id_dato` int(11) NOT NULL,
  `dispositivo_id` int(11) NOT NULL,
  `tipo_dispositivo` enum('sensor','actuador') NOT NULL,
  `valor` varchar(50) NOT NULL,
  `fecha_hora` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuario_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `dispositivos`
--

CREATE TABLE `dispositivos` (
  `id_dispositivo` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `tipo` enum('sensor','servo','led','actuador') NOT NULL,
  `ubicacion` varchar(60) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL,
  `nombre` varchar(60) NOT NULL,
  `correo` varchar(60) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuario`, `nombre`, `correo`, `password`) VALUES
(1, 'Eduardo', 'eduardoapaza406@gmail.com', '$2y$10$CwlOfmm/zTqyrlO8vIAxxeN0r1kq5H8xbL62gtVjWVsTFbejVr6wm'),
(2, 'Santiago', 'Santiagos@gmail.com', '$2y$10$mMBjBU4ilvgfRIgZQpeD9OWV9hnT7.1VAMCOBl4JJx67UnGrJXQka'),
(3, 'Mike', 'Mike173lal@gmail.com', '$2b$12$49tBdqvU56krxFpn877g0.tFZvXBTk97hNRjFgW1ufgtCYjCW3Rvq');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `datos_dispositivos`
--
ALTER TABLE `datos_dispositivos`
  ADD PRIMARY KEY (`id_dato`),
  ADD KEY `dispositivo_id` (`dispositivo_id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `dispositivos`
--
ALTER TABLE `dispositivos`
  ADD PRIMARY KEY (`id_dispositivo`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `correo` (`correo`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `datos_dispositivos`
--
ALTER TABLE `datos_dispositivos`
  MODIFY `id_dato` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `dispositivos`
--
ALTER TABLE `dispositivos`
  MODIFY `id_dispositivo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `datos_dispositivos`
--
ALTER TABLE `datos_dispositivos`
  ADD CONSTRAINT `datos_dispositivos_ibfk_1` FOREIGN KEY (`dispositivo_id`) REFERENCES `dispositivos` (`id_dispositivo`),
  ADD CONSTRAINT `datos_dispositivos_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
