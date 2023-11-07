CREATE TABLE
    IS601_Entities(
        id int auto_increment PRIMARY KEY,
        name VARCHAR(100) not null UNIQUE,
        description text default (concat(name,' entity.')),
        is_active tinyint(1) default 1,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);