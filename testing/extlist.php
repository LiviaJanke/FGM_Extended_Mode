<?php

require("headfoot.php");

head("cluster","Extended Mode List");

if (isset($_GET["year"]))
	$year=$_GET["year"];
else
	$year="";

if (isset($_GET["sc"]))
	$sc=$_GET["sc"];
else
	$sc="";

echo("<FORM METHOD=GET ACTION=\"extlist.php\" >");

	echo("<B>Year</B><br>");

    echo("<SELECT NAME=\"year\" onchange=\"this.form.submit()\">");
    for($loop=1999;$loop<=date("Y");$loop++)
    {
	if ($loop==1999)
		echo "<OPTION VALUE=\"\">\r";
	else
	{
	        echo("<OPTION VALUE=$loop");
	       	if ($year==$loop)
	            echo(" SELECTED");
	        echo(">".$loop."\r");
	}
    }
    echo("</SELECT>\r");

echo "<P>";
	
echo("<B>Spacecraft</B><br>");
echo "<SELECT NAME=\"sc\" onchange=\"this.form.submit()\">";
for($loop=0;$loop<=4;$loop++)
{
	if ($loop==0)
	{
		echo "<OPTION VALUE=\"\">\r";
	}
	else
	{
		echo "<OPTION VALUE=$loop";
		if ($sc==$loop)
			echo " SELECTED";
		echo ">".$loop."\r";
	}
}
echo "</SELECT><P>\r";

echo "</FORM>";

// echo("<INPUT TYPE=SUBMIT NAME=BUTTON VALUE=\"Press for Extended Mode List\"><p>");


