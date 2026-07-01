_level0.cookylife.read_team();
_level0.cookylife.read_cookie();
trace("my_team_played " + my_team_played);
if(_level0.myteamid >= 1 and _level0.myteamid <= 20 and my_team_played < 38)
{
   myteamid = MASTER_TEAM_ID;
}
else
{
   gotoAndStop("newgame");
   play();
}
