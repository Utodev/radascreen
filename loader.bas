10 REM activate radastanian mode
20 OUT 64571,64: OUT 64827,3
30 REM Load screen and palette (6144 + 16 bytes)
40 LOAD "" CODE 16384
50 REM set palette
60 FOR p =  0 TO 15: OUT 48955, p: OUT 65339, PEEK(p + 22528): NEXT p
40 LOAD "" CODE 16384
70 PAUSE 0
80 REM deactivate radastanian mode
90 OUT 64571,64: OUT 64827,0
100 CLS