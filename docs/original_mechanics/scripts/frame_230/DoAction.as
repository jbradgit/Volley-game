trace("frame 32");
if(mtp)
{
   s = 1;
   while(s <= total_gs)
   {
      trace(goal_flash_time[s] + " " + goal_flash_score[s]);
      s++;
   }
   all_sd = false;
   while(!all_sd)
   {
      all_sd = true;
      s = 1;
      while(s <= total_gs - 1)
      {
         if(goal_flash_time[s] > goal_flash_time[s + 1])
         {
            temp = goal_flash_score[s];
            goal_flash_score[s] = goal_flash_score[s + 1];
            goal_flash_score[s + 1] = temp;
            temp = goal_flash_time[s];
            goal_flash_time[s] = goal_flash_time[s + 1];
            goal_flash_time[s + 1] = temp;
            all_sd = false;
         }
         s++;
      }
   }
   s = 1;
   while(s <= total_gs)
   {
      trace(goal_flash_time[s] + " " + goal_flash_score[s]);
      s++;
   }
   replay = false;
   gotoAndPlay(4);
}
