if(!man1chk and shadow._y < 240)
{
   man1chk = true;
   trace("CHECK***********");
   if(opponent1.man.hitTest(ball._x,ball._y,false))
   {
      dbx -= 10 + random(8);
      man1chk = 2;
   }
}
if(!man2chk and shadow._y < 200)
{
   man2chk = true;
   trace("CHECK***********");
   if(opponent2.man.hitTest(ball._x,ball._y,false))
   {
      dbx -= 20 + random(8);
      man2chk = 2;
   }
}
if(!man3chk and shadow._y < 200)
{
   man3chk = true;
   trace("CHECK***********");
   if(opponent3.man.hitTest(ball._x,ball._y,false))
   {
      dbx = dbx + 10 + random(8);
      man3chk = 2;
   }
}
if(_level0.kicked == true and cchecked == false and man.finished)
{
   cchecked = true;
   dbx = man._x + 15 - xball;
   dby = z;
   diag = int(dbx);
   trace("BANG!" + z + " " + dbx);
   if(z < 40 and Math.abs(dbx) < 30)
   {
      booted = true;
      innet = false;
      score += 100 / bounced;
      shotsnd.gotoandPlay(2);
   }
   else
   {
      complete_miss = true;
   }
}
dby = z;
if(dive and no_dive)
{
   if(destination > keeps._x)
   {
      keeps._x += 1;
   }
   if(destination < keeps._x)
   {
      keeps._x -= 1;
   }
}
if(booted == true and dive == false)
{
   dive = true;
   destination = xball - 18 * dbx;
   divedirn = "up";
   if(random(10) < 8)
   {
      if(destination > 310 and destination < 500)
      {
         divedirn = "right";
         keeps.gotoandplay("dive_right");
         no_dive = false;
      }
      if(destination < 250 and destination > 50)
      {
         no_dive = false;
         divedirn = "left";
         keeps.gotoandplay("dive_left");
      }
   }
}
if(t > 7)
{
   end = 1;
}
if(score > 25000)
{
   evel = keane.eve;
}
if(end == 0 and xball < 600)
{
   gotoAndStop("mainloop");
   play();
}
