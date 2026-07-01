winners = trim_name(winners);
num = 1;
i = winningt;
trace("winningt=" + i);
col = convert_col_to_number(colour[i]);
str = convert_col_to_number(stripe1[i]);
slv = convert_col_to_number(sleeves[i]);
cla = convert_col_to_number(collar[i]);
eval("shirt" + num).gotoandstop(1);
eval("shirt" + num).colour.gotoandstop(col);
eval("shirt" + num).collar.gotoandstop(cla);
eval("shirt" + num).sleeves.gotoandstop(slv);
eval("shirt" + num).stripe1.gotoandstop(str);
if(team[i] == "Blackburn")
{
   this["shirt" + num].colour.gotoandstop(10);
   this["shirt" + num].sleeves.gotoandstop(10);
   this["shirt" + num].stripe1.gotoandstop(10);
}
if(team[i] == "Reading")
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
