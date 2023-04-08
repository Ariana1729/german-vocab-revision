from functools import reduce

#   """""""""""""
#   | Debugging |
#   """""""""""""

with open("/tmp/aaa","w") as f:
    f.write("")
def debw(s):
    with open("/tmp/aaa","a") as f:
        f.write(f"{s}\n")

#   """""""""""""""""""""""""""""
#   | Handling parsing of input |
#   """""""""""""""""""""""""""""

if False:
    import re

    # syntax:
    #   [der/die/das] [noun singular], die [noun plural]
    #   der/die [noun], die [noun(m) plural]
    #   der/die [noun(m)]/[noun(f)], die [noun(m) plural]/die [noun(n) plural]
    #   [der/die/das] [noun singular] (Sg.)
    #   [der/die/das] [noun plural] (Pl.)
    #   [verb], er [verb (present)], er hat [verb (perfect)]
    #   [verb], er [verb (present)], er ist [verb (perfect)]
    #   [verb], er [verb (present)], er [verb (past)] (Prät.)
    #   ([type], [form1], [form2], ...) [form1], [form2], ...

    re_noun1 = re.compile("(der|die|das) (\w+), die (\w+)")
    re_noun2 = re.compile("(der|die|das) (\w+) \(Sg.\)")
    re_noun3 = re.compile("(der|die|das) (\w+) \(Pl.\)")
    re_noun4 = re.compile("der/die (\w+), die (\w+)")
    re_noun5 = re.compile("der/die (\w+)/(\w+), die (\w+)/die (\w+)")
    re_verb1 = re.compile("(\w+), er (\w+), er (hat) (\w+)") # transitive verbs
    re_verb2 = re.compile("(\w+), er (\w+), er (ist) (\w+)") # intransitive verbs
    re_verb3 = re.compile("(\w+), er (\w+), er (\w+) \(Prät.\)")
    re_custo = re.compile("\((\w+), (\w+, )*(\w+)\)( (\w+),)+ (\w+)")

class Word:
    def __init__(self,line):
        ger,eng = line.split(" - ")
        self.ger = ger
        self.eng = eng
        self.weight = 1
        if ger[:3] in ["der","die","das"]: # noun
            if ger[3] != "/": # noun 1,2,3
                self.type = "Noun"
                ger = ger.split(", ")
                if len(ger) == 2: # noun 1
                    self.data = {
                        "Gender": ger[0][:3],
                        "Singular": ger[0][4:],
                        "Plural": ger[1][4:]}
                elif ger[0].endswith(" (Sg.)"): # noun 2
                    self.data = {
                        "Gender": ger[0][:3],
                        "Singular": ger[0][4:-6],
                        "Plural": None}
                elif ger[0].endswith(" (Pl.)"): # noun 3
                    self.data = {
                        "Gender": ger[0][:3],
                        "Singular": None,
                        "Plural": ger[0][4:-6]}
                else:
                    print(f"[DEBUG] An error occured with {line}")
                    exit()
            else: # noun 4,5
                self.type = "Noun (m/f)"
                ger = ger.split(", ")
                if "/" not in ger[1]: # noun 4
                    self.data = {
                        "Singular (m)": ger[0][8:],
                        "Singular (f)": ger[0][8:]}
                        # "Plural (m)": ger[1][4:],
                        # "Plural (f)": ger[1][4:]}
                else: # noun 5
                    ger[0] = ger[0][8:].split("/")
                    ger[1] = ger[1].split("/")
                    self.data = {
                        "Singular (m)": ger[0][0],
                        "Singular (f)": ger[0][1]}
                        # "Plural (m)": ger[1][0][4:],
                        # "Plural (f)": ger[1][1][4:]}
        elif ", er " in ger or ", es " in ger: # verb
            self.type = "Verb"
            ger = ger.split(", ")
            if ger[2][3:6] in ["hat","ist"]: # verb 1,2
                self.data = {
                    "Infinitive": ger[0],
                    "Present": ger[1][3:]}
                    # "Perfect": ger[2][7:]}
                    # "Perfect auxillary verb": ger[2][3:6]}
            elif ger[2].endswith(" (Prät.)"): # verb 3
                self.data = {
                    "Infinitive": ger[0],
                    "Present": ger[1][3:],
                    "Past": ger[2][3:-8]}
            else:
                print(f"[DEBUG] An error occured with {line}")
                exit()
        elif ger[0] == "(":
            ger = ger.split(") ")
            ger[0] = ger[0][1:].split(", ")
            ger[1] = ger[1].split(", ")
            self.type = ger[0][0]
            self.data = {i:j for i,j in zip(ger[0][1:],ger[1])}
        else:
            self.type = "Unknown"
            self.data = {"Word": self.ger}
        return
    def __str__(self):
        return f"Type: {self.type}\nEnglish: {self.eng}\n"+"\n".join(f"\t{i}: {j}" for i,j in self.data.items())

