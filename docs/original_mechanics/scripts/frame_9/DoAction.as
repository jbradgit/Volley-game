function saved_check()
{
   hitkeeper = 0;
   if(keeps.hittest(ball._x,ball._y,true))
   {
      hitkeeper = 1;
   }
   if(keeps.hittest(ball._x - 10,ball._y - 8,true))
   {
      hitkeeper = 1;
   }
   if(keeps.hittest(ball._x + 10,ball._y - 8,true))
   {
      hitkeeper = 1;
   }
   if(keeps.hittest(ball._x,ball._y - 15,true))
   {
      hitkeeper = 1;
   }
   if(keeps.hittest(ball._x,ball._y - 7,true))
   {
      hitkeeper = 1;
   }
   if(keeps.hittest(ball._x - 5,ball._y - 5,true))
   {
      hitkeeper = 1;
   }
   if(keeps.hittest(ball._x + 5,ball._y - 5,true))
   {
      hitkeeper = 1;
   }
   if(keeps.hittest(ball._x,ball._y + 3,true))
   {
      hitkeeper = 1;
   }
   if(hitkeeper == 0)
   {
      trace("not hit keeper bill");
   }
   else
   {
      trace("borft keeper");
      peep.gotoandplay("near_miss");
   }
   trace("dbx = " + dbx);
   if(dbx > 1 and xball < 170)
   {
      leftcorner = 1;
      rightcorner = 0;
      corner = 1;
      trace("left corner");
   }
   if(dbx < 1 and xball > 400)
   {
      rightcorner = 1;
      leftcorner = 0;
      corner = 1;
      trace("right corner");
   }
   if(z > 75)
   {
      trace("top net set to 1 when z = " + z);
      topnet = 1;
      znet = z;
   }
}
t += 0.06;
if(booted == 0)
{
   yball = 300;
   xball = 0 + y * 10;
   y = cangle * velocity * t + bounce;
   z = sangle * velocity * t - 5 * t * t;
   z *= 10;
   if(z < 0)
   {
      trace("bounce");
      t = 0;
      bounce = y;
      bounced = 2;
      bounceyball = yball - 200;
      velocity *= 0.7;
      z = 0;
   }
   yscale = 10 + 90 * yball / 325;
}
else if(innet == false)
{
   xball -= dbx;
   yball -= ybit;
   z += dby / 13;
   yscale = 10 + 90 * yball / 325;
   if(yball < 160 and checked == false)
   {
      saved_check();
      checked = true;
      trace("xball = " + xball);
      trace("z = " + z);
      if(hitkeeper == 0)
      {
         trace("lpost " + Math.abs(xball - lpost));
         trace("rpost " + Math.abs(xball - rpost));
         trace("bar " + (barpos - ball._y));
         if(Math.abs(xball - rpost) < posttolerance and z < barh)
         {
            rposthit = true;
            trace("post--r");
            ybit = - ybit;
            dbx = -10;
            score += 150 / bounced;
            crink.gotoandplay(2);
            if(random(10) > 5)
            {
               peep.gotoandplay("near_miss");
            }
         }
         if(Math.abs(xball - lpost) < posttolerance and z < barh)
         {
            lposthit = true;
            trace("post--l");
            ybit = - ybit;
            dbx = 10;
            score += 150 / bounced;
            crink.gotoandplay(2);
            if(random(10) > 5)
            {
               peep.gotoandplay("near_miss");
            }
         }
         if(z >= barh - 15 and z <= barh and xball > lpost and xball < rpost)
         {
            if(lposthit or rposthit)
            {
               hitbar = false;
            }
            else
            {
               hitbar = true;
               trace("bar !!!!");
               ybit = ybit;
               dbx = dbx;
               dby = 10;
               score += 150 / bounced;
               crink.gotoandplay(2);
               if(random(10) > 5)
               {
                  peep.gotoandplay("near_miss");
               }
            }
         }
         if(xball > lpost and xball < rpost and z < barh and rposthit == false and lposthit == false and hitbar == false)
         {
            lposthit = false;
            rposthit = false;
            hitbar = false;
            innet = true;
            trace("GOOOOOOOOOAAAAAAAALLLLLLLLLL");
         }
      }
      else
      {
         score += 300 / bounced;
         if(divedirn == "left")
         {
            ybit = - ybit;
            dbx = 10;
            dby = - dby;
         }
         else
         {
            ybit = - ybit;
            dbx = -10;
            dby = - dby;
         }
         if(no_dive)
         {
            trace("zzz=" + z);
            if(z < 30)
            {
               keeps.gotoandstop("low_catch");
            }
            else if(z < 60)
            {
               keeps.gotoandstop("mid_catch");
            }
            else
            {
               keeps.gotoandstop("high_catch");
            }
            held = true;
         }
      }
   }
}
else
{
   xball -= dbx;
   yball -= 6;
   z += dby / 12;
   yscale = 10 + 90 * yball / 325;
   if(rightcorner == 1)
   {
      trace("RIGHTCORNER");
      dbx = 10;
      rightcorner = 0;
   }
   if(leftcorner == 1)
   {
      trace("leftCORNER********");
      dbx = -10;
      leftcorner = 0;
   }
   if(topnet == 1)
   {
      trace("top of the net !");
      z = znet - 20;
   }
   if(yball < 150)
   {
      end = 1;
      score += 4000 / bounced;
      sc = 1;
      _level0.goalnet.gotoandplay("goal");
      _level0.peep.gotoandplay("goal");
      time_to_next_goal++;
      wenger_is_a_poof += String(bounced - 1);
      jim = random(2) + 1;
      jimb = 1;
      while(jimb <= jim)
      {
         j2im = random(3);
         numlarry = new Array("2","3","4","5");
         wenger_is_a_poof += numlarry[j2im];
         jimb++;
      }
   }
}
if(yball < 100)
{
   end = 1;
}
if(hitbar)
{
   if(z > 200)
   {
      end = 1;
   }
}
if(lposthit or rposthit or hitkeeper == 1)
{
   if(yball > 200)
   {
      end = 1;
   }
}
if(held)
{
   ball._visible = false;
   ball2._visible = false;
   shadow._visible = false;
}
else
{
   if(yball < 130)
   {
      shadow._visible = false;
   }
   else
   {
      shadow._visible = true;
   }
   if(innet == false)
   {
      setProperty("/ball", _Y, yball - z);
      setProperty("/ball", _X, xball);
      setProperty("/ball", _xscale, yscale * 0.8);
      setProperty("/ball", _yscale, yscale * 0.8);
      ball2._visible = false;
      ball._visible = true;
   }
   else
   {
      setProperty("/ball2", _Y, yball - z);
      setProperty("/ball2", _X, xball);
      setProperty("/ball2", _xscale, yscale);
      setProperty("/ball2", _yscale, yscale);
      ball._visible = false;
      ball2._visible = true;
   }
   setProperty("/shadow", _Y, yball);
   setProperty("/shadow", _X, xball);
   setProperty("/shadow", _xscale, yscale);
   setProperty("/shadow", _yscale, yscale);
}
