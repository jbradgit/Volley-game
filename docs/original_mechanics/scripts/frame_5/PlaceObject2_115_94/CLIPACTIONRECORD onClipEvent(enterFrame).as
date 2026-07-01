onClipEvent(enterFrame){
   if(!_level0.paused)
   {
      if(Key.isDown(39))
      {
         _level0.man._x += 5;
         eve += 1;
         if(_level0.man._x > 500)
         {
            _level0.man._x = 500;
         }
      }
      else if(Key.isDown(37))
      {
         _level0.man._x -= 5;
         eve += 1;
         if(_level0.man._x < 50)
         {
            _level0.man._x = 50;
         }
      }
      if(Key.isDown(32))
      {
         kick();
      }
   }
}