#   """""""""""""""""""""""
#   | Parsing into a tree |
#   """""""""""""""""""""""

vocab = open("vocab","r").read().strip().split("\n")
words = []
parts = [["Willkommen",["ABC",["1a",1337,1337]]]] # [chaptername, [sectionname, start, end], ...], i.e. [["Willkommen",["ABC",["1a",1,2]]],[...
for i in vocab:
    j = 0
    while i[j] == " ":
        j += 4
    match j:
        case 0:
            parts[-1][-1][-1][-1] = len(words)
            del parts[-1][-1][1]
            del parts[-1][1]
            parts.append([i,["ABC",["99",1337,1337]]])
        case 4:
            parts[-1][-1][-1][-1] = len(words)
            del parts[-1][-1][1]
            parts[-1].append([i[4:],["99",1337,1337]])
        case 8:
            parts[-1][-1][-1][-1] = len(words)
            parts[-1][-1].append([i[8:],len(words),None])
        case 12:
            if i[12]=="#":
                continue
            words.append(Word(i[12:]))
parts = parts[1:]
parts[-1][-1][-1][-1] = len(words)
del parts[-1][-1][1]
del parts[-1][1]
parts = ["Chapters"]+parts

#   """""""""""
#   | UI pain |
#   """""""""""

import curses

#   """""""""""""""""
#   | Input handler |
#   """""""""""""""""

chrs = list(b"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ \t")
kmap = {e:g for e,g in zip(b"aouAOUs","äöüÄÖÜß")}
cltrmap = {e:g for e,g in zip([1,15,21,19],"äöüß")}
#germap = {e:g for e,g in zip("äöüÄÖÜß".encode()[1::2],"äöüÄÖÜß")}
def getline(stdscr):
    s = ""
    buf = None
    while True:
        c = stdscr.getch()
        if buf:
            if buf == 195:
                s += bytes([buf,c]).decode("utf-8")
                stdscr.addstr(s[-1])
                buf = None
            elif buf == 11:
                if c in kmap:
                    s += kmap[c]
                    stdscr.addstr(s[-1])
                else:
                    s += "?"
                    stdscr.addstr(s[-1])
                buf = None
            continue
        if c == b"\n"[0]:
            break
        if c in chrs:
            s += chr(c)
            stdscr.addstr(s[-1])
        elif c in cltrmap:
            s += cltrmap[c]
            stdscr.addstr(s[-1])
        elif c in [127,263,330]:
            if s == "":
                continue
            y,x = stdscr.getyx()
            stdscr.move(y,x-1)
            stdscr.delch()
            s = s[:-1]
        elif c in [11,195]:
            buf = c
        else:
            # stdscr.addstr(f"\n {c} \n")
            continue
    return s

#   """"""""""""""""""""""""
#   | Generating word list |
#   """"""""""""""""""""""""

def parse_range(s):
    try:
        s = [(lambda l:[l[0]] if len(l)==1 else range(l[0],l[1]+1))([int(j) for j in i.split("-")]) for i in s.replace(" ","").split(",")]
    except:
        return None
    return [j for i in s for j in i]

def gen_wls_str(x,n=[]):
    if type(x) is int:
        if x==1: yield ".".join(str(i+1) for i in n)
    else:
        for m,i in enumerate(x):
            yield from gen_wls_str(i,n+[m])

