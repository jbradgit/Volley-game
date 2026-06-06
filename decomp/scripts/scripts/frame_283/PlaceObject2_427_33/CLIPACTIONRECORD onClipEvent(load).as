onClipEvent(load){
   _level0.players = "Loading";
   _level0.scores = "Scores";
   command = "init";
   this.loadVariables("lfc_vseason.php3?" + int(Math.random() * 100000),"POST");
}
