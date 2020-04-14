<?php



#Writing error on stderr
function callErr($msg, $code)
{
    fwrite(STDERR, "$msg\n");
    exit($code);
}

#If true, parse is in the directory,and test.php will test it
$parseDo = true;

#same as parseDo, just with interpret
$interpretDo = true;

#recursive search directory mark
$recursive = false;

#name of the interpret script
$interpret = "./interpret.py";

#name of the parse script
$parse = "./parse.php";

#path to the directory with test files
$testPath = ".";

#opts for arguments of the program
$opts = array("help", "directory:", "recursive", "parse-script:", "int-script:", "parse-only", "int-only");
$shortopts = "help";
$shortopts .= "directory:";
$shortopts .= "recursive";
$shortopts .= "parse-script:";
$shortopts .= "int-script:";
$shortopts .= "parse-only";
$shortopts .= "int-only";

#get the argument of the program to array, check if there is something undefined
$args = getopt($shortopts, $opts);
if (count($args) != $argc - 1) {
    callErr("Undefined argument show help with argument --help", 10);
}
#if there is some argument
if ($argc != 1) {
    if (isset($args["help"])) {
        #if argument help is set, must be only one
        if ($argc > 2) {
            callErr("Undefined argument show help with argument --help", 10);
        }
        echo("Help for using the program test.php\n");
        echo("parameter --help for print out the help, must be only param\n");
        echo("parameter --directory=path for setting the directory where the tests are located\n");
        echo("parameter --recursive searching of the tests will be done in all subdirectories\n");
        echo("parameter --parse-script=file file is script in php 7.3 for analysis of source code(ippcode19), without this parameter, file must be in saame directory as this program\n");
        echo("parameter --int-script=file file is script in python 3.6 for implementation of source code(ippcode19 saved in XML format generated by parser), without this parameter, file must be in saame directory as this program\n");
        echo("parameter --parse-only will be done only tests for file for parsing the source, cannot be with parameter --int-onlu or --int-script\n");
        echo("parameter --int-only will be done only tests for interpreting the xml file, cannot be with param --parse-only or --parse-script\n");
        die(0);
    }
}
#change of the path to tests
if (isset($args["directory"])) {
    if(is_dir($args["directory"])==false){
        callErr("the given directory not found",11);
    }
    $testPath = $args["directory"];
}

#program will search in the tests recursively
if (isset($args["recursive"])) {
    $recursive = true;
}


if (isset($args["parse-script"])) {
    $parse = $args["parse-script"];

}

if (isset($args["int-script"])) {
    $interpret = $args["int-script"];

}

#cannot be parse only and int-script set at the same time
if (isset($args["parse-only"])) {
    if (isset($args["int-script"]) or isset($args["int-only"])) {
        callErr("Not allowed arguments", 10);
    } else {
        $parseDo = true;
        $interpretDo = false;
    }
}

#cannot be parse only and int-script set at the same time
if (isset($args["int-only"])) {
    if (isset($args["parse-script"]) or isset($args["parse-only"])) {
        callErr("Not allowed arguments", 10);
    } else {
        $interpretDo = true;
        $parseDo = false;
    }
}

if(file_exists($parse)==false and $parseDo==true) {
    callErr("Parse file missing", 11);
}

if(file_exists($interpret)==false and $interpretDo==true) {
    callErr("Interpret file missing", 11);
}


#searching for the tests, and initialization of the array with they names
if (!$recursive) {
    foreach (glob($testPath . '/*.*') as $filename) {
        $filesInDir[] = $filename;
    }
} else {#same but recursive
    foreach (new RecursiveIteratorIterator(new RecursiveDirectoryIterator($testPath)) as $file) {
        if (!is_dir($file)) {
            $filesInDir[] = $file->getPathname();
        }
    }
}

#set the src files, from all the files
foreach ($filesInDir as $file) {
    if (preg_match("/.+(.src)$/", $file)) {
        $srcFiles[] = $file;
    }
}
if (empty($srcFiles)) {
    callErr("Files with source code was not find", 11);
}
#if file with parse is missing and should not
/*
if ((in_array("$parse", $filesInDir) == False) and ($parseDo == True)) {

    callErr("missing parse.php", 11);
}

#if file with interpreter is missing and should not
if ((in_array("$interpret", $filesInDir) == false) and $interpretDo == True) {
    callErr("missing interpret.py", 11);
}
*/
#how many test i foung
$testNum = count($srcFiles);

#how many of them failed
$testFailed = 0;

#how many of them passed
$testPassed = 0;

#html code that we will appending by every test, and generate at the end of the testing
$htmlCode = "";

#how many tests is done
$testDone = 0;

#if we will not do parse testing, we filter only files for intepreter,
#same with interpret testing
#if we do both testing we filter tests for both programs only
if ($parseDo == False) {
    $srcFiles = preg_grep("/(\.\/int-only)/", $srcFiles);
} elseif ($interpretDo == False) {
    $srcFiles = preg_grep("/(\.\/parse-only)/", $srcFiles);
} else {
    $srcFiles = preg_grep("/(\.\/both)/", $srcFiles);
}

