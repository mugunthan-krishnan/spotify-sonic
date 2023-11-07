CREATE TABLE
    IS601_User_Entities(
        id int auto_increment PRIMARY KEY,
        user_id int not null,
        entity_id int not null,
        is_active tinyint(1) default 1,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (entity_id) REFERENCES IS601_Entities(id),
        FOREIGN KEY (user_id) REFERENCES IS601_Users(id)
);