<?php

define("TEMPLIMIT",192);
define("PACKETINTERVAL",5.15222);
define("FACTOR12",0.119576);
define("FACTOR5",0.021615);

define("CACHE","/www/Cache/");

$oddtotal=0;
$eventotal=0;

include("headfoot.php");

$sci_units=(isset($_GET['sciunits']) && $_GET['sciunits']=='TRUE');

if (isset($_GET["mission"]))
{
        $mission=$_GET["mission"];
}
else
{
        $mission="cluster";
}

// FUNCTIONS

function fgetb($handle)
{
	// slight mod to create a get byte command

	return ord(fgetc($handle));
}

function fgetw($handle)
{
	$a=ord(fgetc($handle));
	$b=ord(fgetc($handle));
	return $a*256+$b;
}

function field($eng)
{
	if (($eng>=0) && ($eng<=127))
		return $eng;
	else
		return ($eng-256);
}

function shift($number,$direction)
{
	if ($direction>0)
		return $number<<$direction;
	elseif ($direction<0)
		return $number>>-$direction;
	else
		return $number;
}

function binbyte($number)
{
	$out="";
	for($n=7;$n>=0;$n--)
	{
		$out.=($number&pow(2,$n))?"1":"0";
	}
	return $out;
}

function binword($number)
{
	return binbyte($number>>8).binbyte($number&0xFF);
}

function binvec($number)
{
	$out="";
	for($n=14;$n>=0;$n--)
	{
		$out.=($number&pow(2,$n))?"1":"0";
	}
	return $out;
}

function binbig($number)
{
	return(binbyte($number>>24)."-".binbyte(($number>>16)&0xFF)."-".binbyte(($number>>8)&0xFF)."-".binbyte($number&0xFF));
}

function blob($image,$x,$y,$c)
{
	
	ImageSetPixel($image,$x,$y-1,$c);
	ImageSetPixel($image,$x+1,$y-1,$c);
	ImageSetPixel($image,$x-1,$y-1,$c);
	
	ImageSetPixel($image,$x,$y,$c);
	ImageSetPixel($image,$x+1,$y,$c);
	ImageSetPixel($image,$x-1,$y,$c);

	ImageSetPixel($image,$x,$y+1,$c);
	ImageSetPixel($image,$x+1,$y+1,$c);
	ImageSetPixel($image,$x-1,$y+1,$c);
}

function aliasedblob($image,$x,$y)
{
	global $black,$grey,$lightgrey;
	
	ImageSetPixel($image,$x,$y-1,$grey);
	ImageSetPixel($image,$x+1,$y-1,$lightgrey);
	ImageSetPixel($image,$x-1,$y-1,$lightgrey);
	
	ImageSetPixel($image,$x,$y,$black);
	ImageSetPixel($image,$x+1,$y,$grey);
	ImageSetPixel($image,$x-1,$y,$grey);

	ImageSetPixel($image,$x,$y+1,$grey);
	ImageSetPixel($image,$x+1,$y+1,$lightgrey);
	ImageSetPixel($image,$x-1,$y+1,$lightgrey);
}


function bigblob($image,$x,$y,$c)
{
	ImageEllipse($image,$x,$y,6,6,$c);
}

// DEFINES

$phid=array(	1=>"LTOF (Long Term Orbit)",
				2=>"LTEF (Long Term Event)",
				3=>"STOF (Short Term Orbit)",
				4=>"STEF (Short Term Event)",
				5=>"SATT (Spacecraft Attitide and Spin Rate)",
				6=>"TCAL (Time Calibration)",
				7=>"CMDH (Command History)",
				8=>"COVH (Covariance Matrix)",
				31=>"FGM Normal Science Spacecraft 1",
				71=>"FGM Normal Science Spacecraft 2",
				111=>"FGM Normal Science Spacecraft 3",
				151=>"FGM Normal Science Spacecraft 4",
				38=>"FGM Burst Science Spacecraft 1",
				78=>"FGM Burst Science Spacecraft 2",
				118=>"FGM Burst Science Spacecraft 3",
				158=>"FGM Burst Science Spacecraft 4",
				45=>"FGM Housekeeping Spacecraft 1",
				85=>"FGM Housekeeping Spacecraft 2",
				125=>"FGM Housekeeping Spacecraft 3",
				165=>"FGM Housekeeping Spacecraft 4",
				51=>"Spacecraft Housekeeping Spacecraft 1",
				91=>"Spacecraft Housekeeping Spacecraft 2",
				131=>"Spacecraft Housekeeping Spacecraft 3",
				171=>"Spacecraft Housekeeping Spacecraft 4",
				49=>"WEC Housekeeping Spacecraft 1",
				89=>"WEC Housekeeping Spacecraft 2",
				129=>"WEC Housekeeping Spacecraft 3",
				169=>"WEC Housekeeping Spacecraft 4");

$phid_type=array(	1=>"LTOF",
					2=>"LTEF",
					3=>"STOF",
					4=>"STEF",
					5=>"SATT",
					7=>"SCCH",
					31=>"NS",
					71=>"NS",
					111=>"NS",
					151=>"NS",
					38=>"BS",
					78=>"BS",
					118=>"BS",
					158=>"BS",
					45=>"HK",
					85=>"HK",
					125=>"HK",
					165=>"HK",
					51=>"SCHK",
					91=>"SCHK",
					131=>"SCHK",
					171=>"SCHK",
					49=>"WECHK",
					89=>"WECHK",
					129=>"WECHK",
					169=>"WECHK");

// $lengths=array(	31=>780,71=>780,111=>780,151=>780,
// 				38=>3596,78=>3596,
// 				38=>2232

if ($mission=="cluster")
{
$groundstation=array(	0=>"Unknown",
						1=>"Vilspa 1",
						2=>"Vilspa 2",
						3=>"Kiruna",
						4=>"Perth",
						5=>"Kourou",
						6=>"Malindi",
						7=>"Redu",
						8=>"Canberra",
						9=>"Reference",
						10=>"Unexpected",
						11=>"Unexpected",
						12=>"Unexpected",
						13=>"Unexpected",
						14=>"Unexpected",
						15=>"N/A");
}
elseif ($mission=="doublestar")
{
	$groundstation=array();
}

$datastream=array(	0x00=>"Real Time VC0",
					0x02=>"Real Time VC2",
					0x03=>"Real Time VC3",
					0x40=>"Playback VC0",
					0x42=>"Playback VC2",
					0x43=>"Playback VC3",
					0xF0=>"Recall VC0",
					0xF2=>"Recall VC2",
					0xF3=>"Recall VC3",
					0xE0=>"Recall Playback VC0",
					0xE2=>"Recall Playback VC2",
					0xE3=>"Recall Playback VC3",
					0xFF=>"N/A");

$errors=array(	"Parameter Count Overflow","Interface Fault","RAM Check Fail","MSA Fault",
				"ADC Fail (Reset)","ADC Fail (Timeout)","ADC Fail (Bus ACK)","Startup Word Not Recognised during Boot",
				"Reset Pulse Not Detected / No HF Clock","Code Patch Fail","DPU Fault","IEL Fail (Stack Full",
				"Sum Check Code Fail","<I>Not Used</I>","Incorrect Number Of Vectors","Warning Of Possible Corrupt Science Data");

$dpu=array(	1=>"Engineering Model Main",
			2=>"Engineering Model Redundant",
			3=>"F6 Main (S/C 2)",
			4=>"F6 Redundant (S/C 2)",
			5=>"F7 Main (S/C 3)",
			6=>"F7 Redundant (S/C 3)",
			7=>"F8 Main (S/C 4)",
			8=>"F8 Redundant (S/C 4)",
			9=>"F9 Main (S/C 1)",
			10=>"F9 Redundant (S/C 1)",
			11=>"F1 Main (Flight Spare)",
			12=>"F1 Redundant (Flight Spare)");



$tempDeg=array(	-60,	-59,	-58,	-57,	-56,	-55,	-54,	-53,
				-52,	-51,	-50,	-49,	-48,	-47,	-46,	-45,
				-44,	-43,	-42,	-41,	-40,	-39,	-38,	-37,
				-36,	-35,	-34,	-33,	-32,	-31,	-30,	-29,
				
				-28,	-27,	-26,	-25,	-24,	-23,	-22,	-21,
				-20,	-19,	-18,	-17,	-16,	-15,	-14,	-13,
				-12,	-11,	-10,	-9,		-8,		-7,		-6,		-5,
				-4,		-3,		-2,		-1,		0,		1,		2,		3,
				
				4,		5,		6,		7,		8,		9,		10,		11,
				12,		13,		14,		15,		16,		17,		18,		19,
				20,		21,		22,		23,		24,		25,		26,		27,
				28,		29,		30,		31,		32,		33,		34,		35,
				
				36,		37,		38,		39,		40,		41,		42,		43,
				44,		45,		46,		47,		48,		49,		50,		51,
				52,		53,		54,		55,		56,		57,		58,		59,
				60,		61,		62,		63,		64,		65,		66,		67,
				
				68,		69,		70,		71,		72,		73,		74,		75,
				76,		77,		78,		79,		80,		81,		82,		83,
				84,		85,		86,		87,		88,		89,		90,		91,
				92,		93,		94,		95,		96,		97,		98,		99,
				
				100,	101,	102,	103,	104,	105,	106,	107,
				108,	109,	110,	111,	112,	114,	115,	116,
				117,	119,	120,	121,	123,	125,	128,	130,
				132,	134,	136,	138,	142,	146,	148,	150);

$tempEng=array(	4514,	4481,	4448,	4415,	4382,	4349,	4308,	4267,
				4227,	4186,	4145,	4097,	4048,	4000,	3951,	3903,
				3847,	3792,	3736,	3681,	3625,	3563,	3501,	3440,
				3378,	3316,	3251,	3185,	3120,	3054,	2989,	2922,
				2855,	2787,	2720,	2653,	2587,	2521,	2454,	2388,
				2322,	2259,	2196,	2133,	2070,	2007,	1949,	1891,
				1832,	1774,	1716,	1664,	1611,	1559,	1506,	1454,
				1408,	1362,	1316,	1270,	1224,	1184,	1144,	1105,
				1065,	1025,	991,	957,	924,	890,	856,	827,
				799,	770,	742,	713,	689,	665,	642,	618,
				594,	574,	554,	535,	515,	495,	479,	462,
				446,	429,	413,	399,	386,	372,	359,	345,
				334,	323,	311,	300,	289,	280,	271,	261,
				252,	243,	235,	228,	220,	213,	205,	199,
				192,	186,	179,	173,	168,	163,	157,	152,
				147,	143,	138,	134,	129,	125,	121,	118,
				114,	111,	107,	104,	101,	98,		95,		92,
				89,		87,		84,		82,		79,		77,		75,		72,
				70,		68,		66,		64,		63,		61,		59,		57,
				56,		54,		53,		51,		50,		48,		47,		45,
				44,		43,		42,		41,		40,		39,		38,		37,
				36,		35,		34,		33,		32,		31,		30,		29,
				28,		27,		26,		25,		24,		23,		22,		21,
				20,		19,		18,		17,		16,		15,		14,		13);

$maskA=array(0xFF,0x01,0x03,0x07,0x0F,0x1F,0x3F,0x7F);
$maskB=array(0xFE,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF);
$maskC=array(0x00,0xFC,0xF8,0xF0,0xE0,0xC0,0x80,0x00);

$shiftA=array( +7,+14,+13,+12,+11,+10,+ 9, +8); // +ve == Left Shift ie *2^x
$shiftB=array( -1, +6, +5, +4, +3, +2, +1,  0); // -ve == Right shift ie /2^x
$shiftC=array(  0, -2, -3, -4, -5, -6, -7,  0);

$msaflag=array(0x12,0x34,0x56,0x78,0x9A,0xBC,0xDE,0xF0);


// Get Constants from const.fgm file

if ($mission=="cluster")
{
	$const=$_ENV["CLUSTER_CALIBRATION_DEFAULT"]."/const.fgm";
}
elseif ($mission=="doublestar")
{
	$const=$_ENV["DSP_CALIBRATION_DEFAULT"]."/const.fgm_DS";
}
else
{
	exit("Mission .\"".$mission."\" is unknown.");
}

