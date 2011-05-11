CREATE TABLE IF NOT EXISTS `research_patient` (
`id`  int(11) UNSIGNED NOT NULL AUTO_INCREMENT ,
`health_id`  varchar(6) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
`research_id`  varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
`days`  tinyint(4) NOT NULL ,
PRIMARY KEY (`id`),
UNIQUE INDEX `health_id` USING BTREE (`health_id`) ,
UNIQUE INDEX `research_id` USING BTREE (`research_id`) 
)
ENGINE=MyISAM
DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci
;

CREATE TABLE IF NOT EXISTS `research_location` (
`id`  int(11) NOT NULL AUTO_INCREMENT ,
`location_id`  int(11) NOT NULL ,
`research_id`  varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
PRIMARY KEY (`id`),
UNIQUE INDEX `location_id` USING BTREE (`location_id`) ,
UNIQUE INDEX `research_id` USING BTREE (`research_id`) 
)
ENGINE=MyISAM
DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

CREATE TABLE IF NOT EXISTS `research_deadperson` (
`id`  int(11) UNSIGNED NOT NULL AUTO_INCREMENT ,
`dead_id`  int(11) UNSIGNED NOT NULL,
`research_id`  varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
`days`  tinyint(4) NOT NULL ,
PRIMARY KEY (`id`),
UNIQUE INDEX `dead_id` USING BTREE (`dead_id`) ,
UNIQUE INDEX `research_id` USING BTREE (`research_id`) 
)
ENGINE=MyISAM
DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci
;

CREATE TABLE IF NOT EXISTS `research_chw` (
`id`  int(11) NOT NULL AUTO_INCREMENT ,
`chw_id`  int(11) NOT NULL ,
`research_id`  varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
PRIMARY KEY (`id`),
UNIQUE INDEX `chw_id` USING BTREE (`chw_id`) ,
UNIQUE INDEX `research_id` USING BTREE (`research_id`) 
)
ENGINE=MyISAM
DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;