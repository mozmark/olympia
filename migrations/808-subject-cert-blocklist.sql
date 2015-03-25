--
-- Bug xxxx - Add support for OneCRL blocklisting by subject / pubkey to AMO
--

DROP TABLE IF EXISTS `blsubjectcert`;

CREATE TABLE `blsubjectcert` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `created` datetime NOT NULL,
    `modified` datetime NOT NULL,
    `subject` longtext NOT NULL,
    `pubkeyhash` varchar(65) NOT NULL,
    `details_id` integer NOT NULL UNIQUE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;

ALTER TABLE `blsubjectcert` ADD CONSTRAINT FOREIGN KEY (`details_id`) REFERENCES `bldetails` (`id`);
