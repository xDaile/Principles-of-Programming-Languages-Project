#!/usr/bin/python

# TODOs


import sys
import xml.etree.ElementTree as ET
import os
import re
import getopt

#regex for checking the string [ -~] are all printable characters
strre=r'^[ -~]*$'

#regex for checking the label and the var name
labre=(r'^([A-Za-z\-$_&%*!?])([A-Za-z0-9\-_$&%*!?])*$')
stringregex=re.compile(strre)
labelregex=re.compile(labre)
varregex=labelregex

#list of global variabiles
GF = []

#stack with frames
framesStack = []

#LF is empty because stack wasnt pushed yet,top of the framestack
LF = None

#TF is empty because createframe wasnt used yet
TF = None  # BUT IT IS NOT DEFINED

#stack for pushs/pops instructions
stack = []

#stack with call positions
calls = []

# list with name of the instructions,and number of their arguments
listOfins = {"MOVE": "2", "CREATEFRAME": "0", "PUSHFRAME": "0", "POPFRAME": "0", "DEFVAR": "1", "CALL": "1",
             "RETURN": "0", "PUSHS": "1", "POPS": "1", "ADD": "3", "SUB": "3", "MUL": "3", "IDIV": "3", "LT": "3",
             "GT": "3", "EQ": "3", "AND": "3", "OR": "3", "NOT": "2", "INTCHAR": "2", "STRI2INT": "3", "READ": "2",
             "WRITE": "1", "CONCAT": "3", "STRLEN": "2", "GETCHAR": "3", "SETCHAR": "3", "TYPE": "2", "LABEL": "1",
             "JUMP": "1", "JUMPIFEQ": "3", "JUMPIFNEQ": "3", "EXIT": "1", "DPRINT": "1", "BREAK": "0"}

#list of label names
listOfLabels = []

"""
Functions declaration
"""

#get the string, convert the \num num num to char
def getStr(str):
    str=str["value"]
    seqMatch = r'[\\][\d][\d][\d]'
    seqRe = re.compile(seqMatch)
    matches = seqRe.findall(str)
    for match in matches:
        rep=match[1:]
        rep=int(rep)
        rep=chr(rep)
        str=str.replace(match,rep)
    return (str)

#check the string value with the regex
def checkString(str):
    denyre = (r'[#]|([\\][\d][^0-9])|([\\][\d][\d][^0-9])|([\\][^0-9])|[\x00-\x1F]')
    regexDeny = re.compile(denyre)
    str=str.strip()
    if(str=="" or str==None):
        return
    strDenyChar=regexDeny.search(str)
    if(strDenyChar!=None):
        callErr("bad string value", 32)

#check the name of the label with the regex
def checkLabel(label):
    len=label.__len__()
    if(label=='' or label==None):
        callErr("label name bad format ",32)
    out=labelregex.match(label)
    if(out==None):
            callErr("label name bad format ",32)

#check the name of the variabile, with regex
def checkVarName(item):  # DOROBIT
    out=labelregex.match(item)
    if(out==None):
        callErr("var name bad format ",32)

#XML check if arguments of the instruction, have only one right tag
def checkChild(child):
   for argument in child:
       len=argument.attrib.__len__()
       if(len!=1):
           callErr("too much or not attributes for child",32)
       try:
           argument.attrib["type"]
       except KeyError:
           callErr("attribut in arg is not type",32)

       s=argument.__len__()
       if(s!=0):
           callErr("bad tag ",32)

#push the position of the xml code
def pushPosition(position):
    global calls
    calls.append(position)


#return the position in the xml instructions order, where the label is
def jump(label, i):  # NOT COMPLETE
    checkLabel(label)
    now = i
    for p in listOfLabels:
        if instruction[0].text == p["labelName"]:
            return int(p["position"])
    if (i == now):
        callErr("label not found", 52)
    return i

#returns the type of the sym
def checkType(type, arg):
    if (arg["type"] == "int"):
        return "int"
    if (arg["type"] == "string"):
        return "string"
    if (arg["type"] == "bool"):
        return "bool"
    if (arg["type"] == "nil"):
        return "nil"
    if (arg["type"] == "var"):
        val = getValueFromSym(arg)
        if (val["type"] == "int"):
            return "int"
        if (val["type"] == "string"):
            return "string"
        if (val["type"] == "bool"):
            return "bool"
        if (val["type"] == "nil"):
            return "nil"

#search for the name of the variabile in the global frame
def searchGF(name):
    global GF
    for p in GF:
        if p['name'] == name:
            return p
    callErr("bad name of var GF", 54)

#search for the name of the variabile in the temporary frame
def searchTF(name):
    global TF
    if (TF == None):
        callErr("TF is empty", 55)
    for p in TF:
        if p['name'] == name:
            return p
    callErr("bad name of var TF", 54)

