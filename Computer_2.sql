-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';



-- -----------------------------------------------------
-- Schema Computer_2
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `Computer_2` DEFAULT CHARACTER SET utf8 ;
USE `computer_2` ; -- (수정 12/04 원가형) 스키마명 Computer_2 -> computer2 소문자 사용



-- -----------------------------------------------------
-- Table `Computer_2`.`Team`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Computer_2`.`Team` (
  `team_id` BIGINT NOT NULL AUTO_INCREMENT,
  `team_name` VARCHAR(100) NOT NULL,
  `region` VARCHAR(100) NOT NULL COMMENT '활동지역',
  PRIMARY KEY (`team_id`))
ENGINE = InnoDB;



-- -----------------------------------------------------
-- Table `Computer_2`.`Demon`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Computer_2`.`Demon` (
  `demon_id` BIGINT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  
  -- 노션 인덱스 수정 명칭에 맞게 원래의 rank->grade로 수정
  `grade` ENUM('SS', 'S', 'A', 'B', 'C') NOT NULL COMMENT '악마의 위험도. 초기값 C',
  `status` ENUM('ALIVE', 'DEAD') NOT NULL,
  `bounty` BIGINT NULL COMMENT '현상금. 초기값 null. 현상금 초깃값 팀원들과 상의',
  `civilian_kills` BIGINT NOT NULL COMMENT '민간인 킬 수',
  `civilian_injuries` BIGINT NOT NULL COMMENT '민간인 부상 입힌 수',
  PRIMARY KEY (`demon_id`),
  
  -- D. 정렬 및 등급 조회 (Ranking & Sorting)
  -- 목적: S급, A급 등 악마를 등급별로 조회하거나, 등급순으로 정렬할 때 성능을 높입니다.
  INDEX `idx_demon_grade` (`grade` ASC)) -- (수정 12/04 원가형) 인덱스를 create 테이블 안에 넣음 
ENGINE = InnoDB;

-- ALTER TABLE `Computer_2`.`Demon` -- (삭제 12/04 원가형)
-- ADD INDEX `idx_demon_grade`(`grade` ASC); -- (삭제 12/04 원가형)



-- -----------------------------------------------------
-- Table `Computer_2`.`Hunter`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Computer_2`.`Hunter` (
  `hunter_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '헌터의 ID',
  `team_id` BIGINT NOT NULL COMMENT '헌터는 반드시 하나의 team_ID를 참조함',
  `name` VARCHAR(100) NOT NULL,
  `status` ENUM('ALIVE', 'DEAD') NOT NULL COMMENT '생존상태. 현상금 분배 시 이 값이 DEAD면 분배 하지 않음',
  `demon_id` BIGINT NULL COMMENT '계약한 악마의 PK. 계약 하지 않으면 null',
  `contract_cost` VARCHAR(100) NULL COMMENT '계약 체결 비용(대가). 계약을 체결하지 않으면 null',
  `contract_power` VARCHAR(100) NULL COMMENT '계약에 따라 얻는 힘(능력). 계약을 체결하지 않으면 null',
  `contract_date` DATE NULL COMMENT '계약 체결 날짜. 계약을 체결하지 않으면 null',
  PRIMARY KEY (`hunter_id`),
  INDEX `team_ID_idx` (`team_id` ASC) ,
  INDEX `demon_id_idx` (`demon_id` ASC) ,
  CONSTRAINT `hunter_team_id`
    FOREIGN KEY (`team_id`)
    REFERENCES `Computer_2`.`Team` (`team_id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `hunter_demon_id`
    FOREIGN KEY (`demon_id`)
    REFERENCES `Computer_2`.`Demon` (`demon_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
    
  -- A. 복합 인덱스 수정 및 human -> hunter 이름 수정
  -- 목적: Human 테이블에서 "특정 팀"에 속해있으면서 "특정 상태(생존/사망 등)"인 사람을 찾을 때 사용합니다.
  -- 효과: team_id로 먼저 거르고, 그 안에서 status로 한 번 더 빠르게 찾습니다.
  INDEX `idx_hunter_team_status` (`team_id` ASC, `status` ASC)) -- (수정 12/04 원가형)
ENGINE = InnoDB;

-- ALTER TABLE `Computer_2`.`Hunter` -- (삭제 12/04 원가형)
-- ADD INDEX `idx_hunter_team_status` (`team_id` ASC, `status` ASC); --(삭제 12/04 원가형)



