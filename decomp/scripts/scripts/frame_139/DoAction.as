if(selected)
{
   if(_level0.t_available[myteamid])
   {
      message = "";
   }
   else
   {
      message = "Only Leeds, LFC, NUFC, Arsenal, WHU, Blackburn,Chelsea & Man U are available\r";
      message += "Other teams will be available soon !";
      selected = false;
   }
}
if(!selected)
{
   gotoAndStop("loop");
   play();
}
