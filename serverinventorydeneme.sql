-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: serverinventorydeneme
-- ------------------------------------------------------
-- Server version	9.7.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ 'a666716c-7a99-11f1-ad91-c01850ad9cf2:1-219';

--
-- Table structure for table `custom_columns`
--

DROP TABLE IF EXISTS `custom_columns`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `custom_columns` (
  `id` int NOT NULL AUTO_INCREMENT,
  `column_name` varchar(100) NOT NULL,
  `data_type` enum('TEXT','INTEGER','DECIMAL','DATE','BOOLEAN') DEFAULT NULL,
  `created_at` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `column_name_UNIQUE` (`column_name`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_columns`
--

LOCK TABLES `custom_columns` WRITE;
/*!40000 ALTER TABLE `custom_columns` DISABLE KEYS */;
INSERT INTO `custom_columns` VALUES (11,'Adet','INTEGER','2026-07-27');
/*!40000 ALTER TABLE `custom_columns` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `custom_values`
--

DROP TABLE IF EXISTS `custom_values`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `custom_values` (
  `id` int NOT NULL AUTO_INCREMENT,
  `server_id` int NOT NULL,
  `column_id` int NOT NULL,
  `value` text,
  PRIMARY KEY (`id`),
  KEY `server_id` (`server_id`),
  KEY `column_id` (`column_id`),
  CONSTRAINT `custom_values_ibfk_1` FOREIGN KEY (`server_id`) REFERENCES `servers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `custom_values_ibfk_2` FOREIGN KEY (`column_id`) REFERENCES `custom_columns` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_values`
--

LOCK TABLES `custom_values` WRITE;
/*!40000 ALTER TABLE `custom_values` DISABLE KEYS */;
INSERT INTO `custom_values` VALUES (19,13,11,'12'),(21,12,11,'12'),(25,14,11,'12');
/*!40000 ALTER TABLE `custom_values` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `os_types`
--

DROP TABLE IF EXISTS `os_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `os_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `os_types`
--

LOCK TABLES `os_types` WRITE;
/*!40000 ALTER TABLE `os_types` DISABLE KEYS */;
INSERT INTO `os_types` VALUES (5,'Beykoz'),(4,'denemesistem'),(2,'Linux'),(3,'Özel'),(1,'Windows');
/*!40000 ALTER TABLE `os_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `servers`
--

DROP TABLE IF EXISTS `servers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `servers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `disk_gb` decimal(10,2) NOT NULL,
  `ram_g` int NOT NULL,
  `core_amount` int NOT NULL,
  `os_type_id` int NOT NULL,
  `ip_address` varchar(255) DEFAULT NULL,
  `usage_project` varchar(255) DEFAULT NULL,
  `created_at` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `os_type_id` (`os_type_id`),
  CONSTRAINT `servers_ibfk_1` FOREIGN KEY (`os_type_id`) REFERENCES `os_types` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servers`
--

LOCK TABLES `servers` WRITE;
/*!40000 ALTER TABLE `servers` DISABLE KEYS */;
INSERT INTO `servers` VALUES (2,'DenemeSunucu',125.00,8,12,1,'12.12.12.12','',NULL),(3,'DenemeSunucu2',2048.00,4,4,2,'01.01.01.01','2134',NULL),(4,'Sunucu adını da uzatsam tablo nolacak',12.25,12,12,2,'12','',NULL),(5,'DenemeSunucu3',12288.00,12,8,1,'123122','KaydetDeneme',NULL),(7,'ab',123.00,12,13,2,'13','','2026-07-21'),(8,'HelinErol',3276.80,24,16,1,'102.192.01.01','Helo','2026-07-21'),(9,'ÖzelAlanlarDeneme',12.00,12,1,3,'123122','windows',NULL),(10,'YeniSütunDeneme',12.00,12,16,3,'1.1.1.1','Özel alanlara değer geliyor mu','2026-07-23'),(12,'kaptanoğlu',12544.00,16,8,5,'1.1.1.1','İlayda çok tatlı bir kız *2','2026-07-23'),(13,'DenemeSunucu',12.00,8,12,5,'123122','mrhaba','2026-07-27'),(14,'admindeneme',810.00,9,6,2,'12.01','admindeneme','2026-07-29'),(15,'admindeneme2',5120.00,12,7,1,'6','',NULL),(16,'ingdeneme',1.00,1,1,4,'1','',NULL);
/*!40000 ALTER TABLE `servers` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-30  8:25:10
