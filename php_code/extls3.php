<?php

function rpad($x)
{
	// If 0x000 to 0xFFF just output, but with all three digits
	// if above 0xFFF (prob just 0xFFFF), output in red bold
	if ($x<0x1000)
		return(sprintf("%03X ",$x));
	elseif ($x==0xFFFF)
		return(sprintf("<B><FONT COLOR=\"#F00\">%04X</FONT></B>",$x));
	else
		return(sprintf("<FONT COLOR=\"GRAY\">%04X</FONT>",$x));
}

function lpad($x)
{
	// If 0x000 to 0xFFF just output, but with all three digits
	// if above 0xFFF (prob just 0xFFFF), output in red bold
	if ($x<0x1000)
		return(sprintf(" %03X",$x));
	elseif ($x==0xFFFF)
		return(sprintf("<B><FONT COLOR=\"#F00\">%04X</FONT></B>",$x));
	else
		return(sprintf("<FONT COLOR=\"GRAY\">%04X</FONT>",$x));
}




set_time_limit(600);

require("headfoot.php");
require("setgroup.php");
require("iso.php");

$mission="cluster";

head($mission,"Extended Mode File Listing");

echo "<P><I>The</I> &#9711; <I>links will output and append data to /tmp/ClusterExtMode on Alsvid. This will then need to be manually edited, and deleted prior to using again.</I></P>";

if (file_exists("/tmp/ClusterExtMode"))
	$tmpfilesize=filesize("/tmp/ClusterExtMode");
else
	$tmpfilesize=0;

echo "<P>Click <A HREF=\"DelExtTmpFile.php\" TARGET=\"_blank\"><B>Here</B></A> to delete /tmp/ClusterExtMode (Current Size ".$tmpfilesize." bytes).</P>";

if (isset($_GET["sc"]))
{
	$sc=$_GET["sc"]+0;
	if (($sc<1) || ($sc>4) || ($sc!=(int)$sc))
		$sc=3;
}
else
	$sc=3;

if (isset($_GET["year"]))
{
	$year=$_GET["year"]+0;
	if (($year<2000) || ($year>date("Y")) || ($year!=(int)$year))
		$year=date("Y");
}
else
	$year=date("Y");

if (isset($_GET["month"]))
{
	$month=$_GET["month"]+0;
	if (($month<1) || ($month>12) || ($month!=(int)$month))
		$month=date("m");
}
else
	$month=date("m");

if (isset($_GET["day"]))
{
	$day=$_GET["day"]+0;
	if (($day<1) || ($day>date("t",mktime(0,0,0,$month,1,$year)) || ($day!=(int)$day)))
		$day=date("d");
}
else
	$day=date("d");

if (isset($_GET["version"]))
{
	$version=$_GET["version"];
	if (($version!="A") && ($version!="B") && ($version!="C") && ($version!="K") && ($version!="Q"))
		$version="B";
}
else
	$version="B";


$filename=$_ENV["CLUSTER_RAW_DATA"]."/".sprintf("%04d",$year)."/".sprintf("%02d",$month)."/C".$sc."_".sprintf("%02d%02d%02d",$year-2000,$month,$day)."_".$version.".BS";

echo "<H2>".$filename."</H2>";

$data=file_get_contents($filename);

function byte($offset)
{
	global $data;
        return(ord(substr($data,$offset,1)));
}

$pntr=0;
$newdata="";
$originallength=strlen($data);

while($pntr<$originallength)
{
	$packetlen=((ord(substr($data,$pntr+9,1)))<<16)|(ord(substr($data,$pntr+10,1))<<8)|ord(substr($data,$pntr+11,1));
        $tmmode=ord(substr($data,$pntr+16,1))&0x0F;
        if ($tmmode==0x0F)
        {
		$newdata.=substr($data,$pntr,$packetlen+15);
        }
        $pntr+=$packetlen+15;
}

$data=$newdata; $length=strlen($data);
$pntr=0;

echo "File Length : ".$length." (from ".$originallength.")<BR>";


$prevevenlastreset=0xFFFF;
$prevoddlastreset= 0xFFFF;

