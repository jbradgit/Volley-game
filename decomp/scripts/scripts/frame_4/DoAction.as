my_team_rating = rating[myteamid];
my_opponents_rating = rating[my_opponents];
trace("rats..." + my_team_rating + " " + my_opponents_rating);
diff_rating = 20 - (my_team_rating - my_opponents_rating + 10);
my_win_target = 2000 + my_opponents_rating * 1500 + random(10) * 200;
if(!im_at_home)
{
   my_win_target += 2000;
}
my_draw_target = int(int(my_win_target * 5) / 10);
my_draw_target_txt = "Your target to draw this game is " + my_draw_target;
my_win_target_txt = "Your target to win this game is " + my_win_target;
boselecta = team[myteamid];
if(im_at_home)
{
   boselecta_fixture = boselecta + " v " + team[my_opponents];
}
else
{
   boselecta_fixture = team[my_opponents] + " v " + boselecta;
}
stop();
