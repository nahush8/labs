#!/usr/bin/env python
# encoding: utf-8
"""
llvm_asm_jmps.py
Created by Daniel Fairchild on 2013-06-12.
Usage (in shell):
  llvm-objdump -g -x86-asm-syntax=intel -disassemble target.bin | ./llvm_asm_jmps.py
License:
  I'd appreciate a comment at: http://blog.fairchild.dk/?p=702
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

fcl = re.compile(" *([\da-f]+)\:")
fjre = re.compile("".join([
            " *([\da-f]+)\:\\t.*(",
			"".join(map(lambda x: x+"|", JMPS))[:-1],
            ")\s+(-?[\da-f]+)"]))

def j_line(ln, ljmps):
  jl = len(ljmps)
  outl = [" "]*(jl+2)
  for i in range(jl):
    if ljmps[i][0] == ln: #jmp from
      outl[-(jl-i+2):] = ["-"]*(jl-i+2)
      outl[i] = "," if ljmps[i][0] < ljmps[i][1] else "\'"
    if ljmps[i][1] == ln: #jmp to
      outl[-(jl-i+1):] = ["-"]*(jl-i+1)
      outl[-1] = ">"
      outl[i] = "," if ljmps[i][0] > ljmps[i][1] else "\'"
    if ljmps[i][0] < ln and ljmps[i][1] > ln:
      outl[i] = "|"
    elif ljmps[i][0] > ln and ljmps[i][1] < ln:
      outl[i] = "|"
  return "".join(outl)

def drw_jmps(all_lines, fun_lines):
  ljmps = []
  for cl in fun_lines:
    m = fjre.match(all_lines[fun_lines[cl]])
    if m != None:
      m2 = fcl.match(all_lines[fun_lines[cl]+1])
      if m2 != None:
        l_key = ("%0.2x" % (int(m2.group(1),16)+int(m.group(3))))
        if fun_lines.has_key(l_key):
          ljmps.append((fun_lines[cl], fun_lines[l_key]))
  #the following sorting bands same endpoints together
  ljmps = sorted(ljmps, key=lambda x: -x[1])
  for cl in sorted(fun_lines, key=lambda x: int(x,16)):
    all_lines[fun_lines[cl]]="".join([
                    j_line(fun_lines[cl],ljmps),
                    all_lines[fun_lines[cl]][:-1].lstrip(),
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
    if nasml[i] == "\n" or nasml[i] == ".text:\n" or "ret" in nasml[i]:
      drw_jmps(nasml, asm_lines)
      asm_lines = {}
      fun_decl_lines = {}
  print "".join(nasml)