#search for the name of the variabile in the temporary frame
def searchLF(name):
    global LF
    if (LF == None):
        callErr("LF is empty", 55)
    for p in LF:
        if p['name'] == name:
            return p
    callErr("bad name of var LF", 54)

#function that, will save received item(two sized list)
def saveItemToVar(item, framePart):  # type a value je v frame.. name je v framePart
    global GL, TF, LF
    try:
        frameArr = framePart.text.split("@")
    except AttributeError:
        callErr("name of var is not defined",32)
    if (frameArr.__len__() == 1):
        callErr("item in move is not var", 53)
    checkVarName(frameArr[1])
    if(item["type"]=="int"):
        try:
            int(item["value"])
        except ValueError:
            callErr("item that is going to save is not int",52)
    if (item["type"] == "string"):
        checkString(item["value"])
    if (item["type"] == "nil"):
        if(item["value"]!="nil"):
            callErr("bad nil to var",52)
    if (item["type"] == "bool"):
        if(item["value"]!="true" and item["value"]!="false"):
            callErr("bool to save is neither false nor true",52)
    if (frameArr[0] == "GF"):
        rem = searchGF(frameArr[1])
        GF.remove(rem)
        rem["type"] = item["type"]
        rem["value"] = item["value"]
        GF.append(rem)
    elif (frameArr[0] == "LF"):
        rem = searchLF(frameArr[1])
        LF.remove(rem)
        rem["type"] = item["type"]
        rem["value"] = item["value"]
        LF.append(rem)
    elif (frameArr[0] == "TF"):
        rem = searchTF(frameArr[1])
        TF.remove(rem)
        rem["type"] = item["type"]
        rem["value"] = item["value"]
        TF.append(rem)
    else:
        callErr("item in move is not var", 53)
    return

#XML sorting childs of the intstruction by they tag
def sortArgs(instruction):
    arguments = []
    try:
        if (instruction[0].tag == "arg1"):
            arguments.append(instruction[0])
        elif (instruction[1].tag == "arg1"):
            arguments.append(instruction[1])
        elif (instruction[2].tag == "arg1"):
            arguments.append(instruction[2])

        if (instruction[0].tag == "arg2"):
            arguments.append(instruction[0])
        elif (instruction[1].tag == "arg2"):
            arguments.append(instruction[1])
        elif (instruction[2].tag == "arg2"):
            arguments.append(instruction[2])
        if (instruction.__len__() == 3):
            if (instruction[0].tag == "arg3"):
                arguments.append(instruction[0])
            elif (instruction[1].tag == "arg3"):
                arguments.append(instruction[1])
            elif (instruction[2].tag == "arg3"):
                arguments.append(instruction[2])
        if (arguments.__len__() != instruction.__len__()):
            callErr("sorting arguments went wrong", -5)
    except IndexError:
        callErr("index in child out of range or bad",32)
    except KeyError:
        call("keys in arg is bad",32)
    return arguments

#pop out the frame from LF
def popFrame():
    global TF, framesStack, LF

    len = framesStack.__len__()
    if (len == 0):
        callErr("emptyStack popframe", 55)
    else:
        TF = framesStack.pop()
        if(framesStack.__len__()==0):
            LF=None
        else:
            LF = framesStack[-1]

#push frame from TF,to framestack,actualize LF
def pushFrame(do):
    global LF, TF, framesStack
    if(do==0):
        if(TF==None):
            callErr("frame was not defined",55)
    framesStack.append(TF)
    LF = framesStack[-1]
    TF = None

#creating the TF frame
def createFrame():
    global TF
    TF = []

#Calling the error, msg will be written to stderr, and the program will exit with value of the argument code
def callErr(msg, code):
    print(msg, file=sys.stderr)
    sys.exit(code)
    raise SystemExit

#XML sorting the instructions by they order
def sortchildrenby(parent, attr):
    try:
        parent[:] = sorted(parent, key=lambda child: int(child.get(attr)))
    except TypeError:
        callErr("order of the instructions is not okay",32)

