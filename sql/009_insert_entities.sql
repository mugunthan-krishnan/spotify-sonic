INSERT INTO
    IS601_Entities (
        id,
        name,
        description,
        is_active
    )
VALUES (1, 'Artists', 'Artists entity association allows search and addition ability of artists, to users.', 1) ON DUPLICATE KEY
UPDATE name = name;

INSERT INTO
    IS601_Entities (
        id,
        name,
        description,
        is_active
    )
VALUES (2, 'Tracks', 'Tracks entity association allows search and addition ability of tracks, to users.', 1) ON DUPLICATE KEY
UPDATE name = name;