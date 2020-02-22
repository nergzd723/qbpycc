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
                    #probably a statementon line "+line+" line
                    keyword1 = keyword[keyword.index(letter):]
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
        for letter in keyword:
            if letter == ";" and (keyword[keyword.index(letter)-1]  == '"' or keyword[keyword.index(letter)-1]  == "'"):
                vari = keyword[keyword.index(letter):]
                if vari in self.var:
                    self.printstring = self.printstring + self.varcontent[self.var.index(vari)]
    
        self.data = self.data + "printstring{}: ".format(str(self.mctr+1))+'db "{}", 10\n'.format(self.printstring)
        self.mctr += 1
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
    def interpret(self, keyword):
        if keyword[:3] == "REM" or keyword[:1] == "'":
            keyword1 = keyword[3:]
            self.text = self.text + ";"+keyword1
            return
        elif keyword[:5] == "INPUT":
            if self.fcc:
                self.text = self.text + ";;;;;;;;;;;;;;;;;;;;\n;{}\n;;;;;;;;;;;;;;;;;;;;\n".format(keyword)
            keyword1 = keyword[5:]
            for letter in keyword1:
                if letter == ";":
                    keyword1w = keyword1.split(";")[0]
                    keyword1var = keyword1.split(";")[1]
                    self.printk(keyword1w)
                    self.bss = self.bss + keyword1var+": resb 1024\n" # for now only 255 B
                    self.text = self.text + "mov rax, 0\nmov rdi, 0\nmov rsi, {}\nmov rdx, 255\nsyscall\n".format(keyword1var)
        elif keyword == "END":
            if self.fcc:
                self.text = self.text + ";;;;;;;;;;;;;;;;;;;;\n;{}\n;;;;;;;;;;;;;;;;;;;;\n".format(keyword)
            self.text = self.text + "mov rax, 60\nxor rdi, rdi\nsyscall\n"
        elif keyword == "CLS":
            if self.fcc:
                self.text = self.text + ";;;;;;;;;;;;;;;;;;;;\n;{}\n;;;;;;;;;;;;;;;;;;;;\n".format(keyword)
            return
        elif keyword[:5] == "PRINT":
            varflag = False
            if self.fcc:
                self.text = self.text + ";;;;;;;;;;;;;;;;;;;;\n;{}\n;;;;;;;;;;;;;;;;;;;;\n".format(keyword)
            for letter in keyword:
                if letter == ";" and (keyword[keyword.index(letter)-1]  == '"' or keyword[keyword.index(letter)-1]  == "'"):
                    vari = keyword[keyword.index(letter)+1:]
                    if vari in self.var:
                        self.printstring = self.printstring + self.varcontent[self.var.index(vari)]
                    else:
                        self.text = self.text + "mov rax, 1\nmov rdi, 1\nmov rsi, {}\nmov rdx, 1024\nsyscall\n".format(vari)
                    keyword = keyword.split(";")[0]
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
        elif keyword[:3] == "LET":
            if self.fcc:
                self.text = self.text + ";;;;;;;;;;;;;;;;;;;;\n;{}\n;;;;;;;;;;;;;;;;;;;;\n".format(keyword)
            keyword1 = keyword[3:]
            keyword1 = keyword1.replace(" ", "")
            varname = keyword1.split("=")[0]
            varc = keyword1.split("=")[1]
            self.data = self.data + varname+ ': db "{}", 10'.format(varc)
        else:
            raise CCerr("Not implemented or not an instruction", keyword)

def main():
    fullCC = False
    if "-v" in sys.argv:
        global verbose
        verbose = True
        print("QBpycc: QBasic interpreter to native x86 assembly using Linux syscalls")
        print("Accessing sources...")
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
    os.remove("qbpycc.o")
    os.remove("qbpycc.tmp")
if __name__ == "__main__":
    main()