#XML reading the xml, and sorting the instructions by they order, also checks the root tags,
def sortInstructions(filename):
    sortedInstructions = []
    tree = None
    try:
        tree = ET.parse(filename)
    except ET.ParseError:
        callErr("cannot parse, parseerror", 31)
    except ValueError:
        callErr("cannot parse,valueError", 31)
    except FileNotFoundError:
        callErr("cannot parse,File not found", 11)
    except subprocess.CalledProcessError:
        callErr("cannot parse, process error", 31)
    except OSError as e:
        callErr("cannot open file, osError, permisions maybe?", 11)
    root = tree.getroot()
    nOfTagsRoot=root.attrib.__len__()
    try:
       if(root.attrib["language"]!="IPPcode19"):
            callErr("bad root tag value",32)
    except KeyError:
        callErr("bad root tag",32)
    if(nOfTagsRoot==2):
        try:
            if (root.attrib["name"]):
                pass
        except KeyError:
            try:
                if (root.attrib["description"]):
                    pass
                else:
                    callErr("bad root tag", 32)
            except KeyError:
                callErr("bad root tag",32)
        try:
            if (root.attrib["description"]):
                pass
        except KeyError:
            try:
                if (root.attrib["name"]):
                    pass
                else:
                    callErr("bad root tag", 32)
            except KeyError:
                callErr("bad tag name",32)
    elif(nOfTagsRoot==3):
        try:
            if (root.attrib["description"]):
                if(root.attrib["name"]):
                    pass
        except KeyError:
            callErr("bad root tag", 32)
    elif(nOfTagsRoot>3 ):
        callErr("bad num of attributes in program",32)

    #Root is verified, now sorting the instructions
    sortchildrenby(root, 'order')
    i=1
    for child in root:
        checkChild(child)
        try:
            pos = int(child.attrib["order"])
            op = child.attrib["opcode"]
            op = op.upper()
        except KeyError:
            callErr("bad tag instruction",32)
        lenOfIns=child.attrib.__len__()
        if(lenOfIns!=2):
            callErr("bad atributes in instruction",32)
        position = 0
        if (op == "LABEL"): #saving the labels
            checkLabel(child[0].text)
            if(child[0].attrib["type"]!="label"):
                callErr("bad label type",32)
            for c in listOfLabels:  # check if the label is not existing yet
                if (c["labelName"] == child[0].text):
                    callErr("Same label twice", 52)
            position = int(child.attrib["order"]) - 1
            listOfLabels.append({"labelName": child[0].text, "position": position})
        if op in listOfins: #check number of the arguments
            if (int(child.__len__()) != int(listOfins[op])):
                callErr("bad number of arguments ", 32)
        for ins in sortedInstructions: #check if the order is not twice
            nowPos = int(ins.attrib["order"])
            if (pos == nowPos):
                callErr("bad xml, order is twice", 32)
        sortedInstructions.append(child)
    for insOrd in sortedInstructions:
        if(i!=int(insOrd.attrib["order"])):
            callErr("order is not correct, probably something is missing",32)
        i=i+1
    return sortedInstructions

#return the value from sym(var,string,int,bool,nil)
def getValueFromSym(item):
    itemforOutput = {}
    if (item.attrib["type"] == "var"):
        itemforOutput = getValueFromVar(item)
    else:
        if (item.attrib["type"] != "string" and item.attrib["type"] != "int" and item.attrib["type"] != "bool" and item.attrib["type"] != "nil" and item.attrib["type"] != None):
            callErr("sym has bad type", 32)
        if (item.attrib["type"] == "int"):
            try:
                item.text=int(item.text)
            except ValueError:
                callErr("symb is bad type", 52)
        if (item.attrib["type"] == "bool"):
            boolVal = item.text.upper()
            if (boolVal != "FALSE" and boolVal != "TRUE"):
                callErr("bool is not correct", 52)
        if (item.attrib["type"] == "nil"):
            if (item.text != "nil"):
                callErr("nil is some bad", 52)
        itemforOutput["type"] = item.attrib["type"]  # string,int,nil,bool
        itemforOutput["value"] = item.text
    if (itemforOutput["value"] == None):
        itemforOutput["value"] = ''
    return itemforOutput

#check if the type is var... used when saving something
def checkVarType(typ):
    if (typ != "var"):
        callErr("bad var in instruction", 32)

#will return value from the variable no matter what frame is it in
def getValueFromVar(item):
    itemforOutput = {}
    valueFromFrame = itemFromFrameName(item.text)
    itemforOutput["type"] = valueFromFrame["type"]
    itemforOutput["value"] = valueFromFrame["value"]
    return itemforOutput


# Get the item from the frame by its name
def itemFromFrameName(frameName):
    frameName = frameName.split("@")
    frame = frameName[0]
    if (frameName.__len__() == 1):
        callErr("bad Name of Var", 32)
    Name = frameName[1]
    if (frame == "GF"):
        item = searchGF(Name)  # NONE/ITEM
        if (item == None):
            callErr("Item not find", 54)
        return item

    elif (frame == "LF"):
        item = searchLF(Name)  # NONE/ITEM
        if (item == None):
            callErr("Item not find", 54)
        return item

    elif (frame == "TF"):
        item = searchTF(Name)  # NONE/ITEM
        if (item == None):
            callErr("Item not find", 54)
        return item
    else:
        callErr("item in move is not var", 53)

