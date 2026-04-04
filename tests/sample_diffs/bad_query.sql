-- This file has intentional anti-patterns for testing

SELECT * FROM orders WHERE 1=1;

SELECT o.*, c.name
FROM orders o, customers c
WHERE o.customer_id = c.id;

SELECT name FROM users
WHERE UPPER(email) = 'TEST@EXAMPLE.COM';

DECLARE @sql NVARCHAR(MAX) = 'SELECT * FROM users WHERE name = ''' + @input + '''';
EXEC(@sql);
