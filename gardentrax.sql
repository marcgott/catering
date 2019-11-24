DROP TABLE IF EXISTS `cycle`;
CREATE TABLE IF NOT EXISTS `cycle` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `start` date NOT NULL,
  `end` date NOT NULL,
  `location` varchar(255) NOT NULL,
  `light_hours` int(2) NOT NULL,
  `total_yield` int(4) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;


DROP TABLE IF EXISTS `environment`;
CREATE TABLE IF NOT EXISTS `environment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `location` enum('indoor','outdoor') NOT NULL,
  `light_hours` int(3) NOT NULL,
  `temperature` int(3) NOT NULL,
  `humidity` int(11) NOT NULL,
  `light_source` varchar(255) NOT NULL,
  `lumens` int(5) NOT NULL,
  `wattage` varchar(255) NOT NULL,
  `grow_area` varchar(64) NOT NULL,
  `containment` varchar(255) NOT NULL,
  `max_plants` int(2) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;


DROP TABLE IF EXISTS `log`;
CREATE TABLE IF NOT EXISTS `log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `plant_ID` int(11) NOT NULL,
  `nutrient_ID` int(11) DEFAULT NULL,
  `environment_ID` int(11) DEFAULT NULL,
  `repellent_ID` int(11) DEFAULT NULL,
  `stage` varchar(64) DEFAULT NULL,
  `water` tinyint(1) DEFAULT NULL,
  `trim` varchar(32) DEFAULT NULL,
  `height` decimal(3,1) DEFAULT NULL,
  `span` decimal(3,1) DEFAULT NULL,
  `nodes` int(2) NOT NULL,
  `lux` int(5) NOT NULL,
  `soil_pH` decimal(2,1) NOT NULL DEFAULT '7.0',
  `transplant` tinyint(1) DEFAULT NULL,
  `photo` blob,
  `notes` text CHARACTER SET utf8,
  `logdate` date DEFAULT NULL,
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;


DROP TABLE IF EXISTS `nutrient`;
CREATE TABLE IF NOT EXISTS `nutrient` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `organic` varchar(8) NOT NULL,
  `nitrogen` int(2) NOT NULL,
  `phosphorus` int(2) NOT NULL,
  `potassium` int(2) NOT NULL,
  `trace` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;


DROP TABLE IF EXISTS `options`;
CREATE TABLE IF NOT EXISTS `options` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `option_key` varchar(255) CHARACTER SET utf8 NOT NULL,
  `option_value` text CHARACTER SET utf8 NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;


DROP TABLE IF EXISTS `plant`;
CREATE TABLE IF NOT EXISTS `plant` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8 NOT NULL,
  `gender` varchar(32) NOT NULL,
  `strain_ID` varchar(255) NOT NULL,
  `cycle_ID` varchar(255) NOT NULL,
  `source` varchar(64) NOT NULL,
  `grow_medium` VARCHAR( 64 ) NOT NULL,
  `yield` int(3) NOT NULL,
  `current_stage` varchar(255) DEFAULT NULL,
  `current_environment` int(4) NOT NULL,
  `current_nodes` int(2) NOT NULL,
  `photo` longtext NOT NULL, 
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;


DROP TABLE IF EXISTS `repellent`;
CREATE TABLE IF NOT EXISTS `repellent` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `type` enum('organic','chemical','other') NOT NULL,
  `target` varchar(255) NOT NULL,
  `price` varchar(64) NOT NULL,
  `purchase_location` varchar(255) NOT NULL,
  `notes` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;


DROP TABLE IF EXISTS `report`;
CREATE TABLE IF NOT EXISTS `report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `data` mediumtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;


DROP TABLE IF EXISTS `strain`;
CREATE TABLE IF NOT EXISTS `strain` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `notes` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;
