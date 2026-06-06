trace("frame 25");
use_the_real_draw = false;
if(round == 1 and real_score[ig * 2 - 1] != -99 and use_the_real_draw)
{
   home = real_score[ig * 2 - 1];
   away = real_score[ig * 2];
}
else
{
   homeodds = new Array(10);
   scoreodds = new Array(10);
   score_hg = new Array(10);
   score_ag = new Array(10);
   homeodds[0] = 50;
   homeodds[1] = 55;
   homeodds[2] = 59;
   homeodds[3] = 63;
   homeodds[4] = 67;
   homeodds[5] = 73;
   homeodds[6] = 80;
   homeodds[7] = 85;
   homeodds[8] = 90;
   homeodds[9] = 95;
   homeodds[10] = 97;
   score_hg[0] = 1;
   score_ag[0] = 0;
   scoreodds[0] = 30;
   score_hg[1] = 2;
   score_ag[1] = 0;
   scoreodds[1] = 60;
   score_hg[2] = 2;
   score_ag[2] = 1;
   scoreodds[2] = 70;
   score_hg[3] = 3;
   score_ag[3] = 0;
   scoreodds[3] = 75;
   score_hg[4] = 3;
   score_ag[4] = 1;
   scoreodds[4] = 80;
   score_hg[5] = 3;
   score_ag[5] = 2;
   scoreodds[5] = 84;
   score_hg[6] = 4;
   score_ag[6] = 0;
   scoreodds[6] = 86;
   score_hg[7] = 4;
   score_ag[7] = 1;
   scoreodds[7] = 90;
   score_hg[8] = 4;
   score_ag[8] = 2;
   scoreodds[8] = 94;
   score_hg[9] = 4;
   score_ag[9] = 3;
   scoreodds[9] = 98;
   score_hg[10] = 5;
   score_ag[10] = random(4);
   scoreodds[10] = 100;
   difference = 1 + rating[tm1] - rating[tm2];
   minus = false;
   if(difference < 0)
   {
      difference = -1 * difference;
      minus = true;
   }
   ho = homeodds[difference];
   if(minus)
   {
      ho = 100 - ho;
   }
   scorenumber = random(100);
   score_random = random(100);
   trace("t1 = " + team[tm1] + " " + rating[tm1]);
   trace("t2 = " + team[tm2] + " " + rating[tm2]);
   found_scr = false;
   isc = 0;
   while(isc <= 10)
   {
      if(!found_scr)
      {
         if(score_random < scoreodds[isc])
         {
            gls1 = score_hg[isc];
            gls2 = score_ag[isc];
            found_scr = true;
         }
      }
      isc++;
   }
   if(scorenumber < ho)
   {
      home = gls1;
      away = gls2;
      if(random(100) < 30)
      {
         home = random(4);
         away = home;
      }
   }
   else
   {
      home = gls2;
      away = gls1;
      if(random(100) < 20)
      {
         home = 0;
         away = 0;
      }
   }
   trace(ig + " " + difference + " " + minus);
   if(difference > 4)
   {
      trace("shock possible!");
   }
   if(difference > 4 and !minus)
   {
      trace("away team shock ?");
      trace(home + "v" + away);
      if(away > home)
      {
         trace("SHOCK!");
         away = random(2) + 1;
         home = random(away);
      }
   }
   if(difference > 4 and minus)
   {
      trace("home team shock ?");
      trace(home + "v" + away);
      if(away < home)
      {
         trace("SHOCK!");
         home = random(2) + 1;
         away = random(home);
      }
   }
}
