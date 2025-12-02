-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: chain_db
-- ------------------------------------------------------
-- Server version	8.0.39

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

--
-- Table structure for table `account`
--

DROP TABLE IF EXISTS `account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account` (
  `account_id` int NOT NULL AUTO_INCREMENT,
  `hunter_id` int NOT NULL,
  `balance` int DEFAULT '0',
  `total_income` int DEFAULT '0',
  `total_spent` int DEFAULT '0',
  `last_tx_type` enum('IN','OUT') DEFAULT NULL,
  `last_tx_amount` int DEFAULT NULL,
  `last_tx_desc` varchar(255) DEFAULT NULL,
  `history` text,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`account_id`),
  UNIQUE KEY `uk_account_hunter` (`hunter_id`),
  KEY `idx_account_balance` (`balance`),
  CONSTRAINT `fk_account_hunter` FOREIGN KEY (`hunter_id`) REFERENCES `human` (`hunter_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account`
--

LOCK TABLES `account` WRITE;
/*!40000 ALTER TABLE `account` DISABLE KEYS */;
INSERT INTO `account` VALUES (1,1,2700000,3000000,300000,'IN',250000,'전투 1- 악마벨리알(Belial)현상금 분배',NULL,'2025-12-01 23:54:17'),(2,2,2950000,3100000,150000,'IN',250000,'전투 1- 악마벨리알(Belial)현상금 분배',NULL,'2025-12-01 23:54:17'),(3,3,150000,300000,150000,'OUT',150000,'장비 구매',NULL,'2025-11-30 23:38:23'),(4,4,0,0,0,NULL,NULL,NULL,NULL,'2025-11-30 23:38:23'),(5,5,0,0,0,NULL,NULL,NULL,NULL,'2025-11-30 23:38:23'),(6,6,250000,250000,0,'IN',250000,'레비아탄 교전 보상 입금',NULL,'2025-11-30 23:38:23'),(7,7,0,0,0,NULL,NULL,NULL,NULL,'2025-11-30 23:38:23'),(8,8,300000,400000,100000,'IN',200000,'전투 5 보상 분배',NULL,'2025-12-01 23:17:01'),(9,9,0,0,0,NULL,NULL,NULL,NULL,'2025-11-30 23:38:23'),(10,10,0,0,0,NULL,NULL,NULL,NULL,'2025-11-30 23:38:23'),(11,11,0,0,0,NULL,NULL,NULL,NULL,'2025-12-01 22:21:43'),(12,12,0,0,0,NULL,NULL,NULL,NULL,'2025-12-01 23:06:45'),(13,13,0,0,0,NULL,NULL,NULL,NULL,'2025-12-01 23:06:53'),(14,14,0,0,0,NULL,NULL,NULL,NULL,'2025-12-01 23:06:58'),(15,15,0,0,0,NULL,NULL,NULL,NULL,'2025-12-01 23:15:55');
/*!40000 ALTER TABLE `account` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `battle`
--

DROP TABLE IF EXISTS `battle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `battle` (
  `battle_id` int NOT NULL AUTO_INCREMENT,
  `mission_id` int DEFAULT NULL,
  `demon_id` int NOT NULL,
  `started_at` datetime NOT NULL,
  `ended_at` datetime DEFAULT NULL,
  `location` varchar(150) NOT NULL,
  `outcome` enum('HUMAN_WIN','DEMON_WIN','DRAW','ESCAPE') NOT NULL,
  `civilian_killed` int DEFAULT '0',
  `civilian_injured` int DEFAULT '0',
  `notes` text,
  PRIMARY KEY (`battle_id`),
  KEY `idx_battle_mission` (`mission_id`),
  KEY `idx_battle_demon` (`demon_id`),
  KEY `idx_battle_outcome_started` (`outcome`,`started_at`),
  CONSTRAINT `fk_battle_demon` FOREIGN KEY (`demon_id`) REFERENCES `demon` (`demon_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_battle_mission` FOREIGN KEY (`mission_id`) REFERENCES `mission` (`mission_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `battle`
--

LOCK TABLES `battle` WRITE;
/*!40000 ALTER TABLE `battle` DISABLE KEYS */;
INSERT INTO `battle` VALUES (1,1,1,'2025-11-26 10:00:00','2025-11-26 10:30:00','시흥 중앙구역','HUMAN_WIN',3,10,'벨리알 제압 1차'),(2,1,1,'2025-11-26 11:10:00','2025-11-26 11:40:00','시흥 2지구','HUMAN_WIN',1,5,'벨리알 재등장'),(3,2,2,'2025-11-27 09:00:00',NULL,'서울 동부 지하철','DRAW',0,2,'장기전으로 전환'),(4,3,4,'2025-11-25 15:00:00','2025-11-25 16:20:00','인천항 부두','ESCAPE',4,7,'레비아탄 도주'),(5,4,3,'2025-10-22 14:00:00','2025-10-22 14:50:00','부산 남항','HUMAN_WIN',0,1,'말파스 토벌 완료');
/*!40000 ALTER TABLE `battle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bountyclaim`
--

DROP TABLE IF EXISTS `bountyclaim`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bountyclaim` (
  `claim_id` int NOT NULL AUTO_INCREMENT,
  `battle_id` int NOT NULL,
  `demon_id` int NOT NULL,
  `hunter_id` int NOT NULL,
  `amount` int NOT NULL,
  `claim_date` datetime NOT NULL,
  `notes` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`claim_id`),
  KEY `idx_claim_hunter` (`hunter_id`),
  KEY `idx_claim_battle` (`battle_id`),
  KEY `idx_claim_demon` (`demon_id`),
  CONSTRAINT `fk_claim_battle` FOREIGN KEY (`battle_id`) REFERENCES `battle` (`battle_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_claim_demon` FOREIGN KEY (`demon_id`) REFERENCES `demon` (`demon_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_claim_hunter` FOREIGN KEY (`hunter_id`) REFERENCES `human` (`hunter_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bountyclaim`
--

LOCK TABLES `bountyclaim` WRITE;
/*!40000 ALTER TABLE `bountyclaim` DISABLE KEYS */;
INSERT INTO `bountyclaim` VALUES (1,1,1,1,500000,'2025-11-26 12:00:00','벨리알 제압 보상'),(2,2,1,2,300000,'2025-11-26 12:30:00','벨리알 재교전 보상'),(3,3,2,3,150000,'2025-11-27 10:00:00','아스타로트 교전 보상'),(4,4,4,6,250000,'2025-11-25 17:00:00','레비아탄 교전 보상'),(5,5,3,8,100000,'2025-10-22 15:30:00','말파스 토벌 보상');
/*!40000 ALTER TABLE `bountyclaim` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contract`
--

DROP TABLE IF EXISTS `contract`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contract` (
  `contract_id` int NOT NULL AUTO_INCREMENT,
  `hunter_id` int NOT NULL,
  `demon_id` int NOT NULL,
  `cost_type` enum('LIFE','MEMORY','EMOTION','OTHER') NOT NULL,
  `cost_desc` varchar(255) NOT NULL,
  `status` enum('ACTIVE','BROKEN','EXPIRED') DEFAULT 'ACTIVE',
  PRIMARY KEY (`contract_id`),
  KEY `idx_contract_hunter` (`hunter_id`),
  KEY `idx_contract_demon` (`demon_id`),
  CONSTRAINT `fk_contract_demon` FOREIGN KEY (`demon_id`) REFERENCES `demon` (`demon_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_contract_hunter` FOREIGN KEY (`hunter_id`) REFERENCES `human` (`hunter_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contract`
--

LOCK TABLES `contract` WRITE;
/*!40000 ALTER TABLE `contract` DISABLE KEYS */;
INSERT INTO `contract` VALUES (1,1,1,'LIFE','수명의 3년을 지불','ACTIVE'),(2,3,2,'MEMORY','10년치 기억 봉인','ACTIVE'),(3,4,7,'EMOTION','감정 일부 상실','BROKEN'),(4,6,3,'OTHER','혈액 채취 제공','ACTIVE'),(5,9,4,'LIFE','50% 생명력 지불','EXPIRED');
/*!40000 ALTER TABLE `contract` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `demon`
--

DROP TABLE IF EXISTS `demon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `demon` (
  `demon_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `grade` enum('C','B','A','S','SS') DEFAULT NULL,
  `bounty` int NOT NULL,
  `base_civilian_killed` int NOT NULL DEFAULT '0',
  `base_civilian_injured` int NOT NULL DEFAULT '0',
  `civilian_killed_total` int DEFAULT '0',
  `civilian_injured_total` int DEFAULT '0',
  `base_bounty` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`demon_id`),
  KEY `idx_demon_grade` (`grade`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `demon`
--

LOCK TABLES `demon` WRITE;
/*!40000 ALTER TABLE `demon` DISABLE KEYS */;
INSERT INTO `demon` VALUES (1,'벨리알(Belial)','B',500000,32,87,4,15,0),(2,'아스타로트(Astaroth)','C',200000,22,54,0,2,0),(3,'말파스(Malphas)','C',200000,10,41,0,1,0),(4,'레비아탄(Leviathan)','B',500000,45,63,4,7,0),(5,'바포메트(Baphomet)','C',200000,7,26,0,0,0),(6,'발록(Balrog)','C',200000,18,29,0,0,0),(7,'그림리퍼(Grim Reaper)','C',200000,2,17,0,0,0),(8,'할리퀸(Harlequin)','C',200000,1,8,0,0,0),(9,'데스하운드(Death Hound)','C',200000,3,9,0,0,0),(10,'샤덴(Shadowen)','C',200000,12,22,0,0,0);
/*!40000 ALTER TABLE `demon` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `distribution`
--

DROP TABLE IF EXISTS `distribution`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `distribution` (
  `battle_id` int NOT NULL,
  `hunter_id` int NOT NULL,
  `share_amount` int NOT NULL,
  `is_dead_at_battle` tinyint(1) NOT NULL DEFAULT '0',
  `distributed_at` datetime DEFAULT NULL,
  `status` enum('PENDING','DONE') DEFAULT 'PENDING',
  PRIMARY KEY (`battle_id`,`hunter_id`),
  KEY `idx_dist_hunter` (`hunter_id`),
  KEY `idx_dist_status` (`status`),
  CONSTRAINT `fk_dist_battle` FOREIGN KEY (`battle_id`) REFERENCES `battle` (`battle_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_dist_hunter` FOREIGN KEY (`hunter_id`) REFERENCES `human` (`hunter_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `distribution`
--

LOCK TABLES `distribution` WRITE;
/*!40000 ALTER TABLE `distribution` DISABLE KEYS */;
INSERT INTO `distribution` VALUES (1,1,250000,0,'2025-12-01 23:54:17','DONE'),(1,2,250000,0,'2025-12-01 23:54:17','DONE'),(5,8,200000,0,'2025-12-01 23:17:01','DONE');
/*!40000 ALTER TABLE `distribution` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `human`
--

DROP TABLE IF EXISTS `human`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `human` (
  `hunter_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `status` enum('ACTIVE','INACTIVE','RETIRED','DEAD') DEFAULT 'ACTIVE',
  `team_id` int DEFAULT NULL,
  PRIMARY KEY (`hunter_id`),
  KEY `idx_human_team_status` (`team_id`,`status`),
  CONSTRAINT `fk_human_team` FOREIGN KEY (`team_id`) REFERENCES `team` (`team_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `human`
--

LOCK TABLES `human` WRITE;
/*!40000 ALTER TABLE `human` DISABLE KEYS */;
INSERT INTO `human` VALUES (1,'덴지','ACTIVE',1),(2,'파워','ACTIVE',1),(3,'아키','ACTIVE',2),(4,'키시베','ACTIVE',2),(5,'히메노','INACTIVE',3),(6,'엔젤 헌터','ACTIVE',3),(7,'쿠로사키','RETIRED',4),(8,'류지','ACTIVE',4),(9,'마키마','ACTIVE',5),(10,'하야카와 소년','DEAD',1),(11,'대빵 헌터','ACTIVE',NULL),(12,'애니팡','ACTIVE',4),(13,'애니팡','INACTIVE',4),(14,'애니팡','RETIRED',2),(15,'애니팡팡이','ACTIVE',1);
/*!40000 ALTER TABLE `human` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trigger_random_team` BEFORE INSERT ON `human` FOR EACH ROW BEGIN	-- 트리거 코드 작성
		-- 파이썬에서 team_id를 안보내거나 0으로 보낸 경우
		IF NEW.team_id IS NULL OR NEW.team_id = 0 THEN
        SET NEW.team_id = (
            SELECT t.team_id
            FROM team AS t
            ORDER BY RAND() -- 랜덤 함수
            LIMIT 1
        );
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `mission`
--

DROP TABLE IF EXISTS `mission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mission` (
  `mission_id` int NOT NULL AUTO_INCREMENT,
  `team_id` int NOT NULL,
  `objective` varchar(255) NOT NULL,
  `target_desc` varchar(255) NOT NULL,
  `status` enum('PLANNED','IN_PROGRESS','SUCCESS','FAIL') DEFAULT 'PLANNED',
  `created_at` date NOT NULL,
  `due_date` date NOT NULL,
  PRIMARY KEY (`mission_id`),
  KEY `idx_mission_team` (`team_id`),
  KEY `idx_mission_status` (`status`),
  KEY `idx_mission_duedate` (`due_date`),
  CONSTRAINT `fk_mission_team` FOREIGN KEY (`team_id`) REFERENCES `team` (`team_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mission`
--

LOCK TABLES `mission` WRITE;
/*!40000 ALTER TABLE `mission` DISABLE KEYS */;
INSERT INTO `mission` VALUES (1,1,'도심 SS급 악마 제압','벨리알(Belial) 포획/격퇴','SUCCESS','2025-11-20','2025-11-30'),(2,2,'A급 악마 추적','아스타로트(Astaroth) 활동 수색','PLANNED','2025-11-22','2025-12-10'),(3,3,'해안가 위협 악마 제거','레비아탄(Leviathan) 활동 억제','IN_PROGRESS','2025-11-15','2025-12-05'),(4,4,'저위험 악마 토벌','말파스, 데스하운드 토벌','SUCCESS','2025-10-20','2025-11-01'),(5,5,'특수 악마 조사 임무','그림리퍼 조사 및 자료 확보','PLANNED','2025-11-10','2025-12-20');
/*!40000 ALTER TABLE `mission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `missionassignment`
--

DROP TABLE IF EXISTS `missionassignment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `missionassignment` (
  `assignment_id` int NOT NULL AUTO_INCREMENT,
  `mission_id` int NOT NULL,
  `hunter_id` int NOT NULL,
  `assignment_status` enum('PLANNED','CONFIRMED','IN_PROGRESS','DONE','CANCELLED') DEFAULT 'PLANNED',
  `assigned_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`assignment_id`),
  UNIQUE KEY `uk_mission_hunter` (`mission_id`,`hunter_id`),
  KEY `idx_ma_hunter` (`hunter_id`),
  KEY `idx_ma_status` (`assignment_status`),
  CONSTRAINT `fk_ma_hunter` FOREIGN KEY (`hunter_id`) REFERENCES `human` (`hunter_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_ma_mission` FOREIGN KEY (`mission_id`) REFERENCES `mission` (`mission_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `missionassignment`
--

LOCK TABLES `missionassignment` WRITE;
/*!40000 ALTER TABLE `missionassignment` DISABLE KEYS */;
INSERT INTO `missionassignment` VALUES (1,1,1,'IN_PROGRESS','2025-11-30 23:38:23'),(2,1,2,'IN_PROGRESS','2025-11-30 23:38:23'),(3,1,3,'IN_PROGRESS','2025-11-30 23:38:23'),(4,2,3,'PLANNED','2025-11-30 23:38:23'),(5,2,4,'PLANNED','2025-11-30 23:38:23'),(6,3,5,'IN_PROGRESS','2025-11-30 23:38:23'),(7,3,6,'IN_PROGRESS','2025-11-30 23:38:23'),(8,4,7,'DONE','2025-11-30 23:38:23'),(9,4,8,'DONE','2025-11-30 23:38:23'),(10,5,9,'PLANNED','2025-11-30 23:38:23'),(11,5,10,'PLANNED','2025-11-30 23:38:23');
/*!40000 ALTER TABLE `missionassignment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `team`
--

DROP TABLE IF EXISTS `team`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `team` (
  `team_id` int NOT NULL,
  `team_name` varchar(100) NOT NULL,
  `region` varchar(100) NOT NULL,
  PRIMARY KEY (`team_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `team`
--

LOCK TABLES `team` WRITE;
/*!40000 ALTER TABLE `team` DISABLE KEYS */;
INSERT INTO `team` VALUES (1,'시흥 중앙 헌터팀','시흥시'),(2,'서울 동부 특수부대','서울 동부'),(3,'인천 항만 수색팀','인천항'),(4,'부산 남부 헌터연합','부산 남부'),(5,'제주 사냥꾼 전담팀','제주도');
/*!40000 ALTER TABLE `team` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `v_battle_distribution_detail`
--

DROP TABLE IF EXISTS `v_battle_distribution_detail`;
/*!50001 DROP VIEW IF EXISTS `v_battle_distribution_detail`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_battle_distribution_detail` AS SELECT 
 1 AS `battle_id`,
 1 AS `mission_id`,
 1 AS `mission_objective`,
 1 AS `demon_id`,
 1 AS `demon_name`,
 1 AS `started_at`,
 1 AS `location`,
 1 AS `outcome`,
 1 AS `civilian_killed`,
 1 AS `civilian_injured`,
 1 AS `hunter_id`,
 1 AS `hunter_name`,
 1 AS `is_dead_at_battle`,
 1 AS `share_amount`,
 1 AS `distribution_status`,
 1 AS `distributed_at`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_battle_summary`
--

DROP TABLE IF EXISTS `v_battle_summary`;
/*!50001 DROP VIEW IF EXISTS `v_battle_summary`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_battle_summary` AS SELECT 
 1 AS `battle_id`,
 1 AS `mission_id`,
 1 AS `mission_objective`,
 1 AS `demon_id`,
 1 AS `demon_name`,
 1 AS `started_at`,
 1 AS `location`,
 1 AS `outcome`,
 1 AS `civilian_killed`,
 1 AS `civilian_injured`,
 1 AS `total_claimed_bounty`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_demon_dashboard`
--

DROP TABLE IF EXISTS `v_demon_dashboard`;
/*!50001 DROP VIEW IF EXISTS `v_demon_dashboard`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_demon_dashboard` AS SELECT 
 1 AS `demon_id`,
 1 AS `name`,
 1 AS `grade`,
 1 AS `bounty`,
 1 AS `civilian_killed_total`,
 1 AS `civilian_injured_total`,
 1 AS `risk_level`,
 1 AS `battle_count`,
 1 AS `total_bounty`,
 1 AS `last_battle_at`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_demon_risk`
--

DROP TABLE IF EXISTS `v_demon_risk`;
/*!50001 DROP VIEW IF EXISTS `v_demon_risk`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_demon_risk` AS SELECT 
 1 AS `demon_id`,
 1 AS `name`,
 1 AS `grade`,
 1 AS `bounty`,
 1 AS `civilian_killed_total`,
 1 AS `civilian_injured_total`,
 1 AS `risk_level`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_hunter_financials`
--

DROP TABLE IF EXISTS `v_hunter_financials`;
/*!50001 DROP VIEW IF EXISTS `v_hunter_financials`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_hunter_financials` AS SELECT 
 1 AS `hunter_id`,
 1 AS `hunter_name`,
 1 AS `hunter_status`,
 1 AS `team_name`,
 1 AS `balance`,
 1 AS `total_income`,
 1 AS `total_spent`,
 1 AS `last_tx_type`,
 1 AS `last_tx_amount`,
 1 AS `last_tx_desc`,
 1 AS `updated_at`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_mission_assignment_detail`
--

DROP TABLE IF EXISTS `v_mission_assignment_detail`;
/*!50001 DROP VIEW IF EXISTS `v_mission_assignment_detail`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_mission_assignment_detail` AS SELECT 
 1 AS `assignment_id`,
 1 AS `mission_id`,
 1 AS `objective`,
 1 AS `hunter_id`,
 1 AS `hunter_name`,
 1 AS `team_name`,
 1 AS `assignment_status`,
 1 AS `assigned_at`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_mission_overview`
--

DROP TABLE IF EXISTS `v_mission_overview`;
/*!50001 DROP VIEW IF EXISTS `v_mission_overview`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_mission_overview` AS SELECT 
 1 AS `mission_id`,
 1 AS `objective`,
 1 AS `status`,
 1 AS `created_at`,
 1 AS `due_date`,
 1 AS `team_name`,
 1 AS `battle_count`,
 1 AS `assigned_hunters`*/;
SET character_set_client = @saved_cs_client;

--
-- Dumping events for database 'chain_db'
--

--
-- Dumping routines for database 'chain_db'
--
/*!50003 DROP PROCEDURE IF EXISTS `distribute_bounty` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `distribute_bounty`(IN p_battle_id INT)
BEGIN
    DECLARE v_outcome    VARCHAR(20);
    DECLARE v_mission_id INT;
    DECLARE v_bounty     INT;
    DECLARE v_n          INT;
    DECLARE v_share      INT;
    DECLARE v_done_cnt   INT;

     -- 1. 전투 + 악마 현상금 조회
    SELECT b.outcome, b.mission_id, d.bounty
      INTO v_outcome, v_mission_id, v_bounty
    FROM Battle b
      JOIN Demon d ON b.demon_id = d.demon_id
    WHERE b.battle_id = p_battle_id;

    IF v_outcome IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '존재하지 않는 전투입니다.';
    END IF;

    -- 2. 이미 분배된 전투인지 확인
    SELECT COUNT(*)
      INTO v_done_cnt
    FROM Distribution
    WHERE battle_id = p_battle_id
      AND status = 'DONE';

    IF v_done_cnt > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '이미 보상 지급이 완료된 전투입니다.';
    END IF;

    -- 3. 승리 여부 확인
    IF v_outcome <> 'HUMAN_WIN' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'HUMAN_WIN 전투만 보상 지급할 수 있습니다.';
    END IF;

    -- 4. ACTIVE 헌터 수 조회(생존 헌터만 한에서 n빵. 사망자, 도망자 전부 제외)
    SELECT COUNT(*)
      INTO v_n
    FROM Distribution dist
      JOIN Human h ON dist.hunter_id = h.hunter_id
    WHERE dist.battle_id = p_battle_id
      AND h.status = 'ACTIVE';

    IF v_n = 0 THEN
		-- SQLSTATE '45000'은 MYSQL에서 사용자 정의 예외를 나타내는 표준 코드, 이 코드를 만나면 프로시저 즉시 종료
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '전투에 참여한 ACTIVE 헌터가 없어 보상을 지급할 수 없습니다.';
    END IF;

    -- 5. 1/n 분배액 계산
    SET v_share = v_bounty DIV v_n;

    START TRANSACTION;

        -- 6. Account 업데이트 (ACTIVE 헌터만)
        UPDATE Account a
          JOIN Distribution dist ON a.hunter_id = dist.hunter_id
          JOIN Human h ON h.hunter_id = dist.hunter_id
        SET a.balance      = a.balance + v_share,
            a.total_income = a.total_income + v_share,
            a.last_tx_type = 'IN',
            a.last_tx_amount = v_share,
            a.last_tx_desc  = CONCAT('전투 ', p_battle_id, ' 보상 분배'),
            a.updated_at    = NOW()
        WHERE dist.battle_id = p_battle_id
          AND h.status = 'ACTIVE';

        -- 7. Distribution 상태 DONE + share_amount 기록
        UPDATE Distribution dist
          JOIN Human h ON h.hunter_id = dist.hunter_id
        SET dist.share_amount   = v_share,
            dist.status         = 'DONE',
            dist.distributed_at = NOW()
        WHERE dist.battle_id = p_battle_id
          AND h.status = 'ACTIVE';

        -- 8. 미션 상태 SUCCESS로 변경
        IF v_mission_id IS NOT NULL THEN
            UPDATE Mission
            SET status = 'SUCCESS'
            WHERE mission_id = v_mission_id;
        END IF;

    COMMIT;

    -- Python에서 결과 받기용
    SELECT v_share AS share, v_n AS participant_count;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Final view structure for view `v_battle_distribution_detail`
--

/*!50001 DROP VIEW IF EXISTS `v_battle_distribution_detail`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_battle_distribution_detail` AS select `b`.`battle_id` AS `battle_id`,`b`.`mission_id` AS `mission_id`,`m`.`objective` AS `mission_objective`,`b`.`demon_id` AS `demon_id`,`d`.`name` AS `demon_name`,`b`.`started_at` AS `started_at`,`b`.`location` AS `location`,`b`.`outcome` AS `outcome`,`b`.`civilian_killed` AS `civilian_killed`,`b`.`civilian_injured` AS `civilian_injured`,`dist`.`hunter_id` AS `hunter_id`,`h`.`name` AS `hunter_name`,`dist`.`is_dead_at_battle` AS `is_dead_at_battle`,`dist`.`share_amount` AS `share_amount`,`dist`.`status` AS `distribution_status`,`dist`.`distributed_at` AS `distributed_at` from ((((`battle` `b` left join `mission` `m` on((`b`.`mission_id` = `m`.`mission_id`))) left join `demon` `d` on((`b`.`demon_id` = `d`.`demon_id`))) left join `distribution` `dist` on((`b`.`battle_id` = `dist`.`battle_id`))) left join `human` `h` on((`dist`.`hunter_id` = `h`.`hunter_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_battle_summary`
--

/*!50001 DROP VIEW IF EXISTS `v_battle_summary`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_battle_summary` AS select `b`.`battle_id` AS `battle_id`,`b`.`mission_id` AS `mission_id`,`m`.`objective` AS `mission_objective`,`b`.`demon_id` AS `demon_id`,`d`.`name` AS `demon_name`,`b`.`started_at` AS `started_at`,`b`.`location` AS `location`,`b`.`outcome` AS `outcome`,`b`.`civilian_killed` AS `civilian_killed`,`b`.`civilian_injured` AS `civilian_injured`,ifnull(sum(`bc`.`amount`),0) AS `total_claimed_bounty` from (((`battle` `b` left join `mission` `m` on((`b`.`mission_id` = `m`.`mission_id`))) left join `demon` `d` on((`b`.`demon_id` = `d`.`demon_id`))) left join `bountyclaim` `bc` on((`b`.`battle_id` = `bc`.`battle_id`))) group by `b`.`battle_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_demon_dashboard`
--

/*!50001 DROP VIEW IF EXISTS `v_demon_dashboard`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_demon_dashboard` AS select `r`.`demon_id` AS `demon_id`,`r`.`name` AS `name`,`r`.`grade` AS `grade`,`r`.`bounty` AS `bounty`,`r`.`civilian_killed_total` AS `civilian_killed_total`,`r`.`civilian_injured_total` AS `civilian_injured_total`,`r`.`risk_level` AS `risk_level`,count(distinct `b`.`battle_id`) AS `battle_count`,ifnull(sum(`bc`.`amount`),0) AS `total_bounty`,max(`b`.`started_at`) AS `last_battle_at` from ((`v_demon_risk` `r` left join `battle` `b` on((`r`.`demon_id` = `b`.`demon_id`))) left join `bountyclaim` `bc` on((`r`.`demon_id` = `bc`.`demon_id`))) group by `r`.`demon_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_demon_risk`
--

/*!50001 DROP VIEW IF EXISTS `v_demon_risk`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_demon_risk` AS select `demon`.`demon_id` AS `demon_id`,`demon`.`name` AS `name`,`demon`.`grade` AS `grade`,`demon`.`bounty` AS `bounty`,`demon`.`civilian_killed_total` AS `civilian_killed_total`,`demon`.`civilian_injured_total` AS `civilian_injured_total`,(case when ((`demon`.`civilian_killed_total` >= 40) or (`demon`.`civilian_injured_total` >= 80)) then 'EXTREME' when ((`demon`.`civilian_killed_total` >= 20) or (`demon`.`civilian_injured_total` >= 40)) then 'DANGER' when ((`demon`.`civilian_killed_total` >= 10) or (`demon`.`civilian_injured_total` >= 20)) then 'WARNING' else 'NORMAL' end) AS `risk_level` from `demon` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_hunter_financials`
--

/*!50001 DROP VIEW IF EXISTS `v_hunter_financials`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_hunter_financials` AS select `h`.`hunter_id` AS `hunter_id`,`h`.`name` AS `hunter_name`,`h`.`status` AS `hunter_status`,`t`.`team_name` AS `team_name`,`a`.`balance` AS `balance`,`a`.`total_income` AS `total_income`,`a`.`total_spent` AS `total_spent`,`a`.`last_tx_type` AS `last_tx_type`,`a`.`last_tx_amount` AS `last_tx_amount`,`a`.`last_tx_desc` AS `last_tx_desc`,`a`.`updated_at` AS `updated_at` from ((`human` `h` left join `team` `t` on((`h`.`team_id` = `t`.`team_id`))) left join `account` `a` on((`h`.`hunter_id` = `a`.`hunter_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_mission_assignment_detail`
--

/*!50001 DROP VIEW IF EXISTS `v_mission_assignment_detail`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_mission_assignment_detail` AS select `ma`.`assignment_id` AS `assignment_id`,`ma`.`mission_id` AS `mission_id`,`m`.`objective` AS `objective`,`ma`.`hunter_id` AS `hunter_id`,`h`.`name` AS `hunter_name`,`t`.`team_name` AS `team_name`,`ma`.`assignment_status` AS `assignment_status`,`ma`.`assigned_at` AS `assigned_at` from (((`missionassignment` `ma` join `mission` `m` on((`ma`.`mission_id` = `m`.`mission_id`))) join `human` `h` on((`ma`.`hunter_id` = `h`.`hunter_id`))) left join `team` `t` on((`h`.`team_id` = `t`.`team_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_mission_overview`
--

/*!50001 DROP VIEW IF EXISTS `v_mission_overview`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_mission_overview` AS select `m`.`mission_id` AS `mission_id`,`m`.`objective` AS `objective`,`m`.`status` AS `status`,`m`.`created_at` AS `created_at`,`m`.`due_date` AS `due_date`,`t`.`team_name` AS `team_name`,count(distinct `b`.`battle_id`) AS `battle_count`,count(distinct `ma`.`hunter_id`) AS `assigned_hunters` from (((`mission` `m` join `team` `t` on((`m`.`team_id` = `t`.`team_id`))) left join `battle` `b` on((`m`.`mission_id` = `b`.`mission_id`))) left join `missionassignment` `ma` on((`m`.`mission_id` = `ma`.`mission_id`))) group by `m`.`mission_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-02 11:55:59
