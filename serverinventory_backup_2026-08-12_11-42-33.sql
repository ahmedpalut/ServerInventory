-- MySQL dump 10.13  Distrib 9.7.1, for Win64 (x86_64)
--
-- Host: localhost    Database: serverinventory
-- ------------------------------------------------------
-- Server version	9.7.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `clients`
--

DROP TABLE IF EXISTS `clients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clients` (
  `id` int NOT NULL AUTO_INCREMENT,
  `hostname` varchar(255) COLLATE utf8mb4_turkish_ci NOT NULL,
  `ip_address` varchar(45) COLLATE utf8mb4_turkish_ci DEFAULT NULL,
  `username` varchar(255) COLLATE utf8mb4_turkish_ci DEFAULT NULL,
  `os_name` varchar(100) COLLATE utf8mb4_turkish_ci DEFAULT NULL,
  `status` enum('online','offline') COLLATE utf8mb4_turkish_ci DEFAULT 'offline',
  `site_status` enum('active','inactive') COLLATE utf8mb4_turkish_ci DEFAULT 'inactive',
  `last_seen` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clients`
--

LOCK TABLES `clients` WRITE;
/*!40000 ALTER TABLE `clients` DISABLE KEYS */;
/*!40000 ALTER TABLE `clients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `custom_columns`
--

DROP TABLE IF EXISTS `custom_columns`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `custom_columns` (
  `id` int NOT NULL AUTO_INCREMENT,
  `column_name` varchar(100) COLLATE utf8mb4_turkish_ci NOT NULL,
  `data_type` enum('TEXT','INTEGER','DECIMAL','DATE','BOOLEAN') COLLATE utf8mb4_turkish_ci DEFAULT NULL,
  `created_at` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `column_name` (`column_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_columns`
--

LOCK TABLES `custom_columns` WRITE;
/*!40000 ALTER TABLE `custom_columns` DISABLE KEYS */;
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
  `value` text COLLATE utf8mb4_turkish_ci,
  PRIMARY KEY (`id`),
  KEY `server_id` (`server_id`),
  KEY `column_id` (`column_id`),
  CONSTRAINT `custom_values_ibfk_1` FOREIGN KEY (`server_id`) REFERENCES `servers` (`id`),
  CONSTRAINT `custom_values_ibfk_2` FOREIGN KEY (`column_id`) REFERENCES `custom_columns` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_values`
--

LOCK TABLES `custom_values` WRITE;
/*!40000 ALTER TABLE `custom_values` DISABLE KEYS */;
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
  `name` varchar(100) COLLATE utf8mb4_turkish_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `os_types`
--

LOCK TABLES `os_types` WRITE;
/*!40000 ALTER TABLE `os_types` DISABLE KEYS */;
INSERT INTO `os_types` VALUES (22,'CentOS 7 (64-bit)'),(23,'Microsoft Windows 10 (64-bit)'),(20,'Microsoft Windows Server 2012 (64-bit)'),(7,'Microsoft Windows Server 2016 or later (64-bit)'),(8,'Microsoft Windows Server 2022 (64-bit)'),(21,'Microsoft Windows Server 2025 (64-bit)'),(5,'Oracle Linux 7 (64-bit)'),(17,'Oracle Linux 8 (64-bit)'),(19,'Other 3.x or later Linux (64-bit)'),(6,'Other Linux (64-bit)'),(3,'Red Hat Enterprise Linux 6 (64-bit)'),(2,'Red Hat Enterprise Linux 7 (64-bit)'),(4,'Red Hat Enterprise Linux 8 (64-bit)'),(18,'Red Hat Enterprise Linux 9 (64-bit)'),(1,'Ubuntu Linux (64-bit)');
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
  `name` varchar(100) COLLATE utf8mb4_turkish_ci NOT NULL,
  `disk_gb` decimal(10,2) NOT NULL,
  `ram_g` int NOT NULL,
  `core_amount` int NOT NULL,
  `os_type_id` int NOT NULL,
  `ip_address` varchar(255) COLLATE utf8mb4_turkish_ci DEFAULT NULL,
  `usage_project` varchar(255) COLLATE utf8mb4_turkish_ci DEFAULT NULL,
  `created_at` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `os_type_id` (`os_type_id`),
  CONSTRAINT `servers_ibfk_1` FOREIGN KEY (`os_type_id`) REFERENCES `os_types` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=193 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servers`
--

LOCK TABLES `servers` WRITE;
/*!40000 ALTER TABLE `servers` DISABLE KEYS */;
INSERT INTO `servers` VALUES (1,'SAW34CRINSE01',352.14,32,32,7,'10.234.82.131','UAT Test','2026-05-12'),(2,'SDW34CRPREUW01',316.11,16,16,7,'10.234.82.36','Preuw','2026-05-12'),(3,'SDW34CRSRV01',280.11,20,16,7,'10.234.82.53','Jira&Confluence&SQL Test SQL 2016','2026-05-12'),(4,'SDW34CRWSUR11',316.10,16,8,7,'10.234.82.87','Dev Server','2026-05-12'),(5,'SDW34CRWSUR12',326.11,16,16,7,'10.234.82.77','Dev Server','2026-05-12'),(6,'SDW34D2B2BDEV02',346.12,16,16,7,'10.234.81.5','Portal GFORCE Dev','2026-05-12'),(7,'SDW34D2ISUR01',358.11,8,16,7,'10.234.81.16','INSURE-E Dev','2026-05-12'),(8,'SDW34D2UNQ01',128.09,8,8,7,'10.234.81.7','Emakin Test','2026-05-12'),(9,'SDW34D2UNQ02',128.09,8,8,7,'10.234.81.8','Emakin Dev','2026-05-12'),(10,'SDW34D2UNQ03',282.11,32,16,7,'10.234.80.12','Emakin Prod','2026-05-22'),(11,'SDW34D2UNQ04',136.10,16,8,7,'10.234.80.13','Emakin Prod','2026-05-22'),(12,'SDW34D3WSUR05',348.14,48,32,7,'10.234.82.88','Hasar Projesi Dev','2026-05-12'),(13,'SDWD2HRMS01',168.11,8,16,7,'10.234.81.19','INSURE-E Dev','2026-05-12'),(14,'SP34CRMEAPP',688.09,8,4,7,'10.234.82.80','Mcafee ePO 5.9.1','2026-05-12'),(15,'SPW06CRBDC01',188.09,8,4,8,'10.234.82.5','GIG BDC','2026-05-12'),(16,'SPW06CRPDC01',168.09,8,4,8,'10.234.82.4','GIG PDC','2026-05-22'),(17,'SPW06CRWSUR06',106.11,16,16,8,'10.234.82.42','Boş 2025','2026-05-12'),(18,'SPW06CRWSUR07',554.14,64,32,7,'10.234.82.82','Boş 2025','2026-05-12'),(19,'SPW06D1DC01',138.09,8,4,8,'10.234.80.4','DMZ PDC','2026-05-22'),(20,'SPW06D1DC02',138.09,8,4,8,'10.234.80.5','DMZ BDC','2026-05-12'),(21,'SPW34CRAPP02',832.15,32,32,7,'10.234.82.17','Jira&Confluence&SQL Prod SQL 2016','2026-05-22'),(22,'SPW34CRAPP03',8673.28,32,16,7,'10.234.82.18','Genel SQL Server 2016','2026-05-22'),(23,'SPW34CRAPPT01',316.11,16,16,7,'10.234.82.19','Oracle 19c Upgrade','2026-05-22'),(24,'SPW34CRB2BD01',7270.40,64,16,7,'10.234.82.75','Portal GFORCE DB SQL 2016','2026-05-22'),(25,'SPW34CRBFSRV01',582.10,12,8,20,'10.234.82.40','Bigfix SQL Server','2026-05-22'),(26,'SPW34CRBTOB01',272.14,32,32,7,'10.234.82.46','BTOB Prod','2026-05-22'),(27,'SPW34CRBTOB02',316.11,16,16,7,'10.234.82.44','BTOB Insuree Prod','2026-05-22'),(28,'SPW34CRBTOB03',348.14,48,32,7,'10.234.82.43','BTOB Insuree Prod','2026-05-22'),(29,'SPW34CRCFN01',10629.12,32,4,7,'10.234.82.58','Filenet Prod App','2026-05-22'),(30,'SPW34CRCFNDB01',792.09,32,4,7,'10.234.82.59','Filenet Prod DB SQL 2016','2026-05-22'),(31,'SPW34CRCUID',244.09,4,4,20,'10.234.82.93','PaloAlto User Id','2026-05-22'),(32,'SPW34CRDELTADB',106.09,16,2,8,'10.234.82.37','Boş 2025','2026-05-12'),(33,'SPW34CREXCH01',5826.56,42,16,7,'10.234.82.7, 10.234.82.11','Exchange 2016','2026-05-22'),(34,'SPW34CREXCH02',9697.28,40,16,7,'10.234.82.8','Exchange 2016','2026-05-22'),(35,'SPW34CRFILE01',16445.44,8,8,7,'10.234.82.24','File Server','2026-05-12'),(36,'SPW34CRGCA01',84.08,4,2,7,'10.234.82.41','Certificate Authority','2026-05-12'),(37,'SPW34CRHRMS02',616.11,16,16,7,'10.234.82.28','Hermes GL','2026-05-22'),(38,'SPW34CRIFRSD01',1064.96,16,8,7,'10.234.82.105','IFRS Prod DB','2026-05-22'),(39,'SPW34CRIFRSE01',1095.68,96,16,7,'10.234.82.104','IFRS Prod Exec','2026-05-22'),(40,'SPW34CRIFRSW01',338.09,8,8,7,'10.234.82.103','IFRS Prod Web','2026-05-22'),(41,'SPW34CRIRISK01',376.10,16,8,7,'10.234.82.52','İnforisk','2026-05-12'),(42,'SPW34CRKEY01',224.08,4,2,7,'10.234.82.48','Primary Key Server','2026-05-22'),(43,'SPW34CRKMS01',266.10,16,8,7,'10.234.82.64','KMS & Second Key server','2026-05-12'),(44,'SPW34CRMADB01',1177.60,16,8,20,'10.234.82.26','Enterprise Vault SQL Server','2026-05-22'),(45,'SPW34CRMARC01',26050.56,32,12,20,'10.234.82.27','Enterprise Vault Application Server','2026-05-22'),(46,'SPW34CRMARC01_2',154.09,64,2,8,'10.234.82.13',NULL,'2026-05-12'),(47,'SPW34CRORMAN01',3061.76,16,16,7,'10.234.82.50','Rman DUMP','2026-05-22'),(48,'SPW34CRPOLDYDB',526.09,16,4,7,'10.234.82.51','Poldy SQL','2026-05-22'),(49,'SPW34CRRM01',198.09,8,4,7,'10.234.82.31','Risk Merkezi','2026-05-12'),(50,'SPW34CRRPA01',282.11,32,16,7,'10.234.82.33','Epoch RPA Prod','2026-05-22'),(51,'SPW34CRSRVDESK',3010.56,32,8,7,'10.234.82.47','Servicedesk SQL2016 Ent','2026-05-22'),(52,'SPW34CRTOOL01',1075.20,80,32,7,'10.234.82.49','Tool Server','2026-05-22'),(53,'SPW34CRUI01',266.10,16,8,7,'10.234.82.95','UIPath','2026-05-12'),(54,'SPW34CRWSUR01',1228.80,64,32,7,'10.234.82.20','Winsure','2026-05-22'),(55,'SPW34CRWSUR02',404.15,64,32,7,'10.234.82.21','Winsure','2026-05-22'),(56,'SPW34CRWSUR03',804.16,64,32,7,'10.234.82.22','Winsure','2026-05-22'),(57,'SPW34CRWSUR04',954.16,64,32,7,'10.234.82.23','Winsure','2026-05-22'),(58,'SPW34CRWSUR05',559.15,64,32,7,'10.234.82.45','Winsure Consolidation','2026-05-22'),(59,'SPW34CSAPBO',506.10,96,8,7,'10.234.82.68','SAP BO Prod','2026-05-22'),(60,'SPW34CSAPETL',2539.52,64,16,7,'10.234.82.66','SAP ETL Prod','2026-05-22'),(61,'SPW34CWSUS',516.09,16,4,7,'10.234.82.223','Wsus','2026-05-12'),(62,'SPW34D1B2BP01',936.11,16,16,7,'10.234.80.30','Portal GFORCE','2026-05-22'),(63,'SPW34D1B2BP02',346.13,16,16,7,'10.234.80.29','Portal Prod Node2','2026-05-22'),(64,'SPW34D1BFBRKR',104.08,4,2,20,'10.234.80.27','Bigfix Broker','2026-05-12'),(65,'SPW34D1FTP01',2867.20,12,2,7,'10.234.80.6','Cerberus FTP Server 11.0.4','2026-05-12'),(66,'SPW34D1GIGIT01',266.10,16,8,7,'10.234.80.71','GIGIT','2026-05-22'),(67,'SPW34D1GW01',842.11,32,16,7,'10.234.81.6','Record Server','2026-05-22'),(68,'SPW34D1INET01',308.10,8,8,7,'10.234.80.21','INET','2026-05-22'),(69,'SPW34D1INET02',526.13,16,24,7,'10.234.80.22','Travel BTOB','2026-05-22'),(70,'SPW34D1INETDB01',3758.08,16,16,7,'10.234.80.23','INET DB SQL 2016','2026-05-22'),(71,'SPW34D1INS01',424.14,24,32,7,'10.234.80.60','Insuree 1','2026-05-22'),(72,'SPW34D1INS02',454.14,24,32,7,'10.234.80.61','Insuree 2','2026-05-22'),(73,'SPW34D1INS03',404.14,24,32,7,'10.234.80.62','Insuree 3','2026-05-22'),(74,'SPW34D1INS04',424.15,24,32,7,'10.234.80.63','Insuree 4','2026-05-22'),(75,'SPW34D1INS05',424.14,24,32,7,'10.234.80.64','Insuree 5','2026-05-22'),(76,'SPW34D1INS06',424.14,24,32,7,'10.234.80.65','Insuree 6','2026-05-22'),(77,'SPW34D1INS07',282.11,32,16,21,'10.234.80.66','Insuree 7','2026-05-22'),(78,'SPW34D1INS08',282.11,32,16,21,'10.234.80.68','Insuree 8','2026-05-22'),(79,'SPW34D1INS09',424.14,24,32,7,'10.234.80.58','Insuree 9','2026-05-22'),(80,'SPW34D1INS10',424.14,24,32,7,'10.234.80.59','Insuree 10','2026-05-22'),(81,'SPW34D1SMB01',96.11,16,16,7,'10.234.80.35','SBM','2026-05-22'),(82,'SPW34D1WEBAP01',216.10,16,8,20,'10.234.80.51','Web Servis Prod','2026-05-22'),(83,'SPW34D1WEBAP02',191.10,16,8,20,'10.234.80.52','Web Servis Prod','2026-05-22'),(84,'SPW34D1WEBAP03',266.11,16,16,8,'10.234.80.16','New Web application','2026-05-22'),(85,'SPW34D1WEBAP04',266.11,16,16,8,'10.234.80.17','New Web application','2026-05-22'),(86,'SPW34D2AI01',1024.00,4,12,7,'10.234.81.15','McKinsey','2026-05-12'),(87,'SPW34D2PERT01',258.09,8,8,7,'10.234.81.21','Cesar Pert','2026-05-22'),(88,'SPW34D2WEB02',168.09,8,8,7,'10.234.81.13','Yeni Web Server Gulfsigorta.com.tr','2026-05-22'),(89,'SPW34D2WEB03',168.09,8,8,7,'10.234.81.23','IFRS Test Web','2026-05-12'),(90,'SPW34D3IFRSD01',1044.48,16,16,7,'10.234.81.103','IFRS Test DB','2026-05-12'),(91,'SPW34D3IFRSE01',208.09,8,8,7,'10.234.81.102','IFRS Test Exec','2026-05-12'),(92,'SPW34D3IFRSW01',358.09,8,8,7,'10.234.81.101','IFRS Test Web','2026-05-12'),(93,'SPW34DMZDNS',124.08,4,2,7,'10.234.81.9','DNS Server','2026-05-12'),(94,'SPWD1LBLC01',236.10,16,8,7,'10.234.80.232','Load Balancer','2026-05-12'),(95,'SPWD1LBLC02',436.10,16,8,7,'10.234.80.31','Load Balancer 2','2026-05-22'),(96,'ST34CRPREP01',266.11,16,16,20,'10.234.82.140','Preprod','2026-05-12'),(97,'STW06D1UNIQ01',136.11,16,16,8,'10.234.80.19','Stream new Test','2026-05-12'),(98,'STW32D1INET01',2314.24,8,8,7,'10.234.80.24','Portal GFORCE Test DB','2026-05-12'),(99,'STW32D1INET02',306.08,6,2,7,'10.234.80.20','INET Test','2026-05-22'),(100,'STW34CR19C01',504.15,64,32,7,'10.234.82.30','Epoch RPA Prod','2026-05-22'),(101,'STW34CRCFN01',2846.72,16,2,7,'10.234.82.56','Filenet Test App','2026-05-12'),(102,'STW34CRCFNDB01',216.08,16,2,7,'10.234.82.57','Filenet Test DB SQL 2016','2026-05-12'),(103,'STW34CRINS01',516.11,16,16,7,'10.234.82.32','Insree Test','2026-05-12'),(104,'STW34CRKRNL44',397.12,32,16,7,'10.234.82.25','Hermes - RPA Prod','2026-05-22'),(105,'STW34CRPOLDYT',526.09,16,4,7,'10.234.82.55','Poldy Test','2026-05-12'),(106,'STW34CRWSUR02',472.11,32,16,7,'10.234.82.138','Hasar Projesi Dev','2026-05-12'),(107,'STW34CSAPBO',752.09,32,4,7,'10.234.82.67','SAP BO Test (Akşam 17:00)','2026-05-22'),(108,'STW34CSAPETL',582.09,32,4,7,'10.234.82.65','SAP ETL Test (Akşam 17:00)','2026-05-22'),(109,'STW34D1WSVC11',128.09,8,8,20,'10.234.80.26','Web Servis Test','2026-05-12'),(110,'STW34D2WEBAP01',258.11,8,16,7,'10.234.81.17','INSURE-E Dev','2026-05-12'),(111,'STW34D2WEBAP02',208.11,8,16,7,'10.234.81.18','INSURE-E Dev','2026-05-12'),(112,'STW34D2WEBAP03',148.09,8,8,7,'10.234.81.20','INSURE-E Dev','2026-05-12'),(113,'STW34D3WSUR02',266.09,16,4,7,'10.234.82.91','Dev Server','2026-05-12'),(114,'Glfveeam',1034.24,32,16,8,'10.206.95.15, 10.206.97.15','Veeam',NULL),(115,'glfveeamone',512.11,12,16,8,'10.206.95.20','VeeamOne',NULL),(116,'Glfveeamprx01',516.12,16,12,8,'10.206.95.18, 10.206.97.18','Veeam Proxy',NULL),(117,'Glfveeamprx02',516.12,16,12,8,'10.206.95.16, 10.206.97.16','Veeam Proxy',NULL),(118,'Glfveeamprx03',516.11,16,8,8,'10.206.95.17, 10.206.97.17','Veeam Proxy',NULL),(119,'sdxepcgw02',116.09,16,4,8,'10.234.82.100',NULL,NULL),(120,'SDXTERM_oprsyn',84.08,4,2,8,'10.206.92.250, 10.206.91.8',NULL,NULL),(121,'SNSAAPPP06',316.09,16,4,4,'10.234.82.182','uCMDB Server',NULL),(122,'SPGULFSFTP',208.08,8,2,17,'10.206.91.122',NULL,NULL),(123,'SPHMC01',516.09,16,4,6,NULL,'HMC',NULL),(124,'SPHMC02',516.09,16,4,6,NULL,'HMC',NULL),(125,'SPL06D1RPTS01',308.09,8,8,1,'10.234.80.45','Web Repo',NULL),(126,'SPL34CRISE01',600.11,32,16,4,'10.234.82.162','ISE Node1',NULL),(127,'SPL34CRISE02',600.11,32,16,4,'10.234.82.163','ISE Node2',NULL),(128,'SPL34CRORAMON',416.09,16,4,5,'10.234.82.61','Oracle Monitoring',NULL),(129,'SPL34CRPAEXP',108.09,8,4,1,'10.234.82.94',NULL,NULL),(130,'SPL34CRQRD01',5171.20,48,16,3,'10.234.82.9','Qradar',NULL),(131,'SPL34CSAPIQ_OLD',8448.00,128,8,2,'10.234.82.70','SAPIQ Old Prod',NULL),(132,'SPL34D1ATLS01',366.09,16,2,1,'10.234.80.46','Atlas Global Tamoniki',NULL),(133,'SPL34D1ATLS02',366.08,16,2,1,'10.234.80.47','Atlas Global Tamoniki',NULL),(134,'SPL34D1REDS01',108.09,8,8,1,'10.234.80.49','Redis Slave',NULL),(135,'SPL34D1TRVL01',266.10,16,8,1,'10.234.80.18','Atlas Global Tamoniki Yeni',NULL),(136,'SPL34D1TRVL02',266.10,16,8,1,'10.234.80.15','Atlas Global Tamoniki Yeni',NULL),(137,'SPL34D1VKONF',168.09,8,8,1,'10.234.80.70','Jitsi',NULL),(138,'SPL34D1WEB11',116.09,16,4,1,'10.234.80.48','Redis Master',NULL),(139,'SPL34D2OTOANALIZ01',1126.40,32,6,2,'10.234.81.2','Otoanaliz App',NULL),(140,'SPL34D2OTOANALIZ03',532.10,32,6,2,'10.234.81.3','Otoanaliz DB',NULL),(141,'SPL34D2OTOANALIZTEST01',508.09,8,6,2,'10.234.81.4','Otoanaliz Test',NULL),(142,'SPL34D2USTT01',696.12,48,16,1,'10.234.81.11','Urban Stat',NULL),(143,'SPL34D2USTT02',698.12,48,16,1,'10.234.81.12','Urban Stat',NULL),(144,'SPL34ZABBIX01',316.09,16,4,18,'10.234.82.150','ZABBIX Monitoring',NULL),(145,'SPL34ZABBIX02',316.09,16,4,18,'10.234.82.151','ZABBIX Monitoring',NULL),(146,'SPW06CRVC01',726.55,25,4,19,'10.206.92.10, 10.206.99.10','Vcenter',NULL),(147,'SPW34CRAPPT01',316.11,16,16,7,'10.234.82.19','Oracle 19c Upgrade',NULL),(148,'SPW34CRMON01',582.10,32,8,7,'10.234.82.250','Monitoring',NULL),(149,'SPW34CRMON02',582.10,32,8,7,'10.234.82.251','Monitoring',NULL),(150,'SPW34CRPRTS01',632.10,32,4,7,'10.234.82.71','PartnerSoft',NULL),(151,'SPW34CRPRTS02',816.10,16,4,7,'10.234.82.72','PartnerSoft',NULL),(152,'SPW34CRPRTS03',216.10,16,4,7,'10.234.82.73','PartnerSoft',NULL),(153,'SPW34CRPRTS04',216.11,16,4,7,'10.234.82.74','PartnerSoft',NULL),(154,'STL34CSAPIQ',8847.36,128,8,2,'10.234.82.69','SAP IQ Test',NULL),(155,'STLD1LBLC02',193.09,8,2,22,'10.234.80.32','Grafana Monitoring',NULL),(156,'triscans020aigrm',188.08,8,2,2,'10.234.82.233','Oracle Scan',NULL),(157,'trispans010aigrm',488.09,8,2,2,'10.234.82.232','Oracle Scan',NULL),(158,'WPW34CRRESQ02n',1116.16,96,32,23,'10.234.82.62','ResQ new',NULL),(159,'WPW34CRSAS01-1',1177.60,16,16,23,'10.234.82.16','SAS-1',NULL),(160,'WPW34CRSAS02-1',3338.24,16,16,23,'10.234.82.15','SAS-2',NULL),(161,'WPW34CRSAS03-1',1177.60,16,16,23,'10.234.82.14','SAS-3',NULL),(162,'WPW34CRSAS04-1',1177.60,16,16,23,'10.234.82.12','SAS-4',NULL);
/*!40000 ALTER TABLE `servers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'serverinventory'
--

--
-- Dumping routines for database 'serverinventory'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-12 11:42:33
