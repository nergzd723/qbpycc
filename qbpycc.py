import sys
import os
verbose = False
class Nasmsheet:
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
            self.interpret(word)
    def __init__(self, content):
        self.content = content
        self.text = ""
        self.bss = ""
        self.data = ""
        self.printstring = ""
        self.var = []
        self.varcontent = []
        self.mctr = 0
    def interpret(self, keyword):
        if keyword == "END":
            self.text = self.text + "mov rax, 60\nxor rdi, rdi\nsyscall\n"
        if keyword == "CLS":
            return
        if keyword[:5] == "PRINT":
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
        if keyword == "LET":
            keyword1 = keyword[:3]
            keyword1.replace(" ", "")
            for letter in keyword1:
                if letter == "=":
                    self.var.append(keyword1[keyword1.index(letter)])
                    self.varcontent.append(keyword1[keyword1.index(letter)])
                    break
def main():
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
    sourcehandle = open(source, "r")
    content = sourcehandle.readlines()
    content = [x.strip() for x in content]
    if verbose:
        print("Interpreting...")
    sheet = Nasmsheet(content)
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
    os.system("ld qbpycc.o -o "+output)
    sourcehandle.close()
    os.remove("qbpycc.o")
    os.remove("qbpycc.tmp")
if __name__ == "__main__":
    main()