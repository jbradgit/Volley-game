function get_scorer_for_goalflash(team_in, scorer_in)
{
   var _loc1_ = team_in;
   tmp_array = new Array(11);
   trace(players[_loc1_]);
   start_idx = 0;
   pix = 1;
   while(pix <= 11)
   {
      finish_idx = start_idx;
      while(finish_idx < 200)
      {
         if(players[_loc1_].substr(finish_idx,1) == "+")
         {
            break;
         }
         finish_idx++;
      }
      tmp_array[pix] = players[_loc1_].substr(start_idx,finish_idx - start_idx);
      trace(tmp_array[pix]);
      start_idx = finish_idx + 1;
      pix++;
   }
   return tmp_array[scorer_in];
}
function get_scorer_random()
{
   gsr = random(100);
   gsr_ret = 9;
   if(gsr > 50)
   {
      gsr_ret = random(2) + 10;
   }
   else if(gsr > 12)
   {
      gsr_ret = random(4) + 6;
   }
   else
   {
      gsr_ret = random(4) + 2;
   }
   trace("SCORER>>>" + gsr_ret);
   return gsr_ret;
}
trace("frame 27");
if(!this_cycle)
{
   scores_home[ig] = home;
   scores_away[ig] = away;
   start_gs = total_gs;
   iig = 1;
   while(iig <= home + away)
   {
      total_gs++;
      goal_flash_time[total_gs] = random(90) + 1;
      iig++;
   }
   all_sd = false;
   while(!all_sd)
   {
      all_sd = true;
      s = start_gs + 1;
      while(s <= total_gs - 1)
      {
         if(goal_flash_time[s] > goal_flash_time[s + 1])
         {
            temp = goal_flash_time[s];
            goal_flash_time[s] = goal_flash_time[s + 1];
            goal_flash_time[s + 1] = temp;
            all_sd = false;
         }
         s++;
      }
   }
   home_get = home;
   away_get = away;
   home_current = 0;
   away_current = 0;
   iig = 1;
   while(iig <= home + away)
   {
      maxn = home_get + away_get;
      gn = random(maxn) + 1;
      goal_scorers_num = get_scorer_random();
      if(gn <= home_get)
      {
         goal_scorers_name_h = "(" + goal_flash_time[start_gs + iig] + " mins)";
         goal_scorers_name_a = "";
         home_current++;
         home_get--;
      }
      else
      {
         goal_scorers_name_h = "";
         goal_scorers_name_a = "(" + goal_flash_time[start_gs + iig] + " mins)";
         away_get--;
         away_current++;
      }
      goal_flash_score[start_gs + iig] = trim_name(home_slot[ig]) + " " + home_current + " " + goal_scorers_name_h + " " + trim_name(away_slot[ig]) + " " + away_current + " " + goal_scorers_name_a;
      iig++;
   }
   if(home > away)
   {
      won[tm1]++;
      lost[tm2]++;
   }
   else if(away > home)
   {
      won[tm2]++;
      lost[tm1]++;
   }
   else
   {
      drawn[tm1]++;
      drawn[tm2]++;
   }
}
else
{
   my_fixure_id = ig;
}
ig++;
