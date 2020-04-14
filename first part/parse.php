<?php
$instructions = array("MOVE","CREATEFRAME","PUSHFRAME","POPFRAME","DEFVAR","CALL","RETURN","PUSHS","POPS","ADD","SUB","MUL","IDIV","LT","GT","EQ","AND","OR","NOT","INT2CHAR","STRI2INT","READ","WRITE","CONCAT","STRLEN","GETCHAR","SETCHAR","TYPE","LABEL","JUMP","JUMPIFEQ","JUMPIFNEQ","EXIT","DPRINT","BREAK");
$instr_var_sym = array("MOVE","INT2CHAR","STRLEN","TYPE","NOT");
$instr_empty= array("PUSHFRAME","POPFRAME","CREATEFRAME","RETURN","BREAK");
$instr_var= array("DEFVAR","POPS");
$instr_sym=array("PUSHS","WRITE","EXIT","DPRINT");
$instr_lab=array("CALL","LABEL","JUMP");
$instr_lab_sym_sym=array("JUMPIFEQ","JUMPIFNEQ");
$instr_var_type=array("READ");
$instr_var_sym_sym=array("ADD","SUB","MUL","IDIV","LT","GT","EQ","AND","OR","CONCAT","GETCHAR","SETCHAR","STRI2INT");
//regular expresions
$boolregex = '/^bool@(false|true)$/';//if is not possible TRUE/FALSE then remove i
$commentregex= '/#.*$/';
$intregex='/^int@([+]|[-])?([0]|[1-9][0-9]*)+$/';
$varregex='/^(GF|LF|TF)@([a-z]|[0-9]|[A-Z]|[\-_\$&%\*!\?])+$/';
$typeregex='/^(int|string|bool)@$/';
$stringregex='/^string@([[:graph:]]|\\\\\d\d\d)+/'; //NEMAL BY TU BYT ESTE DOLAR???? na konci aby neboli za strignom kraviny
$labelregex='/^([a-z]|[A-Z]|[\-_\$&%\*!\?])([a-z]|[A-Z]|[0-9]|[\-_\$&%\*!\?])*$/';
$nilregex='/^(nil@nil)+$/';


// Sign for stats
class _sign{
    public $full=0;
    public $sign_loc=0;
    public $sign_com=0;
    public $sign_jump=0;
    public $sign_lab=0;
}

// function that check if the variabile is in the right format
function check_var($arg){
    global $varregex,$n_lines,$gen;
    if (find_type($arg) !== 'var') {
        $gen=23;
        exit(err_call("Argument 1 on line $n_lines is in bad format.\n", 23));
    }
    if (preg_match_all($varregex, $arg) != 1) {
        $gen=23;
        exit(err_call("Argument 1 on line $n_lines is in bad format.\n", 23));
    }
}

// checking if the ".ippcode2019" is at the first line
function check_first_line($text){
    global $commentregex,$n_comm;
    if(preg_match_all($commentregex,$text)){
        $n_comm++;
        $position_comm = strpos($text, "#");
        $text = substr($text, 0, $position_comm);
        $text=trim($text);
    }
    global $n_lines,$dom,$program;
    $text=trim(mb_strtolower("$text", 'UTF-8'));
    $comp_text=(mb_strtolower(".IPPcode19", 'UTF-8'));
    $text=strval("$text");
    if(strcmp($comp_text,$text)==0){
        $n_lines++;
        return 0;
    }
    else{
        return 1;

    }
}

//find the type of the given argument, by the regex
function find_type($unknown_type){
    global $boolregex, $nilregex,$intregex,$stringregex,$typeregex,$typeregex;
    global $varregex,$boolregex,$intregex,$stringregex,$nilregex,$typeregex;
    if(preg_match_all($varregex,$unknown_type)) {
        return "var";
    }
    elseif(preg_match_all($boolregex,$unknown_type)) {
        return "bool";
    }
    elseif(preg_match_all($intregex,$unknown_type)) {
        return "int";
    }
    elseif(preg_match_all($stringregex,$unknown_type)) {
        $matches=array();
        $matches2=array();
        if(preg_match_all('/[\\\]/',$unknown_type,$matches)){
            preg_match_all('/(\d\d\d)/',$unknown_type,$matches2);

            $matches=$matches[0];
            $matches2=$matches2[0];
            if(count($matches)!=count($matches2)) {
                die(err_call("Character / without numbers cannot be in string\n", 23));
            }
        }
        return "string";
    }
    elseif(preg_match_all($nilregex,$unknown_type)) {
        return "nil";
    }
    elseif(preg_match_all($typeregex,$unknown_type)) {
        return "type";
    }
    elseif(preg_match_all('/@/',$unknown_type)) {
        $gen=23;
        return 0;//TOTO ESTE NEJAKO PREMYSLI
       // return 0;
    }
    else{
        return "label";
    }
}

