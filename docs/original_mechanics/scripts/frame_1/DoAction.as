_global.ipb_get_gname = function()
{
   var _loc3_ = _root._url;
   var _loc5 = "";
   var _loc2_ = "";
   var _loc6 = _loc3_.lastIndexOf("\\") + 1;
   if(_loc6 == -1 || _loc6 == 0)
   {
      _loc6 = _loc3_.lastIndexOf("/") + 1;
   }
   var _loc1_ = _loc6;
   var _loc7 = String(_loc3_).length;
   while(_loc1_ < String(_loc3_).length)
   {
      _loc2_ = _loc3_.charAt(_loc1_);
      if(_loc2_ == ".")
      {
         break;
      }
      _loc5 += _loc2_;
      _loc1_ = _loc1_ + 1;
   }
   return _loc5;
};
ipb_gname = _global.ipb_get_gname();
xx = new LoadVars();
xx.onLoad = function(success)
{
   if(success)
   {
      _global.ipb_scoreVar = this.scoreVar;
   }
};
fname = "arcade/gamedata/" + ipb_gname + "/" + ipb_gname + ".txt";
xx.load(fname);
