function draw_bar()
{
   perc = 450 * score / my_win_target;
   if(perc > 450)
   {
      perc = 450;
   }
   slider.bar._x = startpoint + perc;
}
function show_flags()
{
   celticflag._visible = boselecta == "Celtic";
   if(boselecta == "Dunfermline" or boselecta == "Aberdeen" or boselecta == "Hibernian" or boselecta == "Partick T" or boselecta == "Livingston" or boselecta == "St Mirren" or boselecta == "East Fife" or boselecta == "Hearts" or boselecta == "Dundee Utd" or boselecta == "Dundee" or boselecta == "Motherwell" or boselecta == "Airdrie" or boselecta == "Kilmarnock")
   {
      celticflag._visible = true;
      celticflag.gotoandstop(2);
   }
   if(boselecta == "Rangers")
   {
      celticflag._visible = true;
      celticflag.gotoandstop(3);
   }
   if(boselecta == "Cardiff" or boselecta == "Wrexham")
   {
      celticflag._visible = true;
      celticflag.gotoandstop(4);
   }
   if(boselecta == "Swansea")
   {
      celticflag._visible = true;
      celticflag.gotoandstop(5);
   }
}
startpoint = slider.bar._x;
slider.bar._visible = false;
trace("START..." + startpoint);
draw_bar();
score_flash = "";
next_goal = 1;
last_checked = 0;
attempts = 10;
trace("kp" + keeps._xscale);
trace("kp" + keeps._yscale);
newsound = new Sound();
_level0.cityarewank = "cityarewank";
paused = false;
_quality = "medium";
keeps._yscale = 78 - (divvy - 1) * 2;
trace("game....." + myteamid);
trace("game....." + boselecta);
boselecta = "Liverpool FC";
myteamid = 9;
shorts[myteamid] = "red";
socks[myteamid] = "red";
man = eval(selected_player);
show_flags();
_level0.tcat = colour[myteamid];
time_to_next_goal = 0;
opponent1.bubble._visible = false;
opponent2.bubble._visible = false;
opponent3.bubble._visible = false;
if(td < 10)
{
   wenger_is_a_poof = " " + td1 + "goals";
}
else
{
   wenger_is_a_poof = td1 + "goals";
}
man._x = 450;
man._y = 300;
score = 0;
peep.gotoandplay("whistle");
songtxt = "";
