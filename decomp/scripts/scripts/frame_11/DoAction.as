rotator.gotoandplay(rotator.next);
dminute = (10 - attempts) * 10 + 10;
this_cyc_count = 0;
save_score_flash = score_flash;
score_flash = "";
check_g = next_goal;
while(check_g <= total_gs)
{
   if(dminute >= goal_flash_time[check_g])
   {
      score_flash += goal_flash_score[check_g] + "\r";
      next_goal = check_g + 1;
      this_cyc_count++;
      if(this_cyc_count >= 2)
      {
         break;
      }
   }
   check_g++;
}
if(this_cyc_count == 0)
{
   score_flash = save_score_flash;
}
if(random(100) > 50)
{
   opponent1.man.head.gotoandstop("lookright");
}
else
{
   opponent1.man.head.gotoandplay("blink");
}
if(random(100) > 50)
{
   opponent2.man.head.gotoandstop("lookright");
}
else
{
   opponent2.man.head.gotoandplay("blink");
}
if(random(100) > 50)
{
   opponent3.man.head.gotoandstop("lookright");
}
else
{
   opponent3.man.head.gotoandplay("blink");
}
if(sc == 1)
{
   songtxt = song;
   if(random(100) > 10)
   {
      r_message = new Array();
      r_message[0] = "Look Out!";
      r_message[1] = "Rush-like Shooting!!";
      r_message[2] = "I could do better than that";
      r_message[3] = "Who are ya?";
      r_message[4] = "How much do you get paid?";
      r_message[5] = "It\'s a game of 2 halves";
      r_message[6] = "Anything can happen over 90 minutes";
      r_message[7] = "Jumpers for goalposts";
      r_message[8] = "Offside! But not interfering with play";
      r_message[9] = "Come on ref!";
      r_message[10] = "Shocking defending";
      r_message[11] = "Run away!";
      r_message[12] = "His foot\'s like a traction engine!";
      r_message[13] = "He\'s got football pie all over his face";
      r_message[14] = "This is too easy";
      r_message[15] = "Come on Linesman?";
      r_message[16] = "Ohh, the tension is mounting!";
      r_message[17] = "Ha ha!";
      r_message[18] = "Does my bum look big in this?";
      opponent2.bubble.message = r_message[random(19)];
      opponent2.bubble._visible = true;
   }
}
else
{
   songtxt = "";
}
mb2 = td;
if(complete_miss and random(100) > 50)
{
   opponent1.bubble.message = "Ha ha!";
   opponent1.bubble._visible = true;
}
if(random(100) > 90 and sc != 1)
{
   opponent3.bubble.message = "Who are ya?";
   opponent3.bubble._visible = true;
}
else
{
   if(man1chk == 2)
   {
      opponent1.bubble.message = "This is too easy!";
      opponent1.bubble._visible = true;
   }
   if(man2chk == 2)
   {
      opponent2.bubble.message = "I could do better than that";
      opponent2.bubble._visible = true;
   }
   if(man3chk == 2)
   {
      opponent3.bubble.message = "Look out!";
      opponent3.bubble._visible = true;
   }
}