//return the type by the variabile , example string@osdifjosdjf will return string
function type_var($unknown_type){
    if(preg_match_all('/bool/',$unknown_type)){
        return 'bool';
    }
    elseif(preg_match_all('/string/',$unknown_type)){
        return 'string';
    }
    elseif(preg_match_all('/int/',$unknown_type)){
        return 'int';
    }
    elseif(preg_match_all('/nil/',$unknown_type)){
        return 'nil';
    }
    else{
        return 'error';
    }

}

//replace the escape sequention by the char
function str_repair($str){
    return $str;
}

//check the sym if it is in the correct format
function check_sym($arg){

    global $stringregex,$intregex,$nilregex,$boolregex,$varregex,$typeregex,$n_lines,$gen;
    if (find_type($arg) == 'string') {
        if (preg_match_all($stringregex, $arg) != 1) {
            if((preg_match_all('/^string@$/',$arg)!=1)){
                $gen=23;
               exit( err_call("Argument on line $n_lines is in bad format.\n", 23));
            }

        }
    }
    elseif (find_type($arg) == 'int') {
        if (preg_match_all($intregex, $arg) != 1) {
            if((preg_match_all('/^int@$/',$arg)==1)){
                return 0;
            }
            $gen=23;
            exit( err_call("Argument on line $n_lines is in bad format.\n", 23));
        }
    }
    elseif (find_type($arg) == 'nil') {
        if (preg_match_all($nilregex, $arg) != 1) {
            if((preg_match_all('/^nil@$/',$arg)==1)){
                return 0;
            }
            $gen=23;
            exit( err_call("Argument on line $n_lines is in bad format.\n", 23));
        }
    }
    elseif (find_type($arg) == 'bool') {
        if (preg_match_all($boolregex, $arg) != 1) {
            if((preg_match_all('/^bool@$/',$arg)==1)){
                return 0;
            }
            $gen=23;
            exit( err_call("Argument on line $n_lines is in bad format.\n", 23));
        }
    }
    elseif (find_type($arg) == 'var') {
        if (preg_match_all($varregex, $arg) != 1) {
            $gen=23;
            exit( err_call("Argument on line $n_lines is in bad format.\n", 23));
        }
    }
    elseif (find_type($arg) == 'type') {
        if (preg_match_all($typeregex, $arg) != 1) {
            $gen=23;
            exit( err_call("Argument on line $n_lines is in bad format.\n", 23));
        }
    }
    else {
        $gen=23;
        exit(err_call("SOmething wrong on line $n_lines is in bad format.\n", 23));
    }
}

//check the label if it is in the correct format
function check_lab($arg){
    global $labelregex,$n_lines,$gen;
    if(preg_match_all($labelregex,$arg)!=1){
        $gen=23;
        exit(err_call("Argument on line $n_lines is in bad format.\n",23));
    }
}

//generate the xml output for the instruction like move, add etc.
function xml_instruction($order,$argument){
    global $dom,$ins,$program;
    $ins = $dom->createElement('instruction');
    $ins->setAttribute('order',$order);
    $ins->setAttribute('opcode',$argument);
    $program->appendChild($ins);
}
//generate the xml output for the label
function xml_lab($argument){
    global $dom,$ins;
    $child=$dom->createElement('arg1');
    $child->setAttribute('type','label');
    $text=$dom->createTextNode("$argument");
    $child->appendChild($text);
    $ins->appendChild($child);
}