#actual position in code
i = 0

#done instruction
doneInsNum = 0

#input for the interpreter
itemforInput = 0

#mark if the argument sorce was find
src=False#WARNING DO DOKUMENTACIE... pri vstupe z stdin treba zadat xml ihned, nie entrovat
inpB=False

#file with source
srcF=-1

#file with input for the interpreter
inpF=-1

#get the arguments of the program, also check them
try:
    opts,args=getopt.getopt(sys.argv[1:],["help","source=","-input="],["help","source=","input="])
except getopt.GetoptError:
    callErr("Bad arguments of the program",10)
lenofOpt=opts.__len__()
if(lenofOpt>2):
    callErr("too much arguments",10)
for optArg in opts:
    if(optArg[0]=="--help"):
        if(lenofOpt==1):
            print("Help for the program")
            print("This is interpret Help")
            print("If you want some help use --help argument")
            print("If you have file with xml representation you ca use argument --source= file, in other case xml will loaded from stdin at the beginging of the program interpret.py ")
            print("if you have file with input for file, you can use argument --input=file, in other case input will be loaded from stdin")
            print("for other details see documentation")
            sys.exit(0)
        else:
            callErr("bad arguments try --help",10)
    if(optArg[0]=="--source"):
        src=True
        fileWithSrc=optArg[1]
    if(optArg[0]=="--input"):
        inpB=True
        fileWithInp=optArg[1]

#if src was not set, argument --source-file=file.xml was not find,
if(inpB==False):
    itemforInput=sys.stdin

#if the file with the input is set
if(inpB==True):
    try:
        itemforInput = open(fileWithInp)
    except OSError:
        callErr("cannot open file", 11)
if(src==False):
    sortedInstructions = sortInstructions(sys.stdin)
if(src==True):
    sortedInstructions=sortInstructions(fileWithSrc)

#num of the instructions
len = sortedInstructions.__len__()

