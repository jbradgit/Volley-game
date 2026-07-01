disable_check = true;
myURL = _url;
okDomain = "*";
okDomain1 = "*";
okDomain2 = "*";
okDomain3 = "*";
development_domain = "stotty";
if(myURL.indexOf(development_domain) != -1 or myURL.indexOf(okDomain) != -1 or myURL.indexOf(okDomain1) != -1 or myURL.indexOf(okDomain2) != -1 or myURL.indexOf(okDomain3) != -1 or disable_check)
{
   play();
}
else
{
   gotoAndStop("bad");
}
