CREATE TABLE
    IS601_Top_Artists(
        artists json,
        curMonth int,
        curYear int,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY(curMonth, curYear)
)