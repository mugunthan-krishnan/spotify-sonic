CREATE TABLE
    IS601_User_Tracks(
        id int auto_increment PRIMARY KEY,
        spotifyid VARCHAR(100),
        userid int,
        customtrack SMALLINT not null, 
        name VARCHAR(20) not null,
        artistname VARCHAR(200),
        albumname VARCHAR(100),
        albumurl VARCHAR(100),
        duration VARCHAR(100),
        is_active tinyint(1) default 1,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (userid) REFERENCES IS601_Users(id)
)