$h=@fopen($const,"rb");
if ($h)
{
	if ($mission=="cluster")
	{
		$dummy=fgets($h);
		$fgm_freq=fscanf($h,"%f %f %f %f");
		$dummy=fgets($h);
		$delay[0][2]=fscanf($h,"%d %d %d %d");  // OB R23  ie $delay[sensor][range][sc]
		$delay[0][3]=$delay[0][2];
		$delay[0][4]=fscanf($h,"%d %d %d %d");  // OB R45     sensor = 0 OB, 1 IB
		$delay[0][5]=$delay[0][4];
		$delay[1][2]=fscanf($h,"%d %d %d %d");  // IB R23     range =0 R23, 1 R45
		$delay[1][3]=$delay[1][2];
		$delay[1][4]=fscanf($h,"%d %d %d %d");  // IB R45
		$delay[1][5]=$delay[1][4];
												// $delay[0..1][2..5][0..3]
	}
	elseif ($mission=="doublestar")
	{
		$dummy=fgets($h);
		$fgm_freq=fscanf($h,"%f %f %f %f");
		$dummy=fgets($h);
		$tmp1=fscanf($h,"%d %d %d %d");  // TC1 OB R3 , TC1 IB R3 , TC2 OB R3 , TC2 IB R3
		$tmp2=fscanf($h,"%d %d %d %d");  //        R4
		$tmp3=fscanf($h,"%d %d %d %d");  //        R5
		$tmp4=fscanf($h,"%d %d %d %d");  //        R6
		$tmp5=fscanf($h,"%d %d %d %d");  //        R7
										 // $delay[0..1][3..7][0..1]
		// OB Sensor
		$delay[0][3]=array($tmp1[0],$tmp1[2]);
		$delay[0][4]=array($tmp2[0],$tmp2[2]);
		$delay[0][5]=array($tmp3[0],$tmp3[2]);
		$delay[0][6]=array($tmp4[0],$tmp4[2]);
		$delay[0][7]=array($tmp5[0],$tmp5[2]);
		// IB Sensor
		$delay[1][3]=array($tmp1[1],$tmp1[3]);
		$delay[1][4]=array($tmp2[1],$tmp2[3]);
		$delay[1][5]=array($tmp3[1],$tmp3[3]);
		$delay[1][6]=array($tmp4[1],$tmp4[3]);
		$delay[1][7]=array($tmp5[1],$tmp5[3]);
	}
//	echo "<PRE>"; var_dump($delay); echo "</PRE>";
}
else
{
	exit("Fatal Error: Can't open const.fgm file \"".$const."\"");
}
if (isset($_GET["freq"]) && $_GET["freq"])
{
	$samplingrate=$fgm_freq[$_GET["sc"]-1];
}
else
{
	$samplingrate=pow(2,23)/35/4/297;
}
// $samplingrate=201.793;
$ns=9/$samplingrate;
$bs=3/$samplingrate;
$ns_filter=0.5*((9*4-1)/$samplingrate);
$bs_filter=0.5*((3*4-1)/$samplingrate);
$grad=16/$samplingrate;

// PROGRAM PROPER

if ($mission=="cluster")
{
	$raw=getenv("CLUSTER_RAW_DATA");
	$sc_type="C";
}
elseif ($mission=="doublestar")
{
	$raw=getenv("DSP_RAW_DATA");
	$sc_type="D";
}
else
{
	exit("Mission \"".$mission."\" is unknown.");
}

$sc=$_GET["sc"];
$version=$_GET["version"];
$year=$_GET["year"];
$month=$_GET["month"];
$day=$_GET["day"];
$type=$_GET["type"];

if (isset($_GET["packet0"]))
	$packet0=$_GET["packet0"];
else
	$packet0=0;

if (isset($_GET["packet1"]))
	$packet1=$_GET["packet1"];
else
	$packet1=0;

if (isset($_GET["packet2"]))
	$packet2=$_GET["packet2"];
else
	$packet2=0;

if (isset($_GET["packet3"]))
	$packet3=$_GET["packet3"];
else
	$packet3=0;

$filename=$sc_type.$sc."_".sprintf("%02d",$year-2000).$month.$day."_".$version.".".$type;

head($mission,"Packet Inspect - ".$filename);

$handle=@fopen($raw."/".$year."/".$month."/".$filename,"rb");

