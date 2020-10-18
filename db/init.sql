--  DATABASE SCHEMA
-- |    uuid     |     img     | prediction |
-- |    (str)    |   (bytes)   |   (str)    |
-- |    (50)     |    (16MB)   |   (512)    |
-- |   cbf6d9f6  |   /9j/4Q... |     dog    |
CREATE DATABASE IF NOT EXISTS prediction;
USE prediction;
CREATE TABLE IF NOT EXISTS predictions (
	uuid VARCHAR(50),
	img MEDIUMTEXT DEFAULT NULL,
	prediction VARCHAR(512) DEFAULT NULL,
	PRIMARY KEY (uuid)

);
SET GLOBAL sort_buffer_size = 1024 * 1024 * 100;
