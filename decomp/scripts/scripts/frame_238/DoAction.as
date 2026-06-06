trace("ROUND = " + round);
if(test_high_scores)
{
   max_fixture_game = 1;
}
if(round < max_fixture_game)
{
   i = 1;
   while(i <= teams)
   {
      num = i;
      this["t" + num] = "";
      i++;
   }
   gotoAndStop("nextround");
   play();
}
