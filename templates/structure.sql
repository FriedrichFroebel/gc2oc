CREATE TABLE IF NOT EXISTS `metadata` (
    `revision`          INTEGER NOT NULL,
    `lastUpdateCheck`   TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS `gc2oc` (
    `ocCode`    TEXT NOT NULL UNIQUE,
    `gcCode`    TEXT NOT NULL,
    PRIMARY KEY(`ocCode`)
);
