function trim_name(name_in)
{
   var _loc1_ = name_in;
   last_char = _loc1_.charAt(_loc1_.length - 1);
   extra_spaces = 0;
   if(last_char == " ")
   {
      do
      {
         extra_spaces++;
         last_char = _loc1_.charAt(_loc1_.length - extra_spaces - 1);
      }
      while(last_char == " ");
      name_out = _loc1_.substring(0,_loc1_.length - extra_spaces);
   }
   else
   {
      name_out = _loc1_;
   }
   return name_out;
}
function convert_col_to_number(team_in)
{
   var _loc1_ = team_in;
   if(_loc1_ == "red")
   {
      rcol = 1;
   }
   if(_loc1_ == "white")
   {
      rcol = 2;
   }
   if(_loc1_ == "blue")
   {
      rcol = 3;
   }
   if(_loc1_ == "black")
   {
      rcol = 4;
   }
   if(_loc1_ == "yellow")
   {
      rcol = 5;
   }
   if(_loc1_ == "green")
   {
      rcol = 6;
   }
   if(_loc1_ == "claret")
   {
      rcol = 7;
   }
   if(_loc1_ == "skyblue")
   {
      rcol = 8;
   }
   if(_loc1_ == "orange")
   {
      rcol = 9;
   }
   if(_loc1_ == "rovers")
   {
      rcol = 10;
   }
   return rcol;
}
function add_new_team(add_rating, add_st, add_name, add_colour, add_shorts, add_socks, add_socks_top, add_stripe, add_sleeves, add_collar, add_song)
{
   team_id_count++;
   thid = team_id_count;
   rating[thid] = add_rating;
   shirt_type[thid] = add_st;
   team[thid] = add_name;
   colour[thid] = add_colour;
   collar[thid] = add_collar;
   shorts[thid] = add_shorts;
   stripe1[thid] = add_stripe;
   sleeves[thid] = add_sleeves;
   socks[thid] = add_socks;
   socks_top[thid] = add_socks_top;
   best_song[thid] = add_song;
   t_available[thid] = true;
   t_map[thid] = thid;
   trace(add_name);
}
game_id = 10;
played = new Array(20);
won = new Array(20);
drawn = new Array(20);
lost = new Array(20);
pts = new Array(20);
for_goals = new Array(20);
against_goals = new Array(20);
player_played = new Array(23);
player_goals = new Array(23);
player_sub_used = new Array(23);
player_name = new Array(23);
manager_rating = 0;
high_threshold = 16000;
low_threshold = 3000;
team = new Array();
picked = new Array();
pos = new Array();
v = new Array();
rating = new Array();
teams = 20;
message = "";
colour = new Array();
map_colour = new Array();
stripe1 = new Array();
sleeves = new Array();
collar = new Array();
shorts = new Array();
socks = new Array();
games = teams / 2;
maxgames = games;
selected = false;
last_team = new Array(16);
first_time_pick = true;
last_formation = "none";
t_available = new Array(32);
t_map = new Array(32);
shirt_type = new Array();
team_id_count = 0;
add_new_team(10,"sleeves","Arsenal","red","white","white","red","red","white","white","We won the league at White Hart Lane!");
add_new_team(6,"sleeves","Aston Villa","claret","white","claret","claret","claret","skyblue","claret","O\'Leary !");
add_new_team(4,"hoops","Reading","blue","blue","blue","white","white","blue","white","Come on you Blues !");
add_new_team(7,"stripe","Newcastle","black","black","black","white","white","black","black","there\'s only 1 James Milner...");
add_new_team(9,"plain","Chelsea","blue","blue","white","white","blue","blue","white","There\'s only 1 Kezman!");
add_new_team(5,"plain","Fulham","white","black","white","black","white","white","black","Al Fayed\'s Black and White Army!");
add_new_team(7,"plain","Everton","blue","white","blue","white","blue","blue","blue","ROONEY ! ROONEY !");
add_new_team(4,"stripe","Sunderland","white","black","red","black","red","white","white","THE LORDS MY SHEPHERD !");
add_new_team(9,"plain","Liverpool FC","red","red","red","white","red","red","red","1 Michael Owen?");
add_new_team(4,"plain","Middlesbro","red","red","red","white","red","red","red","EIO EIO EIO EIO !");
add_new_team(5,"stripe","Wigan","blue","blue","white","blue","white","blue","blue","1 Darren Huckerby!");
add_new_team(10,"plain","Man Utd","red","white","black","white","red","red","red","There\'s only 1 Ronaldo!");
add_new_team(5,"plain","Tottenham","white","darkblue","white","darkblue","white","white","white","Keano ! there\'s only 1 Keano");
add_new_team(6,"halves","Blackburn","white","blue","blue","white","blue","blue","blue","Souness\' Blue and White Army !");
add_new_team(6,"sleeves","West Ham","claret","white","claret","claret","claret","skyblue","claret","Oh when the Saints go marching in!");
add_new_team(5,"plain","Bolton","white","white","white","blue","white","white","white","We are the 1 and only Wanderers!");
add_new_team(1,"plain","Derby","white","black","white","black","white","white","white","EEEEEEEEEAGLES !");
add_new_team(3,"plain","Birmingham","blue","white","white","blue","blue","blue","blue","Come on you Addicks");
add_new_team(7,"plain","Man City","skyblue","white","skyblue","white","skyblue","skyblue","skyblue","Blue Moon - I saw you standing alone");
add_new_team(6,"plain","Portsmouth","blue","white","red","white","blue","blue","white","Harry & Jim, Premier League !");
i = 1;
while(i <= teams)
{
   team[i] = trim_name(team[i]);
   i++;
}
players = new Array(20);
best_song = new Array(20);
the_draw = new Array(-99,1,7,4,8,12,24,6,5,11,17,30,13,14,3,21,25,15,32,23,27,28,18,31,20,26,10,29,16,2,9,22,19);
real_score = new Array(-99,5,1,1,2,6,0,0,4,4,1,2,0,2,3,1,0,2,1,1,0,3,0,4,3,0,3,1,0,2,1,2,0);
our_player = new Array(23);
best_pos = new Array(23);
best_side = new Array(23);
quirk = new Array(23);
description = new Array(23);
our_player_rating = new Array(23);
fixture_list = new Array();
fixture_list[1] = "11 Aug 2007 02v0916v0417v2007v1110v1408v1315v19";
fixture_list[2] = "12 Aug 2007 01v0605v1812v03";
fixture_list[3] = "14 Aug 2007 18v0813v0704v0109v15";
fixture_list[4] = "15 Aug 2007 14v0206v1619v1720v1203v0511v10";
fixture_list[5] = "18 Aug 2007 18v1514v0106v1004v0220v1603v0713v1711v08";
fixture_list[6] = "19 Aug 2007 09v0519v12";
fixture_list[7] = "25 Aug 2007 01v1902v0616v0305v2017v1807v1408v0915v11";
fixture_list[8] = "26 Aug 2007 12v1310v04";
fixture_list[9] = "01 Sep 2007 14v1916v0706v1309v1712v0810v1804v1103v15";
fixture_list[10] = "02 Sep 2007 01v2002v05";
fixture_list[11] = "15 Sep 2007 18v1605v1407v1220v0908v0313v0115v1011v06";
fixture_list[12] = "16 Sep 2007 19v02";
fixture_list[13] = "17 Sep 2007 17v04";
fixture_list[14] = "22 Sep 2007 01v1714v2006v1909v1810v0803v11";
fixture_list[15] = "23 Sep 2007 02v0716v1312v0504v15";
fixture_list[16] = "29 Sep 2007 18v1205v0617v1619v0420v0308v1415v0111v09";
fixture_list[17] = "30 Sep 2007 07v10";
fixture_list[18] = "01 Oct 2007 13v02";
fixture_list[19] = "06 Oct 2007 02v1514v1812v11";
fixture_list[20] = "07 Oct 2007 01v0816v0506v2009v1319v1004v0703v17";
fixture_list[21] = "20 Oct 2007 01v1602v1214v0307v0906v1719v1810v0511v20";
fixture_list[22] = "21 Oct 2007 15v08";
fixture_list[23] = "22 Oct 2007 04v13";
fixture_list[24] = "27 Oct 2007 18v1105v1917v0712v1020v1503v0408v0613v14";
fixture_list[25] = "28 Oct 2007 16v0209v01";
fixture_list[26] = "03 Nov 2007 01v1202v1714v0907v1806v0310v1304v2011v05";
fixture_list[27] = "04 Nov 2007 15v16";
fixture_list[28] = "05 Nov 2007 19v08";
fixture_list[29] = "10 Nov 2007 16v1005v0717v1509v0612v1408v0413v11";
fixture_list[30] = "11 Nov 2007 18v0220v19";
fixture_list[31] = "12 Nov 2007 03v01";
fixture_list[32] = "24 Nov 2007 01v1118v2016v1217v0507v0819v0310v0204v09";
fixture_list[33] = "25 Nov 2007 06v1415v13";
fixture_list[34] = "01 Dec 2007 02v0114v0405v1509v1612v0620v0703v1008v1713v1811v19";
fixture_list[35] = "08 Dec 2007 02v2014v1516v1105v0807v0612v1710v0104v1803v0913v19";
fixture_list[36] = "15 Dec 2007 01v0518v0317v1006v0409v1219v1620v1308v0215v0711v14";
fixture_list[37] = "22 Dec 2007 01v1302v1914v0516v1806v1109v2012v0710v1504v1703v08";
fixture_list[38] = "26 Dec 2007 18v1005v0217v0907v1619v1420v0108v1213v0615v0311v04";
fixture_list[39] = "29 Dec 2007 18v0605v0417v1407v0119v0920v1008v1613v0315v1211v02";
fixture_list[40] = "01 Jan 2008 01v1502v1314v0816v1706v0509v1112v1810v0704v1903v20";
fixture_list[41] = "12 Jan 2008 01v1802v0316v1405v1317v1107v1912v0410v0908v2015v06";
fixture_list[42] = "19 Jan 2008 18v0514v1006v0109v0219v1504v1620v1703v1213v0811v07";
fixture_list[43] = "29 Jan 2008 01v0416v0617v1910v1108v1815v09";
fixture_list[44] = "30 Jan 2008 02v1405v0307v1312v20";
fixture_list[45] = "02 Feb 2008 18v1714v0706v0209v0819v0104v1020v0503v1613v1211v15";
fixture_list[46] = "09 Feb 2008 01v1402v0416v2005v0917v1307v0310v0608v1115v18";
fixture_list[47] = "10 Feb 2008 12v19";
fixture_list[48] = "23 Feb 2008 18v0114v1606v1509v1019v0704v1220v0803v0213v0511v17";
fixture_list[49] = "01 Mar 2008 01v0218v1316v0917v0807v2006v1219v1110v0304v1415v05";
fixture_list[50] = "08 Mar 2008 02v1014v0605v1709v0412v1620v1803v1908v0713v1511v01";
fixture_list[51] = "15 Mar 2008 01v1018v0417v1206v0709v0319v1320v0208v0515v1411v16";
fixture_list[52] = "22 Mar 2008 02v0814v1116v1905v0107v1512v0910v1704v0603v1813v20";
fixture_list[53] = "29 Mar 2008 18v1916v0105v1017v0609v0712v0220v1103v1408v15";
fixture_list[54] = "30 Mar 2008 13v04";
fixture_list[55] = "05 Apr 2008 01v0902v1614v1306v0819v0510v1204v0315v2011v18";
fixture_list[56] = "06 Apr 2008 07v17";
fixture_list[57] = "12 Apr 2008 18v0716v1505v1117v0209v1412v0120v0403v0608v1913v10";
fixture_list[58] = "19 Apr 2008 01v0314v1207v0506v0919v2010v1604v0815v1711v13";
fixture_list[59] = "20 Apr 2008 02v18";
fixture_list[60] = "26 Apr 2008 18v0905v1217v0107v0219v0620v1408v1013v1615v0411v03";
fixture_list[61] = "03 May 2008 01v0702v1114v1716v0806v1809v1912v1510v2004v0503v13";
fixture_list[62] = "11 May 2008 18v1405v1617v0307v0410v1920v0608v0113v0915v0211v12";
max_fixture_game = 62;
