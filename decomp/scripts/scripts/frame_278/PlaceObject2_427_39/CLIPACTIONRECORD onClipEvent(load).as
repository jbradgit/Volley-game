onClipEvent(load){
   _level0.players = "Loading";
   _level0.scores = "Scores";
   a = _level0.tcat;
   b = _level0.mb1;
   bb = _level0.total_r;
   c = _level0.name;
   d = _level0.total_po;
   e = _level0.total_pt;
   evel = _level0.evel;
   eve = _level0.eve;
   vel = _level0.vel;
   command = "update";
   if(_level0.locked)
   {
      this.loadVariables("lfc_vseason.php3?" + int(Math.random() * 100000),"POST");
      _level0.locked = false;
   }
}
