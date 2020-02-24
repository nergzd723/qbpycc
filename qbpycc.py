import sys
import os
verbose = False
class CCerr(Exception):
    def __init__(self, message, keyword):
        print("qbpycc: error "+message+" :\n"+keyword)
        exit(1)
class Nasmsheet:
    def printk(self, keyword):
        if '"' not in keyword:
            for letter in keyword:
                if letter.isdigit():
                    #probably has something to deal with math
                    keyword1 = keyword[keyword.index(letter):]
                    # Look, imagine we have PRINT 5+10
                    # Parsing it could be very difficult and also not efficient
                    # Temporary solution is just doing calculation in Python shell
                    # So, we just do self.printstring = *insert calculations here*
                    # But it won`t work in any other way
                    # Need parser very much
                    exec("self.printstring = str({})".format(keyword1))
                    # We already have number how much times has PRINT called
                    # So we increase it by 1, do printstring*insertnumberhere*: db "*insert value here*", 10
                    self.data = self.data + "printstring{}: ".format(str(self.mctr+1))+'db "{}", 10\n'.format(self.printstring)
                    self.mctr += 1
                    self.text = self.text + "mov rax, 1\nmov rdi, 1\nmov rsi, {}\nmov rdx, {}\nsyscall\n".format("printstring"+str(self.mctr), len(self.printstring)+1)
                    self.printstring = ""
                    return
        for letter in keyword:
            if letter == '"' or letter == "'":
                # Found "!
                # Cutting string before "!
                keyword1 = keyword[keyword.index(letter):]
                # Then searching for another one " or '
                for lette in keyword1:
                    if lette == '"' or lette == "'":
                        # Found second "!
                        # slicing string
                        keyword1 = keyword1[keyword1.index(letter)+1:]
                        keyword1 = keyword1[:-1]
                        # Got it, break from cycle
                        self.printstring = keyword1
                        break
        for letter in keyword:
            # Huh, it looks like we have ; symbol
            # It means that after that symbol it is an variable OR EXPRESSION!
            if letter == ";" and (keyword[keyword.index(letter)-1]  == '"' or keyword[keyword.index(letter)-1]  == "'"):
                # If we have it in internal buffer, just add it to string!
                vari = keyword[keyword.index(letter):]
                if vari in self.var:
                    self.printstring = self.printstring + self.varcontent[self.var.index(vari)]
                # Honestly, think that that internal buffer wasn't a good idea
                # Need parser EVEN MORE
        # doing the same thing as earlier
        self.data = self.data + "printstring{}: ".format(str(self.mctr+1))+'db "{}", 10\n'.format(self.printstring)
        self.mctr += 1
        # To perform a PRINT syscall we need rax set to OUTPUT, rdi set to STDOUT, rsi set to adress of string, and rdx set to lenght of it.
        # Just insert it here
        self.text = self.text + "mov rax, 1\nmov rdi, 1\nmov rsi, {}\nmov rdx, {}\nsyscall\n".format("printstring"+str(self.mctr), len(self.printstring)+1)
        self.printstring = ""
    def export(self):
        sheet = "bits 64\nsection .bss\n" #section bss
        sheet = sheet + self.bss
        sheet = sheet+"section .text\n" #code section
        sheet = sheet+"global _start\n" #entry label
        sheet = sheet+"_start:\n"
        sheet = sheet + self.text
        sheet = sheet+"section .data\n" #section data
        sheet = sheet + self.data
        sheet = sheet + "\n"
        return sheet
    def interpretall(self):
        for word in self.content:
            try:
                self.interpret(word)
            except:
                # If we even hit an internal Python error, we should quit, can't proceed further, needs bugfix
                raise CCerr("general compiler error", word)
    def __init__(self, content, isFullcc):
        self.content = content
        self.text = ""
        self.bss = ""
        self.data = ""
        self.printstring = ""
        self.var = []
        self.varcontent = []
        self.mctr = 0
        self.fcc = isFullcc
        self.varb = ""
    def interpret(self, keyword):
        if keyword[:3] == "REM" or keyword[:1] == "'":
            # REM or ' are comments
            keyword1 = keyword[1:]
            # This is a tricky thing. Python don't know is it a REM or a '
            # We can cutoff first symbol immedeately
            # I've done stupid thing there, if second letter is E than assume it's a REM
            # But if we encounter something like 'EEEEE it will cutoff some characters
            # Bugfix is pretty easy though
            if keyword1[0] == "E":
                keyword1 = keyword1[2:]
            self.text = self.text + ";"+keyword1+"\n"
            return
        elif keyword[:5] == "INPUT":
            if self.fcc:
                self.text = self.text + ";;;;;;;;;;;;;;;;;;;;\n;{}\n;;;;;;;;;;;;;;;;;;;;\n".format(keyword)
            keyword1 = keyword[5:]
            for letter in keyword1:
                if letter == ";":
                    # Find the variable to store input
                    keyword1w = keyword1.split(";")[0]
                    keyword1var = keyword1.split(";")[1]
                    # Call printk
                    self.printk(keyword1w)
                    # Reserve 1024B for the buffer
                    self.bss = self.bss + keyword1var+": resb 1024\n" # for now only 1024 B
                    # To perform a INPUT, we need rax set to INPUT, rdi set to STDIN, rsi set to variable, rdx set to size in bytes
                    self.text = self.text + "mov rax, 0\nmov rdi, 0\nmov rsi, {}\nmov rdx, 1024\nsyscall\n".format(keyword1var)
        elif keyword == "END":
            if self.fcc:
                self.text = self.text + ";;;;;;;;;;;;;;;;;;;;\n;{}\n;;;;;;;;;;;;;;;;;;;;\n".format(keyword)
                # To end the program, we need RAX set to 60, rdi set to 0
            self.text = self.text + "mov rax, 60\nxor rdi, rdi\nsyscall\n"
        elif keyword == "CLS":
            # CLS reason in all QBASIC programs is clearing the screen
            # But we can't clear STDOUT
            # So just skip it!
            if self.fcc:
                self.text = self.text + ";;;;;;;;;;;;;;;;;;;;\n;{}\n;;;;;;;;;;;;;;;;;;;;\n".format(keyword)
            return
        elif keyword[:5] == "PRINT":
            # Already explained
            varflag = False
            if self.fcc:
                self.text = self.text + ";;;;;;;;;;;;;;;;;;;;\n;{}\n;;;;;;;;;;;;;;;;;;;;\n".format(keyword)
            for letter in keyword:
                if letter == ";" and (keyword[keyword.index(letter)-1]  == '"' or keyword[keyword.index(letter)-1]  == "'"):
                    vari = keyword[keyword.index(letter)+1:]
                    keyword = keyword.split(";")[0]
                    varflag = True
                    self.varb = vari
            if '"' not in keyword:
                for letter in keyword:
                    if letter.isdigit():
                        #probably a MATH
                        keyword1 = keyword[keyword.index(letter):]
                        #using Python to MATH, I am not crazy to parse it by myself
                        exec("self.printstring = str({})".format(keyword1))
                        self.data = self.data + "printstring{}: ".format(str(self.mctr+1))+'db "{}", 10\n'.format(self.printstring)
                        self.mctr += 1
                        self.text = self.text + "mov rax, 1\nmov rdi, 1\nmov rsi, {}\nmov rdx, {}\nsyscall\n".format("printstring"+str(self.mctr), len(self.printstring)+1)
                        self.printstring = ""
                        return
            for letter in keyword:
                if letter == '"' or letter == "'":
                    keyword1 = keyword[keyword.index(letter):]
                    for lette in keyword1:
                        if lette == '"' or lette == "'":
                            keyword1 = keyword1[keyword1.index(letter)+1:]
                            keyword1 = keyword1[:-1]
                            self.printstring = keyword1
                            break
    
            self.data = self.data + "printstring{}: ".format(str(self.mctr+1))+'db "{}", 10\n'.format(self.printstring)
            self.mctr += 1
            self.text = self.text + "mov rax, 1\nmov rdi, 1\nmov rsi, {}\nmov rdx, {}\nsyscall\n".format("printstring"+str(self.mctr), len(self.printstring)+1)
            self.printstring = ""
            if varflag:
                vari = self.varb
                # indexable by compiler
                if vari in self.var:
                    self.printstring = self.printstring + self.varcontent[self.var.index(vari)]
                # not indexable by compiler or doesnt exist AT ALL
                else:
                    self.text = self.text + "mov rax, 1\nmov rdi, 1\nmov rsi, {}\nmov rdx, 1024\nsyscall\n".format(vari)
        elif keyword[:3] == "LET":
            if self.fcc:
                self.text = self.text + ";;;;;;;;;;;;;;;;;;;;\n;{}\n;;;;;;;;;;;;;;;;;;;;\n".format(keyword)
            # First, cutoff these LET characters
            keyword1 = keyword[3:]
            # Then, remove ANY whitespaces
            keyword1 = keyword1.replace(" ", "")
            # Split by "="
            varname = keyword1.split("=")[0]
            varc = keyword1.split("=")[1]
            # varname should be a name of variable
            # varcontent - it's content
            # write values to DATA sections
            self.data = self.data + varname+ ': db "{}", 10\n'.format(varc)
            # However, USE internal buffer too
            self.var.append(varname)
            self.varcontent.append(varc)
        else:
            raise CCerr("Not implemented or not an instruction", keyword)