if ($handle)
{
	$index=0;
	$count=0;
	$filesize=filesize($raw."/".$year."/".$month."/".$filename);
	while($index<$filesize)
	{
		fseek($handle,$index,SEEK_SET);
		$scetday=fgetw($handle);
		$scetms=fgetw($handle)*65536+fgetw($handle);
		$scetus=fgetw($handle);
	
		fseek($handle,8,SEEK_CUR);
		$tm=fgetb($handle) & 0x0F;
		fseek($handle,-8,SEEK_CUR);
		
		// if $_GET["modef"] is set then we only do this when $tm=0xF, otherwise we don't care
		// what $tm is.
		
		if (($tm==0xF) | !(isset($_GET["modef"]) && $_GET["modef"]=="TRUE"))
		{
			$scet[$count]=mktime(0,0,$scetms/1000,1,1+$scetday,1958)+($scetms%1000)/1e3+$scetus/1e6;
			$scetepoch[$count]=$scetday;
			$scetseconds[$count]=$scetms/1000+$scetus/1000000;
			
			$scetmilli[$count]=$scetms;
			$scetmicro[$count]=$scetus;
			
			$offset[$count]=$index;
			
			$tm_mode[$count]=$tm;
			
			$count++;
		}
		fseek($handle,$index+9,SEEK_SET);
		$packetsize=fgetb($handle)*65536+fgetb($handle)*256+fgetb($handle);
		$index+=$packetsize+15;
	}

	$self=$_SERVER['SCRIPT_NAME'];  // Set $self to the script name, including any path offset from the server root

	$self=explode("/",$self);  // Break up the full filename into paths and name.
	$self=$self[count($self)-1];  // And get the final element only (ie the name).

	$packetposition=$packet3*1000+$packet2*100+$packet1*10+$packet0;

	if ($packetposition>($count-1))
		$packetposition=$count-1;

	
	
	echo "<P>Select packet from 0 to ".($count-1)."</P>";

	echo "<FORM NAME=choosepacket METHOD=GET ACTION=".$self.">";
	echo "<INPUT TYPE=HIDDEN NAME=year VALUE=".$year.">";
	echo "<INPUT TYPE=HIDDEN NAME=month VALUE=".$month.">";
	echo "<INPUT TYPE=HIDDEN NAME=day VALUE=".$day.">";
	echo "<INPUT TYPE=HIDDEN NAME=sc VALUE=".$sc.">";
	echo "<INPUT TYPE=HIDDEN NAME=version VALUE=".$version.">";
	echo "<INPUT TYPE=HIDDEN NAME=type VALUE=".$type.">";
	echo "<INPUT TYPE=HIDDEN NAME=mission VALUE=".$mission.">";

	$packet3limit=(int)(($count-1)/1000);
	$packet2limit=(int)(($count-1-$packet3limit*1000)/100);
	$packet1limit=(int)(($count-1-$packet3limit*1000-$packet2limit*100)/10);
	$packet0limit=       $count-1-$packet3limit*1000-$packet2limit*100-$packet1limit*10;

//	$packet3=min($packet3,$packet3limit);
//	$packet2=min($packet2,$packet2limit);
//	$packet1=min($packet1,$packet1limit);
//	$packet0=min($packet0,$packet0limit);
	
	echo "<SELECT NAME=packet3 onChange=\"document.choosepacket.submit();\">\n";
	for($packetloop=0;$packetloop<=$packet3limit;$packetloop++)
	{
		echo "<OPTION VALUE=".$packetloop;
		if ($packet3==$packetloop)
			echo " SELECTED";
		echo ">".sprintf("%05d",($packetloop*1000))."&nbsp;&nbsp;&nbsp;".date("H:i:s\Z",$scet[$packetloop*1000])."\n";
	}
	echo "</SELECT>\n";

	echo "<SELECT NAME=packet2 onChange=\"document.choosepacket.submit();\">\n";
	for($packetloop=0;$packetloop<=(($packet3==$packet3limit)?$packet2limit:9);$packetloop++)
	{
		echo "<OPTION VALUE=".$packetloop;
		if ($packet2==$packetloop)
			echo " SELECTED";
		echo ">".sprintf("%05d",($packet3*1000+$packetloop*100))."&nbsp;&nbsp;&nbsp;".date("H:i:s\Z",$scet[$packet3*1000+$packetloop*100])."\n";
	}
	echo "</SELECT>\n";

	echo "<SELECT NAME=packet1 onChange=\"document.choosepacket.submit();\">\n";
	for($packetloop=0;$packetloop<=((($packet3==$packet3limit) && ($packet2==$packet2limit))?$packet1limit:9);$packetloop++)
	{
		echo "<OPTION VALUE=".$packetloop;
		if ($packet1==$packetloop)
			echo " SELECTED";
		echo ">".sprintf("%05d",($packet3*1000+$packet2*100+$packetloop*10))."&nbsp;&nbsp;&nbsp;".date("H:i:s\Z",$scet[$packet3*1000+$packet2*100+$packetloop*10])."\n";
	}
	echo "</SELECT>\n";

	echo "<SELECT NAME=packet0 onChange=\"document.choosepacket.submit();\">\n";
	for($packetloop=0;$packetloop<=((($packet3==$packet3limit) && ($packet2==$packet2limit) && ($packet1==$packet1limit))?$packet0limit:9);$packetloop++)
	{
		echo "<OPTION VALUE=".$packetloop;
		if ($packet0==$packetloop)
			echo " SELECTED";
		echo ">".sprintf("%05d",($packet3*1000+$packet2*100+$packet1*10+$packetloop))."&nbsp;&nbsp;&nbsp;".date("H:i:s\Z",$scet[$packet3*1000+$packet2*100+$packet1*10+$packetloop]);
		if ($type=="BS")
		{
			if ($tm_mode[$packet3*1000+$packet2*100+$packet1*10+$packetloop]==0x0C)
				echo " Normal";
			elseif ($tm_mode[$packet3*1000+$packet2*100+$packet1*10+$packetloop]==0x0D)
				echo " Burst";
			elseif ($tm_mode[$packet3*1000+$packet2*100+$packet1*10+$packetloop]==0x0E)
				echo " In Extended Mode";
			elseif ($tm_mode[$packet3*1000+$packet2*100+$packet1*10+$packetloop]==0x0F)
				echo " Data Dump";
			else
				printf(" Mode 0x%1X",$tm_mode[$packet3*1000+$packet2*100+$packet1*10+$packetloop]==0x0F);
		}
	}
	echo "</SELECT>\n";

	
	
	echo "<BR><INPUT TYPE=CHECKBOX NAME=hexdump VALUE=TRUE ".((isset($_GET["hexdump"]) && $_GET["hexdump"]=="TRUE")?" CHECKED":"")." onChange=\"document.choosepacket.submit();\">Hex Dump";

	echo "<BR><INPUT TYPE=CHECKBOX NAME=freq VALUE=TRUE ".((isset($_GET["freq"]) && $_GET["freq"]=="TRUE")?" CHECKED":"")." onChange=\"document.choosepacket.submit();\">Frequency <FONT SIZE=-1><I>(Unchecked=2<sup>23</sup>/35/4/297=201.746Hz, Checked=Use const.fgm)</I></FONT>";

	echo "<BR><INPUT TYPE=CHECKBOX NAME=sciunits VALUE=TRUE ".((isset($_GET["sciunits"]) && $_GET["sciunits"]=="TRUE")?" CHECKED":"")." onChange=\"document.choosepacket.submit();\">Science Units";

	if ($type=="BS")
	{
		echo "<BR><INPUT TYPE=\"CHECKBOX\" NAME=\"modef\" VALUE=\"TRUE\" ".((isset($_GET["modef"]) && $_GET["modef"]=="TRUE")?" CHECKED":"")." onChange=\"document.choosepacket.submit();\">Mode F packets only";
	}	
	
	echo "</FORM>";

	$before=mktime(0,0,0,$month,$day-1,$year);  $byear=date("Y",$before);  $bmonth=date("m",$before);  $bday=date("d",$before);
	$after=mktime(0,0,0,$month,$day+1,$year);  $ayear=date("Y",$after);  $amonth=date("m",$after);  $aday=date("d",$after);

	// "&sciunits=".(isset($_GET["sciunits"])?$_GET["sciunits"]:"")."&modef=".(isset($_GET["modef"])?$_GET["modef"]:"").
	
	
	echo "<A HREF=\"packet_inspect_process.php?year=".$byear."&month=".$bmonth."&day=".$bday."&version=".$version."&type=".$type."&sc=".$sc."&hexdump=".((isset($_GET["hexdump"]) && $_GET["hexdump"]=="TRUE")?"TRUE":"FALSE")."&freq=".((isset($_GET["freq"]) && $_GET["freq"]=="TRUE")?"TRUE":"FALSE")."&mission=".$mission."&sciunits=".(isset($_GET["sciunits"])?$_GET["sciunits"]:"")."&modef=".(isset($_GET["modef"])?$_GET["modef"]:"")."\"><IMG SRC=\"../Images/bigleftarrow.png\" ALT=\"Previous Day\" BORDER=0></A> ";
	echo "<A HREF=\"packet_inspect_selection.php?year=".$year."&month=".$month."&day=".$day."&freq=".((isset($_GET["freq"]) && $_GET["freq"]=="TRUE")?"TRUE":"FALSE")."&mission=".$mission."&sciunits=".(isset($_GET["sciunits"])?$_GET["sciunits"]:"")."&modef=".(isset($_GET["modef"])?$_GET["modef"]:"")."\"><IMG SRC=\"../Images/menu.png\" ALT=\"Menu\" BORDER=0></A> ";
	echo "<A HREF=\"packet_inspect_process.php?year=".$ayear."&month=".$amonth."&day=".$aday."&version=".$version."&type=".$type."&sc=".$sc."&hexdump=".((isset($_GET["hexdump"]) && $_GET["hexdump"]=="TRUE")?"TRUE":"FALSE")."&freq=".((isset($_GET["freq"]) && $_GET["freq"]=="TRUE")?"TRUE":"FALSE")."&mission=".$mission."&sciunits=".(isset($_GET["sciunits"])?$_GET["sciunits"]:"")."&modef=".(isset($_GET["modef"])?$_GET["modef"]:"")."\"><IMG SRC=\"../Images/bigrightarrow.png\" ALT=\"Next Day\" BORDER=0></A>";
	echo "&nbsp;&nbsp;<A HREF=\"packet_inspect_process.php?year=".$year."&month=".$month."&day=".$day."&version=".$version."&type=".$type."&sc=".(($sc%($mission=="cluster"?4:2))+1)."&hexdump=".((isset($_GET["hexdump"]) && $_GET["hexdump"]=="TRUE")?"TRUE":"FALSE")."&freq=".((isset($_GET["freq"]) && $_GET["freq"]=="TRUE")?"TRUE":"FALSE")."&mission=".$mission."&sciunits=".(isset($_GET["sciunits"])?$_GET["sciunits"]:"")."&modef=".(isset($_GET["modef"])?$_GET["modef"]:"")."\"><IMG SRC=\"../Images/cycle.png\" ALT=\"Next Spacecraft\" BORDER=0></A>";
	echo "<BR>";

	$pb=$packetposition-1; if ($pb<0) $pb=0;
	$p3=(int)($pb/1000);
	$p2=(int)(($pb-$p3*1000)/100);
	$p1=(int)(($pb-$p3*1000-$p2*100)/10);
	$p0=       $pb-$p3*1000-$p2*100-$p1*10;
	echo "<A HREF=\"packet_inspect_process.php?year=".$year."&month=".$month."&day=".$day."&version=".$version."&type=".$type."&sc=".$sc."&hexdump=".((isset($_GET["hexdump"]) && $_GET["hexdump"]=="TRUE")?"TRUE":"FALSE")."&freq=".((isset($_GET["freq"]) && $_GET["freq"]=="TRUE")?"TRUE":"FALSE")."&packet0=".$p0."&packet1=".$p1."&packet2=".$p2."&packet3=".$p3."&mission=".$mission."&sciunits=".(isset($_GET["sciunits"])?$_GET["sciunits"]:"")."&modef=".(isset($_GET["modef"])?$_GET["modef"]:"")."\"><IMG SRC=\"../Images/leftarrow.png\" ALT=\"Previous Packet\" BORDER=0></A> ";

	$pa=$packetposition+1; if ($pa>=$count) $pa=$count-1;
	$p3=(int)($pa/1000);
	$p2=(int)(($pa-$p3*1000)/100);
	$p1=(int)(($pa-$p3*1000-$p2*100)/10);
	$p0=       $pa-$p3*1000-$p2*100-$p1*10;
	echo "<A HREF=\"packet_inspect_process.php?year=".$year."&month=".$month."&day=".$day."&version=".$version."&type=".$type."&sc=".$sc."&hexdump=".((isset($_GET["hexdump"]) && $_GET["hexdump"]=="TRUE")?"TRUE":"FALSE")."&freq=".((isset($_GET["freq"]) && $_GET["freq"]=="TRUE")?"TRUE":"FALSE")."&packet0=".$p0."&packet1=".$p1."&packet2=".$p2."&packet3=".$p3."&mission=".$mission."&sciunits=".(isset($_GET["sciunits"])?$_GET["sciunits"]:"")."&modef=".(isset($_GET["modef"])?$_GET["modef"]:"")."\"><IMG SRC=\"../Images/rightarrow.png\" ALT=\"Next Packet\" BORDER=0></A> ";

	echo "<PRE>";
	echo "Packet #            : ".$packetposition."\n";
	echo "Position            : ".$offset[$packetposition]." bytes\n\n";

	printf("Frequency           : %.6f Hz\n",$samplingrate);

	fseek($handle,$offset[$packetposition],SEEK_SET);
	$ddshead=array_slice(unpack("C*",fread($handle,15)),0);

	printf("\n<B>DDS HEADER</B>\n");
	printf("RAW                 : ");
	printf("<FONT COLOR=RED>%02X %02X %02X %02X %02X %02X %02X %02X</FONT> ",$ddshead[0],$ddshead[1],$ddshead[2],$ddshead[3],$ddshead[4],$ddshead[5],$ddshead[6],$ddshead[7]);
	printf("<FONT COLOR=BLUE>%02X</FONT> ",$ddshead[8]);
	printf("<FONT COLOR=RED>%02X %02X %02X</FONT> ",$ddshead[9],$ddshead[10],$ddshead[11]);
	printf("<FONT COLOR=BLUE>%02X</FONT> ",$ddshead[12]);
	printf("<FONT COLOR=RED>%02X</FONT> ",$ddshead[13]);
	printf("<FONT COLOR=BLUE>%02X</FONT> ",$ddshead[14]);
	printf("\n\n");

	if ($packetposition>0)
	{
		$delta=$scet[$packetposition]-$scet[$packetposition-1];
		$divisor=round($delta/PACKETINTERVAL);
		if (abs($delta-(PACKETINTERVAL*$divisor))>0.01)
		{
			$iffy=TRUE;
		}
		else
		{
			$iffy=FALSE;
		}
		printf("<FONT COLOR=GRAY>SCET (prior)        : %s.%06d</FONT>\n",date("Y-m-d\TH:i:s",$scet[$packetposition-1]),(int)(($scet[$packetposition-1]-(int)$scet[$packetposition-1])*1e6));

		printf("<FONT COLOR=GRAY>                    :               %5d.%06d</FONT>\n",(int)$delta,(int)(1e6*($delta-(int)$delta)));

	}

	if (isset($iffy) and ($iffy==TRUE))
	{
		printf("SCET                : <FONT COLOR=RED>%s.%06d</FONT>\n",date("Y-m-d\TH:i:s",$scet[$packetposition]),(int)(($scet[$packetposition]-(int)$scet[$packetposition])*1e6));
	}
	else
	{
		printf("SCET                : %s.%06d\n",date("Y-m-d\TH:i:s",$scet[$packetposition]),(int)(($scet[$packetposition]-(int)$scet[$packetposition])*1e6));
	}

	if ($packetposition<($count-1))
	{
		$delta=$scet[$packetposition+1]-$scet[$packetposition];
		printf("<FONT COLOR=GRAY>                    :               %5d.%06d</FONT>\n",(int)$delta,(int)(1e6*($delta-(int)$delta)));
		printf("<FONT COLOR=GRAY>SCET (after)        : %s.%06d</FONT>\n",date("Y-m-d\TH:i:s",$scet[$packetposition+1]),(int)(($scet[$packetposition+1]-(int)$scet[$packetposition+1])*1e6));
	}

	printf("Epoch Day           : %5d\n",$scetepoch[$packetposition]);
	printf("Seconds             : %5.6f\n",$scetseconds[$packetposition]);
	printf("<FONT COLOR=GRAY>ms / &#181;s             : %8d %4d</FONT>\n",$scetmilli[$packetposition],$scetmicro[$packetposition]);
	
	printf("PHID                : 0x%02X (%d)",$ddshead[8],$ddshead[8]);
	if (isset($phid[$ddshead[8]]))
	{
		echo " <I>".$phid[$ddshead[8]]."</I>";
	}
	echo "\n";
	$packetlength=$ddshead[9]*65536+$ddshead[10]*256+$ddshead[11];
	printf("Length              : 0x%06X (%d)",$packetlength,$packetlength);
	if ($packetlength>8192)
	{
		printf(" <FONT COLOR=RED>PACKET EXCESSIVELY LARGE (TRUNCATING)</FONT>");
		$packetlength=8192;
	}
	printf("\n");
	printf("Spacecraft          : %01x\n",$ddshead[12]>>4);
	printf("Groundstation       : %d <I>%s</I>\n",$ddshead[12]&0xF,$groundstation[$ddshead[12]&0xF]);
	printf("Data Stream         : 0x%02X (%d)",$ddshead[13],$ddshead[13]);
	if (isset($datastream[$ddshead[13]]))
	{
		echo " <I>".$datastream[$ddshead[13]]."</I>";
	}
	echo "\n";
	$tq=$ddshead[14]>>4;
	printf("Time Quality        : %01X <I>%s</I>\n",$tq,($tq==0)?"Actual Time":(($tq==1)?"Extrapolated Time":(($tq==2)?"Contingency Time":"Unknown")));
	printf("TASI                : 0x%01x (%d)\n",$ddshead[14] & 0xF,$ddshead[14] & 0xF);



fseek($handle,$offset[$packetposition]+15,SEEK_SET);
$packet=array_slice(unpack("C*",fread($handle,$packetlength)),0);


if ($sc==($ddshead[12]>>4) && $phid_type[$ddshead[8]]==$type && ($type=="NS" || $type=="BS" || $type=="HK"))
{
	$dopacketdump=FALSE;
	if ($type=="HK")
	{
		if ($packetlength!=30)
		{
			echo "<FONT COLOR=RED>Incorrect packet size for a FGM Housekeeping file.</FONT><BR>";
			$dopacketdump=TRUE;
		}
		else
		{
			printf("\n<B>INSTRUMENT PACKET HEADER (HK)</B>\n");
			echo "RAW                 : ";
			printf("<FONT COLOR=RED>%02X %02X</FONT> ",$packet[0],$packet[1]);
			printf("<FONT COLOR=BLUE>%02X %02X %02X %02X %02X %02X</FONT> ",$packet[2],$packet[3],$packet[4],$packet[5],$packet[6],$packet[7]);
			printf("<FONT COLOR=RED>%02X %02X</FONT> ",$packet[8],$packet[9]);
			printf("<FONT COLOR=BLUE>%02X %02X</FONT> ",$packet[10],$packet[11]);
			printf("<FONT COLOR=RED>%02X %02X</FONT> ",$packet[12],$packet[13]);
			printf("<FONT COLOR=BLUE>%02X %02X</FONT> ",$packet[14],$packet[15]);
			printf("<FONT COLOR=RED>%02X %02X</FONT> ",$packet[16],$packet[17]);
			printf("<FONT COLOR=BLUE>%02X %02X %02X %02X</FONT> ",$packet[18],$packet[19],$packet[20],$packet[21]);
			printf("<FONT COLOR=RED>%02X %02X %02X %02X</FONT> ",$packet[22],$packet[23],$packet[24],$packet[25]);
			printf("<FONT COLOR=BLUE>%02X %02X</FONT> ",$packet[26],$packet[27]);
			printf("<FONT COLOR=BLUE>%02X %02X</FONT> ",$packet[28],$packet[29]);

			$checka=0; for($a=0;$a<=9;$a++) $checka+=$packet[$a];
			$checkb=0; for($a=10;$a<=29;$a++) $checkb+=$packet[$a];
			if (($checka!=0) && ($checkb==0))
				echo "\n                      <FONT COLOR=LIME><B><I>The Instrument is probably in Extended Mode</I></B></FONT>";
			echo "\n\n";
			$errword=$packet[0]*256+$packet[1];
			$plus12=FACTOR12*($packet[2]*4+($packet[3]>>6));
			$minus12=FACTOR12*((($packet[3]&0x3F)*16+($packet[4]>>4))-1024);
			$plus5=FACTOR5*($packet[6]*4+($packet[7]>>6));
//			$tempval2=($packet[4]&0xF)*64+($packet[5]>>2);
			$tempval=($packet[4]&0xF)*64+($packet[5]>>2);
			if ($plus5!=0)
			{
			$temp_lookup=4.5*10000*$tempval/(2048*$plus5);
				for($j=0;$j<TEMPLIMIT;$j++)
				{
					if ($tempEng[$j]<$temp_lookup)
						break;
				}
				$j=min($j,191);
				$temp=$tempDeg[$j];
			}
			else
			{
				$temp="Not Valid";
			}
			$dpuid=$packet[7]&0xF;
			$reset=$packet[8]*256+$packet[9];
			$swstat=$packet[10]*256+$packet[11];
			$hwstat=$packet[12]*256+$packet[13];
			$inststat=$packet[14]*256+$packet[15];
			$paramblockupdate=$packet[16]>>7;
			$paramupdatecount=$packet[16]&0x7F;
			$ml2count=$packet[17];
			$range1=$packet[21]&0x7;
			$x1=field($packet[18])*pow(2,2*$range1-5);
			$y1=field($packet[19])*pow(2,2*$range1-5);
			$z1=field($packet[20])*pow(2,2*$range1-5);
			$mag1=sqrt($x1*$x1+$y1*$y1+$z1*$z1);
			$range2=$packet[25]&0x7;
			$x2=field($packet[22])*pow(2,2*$range2-5);
			$y2=field($packet[23])*pow(2,2*$range2-5);
			$z2=field($packet[24])*pow(2,2*$range2-5);
			$mag2=sqrt($x2*$x2+$y2*$y2+$z2*$z2);
			printf("<I>Analogue Values</I>\n");
			printf(" +5                 :  %6.3f V (0x%03X)\n",$plus5,($packet[6]*4+($packet[7]>>6)));
			printf("+12                 :  %6.3f V (0x%03X)\n",$plus12,($packet[2]*4+($packet[3]>>6)));
			printf("-12                 : %6.3f V (0x%03X)\n",$minus12,(1024-(($packet[3]&0x3F)*16+($packet[4]>>4))));
			if ($temp=="Not Valid")
				printf("Box Temp            :  Not Valid\n\n");
			else
				if ($tempval==0)
					printf("Box Temp            :  <FONT COLOR=RED>%3d &#176;C</FONT>   (0x%03X)\n\n",$temp,$tempval);
				else
					printf("Box Temp            :  %3d &#176;C   (0x%03X)\n\n",$temp,$tempval);
			printf("                      Range   X       Y       Z       Magnitude\n");
			printf("Field 1ry           : %1d   %5dnT %5dnT %5dnT %8.2fnT\n",$range1,$x1,$y1,$z1,$mag1);
			printf("Field 2ry           : %1d   %5dnT %5dnT %5dnT %8.2fnT\n\n",$range2,$x2,$y2,$z2,$mag2);


			printf("DPU ID              : %1X <I>%s</I>\n",$dpuid,$dpu[$dpuid]);
			printf("Reset Count         : %04X\n",$reset);

			printf("Error Word          : %04X ",$errword);
			if ($errword!=0)
			{
				$errmess="";
				for($e=0;$e<=15;$e++)
				{
					if ($errword & pow(2,15-$e))
					{
						if (strlen($errmess)!=0)
							$errmess.=",\n                        ";
						$errmess.=$errors[$e];
					}
				}
				printf("<I><FONT COLOR=RED>%s</FONT></I>",$errmess);
			}
			echo "\n";

			printf("Software Status     : %04X\n",$swstat);
			printf("    1ry Sensor      : %s, %s\n",($swstat&0x8000)?"Outboard":"Inboard",(($swstat&0x0400)?"Auto":"Manual")." Ranging");
			printf("    2ry Sensor      : %s, %s\n",($swstat&0x4000)?"Outboard":"Inboard",(($swstat&0x0100)?"Auto":"Manual")." Ranging");
			printf("    Outboard        : Cal %s, Flip %s\n",($swstat&0x0008)?"On":"Off",($swstat&0x0004)?"On":"Off");
			printf("    Inboard         : Cal %s, Flip %s\n",($swstat&0x0002)?"On":"Off",($swstat&0x0001)?"On":"Off");
			printf("    Filtering       : %s\n",($swstat&0x08000)?"Enabled":"Disabled");
			printf("    Events          : %s, %s\n",($swstat&0x0040)?"Triggering Enabled":"Triggering Disabled",($swstat&0x0200)?"<FONT COLOR=RED>Event Detected</FONT>":"No Event");
			printf("    IEL             : Main %s, Redundant %s\n",($swstat&0x0020)?"Fast":"Slow",($swstat&0x0010)?"Fast":"Slow");
			printf("    Booted on       : %s\n",($swstat=0x0080)?"Main Bus":"Redundant Bus");
			printf("    Auto Boot       : %s\n",($swstat=0x1000)?"Yes":"No");
			printf("    SEU Monitor     : %s\n",($swstat=0x2000)?"Enabled":"Disabled");

			printf("Hardware Status     : %04X\n",$hwstat);
			printf("    Interfaces      : 1 %s, 2 %s\n",($hwstat&0x8000)?"Enabled":"Disabled",($hwstat&0x4000)?"Enabled":"Disabled");
			printf("    Sensors         : Outboard %s, Inboard %s\n",($hwstat&0x2000)?"Enabled":"Disabled",($hwstat&0x1000)?"Enabled":"Disabled");
			printf("    IEL             : %s\n",($hwstat&0x0800)?"Enabled":"Disabled");
			printf("    Sync 60         : %s\n",($hwstat&0x0400)?"Enabled":"Disabled");
			printf("    DPU 1/2 Reset   : %s\n",($hwstat&0x0200)?"Enabled":"Disabled");
			printf("    TM Data         : %s\n",($hwstat&0x0100)?"Enabled":"Disabled");
			printf("    ADCs            : 1 %s, 2 %s\n",($hwstat&0x0040)?"Enabled":"Disabled",($hwstat&0x0080)?"Enabled":"Disabled");
			printf("    DPUs            : 1 %s%s, 2 %s%s\n",($hwstat&0x0004)?"Powered":"Off",($hwstat&0x0001)?" Reset":"",($hwstat&0x0008)?"Powered":"Off",($hwstat&0x0002)?" Reset":"");

			printf("Instrument Status   : %04X\n",$inststat);
			printf("    Config Instr    : %01X\n",($inststat>>12));
			printf("    DPU Test Seq    : %01X\n",($inststat>>9)&0x07);
			printf("    MSA Data        : %s\n",($inststat&0x0100)?"Filtered":"Not Filtered");
			printf("    Cal Seq         : %01X\n",($inststat>>6)&0x03);
			printf("    Memory Dump     : %s\n",($inststat&0x0020)?"<FONT COLOR=\"RED\">In Progress</FONT>":"No");
			printf("    Code Patch      : %s\n",($inststat&0x0010)?"<FONT COLOR=\"RED\">In Progress</FONT>":"No");
			$tm=$inststat&0x000F;
			if ($mission=="cluster")
				printf("    Telemetry Mode  : %01X <I>%s</I>\n",$tm,($tm==0x0C)?"Normal Science":(($tm==0x0D)?"Burst Science":(($tm==0x0E)?"Extended Mode":(($tm==0x0F)?"Data Dump":""))));
			elseif ($mission=="doublestar")
				printf("    Telemetry Mode  : %01X <I>%s</I>\n",$tm,($tm==0x0C)?"Normal Science":(($tm==0x0A)?"Gradiometer":"<FONT COLOR=RED>Unknown</FONT>"));

			printf("Telecommand         : %04X\n",$packet[16]*256+$packet[17]);
			printf("    Param Block U/D : %s\n",($paramblockupdate?"Yes":"No"));
			printf("    Param U/D Count : %02X\n",$paramupdatecount);
			printf("    ML2 Count       : %02X\n",$ml2count);

			printf("Keyhole             : %04X\n",$packet[26]*256+$packet[27]);
			printf("Memory Mon          : %04X\n",$packet[28]*256+$packet[29]);
		}
	}
	elseif ($type=="NS"  || $type="BS")
	{
			printf("\n<B>INSTRUMENT PACKET HEADER (SCIENCE)</B>\n");
			echo "RAW                 : ";
			printf("<FONT COLOR=RED>%02X %02X</FONT> ",$packet[0],$packet[1]);
			printf("<FONT COLOR=BLUE>%02X %02X</FONT> ",$packet[2],$packet[3]);
			printf("<FONT COLOR=RED>%02X %02X</FONT> ",$packet[4],$packet[5]);
			printf("<FONT COLOR=BLUE>%02X %02X</FONT> ",$packet[6],$packet[7]);
			printf("<FONT COLOR=RED>%02X %02X</FONT> ",$packet[8],$packet[9]);
			printf("<FONT COLOR=BLUE>%02X %02X</FONT> ",$packet[10],$packet[11]);
			printf("<FONT COLOR=RED>%02X %02X</FONT> ",$packet[12],$packet[13]);
			printf("<FONT COLOR=BLUE>%02X %02X</FONT> ",$packet[14],$packet[15]);
			printf("<FONT COLOR=RED>%02X</FONT>\n",$packet[16]);
			echo "                    : <FONT COLOR=RED>";
			for($i=17;$i<=33;$i++)
				printf("%02X ",$packet[$i]);
			echo "</FONT><BR>";
			$tmstat=$packet[0]*256+$packet[1];
			printf("\nTelemetry Status    : %04X\n",$tmstat);
			printf("    Sum Check Fail  : %s\n",($tmstat&0x8000)?"<FONT COLOR=RED>FAIL</FONT>":"No");
			printf("    Vectors Number  : %s\n",($tmstat&0x2000)?"<FONT COLOR=RED>Incorrect</FONT>":"OK");
			printf("    Corrupt Data    : %s\n",($tmstat&0x1000)?"<FONT COLOR=RED>Possibly</FONT>":"No");
			printf("    DPU Test Seq    : %01X\n",($tmstat&0x0E00)>>9);
			printf("    MSA Data        : %s\n",($tmstat&0x0100)?"Filtered":"Not Filtered");
			printf("    Cal Seq Number  : %01X\n",($tmstat&0x00C00)>>6);
			printf("    Memory Dump     : %s\n",($tmstat&0x0020)?"In Progress":"No");
			printf("    Code Patch      : %s\n",($tmstat&0x0010)?"In Progress":"No");
			$tm=$tmstat&0x000F;
			if ($tm==0xC)
			{
				$num1ry=116;
				$num2ry=16;
				$off2ry=654;
				$timeinc=$ns;
				$timeoffset=$ns_filter;
			}
			elseif ($tm==0xD)
			{
				$num1ry=347;
				$num2ry=40; // Strictly speaking, there is room for 42, but that is never used.
				$off2ry=1958;
				$timeinc=$bs;
				$timeoffset=$bs_filter;
			}
			elseif (($mission=="doublestar") && ($tm==0xA))
			{
				$num1ry=66;
				$num2ry=66;
				$off2ry=372;
				$timeinc=$grad;
				$timeoffset=0;  // Filter is Off in Gradiometer Mode
			}
			else  // Fallback, guess it's Cluster normal mode type stuff (probably means it's Extended Mode, so doesn't matter)
			{
				$num1ry=116;
				$num2ry=16;
				$off2ry=654;
				$timeinc=$ns;
				$timeoffset=$ns_filter;
			}

			if ($mission=="cluster")
				printf("    Telemetry Mode  : %01X <I>%s</I>\n",$tm,($tm==0x0C)?"Normal Science":(($tm==0x0D)?"Burst Science":(($tm==0x0E)?"Extended Mode":(($tm==0x0F)?"Data Dump":""))));
			elseif ($mission=="doublestar")
				printf("    Telemetry Mode  : %01X <I>%s</I>\n",$tm,($tm==0x0C)?"Normal Science":(($tm==0x0A)?"Gradiometer":"<FONT COLOR=RED>Unknown</FONT>"));


			$packethf=$packet[2]*256+$packet[3];
			$prevsun=$packet[4]*256+$packet[5];
			$thissun=$packet[6]*256+$packet[7];
			$vec1=$packet[8]*256+$packet[9];
			$vec2=$packet[10]*256+$packet[11];			

			$diffsun=$thissun-$prevsun;
			if ($diffsun<0) $diffsun+=65536;

			$diff1=$packethf-$vec1;
			if ($diff1<0) $diff1+=65536;
			$diff2=$packethf-$vec2;
			if ($diff2<0) $diff2+=65536;
			
			$diffprevsun=$packethf-$prevsun;
			if ($diffprevsun<0) $diffprevsun+=65536;
			$diffthissun=$packethf-$thissun;
			if ($diffthissun<0) $diffthissun+=65536;

			$prevsuntime=$scet[$packetposition]-$diffprevsun/4096;
			$prevsuntime_frac=$prevsuntime-(int)$prevsuntime;

			$thissuntime=$scet[$packetposition]-$diffthissun/4096;
			$thissuntime_frac=$thissuntime-(int)$thissuntime;
			
			
			printf("Packet HF           : %04X\n",$packethf);
			printf("Previous Sun Count  : %04X (%s.%06dZ)\n",$prevsun,date("H:i:s",$prevsuntime),(int)(1000000*$prevsuntime_frac));
			printf("Current Sun Count   : %04X (%s.%06dZ)\n",$thissun,date("H:i:s",$thissuntime),(int)(1000000*$thissuntime_frac));
			printf("    Spin Period     : %6.4fs\n",$diffsun/4096);

			$vectime1ry=$scet[$packetposition]-$diff1/4096-$timeoffset;
			$vectime1ry_frac=$vectime1ry-(int)$vectime1ry;
			printf("1ry Vector time     : %04X (%s.%06dZ -&#916;<sub>AnalogueDelay</sub>)\n",$vec1,date("H:i:s",$vectime1ry),(int)(1000000*$vectime1ry_frac));

			$vectime2ry=$scet[$packetposition]-$diff2/4096;
			$vectime2ry_frac=$vectime2ry-(int)$vectime2ry;
			printf("2ry Vector time     : %04X (%s.%06dZ -&#916;<sub>AnalogueDelay</sub>)\n",$vec2,date("H:i:s",$vectime2ry),(int)(1000000*$vectime2ry_frac));


			printf("Reset Count         : %04X (Last rollover at or near %s)\n",$packet[12]*256+$packet[13],date("Y-m-d\TH:i:s\Z",$scet[$packetposition]-($packet[12]*256+$packet[13])*PACKETINTERVAL));
			$scistat=$packet[14];
			printf("Science Status      : %04X\n",$scistat*256+$packet[15]);
			printf("    1ry Sensor      : %s\n",($scistat&0x80)?"Outboard":"Inboard");
			printf("    2ry Sensor      : %s\n",($scistat&0x40)?"Outboard":"Inboard");
			printf("    Outboard Sensor : %s, %s\n",($scistat&0x10)?"Cal On":"Cal Off",($scistat&0x04)?"Flip On":"Flip Off");
			printf("    Inboard Sensor  : %s, %s\n",($scistat&0x08)?"Cal On":"Cal Off",($scistat&0x02)?"Flip On":"Flip Off");
			printf("    Filtering       : %s\n",($scistat&0x20)?"Enabled":"Disabled");
			printf("    Start Variance  : Vector %d\n",$packet[15]);

			if (($tm==0xC) || ($tm==0xD) || (($mission=="doublestar") && ($tm=0xA)))
			{

				$checkbyte=(int)((($num1ry-1)*3*15)/8);
				$checkbit=(($num1ry-1)*3)%8;
				$rangex=(shift($packet[34+$checkbyte+1]&$maskB[$checkbit],$shiftB[$checkbit])+
 				         shift($packet[34+$checkbyte+2]&$maskC[$checkbit],$shiftC[$checkbit]))&0x1;
				$checkbyte=(int)(((($num1ry-1)*3+1)*15)/8);
				$checkbit=(($num1ry-1)*3+1)%8;
				$rangey=(shift($packet[34+$checkbyte+1]&$maskB[$checkbit],$shiftB[$checkbit])+
 				         shift($packet[34+$checkbyte+2]&$maskC[$checkbit],$shiftC[$checkbit]))&0x1;
				$checkbyte=(int)(((($num1ry-1)*3+2)*15)/8);
				$checkbit=(($num1ry-1)*3+2)%8;
				$rangez=(shift($packet[34+$checkbyte+1]&$maskB[$checkbit],$shiftB[$checkbit])+
 				         shift($packet[34+$checkbyte+2]&$maskC[$checkbit],$shiftC[$checkbit]))&0x1;

 				printf("Number 1ry Vectors  : %d\n",(($rangex+$rangey+$rangez)==0)?($num1ry-1):$num1ry);


 				$checkbyte=(int)((($num2ry-1)*3*15)/8);
				$checkbit=(($num2ry-1)*3)%8;
 				$rangex=(shift($packet[34+$off2ry+$checkbyte+1]&$maskB[$checkbit],$shiftB[$checkbit])+
 				         shift($packet[34+$off2ry+$checkbyte+2]&$maskC[$checkbit],$shiftC[$checkbit]))&0x1;
				$checkbyte=(int)(((($num2ry-1)*3+1)*15)/8);
				$checkbit=(($num2ry-1)*3+1)%8;
 				$rangey=(shift($packet[34+$off2ry+$checkbyte+1]&$maskB[$checkbit],$shiftB[$checkbit])+
 				         shift($packet[34+$off2ry+$checkbyte+2]&$maskC[$checkbit],$shiftC[$checkbit]))&0x1;
				$checkbyte=(int)(((($num2ry-1)*3+2)*15)/8);
				$checkbit=(($num2ry-1)*3+2)%8;
 				$rangez=(shift($packet[34+$off2ry+$checkbyte+1]&$maskB[$checkbit],$shiftB[$checkbit])+
				         shift($packet[34+$off2ry+$checkbyte+2]&$maskC[$checkbit],$shiftC[$checkbit]))&0x1;

 				printf("Number 2ry Vectors  : %d\n",(($rangex+$rangey+$rangez)==0)?($num2ry-1):$num2ry);


//				$off2ry=(int)(($num1ry*45)/8)+1;

				echo "\n<B>Primary Vectors</B>\n";
				echo "<U>  #                      X          Y          Z      Range   Magnitude &#916;Magnitude</U>\n";
				$range=0;

	 			for($vec=0;$vec<=($num1ry*3-1);$vec++)
	 			{
//		 			$vectime=$vectime1ry+((int)($vec/3))*$timeinc;
//		 			$vectimems=(int)(1000*($vectime-(int)$vectime));
					$byteoffset=(int)(($vec*15)/8);
	 				$bitmask=$vec%8;

	 				$num=shift($packet[34+$byteoffset]&$maskA[$bitmask],$shiftA[$bitmask])+
	 				     shift($packet[34+$byteoffset+1]&$maskB[$bitmask],$shiftB[$bitmask])+
	 				     shift($packet[34+$byteoffset+2]&$maskC[$bitmask],$shiftC[$bitmask]);

					$value=$num>>1;
					if ($value>=8192)	$value-=16384;

					$range+=pow(2,2-($vec%3))*($num&0x1);
//					echo $range."\n";

					if	(($vec%3)==0)
					{
						$x=$value;
			 				// $scistat&0x80 is true if OB is 1ry sensor, false if IB is 1ry sensor.
			 				// $range<=3 seperates R23 from R45.
					}
					elseif (($vec%3)==1)
					{
						$y=$value;
					}
					else
					{
						$scale=pow(2,11-2*$range);
						$z=$value;
						$x=$x/$scale;
						$y=$y/$scale;
						$z=$z/$scale;
						if (($range>=2) and ($range<=7) and ($sc>=1) and ($sc<=4))
						{
							$analoguedelay=$delay[($scistat&0x80)?0:1][$range][$sc-1]*1e-9;
						}
						else
						{
							$analoguedelay=0; // This should possibly be flagged as erroneous
						}
			 			$vectime=$vectime1ry+((int)($vec/3))*$timeinc-$analoguedelay;
			 			$vectimeus=(int)(1000000*($vectime-(int)$vectime));
			 			$vectimems=round(1000*($vectime-(int)$vectime),0);
			 			if ($vectimems>=1000)
			 			{
				 			$vectime+=1;
				 			$vectimems-=1000;
			 			}

						if (($vec==($num1ry*3-1)) && ($x==0) && ($y==0) && ($z==0))
							printf("%3d  %s.%03dZ  <FONT COLOR=SILVER>%10.3f %10.3f %10.3f    %1d    %10.3f</FONT>\n",(int)($vec/3),date("H:i:s",$vectime),$vectimems,$x,$y,$z,$range,sqrt($x*$x+$y*$y+$z*$z));
						else
						{
							if (isset($previous_mag))
							{
								printf("%3d  %s.%03dZ  %10.3f %10.3f %10.3f    %1d    %10.3f %10.3f\n",(int)($vec/3),date("H:i:s",$vectime),$vectimems,$x,$y,$z,$range,sqrt($x*$x+$y*$y+$z*$z),abs($previous_mag-sqrt($x*$x+$y*$y+$z*$z)));
							}
							else
							{
								printf("%3d  %s.%03dZ  %10.3f %10.3f %10.3f    %1d    %10.3f\n",(int)($vec/3),date("H:i:s",$vectime),$vectimems,$x,$y,$z,$range,sqrt($x*$x+$y*$y+$z*$z));
							}
							$previous_mag=sqrt($x*$x+$y*$y+$z*$z);
						}

						$val_x_pri[(int)($vec/3)]=$x;
						$val_y_pri[(int)($vec/3)]=$y;
						$val_z_pri[(int)($vec/3)]=$z;
						$val_mag_pri[(int)($vec/3)]=sqrt($x*$x+$y*$y+$z*$z);

						$range=0;
					}
	//				echo (int)($vec/3)." ".(($vec%3)==0?"X":((($vec%3)==1)?"Y":"Z"))." | ".$value." ".($num&1)."\n";
				}

				echo "\n<B>Secondary Vectors</B>\n";
				echo "<U>  #        X          Y          Z      Range   Magnitude</U>\n";

				$range=0;

	 			for($vec=0;$vec<=($num2ry*3-1);$vec++)
	 			{
					$byteoffset=(int)(($vec*15)/8);
	 				$bitmask=$vec%8;

	 				$num=shift($packet[34+$off2ry+$byteoffset]&$maskA[$bitmask],$shiftA[$bitmask])+
	 				     shift($packet[34+$off2ry+$byteoffset+1]&$maskB[$bitmask],$shiftB[$bitmask])+
	 				     shift($packet[34+$off2ry+$byteoffset+2]&$maskC[$bitmask],$shiftC[$bitmask]);


					$value=$num>>1;

//					printf("%02X\n",$value);

					if ($value>=8192)	$value-=16384;

					$range+=pow(2,2-($vec%3))*($num&0x1);

					if	(($vec%3)==0)
					{
						$x=$value;
					}
					elseif (($vec%3)==1)
					{
						$y=$value;
					}
					else
					{
						$scale=pow(2,11-2*$range);
						$z=$value;
						$x=$x/$scale;
						$y=$y/$scale;
						$z=$z/$scale;

						if (($vec==($num2ry*3-1)) && ($x==0) && ($y==0) && ($z==0))
							printf("%3d | <FONT COLOR=SILVER>%10.3f %10.3f %10.3f    %1d    %10.3f</FONT>\n",(int)($vec/3),$x,$y,$z,$range,sqrt($x*$x+$y*$y+$z*$z));
						else
							printf("%3d | %10.3f %10.3f %10.3f    %1d    %10.3f\n",(int)($vec/3),$x,$y,$z,$range,sqrt($x*$x+$y*$y+$z*$z));

						$val_x_sec[(int)($vec/3)]=$x;
						$val_y_sec[(int)($vec/3)]=$y;
						$val_z_sec[(int)($vec/3)]=$z;
						$val_mag_sec[(int)($vec/3)]=sqrt($x*$x+$y*$y+$z*$z);

						$range=0;
					}
				}
				
 				$image=ImageCreate(240,200);
 				$white=ImageColorAllocate($image,255,255,255);
 				$black=ImageColorAllocate($image,  0,  0,  0);
 				$red=  ImageColorAllocate($image,255,  0,  0);
 				$green=ImageColorAllocate($image,  0,255,  0);
 				$blue= ImageColorAllocate($image,  0,  0,255);
 				$grey= ImageColorAllocate($image,128,128,128);
 				$lightgrey=ImageColorAllocate($image,192,192,192);
				
 				$max_x_pri=max($val_x_pri);
 				$min_x_pri=min($val_x_pri);
 				$max_x_sec=max($val_x_sec);
 				$min_x_sec=min($val_x_sec);
 				$spread_x=max(max(abs($max_x_sec),abs($min_x_sec)),max(abs($max_x_pri),abs($min_x_pri)));

 				$max_y_pri=max($val_y_pri);
 				$min_y_pri=min($val_y_pri);
 				$max_y_sec=max($val_y_sec);
 				$min_y_sec=min($val_y_sec);
 				$spread_y=max(max(abs($max_y_sec),abs($min_y_sec)),max(abs($max_y_pri),abs($min_y_pri)));

 				$max_z_pri=max($val_z_pri);
 				$min_z_pri=min($val_z_pri);
 				$max_z_sec=max($val_z_sec);
 				$min_z_sec=min($val_z_sec);
 				$spread_z=max(max(abs($max_z_sec),abs($min_z_sec)),max(abs($max_z_pri),abs($min_z_pri)));
 				
  				$max_mag_pri=max($val_mag_pri);
  				$min_mag_pri=min($val_mag_pri);
  				$spread_mag=max(abs($max_mag_pri),abs($min_mag_pri));
 				
 				$spread=max(max($spread_x,$spread_y),max($spread_z,$spread_mag));
 				
 				$h=fopen("/www/Cache/debug","wb");
 				fputs($h,$spread_x." ".$spread_y." ".$spread_z);
 				fclose($h);
 				
				foreach($val_x_pri as $k => $v)
				{
					blob($image,$k*2,50+48*($val_x_pri[$k]/$spread_x),$red);
					blob($image,$k*2,50+48*($val_y_pri[$k]/$spread_y),$green);
					blob($image,$k*2,50+48*($val_z_pri[$k]/$spread_z),$blue);
					aliasedblob($image,$k*2,50+48*($val_mag_pri[$k]/$spread));
				}
				
 				
  				$max_mag_sec=max($val_mag_sec);
  				$min_mag_sec=min($val_mag_sec);
  				$spread_mag=max(abs($max_mag_sec),abs($min_mag_sec));

				foreach($val_x_sec as $k => $v)
				{
					
					blob($image,2*($k+0.5)*7.25,150+48*($val_x_sec[$k]/$spread_x),$red);
					blob($image,2*($k+0.5)*7.25,150+48*($val_y_sec[$k]/$spread_y),$green);
					blob($image,2*($k+0.5)*7.25,150+48*($val_z_sec[$k]/$spread_z),$blue);
 					aliasedblob($image,2*($k+0.5)*7.25,150+48*($val_mag_sec[$k]/$spread_mag));
				}

				echo "<BR>";
				$f="image".rand();
				ImagePng($image,"/www/Cache/".$f);
				$hash=md5($f."ClustOpsImage");
				echo "<IMG SRC=\"/ClusterOperations/imagepngout.php?file=".$f."&hash=".$hash."\">";

			}
			elseif ($tm==0xF)
			{
				// Checking for Event Capture vs Extended Mode

				$flag=array(array(),array());
				for($n=0;$n<444;$n++)
				{
					$evenword=$packet[$n*8+34  +6]*256+$packet[$n*8+34  +7];
					$oddword= $packet[$n*8+34+4+6]*256+$packet[$n*8+34+4+7];

					$evensensor=$evenword>>15;
					$evenrange=($evenword>>12)&7;
					$evenreset=$evenword&0xFFF;

					$oddsensor=$oddword>>15;
					$oddrange=($oddword>>12)&7;
					$oddreset=$oddword&0xFFF;

					// First check whether the sensor is OB (which is almost always going to be the case)
					if ($evensensor==0)
						$flageven=1;
					else
						$flageven=0;

					// Second change the range is sane (0 and 1 are the only silly values, now)
					
					if (($evenrange>=2) && ($evenrange<=7))  // This was more useful when the valid ranges were 2 to 5
						$flageven++;

					// Check that the reset count incremented by only one (or wrapped around)
						
					if (isset($prevevenreset) && ((abs($prevevenreset-$evenreset)<=1) || ($prevevenreset==0xFFF and $evenreset==0x000)))
						$flageven++;
					
					// Do all of that for the Odd case instead of Even case.

					if ($oddsensor==0)
						$flagodd=1;
					else
						$flagodd=0;

					if (($oddrange>=2) && ($oddrange<=7))  // This was more useful when the valid ranges were 2 to 5
						$flagodd++;

					if (isset($prevoddreset) && ((abs($prevoddreset-$oddreset)<=1) || ($prevoddreset==0xFFF and $oddreset==0x000)))
						$flagodd++;

					$prevevenreset=$evenreset;
					$prevoddreset=$oddreset;

					if ($flageven==3) $eventotal++;
					if ($flagodd==3) $oddtotal++;

				}

				$found=array();
				for($n=34;$n<$packetlength;$n++)
				{
					for($m=0;$m<count($msaflag);$m++)
					{
						if ($msaflag[$m]!=$packet[$n+$m])
							break;
						elseif ($m==(count($msaflag)-1))
							$found[]=$n-34;
					}
				}

				printf("\n<B>Extended Mode</B>\n");
				printf("   Even Vectors     : %d\n",$eventotal);
				printf("   Odd Vectors      : %d\n",$oddtotal);
				printf("<B>Event Capture</B>\n");
				printf("   Flags            : %d\n",count($found));

				if ((($oddtotal>5) || ($eventotal>5)) && (count($found)>0))
					printf("\n<FONT COLOR=RED><B>WARNING : PACKET APPEARS TO CONTAIN <U>BOTH</U> EVENT CAPTURE AND EXTENDED MODE DATA.</B></FONT>\n");

				if (($oddtotal>5) && ($eventotal>5))
					printf("\n<FONT COLOR=RED><B>ERROR : PACKET APPEARS TO CONTAIN ODD & EVEN EXTENDED MODE VECTORS, THIS SHOULDN'T HAPPEN.</B></FONT>\n");

				if (count($found)!=0)
				{
					echo "\n";
					for($n=0;$n<count($found);$n++)
					{
						printf("<B>MSA FLAG HEADER</B>\n");
						printf("RAW                 : ");
						for($m=0;$m<=9;$m++)
						{
							printf("<FONT COLOR=%s>%02X %02X</FONT> ",(($m%2)==0)?"RED":"BLUE",$packet[34+$found[$n]+$m*2],$packet[34+$found[$n]+$m*2+1]);
						}
						echo "\n\n";
						printf("Event Capture Flag  : #%d\n",$n);
						printf("Packet position     : %04X (%d)\n",$found[$n],$found[$n]);
						printf("Reset               : %02X%02X\n",$packet[34+$found[$n]+8],$packet[34+$found[$n]+9]);
						printf("Reset HF Count      : %02X%02X\n",$packet[34+$found[$n]+10],$packet[34+$found[$n]+11]);
						printf("Current HF Count    : %02X%02X\n",$packet[34+$found[$n]+12],$packet[34+$found[$n]+13]);
						printf("Sun Pulse           : %02X%02X\n",$packet[34+$found[$n]+14],$packet[34+$found[$n]+15]);

						$swstat=$packet[34+$found[$n]+16]*256+$packet[34+$found[$n]+17];
						printf("Software Status     : %04X\n",$swstat);
						printf("    1ry Sensor      : %s, %s\n",($swstat&0x8000)?"Outboard":"Inboard",(($swstat&0x0400)?"Auto":"Manual")." Ranging");
						printf("    2ry Sensor      : %s, %s\n",($swstat&0x4000)?"Outboard":"Inboard",(($swstat&0x0100)?"Auto":"Manual")." Ranging");
						printf("    Outboard        : Cal %s, Flip %s\n",($swstat&0x0008)?"On":"Off",($swstat&0x0004)?"On":"Off");
						printf("    Inboard         : Cal %s, Flip %s\n",($swstat&0x0002)?"On":"Off",($swstat&0x0001)?"On":"Off");
						printf("    Filtering       : %s\n",($swstat&0x08000)?"Enabled":"Disabled");
						printf("    Events          : %s, %s\n",($swstat&0x0040)?"Triggering Enabled":"Triggering Disabled",($swstat&0x0200)?"<FONT COLOR=RED>Event Detected</FONT>":"No Event");
						printf("    IEL             : Main %s, Redundant %s\n",($swstat&0x0020)?"Fast":"Slow",($swstat&0x0010)?"Fast":"Slow");
						printf("    Booted on       : %s\n",($swstat=0x0080)?"Main Bus":"Redundant Bus");
						printf("    Auto Boot       : %s\n",($swstat=0x1000)?"Yes":"No");
						printf("    SEU Monitor     : %s\n",($swstat=0x2000)?"Enabled":"Disabled");

						$tmstat=$packet[34+$found[$n]+18]*256+$packet[34+$found[$n]+19];
						printf("Telemetry Status    : %04X\n",$tmstat);
						printf("    Sum Check Fail  : %s\n",($tmstat&0x8000)?"<FONT COLOR=RED>FAIL</FONT>":"No");
						printf("    Vectors Number  : %s\n",($tmstat&0x2000)?"<FONT COLOR=RED>Incorrect</FONT>":"OK");
						printf("    Corrupt Data    : %s\n",($tmstat&0x1000)?"<FONT COLOR=RED>Possibly</FONT>":"No");
						printf("    DPU Test Seq    : %01X\n",($tmstat&0x0E00)>>9);
						printf("    MSA Data        : %s\n",($tmstat&0x0100)?"Filtered":"Not Filtered");
						printf("    Cal Seq Number  : %01X\n",($tmstat&0x00C00)>>6);
						printf("    Memory Dump     : %s\n",($tmstat&0x0020)?"In Progress":"No");
						printf("    Code Patch      : %s\n",($tmstat&0x0010)?"In Progress":"No");
						$tm=$tmstat&0x000F;
						printf("    Telemetry Mode  : %01X <I>%s</I>\n",$tm,($tm==0x0C)?"Normal Science":(($tm==0x0D)?"Burst Science":(($tm==0x0E)?"Extended Mode":(($tm==0x0F)?"Data Dump":""))));

						echo "\n";
					}
				}
				if (($oddtotal>5) || ($eventotal>5))
				{
					if ($sci_units)
					{
						printf("\n<B>MSA EXTENDED MODE DUMP</B> (Field in nT)\n");
						
						printf(	"             %sEVEN PACKET  Graphs%s",
								($eventotal>5)?"<B>":"",
								($eventotal>5)?"</B>":"");
						
						printf(	" <A STYLE=\"%s\" TARGET=\"".rand()."\" HREF=\"extmodegraph.php%s\">ALL</A>",
								($eventotal>5)?"color: blue;":"color: #D0D0D0;",
								"?sc=".$sc."&year=".$year."&month=".$month."&day=".$day."&packetposition=".$packetposition."&version=".$version."&category=even");

						printf(	" |<A STYLE=\"%s\" TARGET=\"".rand()."\" HREF=\"extmodegraph.php%s&fraction=1/3\">1111</A>",
								($eventotal>5)?"color: blue;":"color: #D0D0D0;",
								"?sc=".$sc."&year=".$year."&month=".$month."&day=".$day."&packetposition=".$packetposition."&version=".$version."&category=even");
						printf( "/<A STYLE=\"%s\" TARGET=\"".rand()."\" HREF=\"extmodegraph.php%s&fraction=2/3\">2222</A>|",($eventotal>5)?"color: blue;":"color: #D0D0D0;",
								"?sc=".$sc."&year=".$year."&month=".$month."&day=".$day."&packetposition=".$packetposition."&version=".$version."&category=even",
								($eventotal>5)?"color: blue;":"color: #D0D0D0;");
						printf(	"/<A STYLE=\"%s\" TARGET=\"".rand()."\" HREF=\"extmodegraph.php%s&fraction=3/3\">3333</A>|",($eventotal>5)?"color: blue;":"color: #D0D0D0;",
								"?sc=".$sc."&year=".$year."&month=".$month."&day=".$day."&packetposition=".$packetposition."&version=".$version."&category=even",
								($eventotal>5)?"color: blue;":"color: #D0D0D0;");
						printf(	"                  %sODD PACKET  Graphs%s",
								($oddtotal>5)?"<B>":"",
								($oddtotal>5)?"</B>":"");
						printf(	" <A STYLE=\"%s\" TARGET=\"".rand()."\" HREF=extmodegraph.php%s>ALL</A>",
								($oddtotal>5)?"color: blue;":"color: #D0D0D0;",
								"?sc=".$sc."&year=".$year."&month=".$month."&day=".$day."&packetposition=".$packetposition."&version=".$version."&category=odd");

						printf(	" |<A STYLE=\"%s\" TARGET=\"".rand()."\" HREF=\"extmodegraph.php%s&fraction=1/3\">1111</A>",
								($oddtotal>5)?"color: blue;":"color: #D0D0D0;",
								"?sc=".$sc."&year=".$year."&month=".$month."&day=".$day."&packetposition=".$packetposition."&version=".$version."&category=odd");
						printf( "/<A STYLE=\"%s\" TARGET=\"".rand()."\" HREF=\"extmodegraph.php%s&fraction=2/3\">2222</A>|",($oddtotal>5)?"color: blue;":"color: #D0D0D0;",
								"?sc=".$sc."&year=".$year."&month=".$month."&day=".$day."&packetposition=".$packetposition."&version=".$version."&category=odd",
								($oddtotal>5)?"color: blue;":"color: #D0D0D0;");
						printf(	"/<A STYLE=\"%s\" TARGET=\"".rand()."\" HREF=\"extmodegraph.php%s&fraction=3/3\">3333</A>|",($oddtotal>5)?"color: blue;":"color: #D0D0D0;",
								"?sc=".$sc."&year=".$year."&month=".$month."&day=".$day."&packetposition=".$packetposition."&version=".$version."&category=odd",
								($oddtotal>5)?"color: blue;":"color: #D0D0D0;");
						printf("<BR>");
						printf("<U><B>#    |</B>       %sX          Y          Z         Range  Sensor Reset%s </U> <U>      %sX          Y          Z         Range  Sensor Reset%s</U>\n",
							($eventotal>5)?"<B>":"",
							($eventotal>5)?"</B>":"",
							($oddtotal>5)?"<B>":"",
							($oddtotal>5)?"</B>":"");
					}
					else
					{
						printf("\n<B>MSA EXTENDED MODE DUMP</B> (Field in Engineering Units)\n");
						
						printf(	"            %sEVEN PACKET  Graphs%s",
								($eventotal>5)?"<B>":"",
								($eventotal>5)?"</B>":"");
						
						printf(	" <A STYLE=\"%s\" TARGET=\"".rand()."\" HREF=\"extmodegraph.php%s\">ALL</A>",
								($eventotal>5)?"color: blue;":"color: #D0D0D0;",
								"?sc=".$sc."&year=".$year."&month=".$month."&day=".$day."&packetposition=".$packetposition."&version=".$version."&category=even");

						printf(	" |<A STYLE=\"%s\" TARGET=\"".rand()."\" HREF=\"extmodegraph.php%s&fraction=1/3\">1111</A>",
								($eventotal>5)?"color: blue;":"color: #D0D0D0;",
								"?sc=".$sc."&year=".$year."&month=".$month."&day=".$day."&packetposition=".$packetposition."&version=".$version."&category=even");
						printf( "/<A STYLE=\"%s\" TARGET=\"".rand()."\" HREF=\"extmodegraph.php%s&fraction=2/3\">2222</A>|",($eventotal>5)?"color: blue;":"color: #D0D0D0;",
								"?sc=".$sc."&year=".$year."&month=".$month."&day=".$day."&packetposition=".$packetposition."&version=".$version."&category=even",
								($eventotal>5)?"color: blue;":"color: #D0D0D0;");
						printf(	"/<A STYLE=\"%s\" TARGET=\"".rand()."\" HREF=\"extmodegraph.php%s&fraction=3/3\">3333</A>|",($eventotal>5)?"color: blue;":"color: #D0D0D0;",
								"?sc=".$sc."&year=".$year."&month=".$month."&day=".$day."&packetposition=".$packetposition."&version=".$version."&category=even",
								($eventotal>5)?"color: blue;":"color: #D0D0D0;");
						printf(	"      %sODD PACKET  Graphs%s",
								($oddtotal>5)?"<B>":"",
								($oddtotal>5)?"</B>":"");
						printf(	" <A STYLE=\"%s\" TARGET=\"".rand()."\" HREF=extmodegraph.php%s>ALL</A>",
								($oddtotal>5)?"color: blue;":"color: #D0D0D0;",
								"?sc=".$sc."&year=".$year."&month=".$month."&day=".$day."&packetposition=".$packetposition."&version=".$version."&category=odd");

						printf(	" |<A STYLE=\"%s\" TARGET=\"".rand()."\" HREF=\"extmodegraph.php%s&fraction=1/3\">1111</A>",
								($oddtotal>5)?"color: blue;":"color: #D0D0D0;",
								"?sc=".$sc."&year=".$year."&month=".$month."&day=".$day."&packetposition=".$packetposition."&version=".$version."&category=odd");
						printf( "/<A STYLE=\"%s\" TARGET=\"".rand()."\" HREF=\"extmodegraph.php%s&fraction=2/3\">2222</A>|",($oddtotal>5)?"color: blue;":"color: #D0D0D0;",
								"?sc=".$sc."&year=".$year."&month=".$month."&day=".$day."&packetposition=".$packetposition."&version=".$version."&category=odd",
								($oddtotal>5)?"color: blue;":"color: #D0D0D0;");
						printf(	"/<A STYLE=\"%s\" TARGET=\"".rand()."\" HREF=\"extmodegraph.php%s&fraction=3/3\">3333</A>|",($oddtotal>5)?"color: blue;":"color: #D0D0D0;",
								"?sc=".$sc."&year=".$year."&month=".$month."&day=".$day."&packetposition=".$packetposition."&version=".$version."&category=odd",
								($oddtotal>5)?"color: blue;":"color: #D0D0D0;");
						printf("<BR>");
						printf("<U><B>#    |</B>      %sX      Y      Z      Range  Sensor Reset%s </U> <U>     %sX      Y      Z      Range  Sensor Reset%s</U>\n",
							($eventotal>5)?"<B>":"",
							($eventotal>5)?"</B>":"",
							($oddtotal>5)?"<B>":"",
							($oddtotal>5)?"</B>":"");
					}
					$oddz=$packet[34+0]*256+$packet[34+1];
					if ($oddz>32768) $oddz-=65536;
					$oddz_u=$oddz;
					$oddword=$packet[34+2]*256+$packet[34+3];
					$oddrange=($oddword>>12)&0x7;
					$oddsensor=($oddword>>15)?"IB":"OB";
					$oddreset=$oddword&0x0FFF;
					$oddscale=pow(2,13-2*$oddrange);
					$oddz/=$oddscale;

					if ($sci_units)
					{
						printf("     |                                                                                  %10.3f      %d      %2s     %03X\n",$oddz,$oddrange,$oddsensor,$oddreset);
					}
					else
					{
					printf("     |                                                              %6d      %d      %2s     %03X\n",$oddz_u,$oddrange,$oddsensor,$oddreset);
					}	

					$cachename="ext_mode_packet";
				
					$evencache=CACHE.$cachename."_".$sc."_".sprintf("%04d-%02d-%02d",$year,$month,$day)."_".$version."_".$packetposition."_EVEN";
					$oddcache=CACHE.$cachename."_".$sc."_".sprintf("%04d-%02d-%02d",$year,$month,$day)."_".$version."_".$packetposition."_ODD";
					$complete=CACHE.$cachename."_".$sc."_".sprintf("%04d-%02d-%02d",$year,$month,$day)."_".$version."_".$packetposition."_GOOD";

					if (file_exists($complete))
						unlink($complete);
					if (file_exists($complete))
						exit("Oops, can't unlink ".$complete);
					
					if (file_exists($evencache))
						unlink($evencache);
					if (file_exists($evencache))
						exit("Oops, can't unlink ".$evencache);

					if (file_exists($oddcache))
						unlink($oddcache);
					if (file_exists($oddcache))
						exit("Oops, can't unlink ".$oddcache);

					$fe=fopen($evencache,"w");
					$fo=fopen($oddcache,"w");
					if (!$fe or !$fo)
						exit("Oops, can't open Cache file for writing");
										
					unset($prevoddreset);unset($prevevenreset);
					for($n=0;$n<444;$n++)
					{
						$evenx=$packet[$n*8+34+0]*256+$packet[$n*8+34+1];
						if ($evenx>32768) $evenx-=65536;
						$eveny=$packet[$n*8+34+2]*256+$packet[$n*8+34+3];
						if ($eveny>32768) $eveny-=65536;
						$evenz=$packet[$n*8+34+4]*256+$packet[$n*8+34+5];
						if ($evenz>32768) $evenz-=65536;
						$evenword=$packet[$n*8+34+6]*256+$packet[$n*8+34+7];
						$evenrange=($evenword>>12)&0x7;
						$evensensor=($evenword>>15)?"IB":"OB";
						$evenreset=$evenword&0x0FFF;
						$evenscale=pow(2,13-2*$evenrange);
						
						$evenx_u=$evenx; $eveny_u=$eveny; $evenz_u=$evenz;
						
						$evenx/=$evenscale;
						$eveny/=$evenscale;
						$evenz/=$evenscale;

						$oddx=$packet[$n*8+34+4]*256+$packet[$n*8+34+5];
						if ($oddx>32768) $oddx-=65536;
						$oddy=$packet[$n*8+34+6]*256+$packet[$n*8+34+7];
						if ($oddy>32768) $oddy-=65536;
						$oddz=$packet[$n*8+34+8]*256+$packet[$n*8+34+9];
						if ($oddz>32768) $oddz-=65536;
						$oddword=$packet[$n*8+34+10]*256+$packet[$n*8+34+11];
						$oddrange=($oddword>>12)&0x7;
						$oddsensor=($oddword>>15)?"IB":"OB";
						$oddreset=$oddword&0x0FFF;
						
						$oddx_u=$oddx; $oddy_u=$oddy; $oddz_u=$oddz;
						
						$oddscale=pow(2,13-2*$oddrange);
						$oddx/=$oddscale;
						$oddy/=$oddscale;
						$oddz/=$oddscale;

						
						
						// if the previous reset record hasn't been set, then set it to something sensible
						if (!isset($prevoddreset)) $prevoddreset=$oddreset;

						// if		we have at least 5 (odd) vectors in the packet
						//				and
						//			the sensor is OB
						//				and
						//			the range is between 2 and 7 (was 5)
						//				and
						//			the reset has changed by 0, 1 or 0xFFF if it is currently zero.
						if (($oddtotal>5) && ($oddsensor==0) && (($oddrange>=2 and $oddrange<=7)) && ((($oddreset-$prevoddreset)<=1) || (($oddreset==0) && ($prevoddreset==0xFFF))))
						{
							$oddstart="<B>"; $oddend="</B>";
						}
						else
						{
							$oddstart="<FONT COLOR=GRAY>"; $oddend="</FONT>";
						}

						if (!isset($prevevenreset)) $prevevenreset=$evenreset;

						if (($eventotal>5) && ($evensensor==0) && (($evenrange>=2 and $evenrange<=7)) && ((($evenreset-$prevevenreset)<=1) || (($evenreset==0) && ($prevevenreset==0xFFF))))
						{
							$evenstart="<B>"; $evenend="</B>";
						}
						else
						{
							$evenstart="<FONT COLOR=GRAY>"; $evenend="</FONT>";
						}

						$prevoddreset=$oddreset;
						$prevevenreset=$evenreset;

						if ($sci_units)
							printf("%04X | %s%10.3f %10.3f %10.3f      %d      %2s     %03X%s    %s%10.3f %10.3f %10.3f      %d      %2s     %03X%s\n",$n,$evenstart,$evenx,$eveny,$evenz,$evenrange,$evensensor,$evenreset,$evenend,$oddstart,$oddx,$oddy,$oddz,$oddrange,$oddsensor,$oddreset,$oddend);
						else
							printf("%04X | %s%6d %6d %6d      %d      %2s     %03X%s    %s%6d %6d %6d      %d      %2s     %03X%s\n",$n,$evenstart,$evenx_u,$eveny_u,$evenz_u,$evenrange,$evensensor,$evenreset,$evenend,$oddstart,$oddx_u,$oddy_u,$oddz_u,$oddrange,$oddsensor,$oddreset,$oddend);
						fprintf($fe,"%6d %6d %6d %6d %1d %2s %4d\n",$n,$evenx_u,$eveny_u,$evenz_u,$evenrange,$evensensor,$evenreset);
						fprintf($fo,"%6d %6d %6d %6d %1d %2s %4d\n",$n,$oddx_u, $oddy_u, $oddz_u, $oddrange, $oddsensor, $oddreset);
					}
					
					fclose($fo);
					fclose($fe);
					touch($complete);
					
					$evenx=$packet[$n*8+34+0]*256+$packet[$n*8+34+1];
					if ($evenx>32768) $evenx-=65536;
					$evenx/=$evenscale;
					$eveny=$packet[$n*8+34+2]*256+$packet[$n*8+34+3];
					if ($eveny>32768) $eveny-=65536;
					$eveny/=$evenscale;
					if ($sci_units)
					{
						printf("     | %10.3f %10.3f\n",$evenx,$eveny);
					}
					else
					{
						printf("     | %6d %6d\n",$evenx_u,$eveny_u);
					}

					printf("</PRE><P><FONT SIZE=-1 COLOR=GRAY>Note, fields are in Engineering Units, or nT scaled approximately, with no Calibration applied.  Ranges are 2 (&#177;64nT), 3 (&#177;256nT), 4 (&#177;1024nT), and 5 (&#177;4096nT).  Other ranges are theoretically possible, but should not be seen in flight.  The reset count should increase by one approximatley every 20 vectors, it is the upper 12 bits of the normal reset count only.  Since this increase every 5.152s, this truncated version will only change every 16&#215;5.152s=82.432, which is equivalent to 20.6 spins.  Alternate Extended Mode packets contain either half a vector's worth of data at the start or the end of the packet, determination is based either upon knowledge of the packets position, or by inspection of the data for \"sanity\", eg a slowly increasing reset count.</FONT></P><PRE>");

				}


			}
			
			if (isset($_GET["bindump"]))
			{
				$wrap=$_GET["bindump"];
				echo "\n<B>Binary Dump</B>\n";
				
				for($n=0;$n<($packetlength-34);$n++)
				{
					$bin.=sprintf("%08b",$packet[34+$n]);
				}
			
				for($n=0;$n<(($packetlength-34)*8);$n++)
				{
					if (($wrap==45) and (($n%$wrap==14) or ($n%$wrap==29) or ($n%$wrap==44)))
					{
						printf("<FONT COLOR=\"RED\">");
					}
					printf(substr($bin,$n,1));
					if (($wrap==45) and (($n%$wrap==14) or ($n%$wrap==29) or ($n%$wrap==44)))
					{
						printf("</FONT>");
					}

					if (($n%$wrap)==($wrap-1))
					{
						printf("\n");
					}
				}
			}
			else if (isset($_GET["hexdump"])  && $_GET["hexdump"]=="TRUE")
			{
				echo "\n<B>Hex Dump</B>\n";
				for($n=0;$n<($packetlength-34);$n++)
				{
					if (($n%16)==0)
						printf("%04X | ",$n);
					printf("<FONT COLOR=%s>%02X</FONT>",
					(($n%8)>3) ? (((((int)($n/16))%2)==0)?"#D00000":"#0000D0") :
					            (((((int)($n/16))%2)==0)?"#FF6060":"#6060FF") ,
					            $packet[34+$n]);
					if ((($n%16)!=15) && ($n!=($packetlength-35)))
						echo ",";

					if (($n%16)==15)
						echo "\n";
				}
			}
	}
	elseif ($type=="BS")
	{


	}
}
else
{
	$dopacketdump=TRUE;
}

if ($dopacketdump)
{
	if ($sc!=($ddshead[12]>>4))
	{
		echo "<FONT COLOR=RED SIZE=+1>File name Spacecraft and packet contents do not match!</FONT><BR>";
	}
	elseif ($phid_type[$ddshead[8]]!=$type)
	{
		echo "<FONT COLOR=RED SIZE=+1>File name Type and packet contents do not match!</FONT><BR>";
	}


	echo "\n\n<B>Raw Data Dump</B>\n\n";

	for($n=0;$n<$packetlength;$n+=16)
	{
		printf("%04X | ",$n);
		for($m=0;$m<16;$m++)
		{
			if (($n+$m)<$packetlength)
			{
				printf("%02X ",$packet[$n+$m]);
			}
			else
				echo "   ";

		}
		echo "  ";
		for($m=0;$m<16;$m++)
		{
			if (($n+$m)<$packetlength)
			{
				if (($packet[$n+$m]>32 && $packet[$n+$m]<128))
					echo htmlentities(chr($packet[$n+$m]));
				else
					echo "<FONT COLOR=RED>-</FONT>";
			}
		}
		echo "\n";
	}
}
echo "\n\n";
	echo "Packet #            : ".$packetposition."\n";
	echo "Position            : ".$offset[$packetposition]." bytes\n";

echo "</PRE>";

	$pb=$packetposition-1; if ($pb<0) $pb=0;
	$p3=(int)($pb/1000);
	$p2=(int)(($pb-$p3*1000)/100);
	$p1=(int)(($pb-$p3*1000-$p2*100)/10);
	$p0=       $pb-$p3*1000-$p2*100-$p1*10;
	echo "<A HREF=\"packet_inspect_process.php?year=".$year."&month=".$month."&day=".$day."&version=".$version."&type=".$type."&sc=".$sc."&hexdump=".((isset($_GET["hexdump"]) && $_GET["hexdump"]=="TRUE")?"TRUE":"FALSE")."&freq=".((isset($_GET["freq"]) && $_GET["freq"]=="TRUE")?"TRUE":"FALSE")."&packet0=".$p0."&packet1=".$p1."&packet2=".$p2."&packet3=".$p3."&mission=".$mission."&sciunits=".(isset($_GET["sciunits"])?$_GET["sciunits"]:"")."&modef=".(isset($_GET["modef"])?$_GET["modef"]:"")."\"><IMG SRC=\"../Images/leftarrow.png\" ALT=\"Previous Packet\" BORDER=0></A> ";

	$pa=$packetposition+1; if ($pa>=$count) $pa=$count-1;
	$p3=(int)($pa/1000);
	$p2=(int)(($pa-$p3*1000)/100);
	$p1=(int)(($pa-$p3*1000-$p2*100)/10);
	$p0=       $pa-$p3*1000-$p2*100-$p1*10;
	echo "<A HREF=\"packet_inspect_process.php?year=".$year."&month=".$month."&day=".$day."&version=".$version."&type=".$type."&sc=".$sc."&hexdump=".((isset($_GET["hexdump"]) && $_GET["hexdump"]=="TRUE")?"TRUE":"FALSE")."&freq=".((isset($_GET["freq"]) && $_GET["freq"]=="TRUE")?"TRUE":"FALSE")."&packet0=".$p0."&packet1=".$p1."&packet2=".$p2."&packet3=".$p3."&mission=".$mission."&sciunits=".(isset($_GET["sciunits"])?$_GET["sciunits"]:"")."&modef=".(isset($_GET["modef"])?$_GET["modef"]:"")."\"><IMG SRC=\"../Images/rightarrow.png\" ALT=\"Next Packet\" BORDER=0></A> ";
}
else
{
	$before=mktime(0,0,0,$month,$day-1,$year);  $byear=date("Y",$before);  $bmonth=date("m",$before);  $bday=date("d",$before);
	$after=mktime(0,0,0,$month,$day+1,$year);  $ayear=date("Y",$after);  $amonth=date("m",$after);  $aday=date("d",$after);

	echo "<A HREF=\"packet_inspect_process.php?year=".$byear."&month=".$bmonth."&day=".$bday."&version=".$version."&type=".$type."&sc=".$sc."&hexdump=".((isset($_GET["hexdump"]) && $_GET["hexdump"]=="TRUE")?"TRUE":"FALSE")."&freq=".((isset($_GET["freq"]) && $_GET["freq"]=="TRUE")?"TRUE":"FALSE")."\"><IMG SRC=\"../Images/bigleftarrow.png\" ALT=\"Previous Day\" BORDER=0></A> ";
	echo "<A HREF=\"packet_inspect_selection.php?year=".$year."&month=".$month."&day=".$day."&freq=".((isset($_GET["freq"]) && $_GET["freq"]=="TRUE")?"TRUE":"FALSE")."\"><IMG SRC=\"../Images/menu.png\" ALT=\"Menu\" BORDER=0></A> ";
	echo "<A HREF=\"packet_inspect_process.php?year=".$ayear."&month=".$amonth."&day=".$aday."&version=".$version."&type=".$type."&sc=".$sc."&hexdump=".((isset($_GET["hexdump"]) && $_GET["hexdump"]=="TRUE")?"TRUE":"FALSE")."&freq=".((isset($_GET["freq"]) && $_GET["freq"]=="TRUE")?"TRUE":"FALSE")."\"><IMG SRC=\"../Images/bigrightarrow.png\" ALT=\"Next Day\" BORDER=0></A>";
	echo "&nbsp;&nbsp;<A HREF=\"packet_inspect_process.php?year=".$year."&month=".$month."&day=".$day."&version=".$version."&type=".$type."&sc=".(($sc%4)+1)."&hexdump=".((isset($_GET["hexdump"]) && $_GET["hexdump"]=="TRUE")?"TRUE":"FALSE")."&freq=".((isset($_GET["freq"]) && $_GET["freq"]=="TRUE")?"TRUE":"FALSE")."\"><IMG SRC=\"../Images/cycle.png\" ALT=\"Next Spacecraft\" BORDER=0></A>";
}

foot($mission);

?>