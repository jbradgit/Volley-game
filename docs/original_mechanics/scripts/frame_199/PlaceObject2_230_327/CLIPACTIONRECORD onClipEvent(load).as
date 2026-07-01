onClipEvent(load){
   function write_tables()
   {
      so = SharedObject.getLocal(_level0.savegamename,"/");
      so.data.round = _level0.round;
      so.data.myteam_id = _level0.myteamid;
      i = 1;
      while(i <= 20)
      {
         so.data["played" + i] = _level0.played[i];
         so.data["won" + i] = _level0.won[i];
         so.data["drawn" + i] = _level0.drawn[i];
         so.data["lost" + i] = _level0.lost[i];
         so.data["for_goals" + i] = _level0.for_goals[i];
         so.data["against_goals" + i] = _level0.against_goals[i];
         so.data["pts" + i] = _level0.pts[i];
         i++;
      }
      so.flush();
   }
   function write_player_tables()
   {
      so = SharedObject.getLocal(_level0.savegamename + "ps","/");
      i = 1;
      while(i <= 23)
      {
         so.data["played" + i] = _level0.player_played[i];
         so.data["goals" + i] = _level0.player_goals[i];
         so.data["sub" + i] = _level0.player_sub_used[i];
         so.data["name" + i] = _level0.player_name[i];
         i++;
      }
      so.flush();
   }
   function read_player_tables()
   {
      so = SharedObject.getLocal(_level0.savegamename + "ps","/");
      i = 1;
      while(i <= 23)
      {
         _level0.player_played[i] = so.data["played" + i];
         _level0.player_goals[i] = so.data["goals" + i];
         _level0.player_sub_used[i] = so.data["sub" + i];
         _level0.player_name[i] = so.data["name" + i];
         i++;
      }
   }
   function read_team()
   {
      trace("READ TEAM!");
      so = SharedObject.getLocal(_level0.savegamename,"/");
      _level0.myteamid = so.data.myteam_id;
   }
   function read_tables()
   {
      so = SharedObject.getLocal(_level0.savegamename,"/");
      _level0.round = so.data.round;
      _level0.myteamid = so.data.myteam_id;
      i = 1;
      while(i <= 20)
      {
         _level0.won[i] = so.data["won" + i];
         _level0.played[i] = so.data["played" + i];
         _level0.drawn[i] = so.data["drawn" + i];
         _level0.lost[i] = so.data["lost" + i];
         _level0.against_goals[i] = so.data["against_goals" + i];
         _level0.for_goals[i] = so.data["for_goals" + i];
         _level0.pts[i] = so.data["pts" + i];
         i++;
      }
   }
   function write_cookie(name, played, lost, won, goals, best)
   {
      var _loc1_ = name;
      trace("writing cookie......name : " + _loc1_);
      _loc1_ = "game" + _level0.game_id;
      so = SharedObject.getLocal(_loc1_,"/");
      so.data.name = _loc1_;
      so.data.f1 = best;
      so.data.f2 = played;
      so.data.f3 = won;
      so.data.f4 = lost;
      so.data.f5 = goals;
      so.flush();
   }
   function read_cookie()
   {
      name = "game" + _level0.game_id;
      so = SharedObject.getLocal(name,"/");
      if(so.data.name == null)
      {
         trace("FIRST TIME!");
         so.data.name = name;
         so.data.f1 = 0;
         so.data.f2 = 0;
         so.data.f3 = 0;
         so.data.f4 = 0;
         so.data.f5 = 0;
         so.flush();
         _level0.life_best = 0;
         _level0.life_goals = 0;
         _level0.life_lost = 0;
         _level0.life_won = 0;
         _level0.life_drawn = 0;
      }
      trace("reading cookie....");
      _level0.life_best = so.data.f1;
      _level0.life_played = so.data.f2;
      _level0.life_won = so.data.f3;
      _level0.life_lost = so.data.f4;
      _level0.life_goals = so.data.f5;
      txtName.Text = "Your Stats";
      txtplayed.Text = _level0.life_played;
      txtdefault.Text = _level0.life_drawn;
      txtwon.Text = _level0.life_won;
      txtlost.Text = Number(txtplayed.Text) - Number(txtwon.Text) - Number(txtdefault.Text);
   }
   _visible = true;
}