def main():
    fullCC = False
    if "-v" in sys.argv:
        global verbose
        verbose = True
        print("QBpycc: QBasic interpreter to native x86 assembly using Linux syscalls")
        print("Accessing sources...")
    if "--help" in sys.argv:
        print("Additional args:\n-f -comment the process in the temporary file\n-T - pass the document to stdout\n-v - more verbosity\n-s - save temporary files")
    try:
        r = sys.argv[1:]
        source = r[0]
        output = r[1]
    except IndexError:
        print("Usage: qbpycc file.bas output.bin *additional args*")
        exit(1)
    if "-f" in sys.argv:
        fullCC = True
    sourcehandle = open(source, "r")
    content = sourcehandle.readlines()
    content = [x.strip() for x in content]
    if verbose:
        print("Interpreting...")
    sheet = Nasmsheet(content, fullCC)
    sheet.interpretall()
    shee = sheet.export()
    outputhandle = open("qbpycc.tmp", "w+")
    outputhandle.write(shee)
    outputhandle.close()
    if verbose:
        print("Using NASM...")
    os.system("nasm -felf64 qbpycc.tmp")
    if verbose:
        print("Linking...")
    if "-T" in sys.argv:
        print(shee)
    os.system("ld qbpycc.o -o "+output)
    sourcehandle.close()
    if "-s" not in sys.argv:
        os.remove("qbpycc.o")
        os.remove("qbpycc.tmp")
if __name__ == "__main__":
    main()
