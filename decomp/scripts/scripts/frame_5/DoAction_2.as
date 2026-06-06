function opp_convert_col_to_hex(team_in)
{
   var _loc1_ = team_in;
   if(_loc1_ == "red")
   {
      rcol = 13369344;
   }
   if(_loc1_ == "white")
   {
      rcol = 16777215;
   }
   if(_loc1_ == "blue")
   {
      rcol = 13209;
      rcol = 13209;
   }
   if(_loc1_ == "black")
   {
      rcol = 0;
   }
   if(_loc1_ == "yellow")
   {
      rcol = 16763955;
   }
   if(_loc1_ == "grey")
   {
      rcol = 13421772;
   }
   if(_loc1_ == "green")
   {
      rcol = 3394560;
      rcol = 4692578;
      rcol = 26112;
   }
   if(_loc1_ == "claret")
   {
      rcol = 8650752;
   }
   if(_loc1_ == "skyblue")
   {
      rcol = 6737100;
   }
   if(_loc1_ == "orange")
   {
      rcol = 16750848;
   }
   if(_loc1_ == "rovers")
   {
      rcol = 16777215;
   }
   if(_loc1_ == "darkblue")
   {
      rcol = 2041655;
   }
   return rcol;
}
trace("set defenders up for " + team[my_opponents]);
myColor = new Color(_level0.opponent1.man.socks);
myColor.setRGB(opp_convert_col_to_hex(_level0.socks[_level0.my_opponents]));
myColor1 = new Color(_level0.opponent1.man.shorts);
myColor1.setRGB(opp_convert_col_to_hex(_level0.shorts[_level0.my_opponents]));
myColor2 = new Color(_level0.opponent1.man.shirt);
myColor2.setRGB(opp_convert_col_to_hex(_level0.colour[_level0.my_opponents]));
myColor3 = new Color(_level0.opponent1.man.sleeves);
myColor3.setRGB(opp_convert_col_to_hex(_level0.sleeves[_level0.my_opponents]));
myColor = new Color(_level0.opponent2.man.socks);
myColor.setRGB(opp_convert_col_to_hex(_level0.socks[_level0.my_opponents]));
myColor1 = new Color(_level0.opponent2.man.shorts);
myColor1.setRGB(opp_convert_col_to_hex(_level0.shorts[_level0.my_opponents]));
myColor2 = new Color(_level0.opponent2.man.shirt);
myColor2.setRGB(opp_convert_col_to_hex(_level0.colour[_level0.my_opponents]));
myColor3 = new Color(_level0.opponent2.man.sleeves);
myColor3.setRGB(opp_convert_col_to_hex(_level0.sleeves[_level0.my_opponents]));
myColor = new Color(_level0.opponent3.man.socks);
myColor.setRGB(opp_convert_col_to_hex(_level0.socks[_level0.my_opponents]));
myColor1 = new Color(_level0.opponent3.man.shorts);
myColor1.setRGB(opp_convert_col_to_hex(_level0.shorts[_level0.my_opponents]));
myColor2 = new Color(_level0.opponent3.man.shirt);
myColor2.setRGB(opp_convert_col_to_hex(_level0.colour[_level0.my_opponents]));
myColor3 = new Color(_level0.opponent3.man.sleeves);
myColor3.setRGB(opp_convert_col_to_hex(_level0.sleeves[_level0.my_opponents]));
myColor = new Color(_level0.opponent2.man.trim);
myColor.setRGB(opp_convert_col_to_hex(_level0.socks_top[_level0.my_opponents]));
myColor = new Color(_level0.opponent3.man.trim);
myColor.setRGB(opp_convert_col_to_hex(_level0.socks_top[_level0.my_opponents]));
myColor = new Color(_level0.opponent1.man.trim);
myColor.setRGB(opp_convert_col_to_hex(_level0.socks_top[_level0.my_opponents]));
if(shirt_type[my_opponents] == "middle")
{
   _level0.opponent1.man.stripe1.gotoandplay(2);
   _level0.opponent2.man.stripe1.gotoandplay(2);
   _level0.opponent3.man.stripe1.gotoandplay(2);
   myColor3 = new Color(_level0.opponent1.man.sleeves);
   myColor3.setRGB(opp_convert_col_to_hex(_level0.colour[_level0.my_opponents]));
   myColor3 = new Color(_level0.opponent2.man.sleeves);
   myColor3.setRGB(opp_convert_col_to_hex(_level0.colour[_level0.my_opponents]));
   myColor3 = new Color(_level0.opponent3.man.sleeves);
   myColor3.setRGB(opp_convert_col_to_hex(_level0.colour[_level0.my_opponents]));
}
else if(shirt_type[my_opponents] == "quarters")
{
   _level0.opponent1.man.stripe1.gotoandplay(3);
   _level0.opponent2.man.stripe1.gotoandplay(3);
   _level0.opponent3.man.stripe1.gotoandplay(3);
   myColor3 = new Color(_level0.opponent1.man.sleeves);
   myColor3.setRGB(opp_convert_col_to_hex(_level0.colour[_level0.my_opponents]));
   myColor3 = new Color(_level0.opponent2.man.sleeves);
   myColor3.setRGB(opp_convert_col_to_hex(_level0.colour[_level0.my_opponents]));
   myColor3 = new Color(_level0.opponent3.man.sleeves);
   myColor3.setRGB(opp_convert_col_to_hex(_level0.colour[_level0.my_opponents]));
}
else if(shirt_type[my_opponents] == "halves")
{
   trace("HALVES - opponent!");
   _level0.opponent1.man.stripe1.gotoandplay(5);
   _level0.opponent2.man.stripe1.gotoandplay(5);
   _level0.opponent3.man.stripe1.gotoandplay(5);
   myColor3 = new Color(_level0.opponent1.man.sleeves);
   myColor3.setRGB(opp_convert_col_to_hex(_level0.colour[_level0.my_opponents]));
   myColor3 = new Color(_level0.opponent2.man.sleeves);
   myColor3.setRGB(opp_convert_col_to_hex(_level0.colour[_level0.my_opponents]));
   myColor3 = new Color(_level0.opponent3.man.sleeves);
   myColor3.setRGB(opp_convert_col_to_hex(_level0.colour[_level0.my_opponents]));
}
else if(shirt_type[my_opponents] == "hoops")
{
   _level0.opponent1.man.stripe1.gotoandplay(4);
   _level0.opponent2.man.stripe1.gotoandplay(4);
   _level0.opponent3.man.stripe1.gotoandplay(4);
   myColor3 = new Color(_level0.opponent1.man.sleeves);
   myColor3.setRGB(opp_convert_col_to_hex(_level0.colour[_level0.my_opponents]));
   myColor3 = new Color(_level0.opponent2.man.sleeves);
   myColor3.setRGB(opp_convert_col_to_hex(_level0.colour[_level0.my_opponents]));
   myColor3 = new Color(_level0.opponent3.man.sleeves);
   myColor3.setRGB(opp_convert_col_to_hex(_level0.colour[_level0.my_opponents]));
}
else
{
   myColor3 = new Color(_level0.opponent1.man.sleeves);
   myColor3.setRGB(opp_convert_col_to_hex(_level0.sleeves[_level0.my_opponents]));
   myColor3 = new Color(_level0.opponent2.man.sleeves);
   myColor3.setRGB(opp_convert_col_to_hex(_level0.sleeves[_level0.my_opponents]));
   myColor3 = new Color(_level0.opponent3.man.sleeves);
   myColor3.setRGB(opp_convert_col_to_hex(_level0.sleeves[_level0.my_opponents]));
}
if(_level0.colour[_level0.my_opponents] != _level0.stripe1[_level0.my_opponents])
{
   myColor4 = new Color(_level0.opponent1.man.stripe1);
   myColor4.setRGB(opp_convert_col_to_hex(_level0.stripe1[_level0.my_opponents]));
   myColor4 = new Color(_level0.opponent2.man.stripe1);
   myColor4.setRGB(opp_convert_col_to_hex(_level0.stripe1[_level0.my_opponents]));
   myColor4 = new Color(_level0.opponent3.man.stripe1);
   myColor4.setRGB(opp_convert_col_to_hex(_level0.stripe1[_level0.my_opponents]));
}
else
{
   _level0.opponent1.man.stripe1._visible = false;
   _level0.opponent2.man.stripe1._visible = false;
   _level0.opponent3.man.stripe1._visible = false;
}
