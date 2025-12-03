실행할 때 파일 디렉토리 주의!

실행 전 Computer_2.sql 가져오고

INSERT INTO `Computer_2`.`Team` (team_name, region)
VALUES ('특수과 4과', '도쿄, 일본');

INSERT INTO `Computer_2`.`Demon` 
(name, grade, status, bounty, civilian_kills, civilian_injuries)
VALUES
('Azazel', 'SS', 'ALIVE', 1000000, 50, 20);

-- 전투 기록 생성
INSERT INTO `Computer_2`.`Battle` 
(mission_id, battle_seq, demon_id, outcome, location, civilian_killed, civilian_injured)
VALUES 
(2, 1, 1, 'HUNTER_WIN', '도쿄', 3, 1);


해당 사항을 미리 넣은 후 해보면 훨씬 많은 것을 해볼 수 있음
