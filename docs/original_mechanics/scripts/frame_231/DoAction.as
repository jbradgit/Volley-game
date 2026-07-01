function show_all_the_scores()
{
   var _loc1_ = this;
   trace("games " + games);
   ig = 1;
   while(ig <= 10)
   {
      numh = ig * 2 - 1;
      numa = ig * 2;
      _loc1_["v" + ig] = "v";
      if(ig > games)
      {
         _loc1_["v" + ig] = "";
         _loc1_["t" + numh] = "";
         _loc1_["t" + numa] = "";
         _loc1_["hg" + num] = "";
         _loc1_["ag" + num] = "";
         _loc1_["shirt" + numh].gotoandstop(2);
         _loc1_["shirt" + numa].gotoandstop(2);
      }
      else
      {
         r1 = t1_slot[ig];
         r2 = t2_slot[ig];
         col = convert_col_to_number(colour[r1]);
         str = convert_col_to_number(stripe1[r1]);
         slv = convert_col_to_number(sleeves[r1]);
         cla = convert_col_to_number(collar[r1]);
         _loc1_["shirt" + numh].gotoandstop(1);
         _loc1_["shirt" + numh].colour.gotoandstop(col);
         _loc1_["shirt" + numh].collar.gotoandstop(cla);
         _loc1_["shirt" + numh].sleeves.gotoandstop(slv);
         _loc1_["shirt" + numh].stripe1.gotoandstop(str);
         if(team[r1] == "Blackburn")
         {
            _loc1_["shirt" + numh].colour.gotoandstop(10);
            _loc1_["shirt" + numh].sleeves.gotoandstop(10);
            _loc1_["shirt" + numh].stripe1.gotoandstop(10);
         }
         if(team[r1] == "Reading")
         {
            trace("HOOOOOOPS!");
            _loc1_["shirt" + numh].hoops.gotoandstop(str);
            _loc1_["shirt" + numh].hoops._visible = true;
            _loc1_["shirt" + numh].stripe1._visible = false;
         }
         else
         {
            _loc1_["shirt" + numh].hoops._visible = false;
         }
         col = convert_col_to_number(colour[r2]);
         slv = convert_col_to_number(sleeves[r2]);
         str = convert_col_to_number(stripe1[r2]);
         cla = convert_col_to_number(collar[r2]);
         _loc1_["shirt" + numa].gotoandstop(1);
         _loc1_["shirt" + numa].colour.gotoandstop(col);
         _loc1_["shirt" + numa].collar.gotoandstop(cla);
         _loc1_["shirt" + numa].sleeves.gotoandstop(slv);
         _loc1_["shirt" + numa].stripe1.gotoandstop(str);
         if(team[r2] == "Blackburn")
         {
            _loc1_["shirt" + numa].colour.gotoandstop(10);
            _loc1_["shirt" + numa].sleeves.gotoandstop(10);
            _loc1_["shirt" + numa].stripe1.gotoandstop(10);
         }
         if(team[r2] == "Reading")
         {
            trace("HOOOOOOPS!");
            _loc1_["shirt" + numa].hoops.gotoandstop(str);
            _loc1_["shirt" + numa].hoops._visible = true;
            _loc1_["shirt" + numa].stripe1._visible = false;
         }
         else
         {
            _loc1_["shirt" + numa].hoops._visible = false;
         }
         trace("****game " + ig + " " + scores_home[ig]);
         trace("home slot..." + home_slot[ig]);
         _loc1_["t" + numh] = home_slot[ig];
         _loc1_["t" + numa] = away_slot[ig];
         _loc1_["hg" + ig] = scores_home[ig];
         _loc1_["ag" + ig] = scores_away[ig];
      }
      ig++;
   }
}
trace("back again!!");
if(mtp)
{
   scores_home[my_fixure_id] = home;
   scores_away[my_fixure_id] = away;
}
if(mtp)
{
   if(s1tm1 == myteamid)
   {
      won[s1tm2]--;
      lost[s1tm1]--;
   }
   else
   {
      lost[s1tm2]--;
      won[s1tm1]--;
   }
   if(home > away)
   {
      won[s1tm1]++;
      lost[s1tm2]++;
   }
   else if(away > home)
   {
      won[s1tm2]++;
      lost[s1tm1]++;
   }
   else
   {
      drawn[s1tm1]++;
      drawn[s1tm2]++;
   }
}
