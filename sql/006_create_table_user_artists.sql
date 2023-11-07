CREATE TABLE
    IS601_User_Artists(
        id int auto_increment PRIMARY KEY,
        spotifyid VARCHAR(100),
        userid int,
        customartist tinyint(1) not null, 
        name VARCHAR(20) not null,
        genre text not null,
        spotifyUrl varchar(255),
        imageUrl varchar(255),
        is_active tinyint(1) default 1,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (userid) REFERENCES IS601_Users(id)
)