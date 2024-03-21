-- create a function Safeiv that divides (and returns) the first
-- by the sec numb or returns 0 if the sec numb is equal 0
DROP FUNCTION IF EXISTS SafeDiv (a INT, b INT)
RETURNS FLOAT DETERMINISTIC
BEGIN
	DECLARE result FLOAT DEFAULT 0;

	IF b != 0 THEN
		SET result = a / b;
	END IF;
	RETURN result;
END $$
DELIMITER ;
