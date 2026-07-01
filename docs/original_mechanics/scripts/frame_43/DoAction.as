in_play = score;
temp = score;
gandalf = mb2;
mb2 = int((getTimer() - mb22) / 1000);
_quality = "high";
man._x = 999;
leve = temp;
dst = leve;
if(temp > my_win_target)
{
   home = 1;
   away = 0;
   result_movie.gotoandstop(1);
}
else
{
   home = 0;
   away = 1;
   if(temp > my_draw_target)
   {
      home = 1;
      away = 1;
      result_movie.gotoandstop(2);
   }
   else
   {
      result_movie.gotoandstop(3);
   }
}
if(!im_at_home)
{
   tmp_h = home;
   home = away;
   away = tmp_h;
}
