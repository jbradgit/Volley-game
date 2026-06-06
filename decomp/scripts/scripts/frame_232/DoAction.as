if(manager_rating > 0)
{
   submitpts._visible = true;
   submitptstxt._visible = true;
}
else
{
   submitpts._visible = false;
   submitptstxt._visible = false;
}
show_all_the_scores();
iteam = 1;
while(iteam <= 20)
{
   pts[iteam] = won[iteam] * 3 + drawn[iteam];
   iteam++;
}
cookylife.write_tables();
cookylife.write_player_tables();
my_score = pts[myteamid];
_level0.cookylife.read_cookie();
if(my_score > life_best)
{
   life_best = my_score;
   _level0.cookylife.write_cookie("name",life_played,life_lost,life_won,life_goals,life_best);
}
stop();
