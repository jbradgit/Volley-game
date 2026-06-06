all_over = false;
i = 1;
while(i <= teams)
{
   num = i;
   this["t" + num] = "";
   i++;
}
manager_rating = 0;
if(restore_save)
{
   i = 1;
   while(i <= 23)
   {
      trace("*****" + our_player[i] + " v " + player_name[i] + "  p " + player_played[i]);
      if(our_player[i] != player_name[i])
      {
         player_played[i] = 0;
         player_goals[i] = 0;
         player_sub_used[i] = 0;
         player_name[i] = our_player[i];
      }
      i++;
   }
   cookylife.write_player_tables();
}
else
{
   round = 0;
   i = 1;
   while(i <= teams)
   {
      played[i] = 0;
      won[i] = 0;
      lost[i] = 0;
      drawn[i] = 0;
      for_goals[i] = 0;
      against_goals[i] = 0;
      pts[i] = 0;
      i++;
   }
   i = 1;
   while(i <= 23)
   {
      player_played[i] = 0;
      player_goals[i] = 0;
      player_sub_used[i] = 0;
      player_name[i] = our_player[i];
      i++;
   }
}
