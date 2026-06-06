if(yy.savescore == 1)
{
   if(ipb_score == undefined)
   {
      ipb_score = eval(_global.ipb_scoreVar);
   }
   xx = new LoadVars();
   xx.arcadegid = _root.ibpro_gameid;
   xx.gscore = ipb_score;
   xx.gname = _global.ipb_get_gname();
   xx.enscore = ipb_score * yy.randchar ^ yy.randchar2;
   xx.send("index.php?autocom=arcade&do=savescore","_self","POST");
   stop();
}
_global.ipbSend = function(ipb_score)
{
   _root._visible = false;
   _root.enabled = false;
   xx = new LoadVars();
   yy = new LoadVars();
   xx.sendAndLoad("index.php?autocom=arcade&do=verifyscore",yy,"POST");
};
