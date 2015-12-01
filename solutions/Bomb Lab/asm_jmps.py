#!/usr/bin/env python
# encoding: utf-8
"""
asm_jmps.py
Created by Daniel Fairchild on 2013-06-10.
Usage (in shell):
  objdump -M intel -d  target.bin | ./asm_jmps.py
License:
  I'd appreciate a comment at: http://blog.fairchild.dk/?p=633
  if you find the following usefull. That'll be all.
"""
import sys
import re

JMPS = { #define jumps, synomyms on same line
'ja':'if above', 'jnbe':'if not below or equal',
'jae':'if above or equal', 'jnb':'if not below', 'jnc':'if not carry',
'jb':'if below', 'jnae':'if not above or equal', 'jc':'if carry',
'jbe':'if below or equal', 'jna':'if not above',
'jcxz':'if cx register is 0', 'jecxz':'if cx register is 0',
'je':'if equal', 'jz':'if zero',
'jg':'if greater', 'jnle':'if not less or equal',
'jge':'if greater or equal',
'jl':'if less', 'jnge':'if not greater or equal',
'jle':'if less or equal', 'jnl':'if not less',
'jmp':'unconditional',
'jne':'if not equal', 'jnz':'if not zero',
'jng':'if not greater',
'jno':'if not overflow',
'jnp':'if not parity', 'jpo':'if parity odd',
'jns':'if not sign',
'jo':'if overflow',
'jp':'if parity', 'jpe':'if parity even',
'js':'if sign'}

fcl = re.compile(" +([\da-f]+)\:")
fjre=re.compile("".join([
            " +([\da-f]+)\:\\t.*(",
            "".join(map(lambda x: x+"|", JMPS))[:-1],
            ")\s+\*?0?x?([\da-f]+)"]))

def j_line(ln, ljmps):
  jl = len(ljmps)
  outl = [" "]*(jl+2)
  jdesc=""
  for i in range(jl):
    if ljmps[i][0] == ln: #jmp from
      outl[-(jl-i+2):] = ["-"]*(jl-i+2)
      outl[i] = "," if ljmps[i][0] < ljmps[i][1] else "\'"
      jdesc = "; jump %s" % ljmps[i][2]
    if ljmps[i][1] == ln: #jmp to
      outl[-(jl-i+1):] = ["-"]*(jl-i+1)
      outl[-1] = ">"
      outl[i] = "," if ljmps[i][0] > ljmps[i][1] else "\'"
    if ljmps[i][0] < ln and ljmps[i][1] > ln:
      outl[i] = "|"
    elif ljmps[i][0] > ln and ljmps[i][1] < ln:
      outl[i] = "|"
  return ("".join(outl),jdesc)

def drw_jmps(all_lines, fun_lines):
  ljmps = []
  for cl in fun_lines:
    m = fjre.match(all_lines[fun_lines[cl]])
    if m != None:
      if fun_lines.has_key(m.group(3)):
        ljmps.append((fun_lines[cl], fun_lines[m.group(3)],JMPS[m.group(2)]))
  #the following sorting bands same endpoints together
  ljmps = sorted(ljmps, key=lambda x: -x[1])
  for cl in sorted(fun_lines, key=lambda x: int(x,16)):
    jlr = j_line(fun_lines[cl],ljmps)
    all_lines[fun_lines[cl]]="".join([
                    jlr[0],
                    all_lines[fun_lines[cl]][:-1].lstrip(),jlr[1],
                    "\n"])

if __name__ == "__main__":
  #read lines from stdin
  nasml = sys.stdin.readlines()
  #make a dictionary of asm lines
  asm_lines = {}
  for i in range(len(nasml)):
    m = fcl.match(nasml[i])
    if m != None:
      asm_lines[m.group(1)] = i
    if nasml[i] == "\n" or "\tret " in nasml[i]:
      drw_jmps(nasml, asm_lines)
      asm_lines = {}
      fun_decl_lines = {}
  print "".join(nasml)