//generate the xml output for the sym{const or variabile}
function xml_sym($argument,$name){
    global $dom,$ins,$program,$child;
    $child=$dom->createElement($name);
    $typesm=find_type($argument);
    $text;
    if($typesm=='var'){
        $child->setAttribute('type','var');
        //POZOR vrati jednotku ak dostane len string@
        $text=$dom->createTextNode("$argument");
        $child->appendChild($text);
    }
    elseif($typesm=='string'){
        $child->setAttribute('type','string');
        $argument=str_repair($argument);
        $insert=str_replace('string@','',$argument);
        $text=$dom->createTextNode("$insert");
        $child->appendChild($text);
    }
    elseif($typesm=='bool'){
        $child->setAttribute('type','bool');
        $insert=str_replace('bool@','',$argument);
        $text=$dom->createTextNode("$insert");
        $child->appendChild($text);
    }
    elseif($typesm=='int'){
        $child->setAttribute('type','int');
        $insert=str_replace('int@','',$argument);
        $text=$dom->createTextNode("$insert");
        $child->appendChild($text);
    }
    elseif($typesm=='nil'){
        $child->setAttribute('type','nil');
        $insert=str_replace('nil@','',$argument);
        $text=$dom->createTextNode("$insert");
        $child->appendChild($text);
    }
    elseif($typesm=='type'){
        $value=type_var($argument);
        $child->setAttribute('type',$value);
    }
    $ins->appendChild($child);
}

//generate the xml output for the variabile
function xml_var($argument){
    global $dom,$ins;
    $child = $dom->createElement('arg1');
    $child->setAttribute('type','var');
    $text=$dom->createTextNode("$argument");
    $child->appendChild($text);
    $ins->appendChild($child);
}

//function for writing errors, it returns the second argument because xalling in exit for ending program immediately
function err_call($err_txt, $val){
    fwrite(STDOUT, "$err_txt\n");
    global $gen;
    if($val!=0){
        exit($val);
    }

}

//creating structure for sign for the stats
$stat_sign=new _sign();

//CHECKING the arguments and their count
$unknown_type="@";

//Number of arguments
$count_args=count($argv);
if($count_args>6){
    die(err_call("Too many arguments",10));
}
//array witch avabiable arguments
$ins_arguments=array("--stats","--loc","--comments","--jumps","--labels");

//index for cycle
$index=1;

//bool object for check of arrays
$s_args=new _sign();

//Checking the argumentss
while($index!=($count_args)){

    if(in_array($argv[$index],$ins_arguments)){
        if("--loc"==$argv[$index]){
            if($s_args->sign_loc>0){
                exit(errcal("Argument --loc two times, should be once",10));
            }
            else{
                $s_args->sign_loc=$index;
                $stat_sign->sign_loc=1;
            }
        }

        if("--comments"==$argv[$index]){
            if($s_args->sign_com>0){
                exit(errcal("Argument --comments two times, should be once",10));
            }
            else{
                $stat_sign->sign_com=1;
                $s_args->sign_com=$index;
            }
        }

        if("--labels"==$argv[$index]){
            if($s_args->sign_lab>0){
                exit(errcal("Argument --labels two times, should be once",10));
            }
            else{
                $stat_sign->sign_lab=1;
                $s_args->sign_lab=$index;
            }
        }

        if("--jumps"==$argv[$index]){
            if($s_args->sign_jump>0){
                exit(errcal("Argument --jumps two times, should be once",10));
            }
            else{
                $stat_sign->sign_jump=1;
                $s_args->sign_jump=$index;
            }
        }
    }
    if(preg_match_all('/^--stats=.*/', $argv[$index])){
        if($s_args->full>0){
            exit(errcal("Argument --stats two times, should be once",10));
        }
        else{
            $stat_sign->full=1;
            $s_args->full=$index;
        }
    }
$index++;
}
//check if one argument was not twice or more times
if($s_args->full==0){
    $ret=$s_args->sign_loc+$s_args->sign_com+$s_args->sign_jump+$s_args->sign_lab;
    if($ret!=0){
        exit(err_call("bad arguments ",12));
    }
}

if($count_args>1){
    $i=0;
}

//help param and writing the help on out
if((in_array("--help",$argv))){
    if(($count_args==2)){

        echo "Help for the php parser for the ippcode19\n";
        echo "\n";
        echo "Argument --help argument for printing help\n";
        echo "Program input must be code in language ippcode19\n";
        echo "\nArguments for printing out the stats obout code\n";
        echo "Argument --stats=file param --stats is necessity for printing out the statistics about the code, file is name of the file where the statistics will be printed out\n";
        echo "Argument --comments   for printing out the number of comments\n";
        echo "Argument --labels     for printing out the number of the defined labels where the program can jump\n";
        echo "Argument --jumps      for printing out the number of the jumps in the program\n";
        echo "Argument --loc        for printign out the number of the instructions written in code ippcode2019\n";
        die(0);
    }
    else{
        exit(err_call("with argument --help must be the only one argument",10));
        die(10);
    }
}

//objects for xml document
$dom=0;
$program;

//count of lines
$n_lines=1;

//count of comments
$n_comm=0;

