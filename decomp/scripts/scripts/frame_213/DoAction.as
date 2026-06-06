use_the_real_draw = true;
if(use_the_real_draw)
{
   string1 = Number(fixture_list[round].substr(game * 5 - 5 + 12,2));
   string2 = Number(fixture_list[round].substr(game * 5 - 2 + 12,2));
   r1 = string1;
   r2 = string2;
   picked[r1] = true;
   picked[r2] = true;
}
else
{
   do
   {
      r1 = random(teams) + 1;
   }
   while(picked[r1]);
   picked[r1] = true;
   do
   {
      r2 = random(teams) + 1;
   }
   while(picked[r2]);
   picked[r2] = true;
}
num = game * 2 - 1;
this["t" + num] = team[r1];
pos[num] = r1;
home_slot[game] = team[r1];
away_slot[game] = team[r2];
t1_slot[game] = r1;
t2_slot[game] = r2;
col = convert_col_to_number(colour[r1]);
str = convert_col_to_number(stripe1[r1]);
slv = convert_col_to_number(sleeves[r1]);
cla = convert_col_to_number(collar[r1]);
this["shirt" + num].gotoandstop(1);
this["shirt" + num].colour.gotoandstop(col);
this["shirt" + num].collar.gotoandstop(cla);
this["shirt" + num].sleeves.gotoandstop(slv);
this["shirt" + num].stripe1.gotoandstop(str);
if(team[r1] == "Blackburn")
{
   this["shirt" + num].colour.gotoandstop(10);
   this["shirt" + num].sleeves.gotoandstop(10);
   this["shirt" + num].stripe1.gotoandstop(10);
}
if(team[r1] == "Reading")
{
   trace("HOOOOOOPS!");
   this["shirt" + num].hoops.gotoandstop(str);
   this["shirt" + num].hoops._visible = true;
   this["shirt" + num].stripe1._visible = false;
}
else
{
   this["shirt" + num].hoops._visible = false;
}
num = game * 2;
this["t" + num] = team[r2];
pos[num] = r2;
col = convert_col_to_number(colour[r2]);
slv = convert_col_to_number(sleeves[r2]);
str = convert_col_to_number(stripe1[r2]);
cla = convert_col_to_number(collar[r2]);
this["shirt" + num].gotoandstop(1);
this["shirt" + num].colour.gotoandstop(col);
this["shirt" + num].collar.gotoandstop(cla);
this["shirt" + num].sleeves.gotoandstop(slv);
this["shirt" + num].stripe1.gotoandstop(str);
if(team[r2] == "Blackburn")
{
   this["shirt" + num].colour.gotoandstop(10);
   this["shirt" + num].sleeves.gotoandstop(10);
   this["shirt" + num].stripe1.gotoandstop(10);
}
if(team[r2] == "Reading")
{
   trace("HOOOOOOPS!");
   this["shirt" + num].hoops.gotoandstop(str);
   this["shirt" + num].hoops._visible = true;
   this["shirt" + num].stripe1._visible = false;
}
else
{
   this["shirt" + num].hoops._visible = false;
}
