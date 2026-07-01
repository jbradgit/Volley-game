pick_from_our_squad();
i = 1;
while(i <= 23)
{
   best_pos[i] = p_get_pos(our_player[i]);
   best_side[i] = p_get_side(our_player[i]);
   description[i] = p_get_description(our_player[i]);
   quirk[i] = p_get_quirk(our_player[i]);
   our_player[i] = p_get_name(our_player[i]);
   i++;
}
num = 1;
myteamid = MASTER_TEAM_ID;
i = myteamid;
myteam = team[myteamid];
myteamtrim = trim_name(myteam);
trace(myteam + "." + myteamtrim + "+");
col = convert_col_to_number(colour[i]);
str = convert_col_to_number(stripe1[i]);
slv = convert_col_to_number(sleeves[i]);
cla = convert_col_to_number(collar[i]);
eval("shirt" + num).gotoandstop(1);
eval("shirt" + num).colour.gotoandstop(col);
eval("shirt" + num).collar.gotoandstop(cla);
eval("shirt" + num).sleeves.gotoandstop(slv);
eval("shirt" + num).stripe1.gotoandstop(str);
message = "";