if (($year!="") && ($sc!=""))
{
$tmp="/tmp/ExtMdList_".getmypid();

echo "<H2>".$year." S/C ".$sc."</H2>";

// 0         1         2         3         4         5         6         7         8         9         0         1         2
// 0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
// ==== == == == == == ===                                    =========
// 2016-02-19T10:45:13.000Z 2016-02-18T18:55:15.353Z 2XFGM3401 2SFGMJ010 T S ** 1 TLM OPTION       01 SELECTION,X'C',None;
// 2016-02-19T10:45:55.000Z 2016-02-18T18:55:15.357Z 2XFGM3200 2SFGMJ064 T S ** 2 GENERAL ML 2     01 DATA_WORD,X'0',None;
//
// 2016-02-19T10:45:55.000Z 2SFGMJ064 <= In $command

$lastentry=0;
$lastexit=0;
$entrycnt=0;
$exitcnt=0;
$extcomm=array();
$wasentry=0;
$wasexit=0;
$nonsequential=0;
$bad=array();
$dumpcnt=0;
$extdumpcnt=0;
$wasexit=FALSE;
$noextdumpcnt=0;

$com="find /cluster/data/raw/".$year."/ -iname \"*.SCCH\" -exec strings {} \; | grep \"FGM\" | sort | uniq";
$p=popen($com,"rb");
while(($line=fgets($p))!==FALSE)
{
	$command=substr(trim($line),0,24)." ".substr(trim($line),60,9);

	if ((substr($command,25,1)==$sc) && ( (trim(substr($command,26))=="SFGMJ064") ||
	                                      (trim(substr($command,26))=="SFGMJ059") ||
	                                      (trim(substr($command,26))=="SFGMSEXT") ||
	                                      (trim(substr($command,26))=="SFGMM002") ) )
	{
		$t=mktime(substr($command,11,2),substr($command,14,2),substr($command,17,2),substr($command,5,2),substr($command,8,2),substr($command,0,4))+substr($command,20,3)/1000;
		if (($t-$lastentry)<10)
			continue;
		else
		{
			if ($wasexit)
			{
				$noextdumpcnt++;
				$extcomm[]=substr($command,0,24)." Entry <FONT COLOR=\"RED\">(no Dump)</FONT>";
			}
			else
			{
				$extcomm[]=substr($command,0,24)." Entry";
			}
			$entrycnt++;
			

			
			if ($wasentry)
			{
				$nonsequential++;
				$bad[]=date("Y-m-d",$t);
			}
			$wasentry=TRUE; $wasexit=FALSE;
			
		}
		$lastentry=$t;
		$wasexit=FALSE;
	}
	
	if ((substr($command,25,1)==$sc) && ( (trim(substr($command,26))=="SFGMJ065") ||
	                                      (trim(substr($command,26))=="SFGMJ050") ) )
	{
		$t=mktime(substr($command,11,2),substr($command,14,2),substr($command,17,2),substr($command,5,2),substr($command,8,2),substr($command,0,4))+substr($command,20,3)/1000;
		if (($t-$lastexit)<10)
			continue;
		else
		{
			$extcomm[]=substr($command,0,24)." Exit";
			$exitcnt++;
			if ($wasexit)
			{
				$nonsequential++;
				$bad[]=date("Y-m-d",$t);
			}
			$wasentry=FALSE; $wasexit=TRUE;
		}
		$lastexit=$t;
		$wasexit=TRUE;
	}

	if ((substr($command,25,1)==$sc) && (trim(substr($command,26))=="SFGMJ007"))
	{
		$t=mktime(substr($command,11,2),substr($command,14,2),substr($command,17,2),substr($command,5,2),substr($command,8,2),substr($command,0,4))+substr($command,20,3)/1000;
		if ($wasexit)
		{
//			$extcomm[]=substr($command,0,24)." MSA Dump".sprintf(" %0.1f",($t-$entry_time)/60);
			$extcomm[]=substr($command,0,24)." MSA Dump";
			$extdumpcnt++;
			$wasexit=FALSE;
		}
		$dumpcnt++;
	}
}

$extcomm=array_unique($extcomm); sort($extcomm);

if (count($extcomm)!=0)
{
echo "<PRE>";

echo "Entries       | ".$entrycnt."<BR>";
echo "Exits         | ".$exitcnt."<BR>";
echo "Ext Dumps     | ".$extdumpcnt."<BR>";
echo "Dumps         | ".$dumpcnt."<BR>";
echo "Missing Dumps | ";
if ($noextdumpcnt!=0)
	echo "<FONT COLOR=\"RED\">".$noextdumpcnt."</FONT>";
else
	echo "0";
echo "<BR>&nbsp;<BR>";

if ($entrycnt!=$exitcnt)
	echo "          <FONT COLOR=\"RED\"><B>Entry Exit count mismatch</B></FONT><BR>";
if ($nonsequential!=0)
	echo "          <FONT COLOR=\"RED\">".$nonsequential." Non-Alternating command".(($nonsequential!=1)?"s":"")."</B></FONT><BR>";
if (count($bad)!=0)
{
	echo "<FONT COLOR=\"RED\">";
	foreach($bad as $b)
		echo "            ".$b."<BR>";
	echo "</FONT><BR>";
}

// 0         1         2         3
// 0123456789012345678901234567890123
// ==== == == == == == ===  =--------
// 2016-02-19T10:45:55.000Z 2SFGMJ064 <= In $command

echo "<BR>";
//foreach($extcomm as $comm)
for($i=0;$i<count($extcomm);$i++)
{
//	echo $extcomm[$i];
	if (($i<(count($extcomm)-1)) && (substr($extcomm[$i],25,5)=="Entry") && (substr($extcomm[$i+1],25)=="Exit"))
	{
		echo $extcomm[$i];
		$entry_time=mktime(substr($extcomm[$i],11,2),substr($extcomm[$i],14,2),substr($extcomm[$i],17,2),substr($extcomm[$i],5,2),substr($extcomm[$i],8,2),substr($extcomm[$i],0,4))+substr($extcomm[$i],20,3)/1000;
		$exit_time=mktime(substr($extcomm[$i+1],11,2),substr($extcomm[$i+1],14,2),substr($extcomm[$i+1],17,2),substr($extcomm[$i+1],5,2),substr($extcomm[$i+1],8,2),substr($extcomm[$i+1],0,4))+substr($extcomm[$i+1],20,3)/1000;
		$duration=sprintf("%.2f",($exit_time-$entry_time)/3600);
		while (substr($duration,-1)=="0") $duration=substr($duration,0,-1);
		if (substr($duration,-1)==".") $duration=substr($duration,0,-1);
			printf(" %s hours",$duration);
		if (date("d",$exit_time)!=date("d",$entry_time))
			printf("<BR><FONT COLOR=\"#04F\" SIZE=\"-2\">&emsp;Midnight crossed</FONT>");
		echo "\r\n";
	}
	else if (substr($extcomm[$i],25)=="Exit")
	{
		echo $extcomm[$i]."\r\n";
//		echo "<HR WIDTH=\"300px\" ALIGN=\"LEFT\">";
	}
	else if (substr($extcomm[$i],25)=="MSA Dump")
	{
		echo "<FONT COLOR=\"#CCC\">";
		echo $extcomm[$i];
		echo "</FONT>\r\n";
	}
	else
		echo $extcomm[$i]." <FONT COLOR=\"RED\">(Unusual)</FONT>\r\n";
		
}
echo "</PRE>";
}
else
{
	echo "<PRE><FONT COLOR=\"#A0A0A0\"><I>No Extended Mode commanding</I></FONT></PRE>";
}
}
else
{
echo "Detects entry into Extended mode based upon SFGMJ064 SFGMJ059 SFGMSEXT SFGMM002 commands, and exits based upon these commands SFGMJ065 SFGMJ050.";

}
echo "<BR>&nbsp;<BR>";
foot("cluster");

?>