#going throught every one test, srcInput is variable with source for the test
foreach ($srcFiles as $srcInput) {

    $nameOfTest = substr($srcInput, 0, strrpos($srcInput, "."));

    #if rc file does not exists we will create file with 0
    if ((in_array($nameOfTest . ".rc", $filesInDir)) == false) {
        $rc_file = fopen($nameOfTest . ".rc", "w");
        if (!$rc_file) {
            callErr("cannot open rc file for $nameOfTest", 11);
        }
        fwrite($rc_file, "0\n");
        fclose($rc_file);
    }
    #get content of the file rc
    $rc = file_get_contents($nameOfTest . ".rc");

    #if .in file does not exists it is created(empty file)
    if (in_array($nameOfTest . ".in", $filesInDir)) {
        $inFile = fopen($nameOfTest . ".in", "r");
    } else {
        $inFile = fopen($nameOfTest . ".in", "c+");
    }

    #same as .in
    if (in_array($nameOfTest . ".out", $filesInDir)) {
        $outFile = fopen($nameOfTest . ".out", "r");
    } else {
        $outFile = fopen($nameOfTest . ".out", "c+");
    }
    fclose($outFile);
    fclose($inFile);

    #this can be deleted
    $outFile = $nameOfTest . ".tmp";
    $inputFile = $nameOfTest . ".in";
    #in exec comand must be php7.3 because of server "Merlin"


    #Testing parser
    if ($parseDo == True) {
        $xmlFromParser = 0;
        exec("php7.3 $parse<$srcInput", $xmlFromParser, $parseRet);#if there is only parser and int not, compare xmlforInt, check if in is empty?

        if ($parseRet != 0 and $interpretDo==False) {
            if ($parseRet != $rc) {
                $testFailed++;
                $testDone++;
                $htmlCode .= "<div class=\"testNOK\"><span class=\"DIR\">$nameOfTest</span><p>Expected Result:<strong> $rc</strong></p><p>Result: <span class=\"NOKResult\"><strong>$parseRet</strong></span></p></div>";

            }
            if ($parseRet == $rc) {
                $testPassed++;
                $testDone++;
                #UNDO THIS
                $htmlCode .= "<div class=\"testOK\"><span class=\"DIR\">$nameOfTest</span><p>Expected Result:<strong> $rc</strong></p><p>Result: <span class=\"OKResult\"><strong>$parseRet</strong></span></p></div>";

            }

        }

        #if we are not testing interpret, that is the end of our testing
        if ($interpretDo == False) {
            if ($rc == 0 and $parseRet == 0) {#xml must be compared
                $xml1 = new DOMDocument("1.0", "UTF-8");
                $parseOut = implode("\n", $xmlFromParser);
                $xml1->loadXML($parseOut);
                $strcmp1 = $xml1->C14N();
                $strcmp1 = preg_replace("/\s/", '', $strcmp1);
                $xml2 = new DOMDocument("1.0", "UTF-8");
                $xml = file_get_contents($nameOfTest . ".out");
                $xml2->loadXML($xml);
                $strcmp2 = $xml2->C14N();
                $strcmp2 = preg_replace("/\s/", '', $strcmp2);

                if ($strcmp1 == $strcmp2) {#return value is zero, and should be, and xml files are the same, SUCCESS TESTT
                    $htmlCode .= "<div class=\"testOK\"><span class=\"directory\">$nameOfTest</span><p>Expected Result:<strong> $rc</strong></p><p>Result: <span class=\"OKResult\"><strong>$parseRet</strong></span></p></div>";
                    $testPassed++;
                    $testDone++;
                } else {#return value is zero and should be but xml files are different
                    $htmlCode .= "<div class=\"testNOK\"><span class=\"directory\">$nameOfTest</span><p>Expected Result:<strong> $rc</strong></p><p>Result: <span class=\"NOKResult\"><strong>$parseRet</strong></span></p></div>";
                    $testFailed++;
                    $testDone++;
                }
            }/* else {#return value is zero but it should not
                $htmlCode .= "<div class=\"testNOK\"><span class=\"directory\">$nameOfTest</span><p>Expected Result:<strong> $rc</strong></p><p>Result: <span class=\"NOKResult\"><strong>$parseRet</strong></span></p></div>";
                $testFailed++;
                $testDone++;
            }*/
        }


    }
    #if we are not doing parse testing, file.src contains xml for the interpret
    if ($parseDo == False) {
        $xmlFromParser = file_get_contents($nameOfTest.".src");
    }

    #Testing the interpreter
    if ($interpretDo == True) {
        $in = $nameOfTest . ".in";
        $out = file_get_contents($nameOfTest . ".out");
        $rc = file_get_contents($nameOfTest . ".rc");
        #creating file with xml
        file_put_contents("thisWillIdelete.xml", $xmlFromParser);
        $interpretOut="";
        $interpretRet=0;
        exec("python3.6 " . $interpret . " --input=\"".$in."\" --source=thisWillIdelete.xml 2>/dev/null 1>/dev/null", $interpretOut, $interpretRet);#if there is only parser and int not, compare xmlforInt, check if in is empty?
        $interpretOut=shell_exec("python3.6 " . $interpret . " --input=\"".$in."\" --source=thisWillIdelete.xml 2>/dev/null");#if there is only parser and int not, compare xmlforInt, check if in is empty?
        #deleting created file
        unlink("thisWillIdelete.xml");

        if($interpretRet=="$0")
            $interpretRet=0;

        #if return value is not zero
        if ($interpretRet != 0) {
            #if the return values is same as the value in the rc file, SUCCESS
            if ($interpretRet == $rc) {

                $htmlCode .= "<div class=\"testOK\"><span class=\"directory\">$nameOfTest</span><p>Expected Result:<strong> $rc</strong></p><p>Result OK: <span class=\"OKResult\"><strong>$interpretRet</strong></span></p></div>";
                $testPassed++;
                $testDone++;
            } else {
                $htmlCode .= "<div class=\"testNOK\"><span class=\"directory\">$nameOfTest</span><p>Expected Result:<strong> $rc</strong></p><p>Result BAD: <span class=\"NOKResult\"><strong>$interpretRet</strong></span></p></div>";
                $testFailed++;
                $testDone++;
            }
        } else {#interpret return is zero
            if ($rc != 0) {#it should not be zero
                $htmlCode .= "<div class=\"testNOK\"><span class=\"directory\">$nameOfTest</span><p>Expected Result:<strong> $rc</strong></p><p>Result BAD: <span class=\"NOKResult\"><strong>$interpretRet</strong></span></p></div>";
                $testFailed++;
                $testDone++;
            } else {#int return value is zero, and it should be, we must compare the output of the interpreter, and content from the file.out
                if ($interpretOut == $out) {
                    $htmlCode .= "<div class=\"testOK\"><span class=\"directory\">$nameOfTest</span><p>Expected Result:<strong> $rc</strong></p><p>Result OK: <span class=\"OKResult\"><strong>$interpretRet</strong></span></p></div>";
                    $testPassed++;
                    $testDone++;
                } else {
                    $htmlCode .= "<div class=\"testNOK\"><span class=\"directory\">.$nameOfTest</span><p>Expected Result:<strong> $rc</strong></p><p>Result BAD: <span class=\"NOKResult\"><strong>$interpretRet</strong></span></p></div>";
                    $testFailed++;
                    $testDone++;
                }

            }
        }


    }
}
#if one of the tests does not passed
if($testFailed==0){
    $color="#e6ffe6";
}
else{
    $color="#998888";
}
#generating the html code
if ($htmlCode != ""){
    echo "<!DOCTYPE html>
    <html>
      <head>
         <title>IPPcode19</title>
         <meta charset=\"UTF-8\">
         <style type=\"text/css\">
         body {
         	overflow-x: hidden;

         	background-color: $color;
         	
         }
         .testOK{
         background-color:lightgreen;
         border-radius: 5px;
         margin: 25px;
         padding:10px;
         font-size:20px;

         }
         .testNOK{
         background-color:salmon;
         border-radius: 5px;
         margin: 25px;
         padding:10px;
         font-size:20px;

         }
         
         .content {
         	background-color:grey; 
         	border-radius: 15px;

         	padding:10px;
         	padding-left:50px;
         	padding-right:50px;
         	
         	
            
         	
         }
         p{
         font-size:17px;
         
         }
         h1{
         text-align: center;
         font-size:35px;
         }
         .directory{
         background-color: steelblue;
         font-color:red;

         
         }
         
         .OKResult{
         color:green;
         
         }
         
         .NOKResult{
         color:red;
         
         font-size:25px;
         }
         
         .result {
         	text-align: center;
         	font-size: 27px;
         	padding:10px;
         	font-weight: bold;
         	
         }
         .wrapper {
            margin-right:aut;
            margin-left:auto;
            max-width 960px;        
         	padding-top: 10px;
         	padding-bottom: 10px;
         	padding-left: 200px;
         	padding-right:200px;

         	
         }
         .result span {
         padding:10px;
         }
         .result span .green {
            
         	color: green;
         	margin-right: 4px;
         }
         .result span .red {
         	background-color: red;
         	font-size:21px;
         	padding:3px;
         	border:2px solid black;
         	
         }
       
         </style>
      </head>
      <body>
      <div class='wrapper'>
        <div class=\"content\">
         <h1>IPPcode2019</h1>
         <div class=\"result\">
         <span><span class=\"green\">&#9989;</span>: $testPassed</span>
         <span><span class=\"red\">&#9932;</span>: $testFailed</span>
         <span>celkem: $testDone</span>
       </div>

       <hr>";
    echo "$htmlCode";
    echo "</div></div></body></html>";
    }
die(0);