-- -----------------------------------------------------
-- Table `Computer_2`.`Mission`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Computer_2`.`Mission` (
  `mission_id` BIGINT NOT NULL AUTO_INCREMENT,
  `objective` VARCHAR(100) NOT NULL COMMENT '임무 목표',
  `state` ENUM('PLANNED', 'IN_PROGRESS', 'SUCCESS', 'FAIL') NOT NULL COMMENT '임무 진행 상태',
  `created_at` DATE NOT NULL COMMENT '생성 날짜',
  `due_date` DATE NOT NULL COMMENT '생성 마감',
  PRIMARY KEY (`mission_id`),
  
  -- C. 상태(State) 필터링 최적화
  -- 목적: "현재 진행 중인 임무", "실패한 임무" 등 임무 상태별 조회를 빠르게 합니다.
  INDEX `idx_mission_status`(`state` ASC))
ENGINE = InnoDB;

-- ALTER TABLE `Computer_2`.`Mission` -- (삭제 12/04 원가형)
-- ADD INDEX `idx_mission_status`(`state` ASC); -- (삭제 12/04 원가형)


-- pk가 없는 문제
-- -----------------------------------------------------
-- Table `Computer_2`.`Mission_assignment`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Computer_2`.`Mission_assignment` (
  `team_id` BIGINT NOT NULL,
  `mission_id` BIGINT NOT NULL,
  
  -- B. 외래키(FK) & 조인 성능 최적화
  -- 목적: 특정 팀에게 할당된 임무 목록을 조회할 때 빠릅니다.
  -- Mission이 아닌 Mission_assignment에 팀아이디에 대한 인덱스를 추가하였습니다.
  -- 불필요한 Mission 테이블을 탐색하는거보다 이 테이블에서 거르는것이 더 효율적인 방법입니다.
  INDEX `team_id_idx` (`team_id` ASC) ,
  INDEX `mission_id_idx` (`mission_id` ASC) ,

  CONSTRAINT `assignment_team_id`
    FOREIGN KEY (`team_id`)
    REFERENCES `Computer_2`.`Team` (`team_id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `assignment_mission_id`
    FOREIGN KEY (`mission_id`)
    REFERENCES `Computer_2`.`Mission` (`mission_id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



-- misson id에 외래키 제약 조건이 없음
-- -----------------------------------------------------
-- Table `Computer_2`.`Battle`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Computer_2`.`Battle` (
  `mission_id` BIGINT NOT NULL,
  `battle_seq` BIGINT NOT NULL,
  `demon_id` BIGINT NOT NULL,
  
  -- 착오로 잘못 칭한 'HUMAN_WIN'->'HUNTER_WIN'으로 수정하였습니다.
  `outcome` ENUM('HUNTER_WIN', 'DEMON_WIN') NOT NULL,    
  `location` VARCHAR(100) NOT NULL,
  `civilian_killed` BIGINT NOT NULL,
  `civilian_injured` BIGINT NOT NULL,
   PRIMARY KEY (`mission_id`, `battle_seq`),		
  -- 여기도 다시 살림... 안그러면 오류 나는데?
  
  -- Mission 테이블 참조 외래 키 추가
  CONSTRAINT `fk_battle_mission_id`
    FOREIGN KEY (`mission_id`)
    REFERENCES `Computer_2`.`Mission` (`mission_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    
    CONSTRAINT `fk_battle_demon_id`
    FOREIGN KEY (`demon_id`)
    REFERENCES `Computer_2`.`Demon` (`demon_id`)
    -- ON DELETE SET NULL    여기는 민서2 노션 참고할 것... 날려야 할듯
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  
  -- B. 외래키(FK) & 조인 성능 최적화
  -- 목적: 특정 악마가 참여한 전투 기록을 조회할 때 빠릅니다.
  INDEX `idx_battle_demon` (`demon_id` ASC))
ENGINE = InnoDB;

-- ALTER TABLE `Computer_2`.`Battle` -- (삭제 12/04 원가형)
-- ADD INDEX `idx_battle_demon` (`demon_id` ASC); -- (삭제 12/04 원가형) 



-- -----------------------------------------------------
-- Table `Computer_2`.`Reward`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Computer_2`.`Reward` (
  `reward_id` BIGINT NOT NULL AUTO_INCREMENT,
  `mission_id` BIGINT NOT NULL COMMENT 'Mission의 복합키',
  `battle_seq` BIGINT NOT NULL COMMENT 'Mission의 복합키',
  `team_id` BIGINT NOT NULL,
  `total_amount` BIGINT NOT NULL COMMENT '총현상금',
  PRIMARY KEY (`reward_id`),
  
  UNIQUE INDEX `reward_id_UNIQUE` (`reward_id` ASC) ,
  INDEX `mission_id_idx` (`mission_id` ASC) ,
  INDEX `battle_seq_idx` (`battle_seq` ASC) ,
  INDEX `team_id_idx` (`team_id` ASC) ,
  
-- 복합키로 수정
--   CONSTRAINT `reward_mission_id`
--     FOREIGN KEY (`mission_id`)
--     REFERENCES `Computer_2`.`Battle` (`mission_id`)
--     ON DELETE CASCADE
--     ON UPDATE CASCADE,
--   CONSTRAINT `reward_battle_seq`
--     FOREIGN KEY (`battle_seq`)
--     REFERENCES `Computer_2`.`Battle` (`battle_seq`)
--     ON DELETE CASCADE
--     ON UPDATE CASCADE,

  CONSTRAINT `fk_Reward_Battle`
  FOREIGN KEY (`mission_id`, `battle_seq`)
  REFERENCES `Computer_2`.`Battle` (`mission_id`, `battle_seq`)
  ON DELETE CASCADE
  ON UPDATE CASCADE,

  CONSTRAINT `reward_team_id`
    FOREIGN KEY (`team_id`)
    REFERENCES `Computer_2`.`Team` (`team_id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



-- -----------------------------------------------------
-- Table `Computer_2`.`Battle_Participaton`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Computer_2`.`Battle_Participaton` (
  `mission_id` BIGINT NOT NULL,
  `battle_seq` BIGINT NOT NULL,
  `hunter_id` BIGINT NOT NULL,
  `participated_status` ENUM('ALIVE', 'DEAD') NOT NULL COMMENT '전투 후 헌터의 상태',
  PRIMARY KEY (`mission_id`, `battle_seq`, `hunter_id`),
  
  INDEX `battle_seq_idx` (`battle_seq` ASC) ,
  INDEX `hunter_id_idx` (`hunter_id` ASC) ,

  -- 복합키로 수정
  --  CONSTRAINT `participation_mission_id`
  --     FOREIGN KEY (`mission_id`)
  --     REFERENCES `Computer_2`.`Battle` (`mission_id`)
  --     ON DELETE CASCADE
  --     ON UPDATE NO ACTION,
  --   CONSTRAINT `participation_battle_seq`
  --     FOREIGN KEY (`battle_seq`)
  --     REFERENCES `Computer_2`.`Battle` (`battle_seq`)
  --     ON DELETE CASCADE
  --     ON UPDATE NO ACTION,

  CONSTRAINT `fk_participation_battle`
    FOREIGN KEY (`mission_id`, `battle_seq`)
    REFERENCES `Computer_2`.`Battle` (`mission_id`, `battle_seq`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  
  CONSTRAINT `participation_hunter_id`
    FOREIGN KEY (`hunter_id`)
    REFERENCES `Computer_2`.`Hunter` (`hunter_id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



-- -----------------------------------------------------
-- Table `Computer_2`.`Account`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Computer_2`.`Account` (
  `hunter_id` BIGINT NOT NULL,
  `balance` BIGINT NOT NULL COMMENT '현재 잔액',
  PRIMARY KEY (`hunter_id`),
  CONSTRAINT `account_hunter_id`
    FOREIGN KEY (`hunter_id`)
    REFERENCES `Computer_2`.`Hunter` (`hunter_id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
    
  -- D. 정렬 및 등급 조회 (Ranking & Sorting)
  -- 목적: 보유 금액이 많은 순(랭킹)으로 정렬하거나, 특정 금액 이상/이하의 계정을 찾을 때 빠릅니다.
  INDEX `idx_account_balance`(`balance` ASC)) -- (수정 12/04 원가형)