//count of labels
$n_lab=0;

//count of instructions
$loc=0;

//sign for the ending
$gen=0;

//num of jumps
$jumps=0;

//ipening the file
$file=fopen('php://stdin',"r");//
if($file==FALSE){
    exit(err_call("Error during opening the input file",11));
}

//line that comes to the cycle
$input="";

//order of the instruction
$order=1;

//creating xml
$dom = new DomDocument("1.0", "UTF-8");
$program = $dom->createElement('program');
$program->setAttribute('language','IPPcode19');
$dom->appendChild($program);

//checking the first line
$input_line=fgets($file);
if(($n_lines==1)&&(check_first_line($input_line)==1)){
    $gen=21;
    exit(err_call("Missing 'IPPcode19' at the first line of the file.\n",21));
}
$n_lines=2;

//array for counting jumps
$INS_JUMPS=array("JUMP","JUMPIFEQ","JUMPIFNEQ");

//checking the rest of the code
while(($input_line=fgets($file))!==false){
    global $gen,$n_comm,$loc;
    $input_line = preg_replace('/\s+/', ' ', $input_line);
    $input_line=trim($input_line);   //delete spaces at the beggining and end of the line
    $input=$input_line;
    if(preg_match_all($commentregex,$input_line)){
        $n_comm++;
        global $input;
        $position_comm = strpos($input_line, "#");
        $input = substr($input_line, 0, $position_comm);
        $input=trim($input);
        if($position_comm==0){
            $n_lines++;
            continue;
        }
    }
    //*************************KONTROLA ARGUMENTOV******************************
    if($n_lines>1){

        //Line Into pieces
        $in_arr=explode(' ',$input);

        //Instruction is case insensitive
        $in_arr[0]=strtoupper($in_arr[0]);

        //count of words
        $n_args=count($in_arr);

        //if the first instruction is instruction
        if(in_array($in_arr[0],$INS_JUMPS)==true ){
            $jumps++;
        }

        //counting the labels
        global $n_lab;
        $labs=array("LABEL");
        if(in_array($in_arr[0],$labs)==true ){
            $n_lab++;
        }

        //counting the instructions
        if((in_array($in_arr[0],$instructions)==false )&&($in_arr[0]!=='')){
            $gen=22;
            exit(err_call("One of the fist words -$in_arr[0] is not in correct format. on line $n_lines\n",22));
            continue;
        }
        //If is instruction in group of instructions that need three arguments and number of words is accurate
        elseif((in_array($in_arr[0],$instr_var_sym_sym))&&($n_args==4)) {
            $loc++;
            check_var($in_arr[1]);
            check_sym($in_arr[2]);
            check_sym($in_arr[3]);

            if($gen!==0){
                $order++;
                $n_lines++;
                continue;
            }
            $n_lines++;
            xml_instruction($order,$in_arr[0]);
            xml_var($in_arr[1]);
            xml_sym($in_arr[2],"arg2");
            xml_sym($in_arr[3],"arg3");
            $order++;
            continue;
        }
        elseif((in_array($in_arr[0],$instr_var))&&($n_args==2)) {
            $loc++;

            check_var($in_arr[1]);
            global $dom,$program;
            if($gen!==0){
                $order++;
                $n_lines++;
                continue;
            }
            $n_lines++;
            xml_instruction($order,$in_arr[0]);
            xml_var($in_arr[1]);
            $order++;
            continue;
        }
        elseif((in_array($in_arr[0],$instr_sym))&&($n_args==2)) {
            $loc++;

            check_sym($in_arr[1]);
            global $dom,$program;
            if($gen!==0){
                $order++;
                $n_lines++;
                continue;
            }
            $n_lines++;
            xml_instruction($order,$in_arr[0]);
            xml_sym($in_arr[1],"arg1");
            $order++;
            continue;
        }
        elseif((in_array($in_arr[0],$instr_lab_sym_sym))&&($n_args==4)) {
            $loc++;

            check_lab($in_arr[1]);
            check_sym($in_arr[2]);
            check_sym($in_arr[3]);
            if($gen!==0){
                $order++;
                $n_lines++;
                //$mark=1;
                continue;
            }
            global $dom,$program;
            $n_lines++;
            xml_instruction($order,$in_arr[0]);
            xml_lab($in_arr[1]);
            xml_sym($in_arr[2],"arg2");
            xml_sym($in_arr[3],"arg3");
            $order++;
            continue;
        }
        elseif((in_array($in_arr[0],$instr_var_sym)==true)&&($n_args==3)) {
            $loc++;
            global $ins,$child;

            check_var($in_arr[1]);
            check_sym($in_arr[2]);
            if($gen!==0){
                $order++;
                $n_lines++;
                continue;
            }
            global $dom,$program;
            $n_lines++;
            xml_instruction($order,$in_arr[0]);
            xml_var($in_arr[1]);
            xml_sym($in_arr[2],"arg2");
            $order++;
            continue;
        }
        elseif((in_array($in_arr[0],$instr_empty))&&($n_args==1)) {
            $loc++;
            if($gen!==0){
                $order++;
                $n_lines++;
                continue;
            }
            $n_lines++;
            xml_instruction($order,$in_arr[0]);
            $order++;
            continue;
            }
        elseif((in_array($in_arr[0],$instr_var_type))&&($n_args==3)) {
            $loc++;

            check_var($in_arr[1]);
            if(preg_match_all($typeregex,$in_arr[2])!=1){
                $gen=23;
               exit( err_call("Argument 2 on line $n_lines is in bad format.\n",23));
            }
            if($gen!==0){
                $order++;
                $n_lines++;
                continue;
            }
            $n_lines++;
            $typesm=find_type($in_arr[2]);
            global $dom,$program;
            xml_instruction($order,$in_arr[0]);
            xml_var($in_arr[1]);
            $child=$dom->createElement('arg2');
            $typ=type_var($in_arr[2]);
            $child->setAttribute('type',"$typ");
            $ins->appendChild($child);
            $order++;
            continue;
          }
        elseif((in_array($in_arr[0],$instr_lab))&&($n_args==2)) {
            $loc++;
            $typesm=find_type($in_arr[1]);
            check_lab($in_arr[1]);
            if($gen!==0){
                $order++;
                $n_lines++;
                continue;
            }
            global $dom,$program;
            $n_lines++;
            xml_instruction($order,$in_arr[0]);
            $child=$dom->createElement('arg1');
            $child->setAttribute('type','label');
            $text=$dom->createTextNode("$in_arr[1]");
            $child->appendChild($text);
            $ins->appendChild($child);
            $order++;
            continue;
        }
        elseif($in_arr[0]=='') {
            $n_lines++;
            continue;
        }
        else{
       if($gen!=0 ){
                continue;
            }
            $gen=23;
            exit(err_call("Bad number of arguments on line:$n_lines\n",23));
        }
    }
}
$dom->formatOutput = true;

