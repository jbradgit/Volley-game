trace("frame 30");
if(ig <= games)
{
   gotoAndStop("nextgame");
   play();
}
else
{
   if(mtp)
   {
      played[s1tm1]++;
      played[s1tm2]++;
      if(s1tm1 == myteamid)
      {
         won[s1tm2]++;
         lost[s1tm1]++;
      }
      else
      {
         lost[s1tm2]++;
         won[s1tm1]++;
      }
   }
   cookylife.write_tables();
   cookylife.write_player_tables();
}