ENGINE = InnoDB;

-- ALTER TABLE `Computer_2`.`Account` -- (삭제 12/04 원가형)
-- ADD INDEX `idx_account_balance`(`balance` ASC); -- (삭제 12/04 원가형)



-- -----------------------------------------------------
-- Table `Computer_2`.`Reward_Distribution`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Computer_2`.`Reward_Distribution` (
  `reward_id` BIGINT NOT NULL COMMENT '복합키. {reward_id(Fk->Reward),\nhunter_id(FK->Hunter)}',
  `hunter_id` BIGINT NOT NULL COMMENT '복합키. {reward_id(Fk->Reward),\nhunter_id(FK->Hunter)}',
  
  -- 돈이 지급중인지, 지급 완료 되었는지 나타내는 state가 추가되었습니다. 
  `state` ENUM('IN_PROGRESS', 'SUCCESS') NOT NULL ,
  `distributer_amount` BIGINT NOT NULL,
  `distributed_at` DATE NOT NULL,
  PRIMARY KEY (`reward_id`, `hunter_id`),
  
  -- B. 외래키(FK) & 조인 성능 최적화
  -- 목적: 특정 헌터가 청구한 현상금 내역을 조회할 때 빠릅니다.
  INDEX `hunter_id_idx` (`hunter_id` ASC),
  
  -- C. 상태(Status) 필터링 최적화
  -- 목적: 정산/배분 데이터 중 "지급 대기중"이나 "지급 완료" 건을 빠르게 찾습니다
  INDEX `idx_dist_status`(`state` ASC), -- (수정 12/04 원가형)

  CONSTRAINT `distribution_reward_id`
    FOREIGN KEY (`reward_id`)
    REFERENCES `Computer_2`.`Reward` (`reward_id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `distribution_hunter_id`
    FOREIGN KEY (`hunter_id`)
    REFERENCES `Computer_2`.`Hunter` (`hunter_id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- ALTER TABLE `Computer_2`.`Reward_Distribution` -- (삭제 12/04 원가형)
-- ADD INDEX `idx_dist_status`(`state` ASC); -- (삭제 12/04 원가형)



-- (추가 12/05 원가형)
-- 프로시저 코드
-- 기능 : 상금 분배 + Account 업데이트
-- 목적 : 기존 파이썬에서 처리하던 방식을 프로시저로 구현함으로써 빠르게 처리. 파이썬에선 call로 호출
DROP PROCEDURE IF EXISTS distribute_bounty;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `distribute_bounty`(
    IN p_mission_id INT,
    IN p_battle_seq INT
)
BEGIN
    DECLARE v_outcome    VARCHAR(20);
    DECLARE v_bounty     BIGINT;
    DECLARE v_n          INT;
    DECLARE v_share      BIGINT;
    DECLARE v_done_cnt   INT;
    DECLARE v_reward_id  BIGINT;

     -- 1. 전투 + 악마 현상금 조회
    SELECT b.outcome, d.bounty
      INTO v_outcome, v_bounty
    FROM Battle b
      JOIN Demon d ON b.demon_id = d.demon_id
    WHERE b.mission_id = p_mission_id
      AND b.battle_seq = p_battle_seq;

    IF v_outcome IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '존재하지 않는 전투입니다.';
    END IF;

    -- 2. Reward 조회
    SELECT reward_id
      INTO v_reward_id
    FROM Reward
    WHERE mission_id = p_mission_id
      AND battle_seq = p_battle_seq;

    IF v_reward_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '해당 전투에 대한 Reward가 없습니다.';
    END IF;

    -- 3. 이미 분배된 전투인지 확인
    SELECT COUNT(*)
      INTO v_done_cnt
    FROM Reward_Distribution
    WHERE reward_id = v_reward_id
      AND state = 'SUCCESS';

    IF v_done_cnt > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '이미 보상 지급이 완료된 전투입니다.';
    END IF;

    -- 4. 승리 여부 확인
    IF v_outcome <> 'HUNTER_WIN' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'HUNTER_WIN 전투만 보상 지급할 수 있습니다.';
    END IF;

    -- 5. ALIVE 헌터 수 조회 (IN_PROGRESS 상태인 헌터만)
    SELECT COUNT(*)
      INTO v_n
    FROM Reward_Distribution rd
      JOIN Hunter h ON rd.hunter_id = h.hunter_id
    WHERE rd.reward_id = v_reward_id
      AND rd.state = 'IN_PROGRESS'
      AND h.status = 'ALIVE';

    IF v_n = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '전투에 참여한 ALIVE 헌터가 없어 보상을 지급할 수 없습니다.';
    END IF;

    -- 6. 1/n 분배액 계산
    SET v_share = v_bounty DIV v_n;

    START TRANSACTION;

        -- 7. Account 업데이트 (ALIVE 헌터만, IN_PROGRESS 상태인 헌터만)
        UPDATE Account a
          JOIN Reward_Distribution rd ON a.hunter_id = rd.hunter_id
          JOIN Hunter h ON h.hunter_id = rd.hunter_id
        SET a.balance = a.balance + v_share
        WHERE rd.reward_id = v_reward_id
          AND rd.state = 'IN_PROGRESS'
          AND h.status = 'ALIVE';

        -- 8. Reward_Distribution 상태 SUCCESS + share_amount 기록
        UPDATE Reward_Distribution rd
          JOIN Hunter h ON h.hunter_id = rd.hunter_id
        SET rd.distributer_amount = v_share,
            rd.state = 'SUCCESS',
            rd.distributed_at = NOW()
        WHERE rd.reward_id = v_reward_id
          AND rd.state = 'IN_PROGRESS'
          AND h.status = 'ALIVE';

        -- 9. 미션 상태 SUCCESS로 변경
        UPDATE Mission
        SET state = 'SUCCESS'
        WHERE mission_id = p_mission_id
          AND state != 'SUCCESS';

    COMMIT;

    -- Python에서 결과 받기용
    SELECT v_share AS share, v_n AS participant_count;
END ;;
DELIMITER ;



-- (추가 12/05 원가형)
-- 트리거 코드
-- 기능 : 헌터 등록시 헌터팀 자동 분배 자동화
-- 목적 : 헌터 정보 INSERT시 내부에서 동작하는 자동화 기능 구현을 위함
DROP TRIGGER IF EXISTS trigger_random_team;
DELIMITER $$
CREATE TRIGGER trigger_random_team
BEFORE INSERT ON Hunter
FOR EACH ROW
BEGIN
    IF NEW.team_id IS NULL OR NEW.team_id = 0 THEN
        SET NEW.team_id = (
            SELECT team_id
            FROM Team
            ORDER BY RAND()
            LIMIT 1
        );
    END IF;
END$$
DELIMITER ;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;


-- 악마 더미 데이터 삽입
INSERT INTO Demon (name, grade, bounty, civilian_kills, civilian_injuries) VALUES
('벨리알(Belial)', 'SS', 1200000, 32, 87),
('아스타로트(Astaroth)', 'S', 900000, 22, 54),
('말파스(Malphas)', 'A', 400000, 10, 41),
('레비아탄(Leviathan)', 'SS', 1500000, 45, 63),
('바포메트(Baphomet)', 'A', 380000, 7, 26),
('발록(Balrog)', 'S', 850000, 18, 29),
('그림리퍼(Grim Reaper)', 'B', 150000, 2, 17),
('할리퀸(Harlequin)', 'C', 80000, 1, 8),
('데스하운드(Death Hound)', 'B', 130000, 3, 9),
('샤덴(Shadowen)', 'A', 420000, 12, 22);


-- 악마 더미 데이터 삭제
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE battle;
TRUNCATE TABLE demon;
SET FOREIGN_KEY_CHECKS = 1;


-- 악마 더미 데이터 보기
SELECT * FROM DEMON;


-- 팀 데이터 삽입
INSERT IGNORE INTO team (team_id, team_name, region) VALUES
(1, '서울 중앙 헌터팀', '서울'),
(2, '부산 해안 정예부대', '부산'),
(3, '인천 항만 수색팀', '인천'),
(4, '대구 특수 진압대', '대구'),
(5, '제주 사냥꾼 전담팀', '제주'),
(6, '강릉 물고기 낚시꾼', '강릉');


-- 팀 데이터 보기
SELECT * FROM team;


-- 팀 데이터 삭제
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE `Computer_2`.`Battle_Participaton`;
TRUNCATE TABLE `Computer_2`.`Reward_Distribution`;
TRUNCATE TABLE `Computer_2`.`Reward`;
TRUNCATE TABLE `Computer_2`.`Battle`;
SET FOREIGN_KEY_CHECKS = 1;


-- 헌터 데이터 삭제 + 계좌 데이터 까지
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE `Computer_2`.`Battle_Participaton`;
TRUNCATE TABLE `Computer_2`.`Reward_Distribution`;
TRUNCATE TABLE `Computer_2`.`Reward`;
TRUNCATE TABLE `Computer_2`.`Battle`;
TRUNCATE TABLE `Computer_2`.`Mission_assignment`;
TRUNCATE TABLE `Computer_2`.`Mission`;
TRUNCATE TABLE `Computer_2`.`Account`;
TRUNCATE TABLE `Computer_2`.`Hunter`;
TRUNCATE TABLE `Computer_2`.`Team`;
-- 악마 데이터까지 삭제
-- TRUNCATE TABLE `Computer_2`.`Demon`;
SET FOREIGN_KEY_CHECKS = 1;