echo "<PRE>";
echo "                                                                           Even                  Odd                   Prev Now\r\n";
echo "                                       Reset   Even            Odd         Prev This  This Next  Prev This  This Next  to   to\r\n";
echo "Position   Packet Time                 Cnt  Cnt Min Max    Cnt Min Max     Last 1st   Last 1st   Last 1st   Last 1st   Now  Next\r\n";
echo "========   =========================== ==== ============== ==============  ==== ====  ==== ====  ==== ====  ==== ====  ===  ===\r\n";
while($pntr<$length)
{
	$packetlen=(byte($pntr+9)<<16)|(byte($pntr+10)<<8)|byte($pntr+11);
	$tmmode=byte($pntr+16)&0x0F;
	$resetcnt=(byte($pntr+27)<<8)|byte($pntr+28);

	if ($tmmode==0x0F)
	{
	// Data is from $pntr+15 to $pntr+15+packetlen-1

		$evenrangelist=array_fill(0,4096,0);
		$oddrangelist=array_fill(0,4096,0);


		$evenvecs=0; $evenresetmin=0xFFF; $evenresetmax=0x0000; $evenvecszero=0;

		$prevrange=((byte($pntr+55)<<8)|byte($pntr+56))&0xFFF;
		for($i=1;$i<444;$i++)
		{
			$range=((byte($pntr+55+8*$i)<<8)|byte($pntr+56+8*$i))&0xFFF;
			if ($range>$evenresetmax)
				$evenresetmax=$range;
			if ($range<$evenresetmin)
				$evenresetmin=$range;
			$diff=$range-$prevrange;
			if (($diff==0) || ($diff==1) || ($diff==-4095))
			{
				$evenvecs++;
				if ($diff==0)
					$evenvecszero++;
			}
			$prevrange=$range;
			$evenrangelist[$range]=1;
		}

		$oddvecs=0; $oddresetmin=0xFFF; $oddresetmax=0x0000; $oddvecszero=0;

		$prevrange=((byte($pntr+51)<<8)|byte($pntr+52))&0xFFF;
		for($i=1;$i<445;$i++)
		{
			$range=((byte($pntr+51+8*$i)<<8)|byte($pntr+52+8*$i))&0xFFF;
			if ($range>$oddresetmax)
				$oddresetmax=$range;
			if ($range<$oddresetmin)
				$oddresetmin=$range;	
			$diff=$range-$prevrange;
			if (($diff==0) || ($diff==1) || ($diff==-4095))
			{
				$oddvecs++;
				if ($diff==0)
					$oddvecszero++;
			}
			$prevrange=$range;
			$oddrangelist[$range]=1;
		}
	
		printf("%8d | %s %04X %3d %03X-%03X ",$pntr,unix2iso(scet2unix(substr($data,$pntr+0,8))),$resetcnt,$evenvecs,$evenresetmin,$evenresetmax);
		if ($evenvecs>$oddvecs)	{ printf("<FONT COLOR=RED><B>E</B></FONT>"); $even1=1; } else { printf("<FONT COLOR=GREY>e</FONT>"); $even1=0; }
		if ( (($evenvecs-$evenvecszero)!=0) && (($evenvecs/($evenvecs-$evenvecszero))>15) && (($evenvecs/($evenvecs-$evenvecszero))<23) ) { printf("<FONT COLOR=RED><B>E</B></FONT>"); $even2=1; } else { printf("<FONT COLOR=GREY>e</FONT>"); $even2=0; }
		printf(" ");
		printf("%3d %03X-%03X ",$oddvecs,$oddresetmin,$oddresetmax);
		if ($evenvecs<$oddvecs)	{ printf("<FONT COLOR=RED><B>O</B></FONT>"); $odd1=1; } else { printf("<FONT COLOR=GREY>o</FONT>"); $odd1=0; }
		if ( (($oddvecs-$oddvecszero)!=0) && (($oddvecs/($oddvecs-$oddvecszero))>15) && (($oddvecs/($oddvecs-$oddvecszero))<23) ) { printf("<FONT COLOR=RED><B>O</B></FONT>"); $odd2=1; } else { printf("<FONT COLOR=GREY>o</FONT>"); $odd2=0; }

		printf("  ");

		// This is probably not a good measure
		/* 
		if ((($evenresetmax-$evenresetmin)>17) && (($evenresetmax-$evenresetmin)<27))
			printf("<FONT COLOR=RED>E</FONT>"); else printf("<FONT COLOR=GREY>e</FONT>");
		printf(" ");
		if ((($oddresetmax-$oddresetmin)>17) && (($oddresetmax-$oddresetmin)<27))
			printf("<FONT COLOR=RED>O</FONT>"); else printf("<FONT COLOR=GREY>o</FONT>");
		*/

		$evenfirstreset=    ((byte($pntr+55      )<<8)|byte($pntr+56      ))&0xFFF; // These is for this packet
		$oddfirstreset=     ((byte($pntr+51      )<<8)|byte($pntr+52      ))&0xFFF;
                $evenlastreset=     ((byte($pntr+55+8*443)<<8)|byte($pntr+56+8*443))&0xFFF;
                $oddlastreset=      ((byte($pntr+51+8*444)<<8)|byte($pntr+52+8*444))&0xFFF;
		if (($pntr+3611)<$length)
		{
		$nextevenfirstreset=((byte($pntr+55+3611 )<<8)|byte($pntr+56+3611 ))&0xFFF;
		$nextoddfirstreset= ((byte($pntr+51+3611 )<<8)|byte($pntr+52+3611 ))&0xFFF;
		}
		else
		{
			$nextevenfirstreset=0xFFFF; $nextoddfirstreset=0xFFFF;
		}	



		// Previous Odd Last Reset - Even First Reset       Even Last Reset - Next Odd Reset
		// Previous Even Last Reset - Odd First Reset       Odd Last Reset - Next Even Reset

		printf("%s-%s  " ,lpad($prevoddlastreset),rpad($evenfirstreset));
		printf("%s-%s  ",lpad($evenlastreset),rpad($nextoddfirstreset));

		printf("%s-%s  " ,lpad($prevevenlastreset),rpad($oddfirstreset));
		printf("%s-%s  ",lpad($oddlastreset),rpad($nextevenfirstreset));

		if ($pntr+3611>=$length)
		{
			$nextevenfirstreset=0xFFFF;
			$nextofffirstreset=0xFFFF;
		}


		$diff1=$evenfirstreset-$prevoddlastreset;
		$diff2=$oddfirstreset-$prevevenlastreset;

		if (($diff1==0) || ($diff1==1) || ($diff1==-4095))
		{
			printf("<FONT COLOR=\"BLUE\"><B>E</B></FONT>");
			$even3=1;
		}
		else
		{
			printf("<FONT COLOR=\"GREY\">e</FONT>");
			$even3=0;
		}
		printf(" ");
		if (($diff2==0) || ($diff2==1) || ($diff2==-4095))
		{
			printf("<FONT COLOR=\"BLUE\"><B>O</B></FONT>");
			$odd3=1;
		}
		else
		{
			printf("<FONT COLOR=\"GREY\">o</FONT>");
			$odd3=0;
		}

		printf("  ");
		$diff3=$nextevenfirstreset-$oddlastreset;
		$diff4=$nextoddfirstreset-$evenlastreset;

                if (($diff4==0) || ($diff4==1) || ($diff4==-4095))
		{
                        printf("<FONT COLOR=\"GREEN\"><B>E</B></FONT>");
			$even4=1;
		}
		else
		{
			printf("<FONT COLOR=\"GREY\">e</FONT>");
			$even4=0;
		}
                printf(" ");
                if (($diff3==0) || ($diff3==1) || ($diff3==-4095))
		{
                        printf("<FONT COLOR=\"GREEN\"><B>O</B></FONT>");
			$odd4=1;
		}
		else
		{
			printf("<FONT COLOR=\"GREY\">o</FONT>");
			$odd4=0;
		}

		$prevevenlastreset= $evenlastreset;
		$prevoddlastreset=  $oddlastreset;
	
		$goodeven=($even1 && $even2) && ($even3 || $even4);	
		$goododd =($odd1 && $odd2) && ($odd3 || $odd4);	

		printf("&emsp;");

printf("&emsp;<A TARGET=\"_BLANK\" HREF=\"extls32packet_A.php?sc=%d&year=%d&month=%d&day=%d&version=%s&offset=%d&type=even\" STYLE=\"text-decoration:none\"><FONT COLOR=\"BLUE\">&#9711;</FONT></A>&emsp;&emsp;",$sc,$year,$month,$day,$version,$pntr);
printf("<A TARGET=\"_BLANK\" HREF=\"extls32packet_A.php?sc=%d&year=%d&month=%d&day=%d&version=%s&offset=%d&type=odd\" STYLE=\"text-decoration:none\"><FONT COLOR=\"RED\">&#9711;</FONT></A>&emsp;&emsp;",$sc,$year,$month,$day,$version,$pntr);

		printf("<A TARGET=\"_BLANK\" HREF=\"extls32packet.php?sc=%d&year=%d&month=%d&day=%d&version=%s&offset=%d&type=even\">",$sc,$year,$month,$day,$version,$pntr);
		printf("<IMG VALIGN=\"middle\" SRC=\"block.php?data=");
		for($n=0;$n<4096;$n++) echo $evenrangelist[$n]?"1":"0";
		printf("%s\"></A>&emsp;",$goodeven?"&even":"");
		printf("<A TARGET=\"_BLANK\" HREF=\"extls32packet.php?sc=%d&year=%d&month=%d&day=%d&version=%s&offset=%d&type=odd\">",$sc,$year,$month,$day,$version,$pntr);
		printf("<IMG VALIGN=\"middle\" SRC=\"block.php?data=");
		for($n=0;$n<4096;$n++) echo $oddrangelist[$n]?"1":"0";
		printf("%s\"></A>",$goododd?"&odd":"");
		printf("\r\n");
		flush();
	}
	$pntr+=$packetlen+15;
}
echo "</PRE>";


foot($mission);
?>
