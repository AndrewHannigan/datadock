--source sqlite:////workspaces/datadock/tests/tigerking.db
--to   sqlite:////workspaces/datadock/tests/tigerking_new.db
--name trainer
SELECT
  first_name                   --type String(length=100)
, last_name as alias           --type String(length=100)
, dob                          --type Date
, CASE WHEN tiger_skills > 0.8
       THEN 1
       ELSE 0
       END as binary_tiger_skills    --type Integer
FROM Trainer