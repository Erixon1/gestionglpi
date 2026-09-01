<?php
class DB extends DBmysql {
   public $dbhost = 'glpi-db';
   public $dbport = '3306';
   public $dbuser = 'root';
   public $dbpassword = 'root_pass';
   public $dbdefault = 'glpi_db';
   public $use_utf8mb4 = true;
   public $allow_myisam = false;
   public $allow_datetime = false;
   public $allow_signed_keys = false;
}
