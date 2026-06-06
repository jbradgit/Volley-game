onClipEvent(keyDown){
   k = Key.getAscii();
   l++;
   if(k != e[l])
   {
      trace("nope");
      chance = false;
   }
   else
   {
      trace("yep");
      if(l == 5)
      {
         if(chance)
         {
            trace("yep!!!!");
            _level0.test_high_scores = true;
         }
      }
   }
}
