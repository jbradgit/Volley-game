on(release){
   if(newsound.getVolume() == 0)
   {
      newsound.setVolume(100);
   }
   else
   {
      newsound.setVolume(0);
   }
}
