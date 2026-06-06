onClipEvent(mouseUp){
   found = false;
   trace("up!!");
   i = 1;
   while(i <= _level0.tid)
   {
      box = eval("_level0.shirt" + i);
      boxx = _level0._xmouse - box._x;
      boxy = _level0._ymouse - box._y;
      diff = Math.sqrt(boxx * boxx + boxy * boxy);
      if(diff < 10 and !found)
      {
         _level0.myteamid = _level0.t_map[i];
         _level0.myteam = _level0.team[_level0.myteamid];
         found = true;
         _level0.selected = true;
      }
      i++;
   }
}