///printing out the stats WARNING TO THE FILE MUST BE
if($gen==0){
    echo $dom->saveXML();
    if($stat_sign->full) {
        $f_out=$argv[$s_args->full];
        $f_out = explode("=",$f_out);
        $f_out_name=$f_out[1];
        $stats_file=fopen($f_out_name,"w");
        if($stats_file==FALSE){
            exit(err_call("Error during opening the output file",11));
        }
        $count=count($argv);
        if($count-1>max($s_args->sign_jump,$s_args->sign_com,$s_args->sign_loc,$s_args->full,$s_args->sign_lab)){
            die(err_call("Bad arguments",10));
        }
        $i=0;
        if($s_args->sign_jump==0){
            $s_args->sign_jump=100;
        }
        if($s_args->sign_com==0){
            $s_args->sign_com=100;
        }
        if($s_args->sign_loc==0){
            $s_args->sign_loc=100;
        }
        if($s_args->sign_lab==0){
            $s_args->sign_lab=100;
        }
        while($i<=$count ){
            $arr_for_min=min(array($s_args->sign_com,$s_args->sign_loc,$s_args->sign_jump,$s_args->sign_lab));
            if($arr_for_min==100){
                break;
            }
            if ($s_args->sign_loc == $arr_for_min) {
                $s_args->sign_loc = 100;
                fwrite($stats_file, "$loc" . PHP_EOL);
            }

            if ($s_args->sign_jump == $arr_for_min) {
                $s_args->sign_jump = 100;
                fwrite($stats_file, "$jumps" . PHP_EOL);
            }

            if ($s_args->sign_com == $arr_for_min) {
                $s_args->sign_com = 100;
                fwrite($stats_file, "$n_comm" . PHP_EOL);
            }

            if ($s_args->sign_lab == $arr_for_min) {
                $s_args->sign_lab = 100;
                fwrite($stats_file, "$n_lab" . PHP_EOL);
            }
            $i++;
        }
    }
}
else{
    exit($gen);
}