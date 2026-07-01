onClipEvent(load){
   function write_game_cookie(game_id, f1, f2, f3, f4, f5, f6)
   {
      var _loc1_ = game_id;
      name = "game" + _loc1_;
      so = SharedObject.getLocal(name,"/");
      trace("writing cookie......name : " + _loc1_);
      so.data.game_id = _loc1_;
      so.data.f1 = f1;
      so.data.f2 = f2;
      so.data.f3 = f3;
      so.data.f4 = f4;
      so.data.f5 = f5;
      so.data.f6 = f6;
      so.flush();
   }
   function read_game_cookie(game_id)
   {
      name = "game" + game_id;
      so = SharedObject.getLocal(name,"/");
      if(so.data.game_id == null)
      {
         result = false;
         trace("no cookie....");
      }
      else
      {
         trace("cookie....");
         result = true;
         trace("reading cookie....");
         _level0.checker = so.data.game_id;
         _level0.f1 = so.data.f1;
         _level0.f2 = so.data.f2;
         _level0.f3 = so.data.f3;
         _level0.f4 = so.data.f4;
         _level0.f5 = so.data.f5;
         _level0.f6 = so.data.f6;
      }
      return result;
   }
   _visible = true;
}
