round++;
goal_flash_time = new Array();
goal_flash_score = new Array();
goal_flash_scorer = new Array();
total_gs = 0;
heading = fixture_list[round].substr(0,12);
raw_len = fixture_list[round].length;
games = (raw_len - 12) / 5;
heading = heading.substr(3,3) + " " + heading.substr(7,4);
heading_text = new Array();
maxgames = 10;
i = 1;
while(i <= maxgames)
{
   num = i;
   this["v" + num] = "v";
   this["ag" + num] = "";
   this["hg" + num] = "";
   if(i > games)
   {
      this["v" + num] = "";
   }
   i++;
}
i = 1;
while(i <= teams)
{
   this["shirt" + i].gotoandstop(2);
   i++;
}
