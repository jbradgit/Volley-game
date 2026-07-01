onClipEvent(enterFrame){
   if(_parent.doneLoading == 0)
   {
      total = _parent._parent.getBytesTotal();
      isloaded = _parent._parent.getBytesLoaded();
      p = 100 * (isLoaded / total);
      _parent.bytes = int(isloaded / 1000) add " KB of " add int(total / 1000) add " KB";
      _parent.percent = int(p) add "% LOADED";
      _parent.bar._xscale = p;
      trace("....." + Number(p));
      if(Number(p) >= Number(100))
      {
         _parent._parent.gotoAndPlay(Number(2));
         _parent.gotoAndStop("off");
         _parent.doneLoading = 1;
      }
      else
      {
         _parent._parent.gotoAndPlay(Number(1));
      }
   }
}
