function do_the_tables()
{
   sorted = new Array(20);
   iteam = 1;
   while(iteam <= 20)
   {
      pts[iteam] = won[iteam] * 3 + drawn[iteam];
      sorted[iteam] = iteam;
      iteam++;
   }
   all_done = false;
   while(!all_done)
   {
      all_done = true;
      ti = 1;
      while(ti <= 19)
      {
         if(pts[sorted[ti]] < pts[sorted[ti + 1]])
         {
            all_done = false;
            temp = sorted[ti];
            sorted[ti] = sorted[ti + 1];
            sorted[ti + 1] = temp;
         }
         ti++;
      }
   }
}
function pad_name(name_in, len)
{
   wlength = name_in.length;
   name_out = name_in;
   extra_spaces = len - wlength;
   es = 1;
   while(es <= extra_spaces)
   {
      name_out += " ";
      es++;
   }
   return name_out;
}
do_the_tables();
winners = team[sorted[1]];
winningt = sorted[1];
trace("tOP " + winners + " " + winningt);
iteam = 1;
while(iteam <= 20)
{
   this["t" + iteam] = iteam + ".";
   if(iteam < 10)
   {
      this["t" + iteam] = iteam + ". ";
   }
   if(team[sorted[iteam]] == myteamtrim)
   {
      this["t" + iteam] += pad_name(team[sorted[iteam]],15).toUpperCase();
      total_r = random(100);
      total_po = total_r - iteam;
      total_pt = total_r - pts[sorted[iteam]];
      tot_po = iteam;
      tot_pt = pts[sorted[iteam]];
   }
   else
   {
      this["t" + iteam] += pad_name(team[sorted[iteam]],15);
   }
   this["t" + iteam] += pad_name(String(" P" + played[sorted[iteam]]),4);
   this["t" + iteam] += pad_name(String(" W" + won[sorted[iteam]]),4);
   this["t" + iteam] += pad_name(String(" D" + drawn[sorted[iteam]]),4);
   this["t" + iteam] += pad_name(String(" L" + lost[sorted[iteam]]),4);
   this["t" + iteam] += pad_name(String(" PTS" + pts[sorted[iteam]]),8);
   iteam++;
}