#interpreting the program starts here, one step in the while interprets one instruction from the xml
while (i < len):
    doneInsNum = doneInsNum + 1
    instruction = sortedInstructions[i]

    #name of the instruction
    opcode = instruction.attrib["opcode"]
    opcode = opcode.upper()

    #instruction MOVE
    if (opcode == "MOVE"):
        args = sortArgs(instruction)
        val = getValueFromSym(args[1])
        checkVarType(args[0].attrib["type"])
        saveItemToVar(val, args[0])

    #instruction Createframe
    elif (opcode == "CREATEFRAME"):
        createFrame()

    #instruction pushframe
    elif (opcode == "PUSHFRAME"):
        pushFrame(0)

    #instruction popframe
    elif (opcode == "POPFRAME"):
        popFrame()


    #instruction defvar
    elif (opcode == "DEFVAR"):
        varName = instruction[0].text
        frameArr = varName.split("@")
        frame = frameArr[0]

        #if mark of the frame is bad
        if (frame != "GF" and frame != "TF" and frame != "LF"):
            callErr("defvar bad frame", 32)

        #checking the name of the var
        checkVarName(frameArr[1])
        if (instruction[0].attrib["type"] != "var"):
            callErr("not define var", 32)
        var = frameArr[1]
        insert = {"type": "", "name": var, "value": ""}
        if (frame == "GF"):
            for c in GF:
                if (c["name"] == var):
                    callErr("name of var already exists", 52)
            GF.append(insert)
        elif (frame == "TF"):

            if (TF == None):
                callErr(" Error, undefined frame", 55)
            for c in TF:
                if (c["name"] == var):
                    callErr("name of var already exists", 52)
            TF.append(insert)
        elif (frame == "LF"):
            if (framesStack.__len__() == 0):
                callErr("Error, on stack is nothing", 55)
            for c in LF:
                if (c["name"] == var):
                    callErr("name of var already exists", 52)
            framesStack[-1].append(insert)
        else:
            callErr("error Bad frame", 32)

    #instruction call , it is like calling the function
    elif (opcode == "CALL"):
       # print("call")
        pos = instruction.attrib["order"]
        if (instruction[0].attrib["type"] != "label"):
            callErr("calling on not lable", 32)
        pushFrame(1)
        createFrame()
        pushFrame(1)
        label = instruction[0].text
        checkLabel(label)
        pushPosition(i+1)
        jumpto = jump(label, i)
        i = jumpto

    #instruction Return, return to the instruction after call(which have to be before run)
    elif (opcode == "RETURN"):

        if (calls.__len__() == 0):
            callErr("Error during return", 56)
        pos = calls.pop()
        popFrame()
        popFrame()
        i = pos -1#at the end of the ifs it will count 1+

    #instruction PUSHS
    elif (opcode == "PUSHS"):
        value = getValueFromSym(instruction[0])
        if(value["type"]==""):
            callErr("trying to save non defined value",56)
        stack.append(value)

    #Instruction POPS
    elif (opcode == "POPS"):
        checkVarType(instruction[0].attrib["type"])
        if(stack.__len__() == 0):
            callErr("Empty stack", 56)
        item = stack.pop()
        saveItemToVar(item, instruction[0])

    #instruction add
    elif (opcode == "ADD"):
        args = sortArgs(instruction)
        arg2 = getValueFromSym(args[1])
        arg3 = getValueFromSym(args[2])
        checkVarType(args[0].attrib["type"])
        if ((checkType("int", arg2) != "int") or (checkType("int", arg3) != "int")):
            if(arg2["type"]=="" or arg2["type"]==None or arg3["type"]=="" or arg3["type"]==None):
                callErr("data is not initialized ",56)
            callErr("bad data type in add", 53)
        arg2 = int(arg2["value"])
        arg3 = int(arg3["value"])
        res = {"value": arg2 + arg3, "type": "int"}
        frameToSave = args[0]
        saveItemToVar(res, frameToSave)

    #instruction sub
    elif (opcode == "SUB"):
        args = sortArgs(instruction)
        arg2 = getValueFromSym(args[1])
        arg3 = getValueFromSym(args[2])
        checkVarType(args[0].attrib["type"])
        if ((checkType("int", arg2) != "int") or (checkType("int", arg3) != "int")):
            if(arg2["type"]=="" or arg2["type"]==None or arg3["type"]=="" or arg3["type"]==None):
                callErr("data is not initialized ",56)
            callErr("bad data type in sub", 53)
        arg2 = int(arg2["value"])
        arg3 = int(arg3["value"])
        res = {"value": arg2 - arg3, "type": "int"}
        frameToSave = args[0]
        saveItemToVar(res, frameToSave)

    #instruction mul
    elif (opcode == "MUL"):
        args = sortArgs(instruction)
        arg2 = getValueFromSym(args[1])
        arg3 = getValueFromSym(args[2])
        checkVarType(args[0].attrib["type"])
        if ((checkType("int", arg2) != "int") or (checkType("int", arg3) != "int")):
            if(arg2["type"]=="" or arg2["type"]==None or arg3["type"]=="" or arg3["type"]==None):
                callErr("data is not initialized ",56)
            callErr("bad data type in mul", 53)
        arg2 = int(arg2["value"])
        arg3 = int(arg3["value"])
        res = {"value": arg2 * arg3, "type": "int"}
        frameToSave = args[0]
        saveItemToVar(res, frameToSave)

    #instruction idiv
    elif (opcode == "IDIV"):
        args = sortArgs(instruction)
        arg2 = getValueFromSym(args[1])
        arg3 = getValueFromSym(args[2])
        checkVarType(args[0].attrib["type"])
        if ((checkType("int", arg2) != "int") or (checkType("int", arg3) != "int")):
            if(arg2["type"]=="" or arg2["type"]==None or arg3["type"]=="" or arg3["type"]==None):
                callErr("data is not initialized ",56)
            callErr("bad data type in idiv", 53)
        arg2 = int(arg2["value"])
        arg3 = int(arg3["value"])
        if (arg3 == 0):
            callErr("Dividing by the zero", 57)
        val = int(arg2 / arg3)
        res = {"value": val, "type": "int"}
        frameToSave = args[0]
        saveItemToVar(res, frameToSave)

    #instruction LT
    elif (opcode == "LT"):
        args = sortArgs(instruction)
        arg2 = getValueFromSym(args[1])
        arg3 = getValueFromSym(args[2])
        checkVarType(args[0].attrib["type"])
        if (arg2["type"] == "" or arg2["type"] == None or arg3["type"] == "" or arg3["type"] == None):
            callErr("data is not initialized ", 56)
        if (arg2["type"] != arg3["type"]):
            callErr("not equal types", 53)
        if (arg2["type"] == "int"):
            if (arg2["value"] < arg3["value"]):
                saved = {"type": "bool", "value": "true"}
            else:
                saved = {"type": "bool", "value": "false"}
        elif (arg2["type"] == "bool"):
            if ((arg2["value"] == "false") and (arg3["value"] == "true")):
                saved = {"type": "bool", "value": "true"}
            else:
                saved = {"type": "bool", "value": "false"}
        elif (arg2["type"] == "string"):
            if (arg2["value"] < arg3["value"]):
                saved = {"type": "bool", "value": "true"}
            else:
                saved = {"type": "bool", "value": "false"}
        else:
            callErr("bad type in lt", 32)
        saveItemToVar(saved, args[0])

    #instruction gt
    elif (opcode == "GT"):
        args = sortArgs(instruction)
        arg2 = getValueFromSym(args[1])
        arg3 = getValueFromSym(args[2])
        if (arg2["type"] == "" or arg2["type"] == None or arg3["type"] == "" or arg3["type"] == None):
            callErr("data is not initialized ", 56)
        checkVarType(args[0].attrib["type"])
        if (arg2["type"] != arg3["type"]):
            callErr("not equal types", 53)
        if (arg2["type"] == "int"):
            if (arg2["value"] > arg3["value"]):
                saved = {"type": "bool", "value": "true"}
            else:
                saved = {"type": "bool", "value": "false"}
        elif (arg2["type"] == "bool"):
            if ((arg2["value"] == "true") and (arg3["value"] == "false")):
                saved = {"type": "bool", "value": "true"}
            else:
                saved = {"type": "bool", "value": "false"}
        elif (arg2["type"] == "string"):
            if (arg2["value"] > arg3["value"]):
                saved = {"type": "bool", "value": "true"}
            else:
                saved = {"type": "bool", "value": "false"}
        else:
            callErr("bad type in gt", 32)
        saveItemToVar(saved, args[0])

    #instruction eq
    elif opcode == "EQ":
        args = sortArgs(instruction)
        arg2 = getValueFromSym(args[1])
        arg3 = getValueFromSym(args[2])
        if (arg2["type"] == "" or arg2["type"] == None or arg3["type"] == "" or arg3["type"] == None):
            callErr("data is not initialized ", 56)
        checkVarType(args[0].attrib["type"])
        if(arg2["type"]=="nil" or arg3["type"]=="nil"):
            saved = {"type": "bool", "value": "false"}
        elif (arg2["type"] != arg3["type"]):
            callErr("not equal types", 53)
        if (arg2["type"] == "int"):
            if (arg2["value"] == arg3["value"]):
                saved = {"type": "bool", "value": "true"}
            else:
                saved = {"type": "bool", "value": "false"}
        elif (arg2["type"] == "bool"):
            if (arg2["value"] == arg3["value"]):
                saved = {"type": "bool", "value": "true"}
            else:
                saved = {"type": "bool", "value": "false"}
        elif (arg2["type"] == "string"):
            if (arg2["value"] == arg3["value"]):
                saved = {"type": "bool", "value": "true"}
            else:
                saved = {"type": "bool", "value": "false"}
        elif (arg2["type"] == "nil"):

            if (arg2["value"] == arg3["value"]):
                saved = {"type": "bool", "value": "true"}
            else:
                saved = {"type": "bool", "value": "false"}
        else:
            callErr("bad type in gt", 32)

        saveItemToVar(saved, args[0])

    #instruction and
    elif opcode == "AND":
        args = sortArgs(instruction)
        arg2 = getValueFromSym(args[1])
        arg3 = getValueFromSym(args[2])
        if (arg2["type"] == "" or arg2["type"] == None or arg3["type"] == "" or arg3["type"] == None):
            callErr("data is not initialized ", 56)
        checkVarType(args[0].attrib["type"])
        if (arg2["type"] != "bool" or arg3["type"] != "bool"):
            callErr("bad data type in and", 53)
        if (arg2["value"] == arg3["value"] and arg2["value"]!="false" and arg3["value"]!="false"):
            saved = {"type": "bool", "value": "true"}
        else:
            saved = {"type": "bool", "value": "false"}
        saveItemToVar(saved, args[0])

    #instruction or
    elif opcode == "OR":
        args = sortArgs(instruction)
        arg2 = getValueFromSym(args[1])
        arg3 = getValueFromSym(args[2])
        if (arg2["type"] == "" or arg2["type"] == None or arg3["type"] == "" or arg3["type"] == None):
            callErr("data is not initialized ", 56)
        checkVarType(args[0].attrib["type"])
        if (arg2["type"] != "bool" or arg3["type"] != "bool"):
            callErr("bad data type in or", 53)
        if ((arg2["value"] == "true") or (arg3["value"] == "true")):
            saved = {"type": "bool", "value": "true"}
        else:
            saved = {"type": "bool", "value": "false"}
        saveItemToVar(saved, args[0])

    #instruction not
    elif opcode == "NOT":
        args = sortArgs(instruction)
        arg2 = getValueFromSym(args[1])
        if (arg2["type"] == "" or arg2["type"] == None):
            callErr("data is not initialized ", 56)
        checkVarType(args[0].attrib["type"])
        if (arg2["type"] != "bool"):
            callErr("bad data type in not", 53)
        if (arg2["value"] == "false"):
            saved = {"type": "bool", "value": "true"}
        else:
            saved = {"type": "bool", "value": "false"}
        saveItemToVar(saved, args[0])

    #instruction int2char
    elif opcode == "INT2CHAR":
        args = sortArgs(instruction)
        sym = getValueFromSym(args[1])
        checkVarType(args[0].attrib["type"])
        type = sym["type"]
        if (type != "int" and type != "string"):
            callErr("bad type in instruction int2char", 53)
        if (type == "string"):
            try:
                int(sym["value"])
            except ValueError:
                callErr("value in string cannot be converted to int")
        out = sym["value"]
        out = int(out)
        if (out < 0 or out > 917999):
            callErr("unicode out of range", 58)
        out = chr(out)
        itemToSave = {"type": "string", "value": out}
        saveItemToVar(itemToSave, args[0])

    #instrukction stri2int
    elif (opcode == "STRI2INT"):
        args = sortArgs(instruction)
        str = getValueFromSym(args[1])
        str["value"]=getStr(str)
        #str=getStr(str)
        position = getValueFromSym(args[2])
        checkVarType(args[0].attrib["type"])
        if (str["type"] != "string" or position["type"] != "int"):
            callErr("bad type in str2int", 53)
        pos = position["value"]
        str = str["value"]
        pos = int(pos)
        strLen = str.__len__()
        if (pos >= strLen or pos < 0):
            callErr("bad position in string", 58)
        out = str[pos]
        out = ord(out)
        itemToSave = {"type": "int", "value": out}
        saveItemToVar(itemToSave, args[0])

    #instruction read
    elif (opcode == "READ"):
        args = sortArgs(instruction)
        checkVarType(args[0].attrib["type"])
        if (args[1].attrib["type"] != "type"):
            callErr("bad type", 32)
        inp = itemforInput.readline()
        try:
            if(inp[-1]=="\n"):
                inp=inp[:-1]
        except IndexError:
            pass
        type = args[1].attrib["type"]
        if (type != "type"):
            callErr("bad argument in read", 32)
        type = args[1].text
        if (type == "string"):
            itemToSave = {"type": "string", "value": inp}
        elif (type == "int"):
            try:
                int(inp)
                itemToSave = {"type": "int", "value": inp}
            except ValueError:
                itemToSave = {"type": "int", "value": 0}
        elif (type == "bool"):
            inp = inp.upper()
            if (inp == "TRUE"):
                itemToSave = {"type": "bool", "value": "true"}
            else:
                itemToSave = {"type": "bool", "value": "false"}
        else:
            callErr("bad type in read", 32)
        saveItemToVar(itemToSave, args[0])

    #instruction write
    elif (opcode == "WRITE"):  # ESCAPE SEQ? WARNING HERE
        val = getValueFromSym(instruction[0])
        if(val["type"]=="" or val["type"]==None):
            callErr("try to print empty uninitialized value",56)
        if ((val["value"] != None) and (val["value"] != "")):
            strOut=val["value"]
            if(val["type"]!="nil"):
                print(strOut, end='')

    #instruction concat
    elif (opcode == "CONCAT"):
        args = sortArgs(instruction)
        checkVarType(args[0].attrib["type"])
        sym1 = getValueFromSym(args[1])
        sym2 = getValueFromSym(args[2])
        if(sym1["type"]==None or sym2["type"]==None or sym1["type"]=='' or sym2["type"]==''):
            callErr("concat not initialized values",56)
        if (sym1["type"] != "string" or sym2["type"] != "string"):
            callErr("concat not strings", 53)
        st1 = sym1["value"]
        st2 = sym2["value"]
        if (sym1["value"] == None):
            st1 = ''
        if (sym2["value"] == None):
            st2 = ''
        out = st1 + st2
        itemToSave = {"type": "string", "value": out}
        saveItemToVar(itemToSave, args[0])

    #instruction strlen
    elif (opcode == "STRLEN"):
        args = sortArgs(instruction)
        checkVarType(args[0].attrib["type"])
        sym = getValueFromSym(args[1])
        if (sym["type"] != "string"):
            if(sym["type"]==None or sym["type"]==''):
                callErr("strlen uninitialized", 56)
            callErr("strlen bad type",53)
        str=getStr(sym)
        strLen=str.__len__()
        strLen=strLen
        itemToSave = {"type": "int", "value": strLen}
        saveItemToVar(itemToSave, args[0])

    #instruction getchar
    elif (opcode == "GETCHAR"):
        args = sortArgs(instruction)
        checkVarType(args[0].attrib["type"])
        sym1 = getValueFromSym(args[1])
        sym2 = getValueFromSym(args[2])
        if (sym2["type"] == None or sym1["type"] == '' or sym1["type"] == None or sym2["type"] == ''):
            callErr("getchar uninitialized", 56)
        if (sym2["type"] != "int" or sym1["type"] != "string"):
            callErr("getchar bad types", 53)
        position = int(sym2["value"])
        str = getStr(sym1)
        lenStr = str.__len__()
        if (lenStr <= position or position<0):
            callErr("index out of range getchar", 58)
        out = str[position]
        itemToSave = {"type": "string", "value": out}
        saveItemToVar(itemToSave, args[0])

    #instruction setchar
    elif (opcode == "SETCHAR"):
        args = sortArgs(instruction)
        checkVarType(args[0].attrib["type"])
        varToChange = getValueFromVar(args[0])
        sym1 = getValueFromSym(args[1])
        sym2 = getValueFromSym(args[2])
        if (sym2["type"] != "string" or sym1["type"] != "int" or varToChange["type"] != "string"):
            callErr("setchar bad types", 53)
        charToIn = getStr(sym2)
        if (charToIn.__len__() == 0):
            callErr("not set sym2", 58)
        charToIn = charToIn[0]
        strToChange = getStr(varToChange)
        newStr = list(strToChange)
        lenOfChanged = newStr.__len__()
        positionOfChange = int(sym1["value"])
        if (lenOfChanged == 0):
            callErr("var is empty", 58)
        if (newStr.__len__() <= positionOfChange or positionOfChange < 0):
            callErr("too big or not positive", 58)
        newStr[positionOfChange] = charToIn
        strToWrite = ''
        for ch in newStr:
            strToWrite += ch
        itemToSave = {"type": "string", "value": strToWrite}
        saveItemToVar(itemToSave, args[0])

    #instruction type
    elif (opcode == "TYPE"):
        args = sortArgs(instruction)
        checkVarType(args[0].attrib["type"])
        sym = getValueFromSym(args[1])
        type = sym["type"]
        itemToSave = {"type": "string", "value": type}
        saveItemToVar(itemToSave, args[0])

    #instruction label, do nothing, labels are saved already
    elif (opcode == "LABEL"):
        pass

    #instruction jump, jumps to position in code,
    elif (opcode == "JUMP"):
        arg = instruction[0]
        if (arg.attrib["type"] != "label"):
            callErr("label is needed", 32)
        jumpto = jump(instruction[0].text, i)
        i = jumpto

    #instruction jumpifeq
    elif (opcode == "JUMPIFEQ"):
        args = sortArgs(instruction)
        sym1 = getValueFromSym(args[1])
        sym2 = getValueFromSym(args[2])
        if (args[0].attrib["type"] != "label"):
            callErr("label is needed", 32)
        if (sym1["type"] != sym2["type"]):
            callErr("not same types jumpifeq", 53)
        if (sym1["value"] == sym2["value"]):
            jumpto = jump(instruction[0].text, i)
            i = jumpto

    #instruction jumpifneq
    elif (opcode == "JUMPIFNEQ"):
        args = sortArgs(instruction)
        sym1 = getValueFromSym(args[1])
        sym2 = getValueFromSym(args[2])
        if (args[0].attrib["type"] != "label"):
            callErr("label is needed", 32)
        if (sym1["type"] != sym2["type"]):
            callErr("not same types jumpifneq", 53)
        if (sym1["value"] != sym2["value"]):
            jumpto = jump(instruction[0].text, i)
            i = jumpto

    #instruction exit, will end the program
    elif (opcode == "EXIT"):
        sym = getValueFromSym(instruction[0])
        if (sym["type"] == "int"):
            ex = int(sym["value"])
            if(ex<0 or ex>49):
                callErr("bad error code",57)
            sys.exit(ex)
        if (sym["type"] == "string"):
            try:
                ex = int(sym["value"])
                if (ex < 0 or ex > 49):
                    callErr("bad error code", 57)
                exit(ex)
            except ValueError:
                callErr("bad type", 52)
        elif(sym["type"]==None or sym["type"]==''):
            callErr("unitialized value cannot be on exit",56)
        else:
            callErr("bad type", 52)

    #instruction dprint
    elif (opcode == "DPRINT"):
        sym = getValueFromSym(instruction[0])
        print(sym["value"], file=sys.stderr)

    #instruction break
    elif (opcode == "BREAK"):
        print("done instructions", doneInsNum-1, "\n", file=sys.stderr)
        print("position of instruction in code", i+1, "\n", file=sys.stderr)
        if(GF!=None):
            print("GF", GF, "\n", file=sys.stderr)
        if(TF!=None):
            print("TF", TF, "\n", file=sys.stderr)
        if(LF!=None):
            print("LF", LF, "\n", file=sys.stderr)

    #if the opcode is something else
    else:
        callErr("Wrong Name of the instruction", 32)
    #incrementing the position in the code
    i = i + 1 #

sys.exit(0)
