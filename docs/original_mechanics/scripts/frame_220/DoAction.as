numh = ig * 2 - 1;
numa = ig * 2;
tm1 = pos[numh];
tm2 = pos[numa];
if(tm1 == myteamid or tm2 == myteamid)
{
   trace("my team is playing !!");
   mtp = true;
   if(tm1 == myteamid)
   {
      my_opponents = tm2;
      im_at_home = true;
   }
   else
   {
      my_opponents = tm1;
      im_at_home = false;
   }
   this_cycle = true;
   s1t1 = team[pos[numh]];
   s1t2 = team[pos[numa]];
   s1tm1 = tm1;
   s1tm2 = tm2;
}
else
{
   this_cycle = false;
   played[tm1]++;
   played[tm2]++;
}
