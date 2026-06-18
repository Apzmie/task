-- [1. 기본 조회 4개]
-- 1. 전체 학생 명단 조회
SELECT * FROM students;
-- 2. 90점 이상인 우수 성적 데이터만 조회
SELECT * FROM grades WHERE score >= 90;
-- 3. 학생 이름을 가나다순(오름차순)으로 정렬하여 조회
SELECT * FROM students ORDER BY name ASC;
-- 4. 성적 상위 5개 결과만 조회
SELECT * FROM grades ORDER BY score DESC LIMIT 5;

-- [2. 조인 4개]
-- 5. INNER JOIN: 학생 이름과 성적 조회
SELECT s.name, g.score FROM students s INNER JOIN grades g ON s.student_id = g.student_id;
-- 6. INNER JOIN: 과목명과 그 과목의 성적들 조회
SELECT sub.subject_name, g.score FROM subjects sub INNER JOIN grades g ON sub.subject_id = g.subject_id;
-- 7. JOIN 2번: 학생 이름, 과목명, 성적 모두 조회
SELECT s.name, sub.subject_name, g.score 
FROM grades g 
JOIN students s ON g.student_id = s.student_id 
JOIN subjects sub ON g.subject_id = sub.subject_id;
-- 8. LEFT JOIN: 모든 학생의 이름과 성적 조회 (성적 없는 경우 대비)
SELECT s.name, g.score FROM students s LEFT JOIN grades g ON s.student_id = g.student_id;

-- [3. 집계 3개]
-- 9. AVG: 과목별 평균 점수 계산 (GROUP BY 사용)
SELECT sub.subject_name, AVG(g.score) as avg_score 
FROM grades g JOIN subjects sub ON g.subject_id = sub.subject_id GROUP BY sub.subject_name;
-- 10. SUM: 학생별 총점 계산 (10개 과목 합산 결과)
SELECT s.name, SUM(g.score) as total_score 
FROM students s JOIN grades g ON s.student_id = g.student_id GROUP BY s.name;
-- 11. COUNT: 등록된 성적 데이터 총 개수 확인
SELECT COUNT(*) as total_grade_count FROM grades;

-- [4. 서브쿼리 1개]
-- 12. 전체 학생 평균보다 높은 점수를 받은 학생과 점수 조회
SELECT s.name, g.score FROM students s JOIN grades g ON s.student_id = g.student_id 
WHERE g.score > (SELECT AVG(score) FROM grades);

-- [5. 데이터 수정 및 삭제 2개]
-- 13. 학생 이름 변경 (1번 학생을 '김철수'로 변경) 
UPDATE students SET name = '김철수' WHERE student_id = 1;
-- SELECT * FROM students WHERE student_id = 1;
-- 14. 성적 데이터 삭제 (10번 학생의 모든 성적 삭제)
DELETE FROM grades WHERE student_id = 10;
-- SELECT * FROM grades WHERE student_id = 10;

-- [6. 인덱스 1개]
-- 15. 학생 이름 검색 속도 향상용 인덱스 생성
CREATE INDEX idx_student_name ON students(name);
-- 학생 이름으로 검색하는 경우가 많음. 
-- 인덱스가 없으면 전체를 다 읽어야 하지만(Full Scan),
-- 인덱스를 만들면 '이름순 목차'를 통해 데이터가 어디 있는지 좌표를 바로 알 수 있어
-- 즉시 해당 위치로 건너뛰어(Index Seek) 검색 속도를 대폭 줄임.
-- 인덱스는 리스트가 아니라 계층형 구조(트리)라서 풀스캔 안함.