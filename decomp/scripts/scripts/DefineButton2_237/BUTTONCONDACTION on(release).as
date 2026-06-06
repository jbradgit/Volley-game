on(release){
   _level0.cookylife.read_tables();
   _level0.cookylife.read_player_tables();
   _level0.myteam = _level0.team[_level0.myteamid];
   restore_save = true;
   gotoAndStop("showshirt");
   play();
}