def gen_wls(stdscr,wls,st):
    if wls==None:
        wls=[0]*(len(parts)-1)
    while True:
        s = ", ".join(gen_wls_str(wls))
        if s!="": stdscr.addstr("Current collection: \n"+s+"\n")
        t = reduce(lambda a,b:a[b+1],st,parts)
        tw = reduce(lambda a,b:a[b],st[:-1],wls)
        if type(t) is int:
            stdscr.clear()
            stdscr.move(0,0)
            stdscr.addstr("Error: Only allowed to choose range\n\n")
            st = st[:-1]
            continue
        if type(t[1]) is int:
            s = f"Number of words: {t[2]-t[1]}"
            t = [0]*(t[2]-t[1]+1)
        else:
            s = f"Parts of {t[0]}:\n"
            s += "\n".join(f"  {i+1}: {j[0]}" for i,j in enumerate(t[1:]))
        if len(st) and type(tw[st[-1]]) is int:
            tw[st[-1]] = [tw[st[-1]]]*(len(t)-1)
        s += "\nKey in 0 for all sections, a[range] to add a range, "
        if len(st): s += "b to go back, "
        s += "q to quit and s to start: "
        stdscr.addstr(s)
        inp = getline(stdscr)

        if inp == "b" and len(st):
            st = st[:-1]
            stdscr.clear()
            stdscr.move(0,0)
            continue
        if inp == "q":
            exit()
        if inp == "s":
            break
        if inp[0] == "a":
            inp = parse_range(inp[1:])
            if inp is None:
                stdscr.clear()
                stdscr.move(0,0)
                stdscr.addstr("Error: Not a range!\n\n")
                continue
            if any(not 0<i<len(t) for i in inp):
                stdscr.clear()
                stdscr.move(0,0)
                stdscr.addstr("Error: Number out of range\n\n")
                continue
        else:
            try:
                inp = int(inp)
            except:
                stdscr.clear()
                stdscr.move(0,0)
                stdscr.addstr("Error: Not a number!\n\n")
                continue
            if not 0<=inp<len(t):
                stdscr.clear()
                stdscr.move(0,0)
                stdscr.addstr("Error: Number out of range\n\n")
                continue
            inp -= 1
            if inp == -1:
                tw[st[-1]] = 1
                stdscr.clear()
                stdscr.move(0,0)
                continue
        if type(inp) is list:
            t = reduce(lambda a,b:a[b],st,wls)
            for i in inp:
                t[i-1] = 1
        else:
            st.append(inp)
        stdscr.clear()
        stdscr.move(0,0)
    stdscr.clear()
    stdscr.move(0,0)
    return wls,st

#   """"""""""""""""""""""""
#   | Getting random words |
#   """"""""""""""""""""""""

import random

def expand_wls(idx,wds):
    f = lambda s,n:s if type(s) is int else f(s[n],n)
    if type(wds[1]) is int:
        for n,i in enumerate(idx):
            if i==1:
                yield [wds[1]+n]
    for i,w in zip(idx,wds[1:]):
        if type(i) is int:
            if i==1:
                yield range(f(w,1),f(w,-1))
        else:
            yield from expand_wls(i,w)

def ger_test(stdscr,wls):
    cls = [j for i in expand_wls(wls,parts) for j in i]
    weights = [words[i].weight for i in cls]
    while True:
        wn = random.choices(range(len(cls)),weights)[0]
        w = words[cls[wn]]
        stdscr.addstr(f"English: {w.eng}, Weight: {weights[wn]}/{max(weights)}\n\n")
        stdscr.addstr(f"Type: {w.type}\n")
        c = True
        for typ,ans in w.data.items():
            stdscr.addstr(typ+": ")
            if ans is None:
                ans = ""
            t = getline(stdscr)
            if t != ans:
                stdscr.addstr(f"\nIncorrect, answer is '{ans}'\n")
                c = False
            else:
                stdscr.addstr(f"\nCorrect!\n")
        if c:
            weights[wn] /= len(cls)#**0.5
        else:
            weights[wn] *= len(cls)#**0.5
        c = ""
        while c not in list("cbq"):
            stdscr.addstr("\n(c)ontinue, (b)ack, (q)uit: ")
            c = getline(stdscr)
        stdscr.clear()
        stdscr.move(0,0)
        match c:
            case "c":
                continue
            case "b":
                break
            case "q":
                return False
    for wgt,wds in zip(weights,cls):
        words[wds].weight = wgt
    stdscr.clear()
    stdscr.move(0,0)
    return True

def main(stdscr):
    stdscr.scrollok(True)
    curses.cbreak()
    stdscr.clear()
    stdscr.move(0,0)
    stdscr.addstr(f"Hi! Here's just a really simple thing to help practice vocab\nLoaded {len(words)} words\nYou can add äöüÄÖÜß by typing Cltr+K aouAOUs or Cltr+aous for the lower case ones, try it! Press enter to continue\n")
    stdscr.addstr(f"Input: {getline(stdscr)}\n")
    getline(stdscr)
    stdscr.clear()
    stdscr.move(0,0)
    wls = None
    st = []
    while True:
        wls = None
        st = []
        wls,st = gen_wls(stdscr,wls,st)
        ger_test(stdscr,wls)

curses.wrapper(main)
