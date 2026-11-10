-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 10-11-2026 a las 15:21:54
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `tiendita`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `compras`
--

CREATE TABLE `compras` (
  `id_compra` int(11) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `marca` varchar(255) NOT NULL,
  `modelo` varchar(255) NOT NULL,
  `presentacion` varchar(255) NOT NULL,
  `proveedor` varchar(255) NOT NULL,
  `unitario` decimal(10,2) NOT NULL DEFAULT 0.00,
  `stock` int(11) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `compras`
--

INSERT INTO `compras` (`id_compra`, `nombre`, `marca`, `modelo`, `presentacion`, `proveedor`, `unitario`, `stock`) VALUES
(1, 'Coca Cola', 'Coca Cola', 'Original', '600 ml', 'Coca Cola FEMSA', 18.00, 30),
(2, 'Pepsi', 'Pepsi', 'Original', '600 ml', 'PepsiCo', 16.00, 25),
(3, 'Agua natural', 'Bonafont', 'Natural', '1 litro', 'Danone', 14.00, 40),
(4, 'Jugo de naranja', 'Del Valle', 'Naranja', '500 ml', 'Coca Cola FEMSA', 12.00, 20),
(5, 'Leche entera', 'Lala', 'Entera', '1 litro', 'Grupo Lala', 27.00, 18),
(6, 'Leche deslactosada', 'Santa Clara', 'Deslactosada', '1 litro', 'Santa Clara', 30.00, 15),
(7, 'Pan de caja', 'Bimbo', 'Blanco', '680 g', 'Grupo Bimbo', 45.00, 12),
(8, 'Pan dulce', 'Bimbo', 'Nito', '62 g', 'Grupo Bimbo', 12.00, 24),
(9, 'Galletas', 'Gamesa', 'Emperador', '91 g', 'PepsiCo', 17.00, 20),
(10, 'Galletas saladas', 'Gamesa', 'Crackets', '135 g', 'PepsiCo', 16.00, 18),
(11, 'Papas fritas', 'Sabritas', 'Original', '45 g', 'Sabritas', 18.00, 22),
(12, 'Frituras', 'Barcel', 'Takis Fuego', '62 g', 'Barcel', 19.00, 16),
(13, 'Chocolate', 'Carlos V', 'Original', '18 g', 'Nestle', 10.00, 30),
(14, 'Chocolate en polvo', 'Nesquik', 'Original', '350 g', 'Nestle', 55.00, 8),
(15, 'Cereal', 'Kelloggs', 'Zucaritas', '300 g', 'Kelloggs', 48.00, 10),
(16, 'Arroz', 'Verde Valle', 'Blanco', '1 kg', 'Verde Valle', 28.00, 20),
(17, 'Frijol', 'Verde Valle', 'Negro', '1 kg', 'Verde Valle', 32.00, 18),
(18, 'Azucar', 'Zulka', 'Est?ndar', '1 kg', 'Zulka', 27.00, 25),
(19, 'Sal', 'La Fina', 'Yodatada', '1 kg', 'La Fina', 16.00, 20),
(20, 'Aceite vegetal', 'Nutrioli', 'Vegetal', '850 ml', 'Nutrioli', 38.00, 14),
(21, 'Harina de trigo', 'Tres Estrellas', 'Tradicional', '1 kg', 'Tres Estrellas', 24.00, 12),
(22, 'Harina para hot cakes', 'Gamesa', 'Tradicional', '500 g', 'PepsiCo', 32.00, 10),
(23, 'Sopa de pasta', 'La Moderna', 'Fideo', '200 g', 'La Moderna', 9.00, 40),
(24, 'Atun', 'Tuny', 'En agua', '140 g', 'Tuny', 19.00, 24),
(25, 'Sardinas', 'Ponto', 'En tomate', '425 g', 'Ponto', 32.00, 10),
(26, 'Mayonesa', 'McCormick', 'Tradicional', '390 g', 'McCormick', 48.00, 8),
(27, 'Catsup', 'Heinz', 'Tradicional', '397 g', 'Heinz', 35.00, 9),
(28, 'Cafe soluble', 'Nescafe', 'Clasico', '120 g', 'Nestle', 75.00, 10),
(29, 'Te de manzanilla', 'McCormick', 'Manzanilla', '25 sobres', 'McCormick', 32.00, 8),
(30, 'Detergente', 'Ariel', 'Polvo', '800 g', 'P&G', 42.00, 12),
(31, 'Suavizante', 'Suavitel', 'Fresca Primavera', '850 ml', 'P&G', 30.00, 10),
(32, 'Jabon de barra', 'Zote', 'Rosa', '200 g', 'La Corona', 16.00, 25),
(33, 'Jabon de tocador', 'Dove', 'Original', '90 g', 'Unilever', 20.00, 18),
(34, 'Shampoo', 'Sedal', 'Ceramidas', '340 ml', 'Unilever', 42.00, 8),
(35, 'Pasta dental', 'Colgate', 'Triple Accion', '100 ml', 'Colgate-Palmolive', 28.00, 15),
(36, 'Papel higienico', 'P?talo', 'Regular', '4 rollos', 'Essity', 32.00, 14),
(37, 'Servilletas', 'P?talo', 'Blancas', '250 piezas', 'Essity', 22.00, 12),
(38, 'Pasta dental', 'Oral-B', 'Pro Salud', '75 ml', 'P&G', 35.00, 10),
(39, 'Desodorante', 'Rexona', 'Invisible', '150 ml', 'Unilever', 45.00, 8),
(40, 'Pilas alcalinas', 'Duracell', 'AA', 'Paquete de 2', 'Duracell', 38.00, 12),
(41, 'Fosforos', 'La Central', 'Tradicional', 'Caja', 'La Central', 5.00, 30),
(42, 'Veladora', 'Aurrera', 'Blanca', 'Unidad', 'Proveedor local', 18.00, 15),
(43, 'Bolsa de basura', 'Reyma', 'Mediana', 'Paquete de 10', 'Reyma', 20.00, 12),
(44, 'Vasos desechables', 'Reyma', 'No. 8', 'Paquete de 25', 'Reyma', 18.00, 10),
(45, 'Agua mineral', 'Pe?afiel', 'Natural', '600 ml', 'Pe?afiel', 15.00, 18),
(46, 'Bebida deportiva', 'Gatorade', 'Naranja', '500 ml', 'PepsiCo', 22.00, 14),
(47, 'Yogur', 'Yoplait', 'Fresa', '125 g', 'Yoplait', 10.00, 20),
(48, 'Queso', 'NocheBuena', 'Panela', '400 g', 'Sigma Alimentos', 65.00, 6),
(49, 'Salchichas', 'Fud', 'Pavo', '500 g', 'Sigma Alimentos', 52.00, 8),
(50, 'Tortillas de harina', 'Tia Rosa', 'Tradicional', '10 piezas', 'Grupo Bimbo', 28.00, 10);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ventas`
--

CREATE TABLE `ventas` (
  `id_venta` int(11) NOT NULL,
  `cliente_dni` varchar(255) NOT NULL,
  `producto_ref` varchar(255) NOT NULL,
  `cantidad` int(11) NOT NULL DEFAULT 1,
  `monto` decimal(10,2) NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `compras`
--
ALTER TABLE `compras`
  ADD PRIMARY KEY (`id_compra`);

--
-- Indices de la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD PRIMARY KEY (`id_venta`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `ventas`
--
ALTER TABLE `ventas`
  MODIFY `id_venta` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
