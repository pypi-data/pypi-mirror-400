[![Github](https://img.shields.io/badge/github-artconsole-white)](https://github.com/dimamshirokov/artconsole) [![PyPI Downloads](https://static.pepy.tech/personalized-badge/artconsole?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=MAGENTA&left_text=total%20downloads)](https://pepy.tech/projects/artconsole) [![PyPI Downloads](https://static.pepy.tech/personalized-badge/artconsole?period=monthly&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=MAGENTA&left_text=monthly%20downloads)](https://pepy.tech/projects/artconsole) [![PyPI Downloads](https://static.pepy.tech/personalized-badge/artconsole?period=weekly&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=MAGENTA&left_text=weekly%20downloads)](https://pepy.tech/projects/artconsole) [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/dimamshirokov/artconsole/blob/main/LICENSE)

# Description

API written in python that outputs beautiful ASCII art to the console!
Look at [CHANGELOG.md](https://github.com/dimamshirokov/artconsole/blob/main/CHANGELOG.md) for the changes.

# Installation

```console
pip install artconsole
```

# API Usage

```pycon
>>> import artconsole

>>> artconsole.print_drawing('spiderman')

                             .-"""-.    __                         
                            /       \.-"  "-.                      
                         __:  :\     ;       `.                    
                  _._.-""  :  ; `.   :   _     \                   
                .'   "-.  "   :   \ /;    \    .^.              .-,
    .-".       :        `.     \_.' \'   .'; .'   `.            `dP
 ,-"    \      ;\         \  '.     /". /  :/       `.      __ dP_,
 :    '. \_    ; `.  __.   ;_  `-._/   Y    \         `.   ( dP".';
 ;      \  `.  :   "-._    ; ""-./      ;    "-._       `--dP .'  ;
:    .--.;   \  ;      l   '.    `.     ;        ""--.   dP  /   / 
;   /    :    \/       ;\  . "-.   \___/            __\dP .-"_.-"  
;  /     L_    \`.    :  "-.J   "-._/  ""-._       ( dP\ /   /     
: :      ; \    `.`.  ;     /"+.     ""-.   ""--.._dP-, `._."      
 \;     :   \     `.`-'   _/ /  "-.___   "         \`-'            
  `.    ;    \      `._.-"  (     ("--..__..---g,   \              
    `. :      ;             /\  .-"\       ,-dP ;    ;             
      \;   .-';    _   _.--"  \/    `._,-.-dP-' |    ;             
       :     :---"" """        `.     _:'.`.\   :    ;\            
        \  , :              bug  "-. (,j\ ` /   ;\(// \\           
         `:   \                     "dP__.-"    '-\\   \;          
           \   :                .--dP,             \;              
            `--'                `dP`-'                             
                              .-j                                  
                              `-:_                                 
                                 \)                                
                                  `--'

>>> print(artconsole.return_drawing('mona_lisa'))

                                  _______
                           _,,ad8888888888bba,_
                        ,ad88888I888888888888888ba,
                      ,88888888I88888888888888888888a,
                    ,d888888888I8888888888888888888888b,
                   d88888PP"""" ""YY88888888888888888888b,
                 ,d88"'__,,--------,,,,.;ZZZY8888888888888,
                ,8IIl'"                ;;l"ZZZIII8888888888,
               ,I88l;'                  ;lZZZZZ888III8888888,
             ,II88Zl;.                  ;llZZZZZ888888I888888,
            ,II888Zl;.                .;;;;;lllZZZ888888I8888b
           ,II8888Z;;                 `;;;;;''llZZ8888888I8888,
           II88888Z;'                        .;lZZZ8888888I888b
           II88888Z; _,aaa,      .,aaaaa,__.l;llZZZ88888888I888
           II88888IZZZZZZZZZ,  .ZZZZZZZZZZZZZZ;llZZ88888888I888,
           II88888IZZ<'(@@>Z|  |ZZZ<'(@@>ZZZZ;;llZZ888888888I88I
          ,II88888;   `""" ;|  |ZZ; `"""     ;;llZ8888888888I888
          II888888l            `;;          .;llZZ8888888888I888,
         ,II888888Z;           ;;;        .;;llZZZ8888888888I888I
         III888888Zl;    ..,   `;;       ,;;lllZZZ88888888888I888
         II88888888Z;;...;(_    _)      ,;;;llZZZZ88888888888I888,
         II88888888Zl;;;;;' `--'Z;.   .,;;;;llZZZZ88888888888I888b
         ]I888888888Z;;;;'   ";llllll;..;;;lllZZZZ88888888888I8888,
         II888888888Zl.;;"Y88bd888P";;,..;lllZZZZZ88888888888I8888I
         II8888888888Zl;.; `"PPP";;;,..;lllZZZZZZZ88888888888I88888
         II888888888888Zl;;. `;;;l;;;;lllZZZZZZZZW88888888888I88888
         `II8888888888888Zl;.    ,;;lllZZZZZZZZWMZ88888888888I88888
          II8888888888888888ZbaalllZZZZZZZZZWWMZZZ8888888888I888888,
          `II88888888888888888b"WWZZZZZWWWMMZZZZZZI888888888I888888b
           `II88888888888888888;ZZMMMMMMZZZZZZZZllI888888888I8888888
            `II8888888888888888 `;lZZZZZZZZZZZlllll888888888I8888888,
             II8888888888888888, `;lllZZZZllllll;;.Y88888888I8888888b,
            ,II8888888888888888b   .;;lllllll;;;.;..88888888I88888888b,
            II888888888888888PZI;.  .`;;;.;;;..; ...88888888I8888888888,
            II888888888888PZ;;';;.   ;. .;.  .;. .. Y8888888I88888888888b,
           ,II888888888PZ;;'                        `8888888I8888888888888b,
           II888888888'                              888888I8888888888888888b
          ,II888888888                              ,888888I88888888888888888
         ,d88888888888                              d888888I8888888888ZZZZZZZ
      ,ad888888888888I                              8888888I8888ZZZZZZZZZZZZZ
    ,d888888888888888'                              888888IZZZZZZZZZZZZZZZZZZ
  ,d888888888888P'8P'                               Y888ZZZZZZZZZZZZZZZZZZZZZ
 ,8888888888888,  "                                 ,ZZZZZZZZZZZZZZZZZZZZZZZZ
d888888888888888,                                ,ZZZZZZZZZZZZZZZZZZZZZZZZZZZ
888888888888888888a,      _                    ,ZZZZZZZZZZZZZZZZZZZZ888888888
888888888888888888888ba,_d'                  ,ZZZZZZZZZZZZZZZZZ88888888888888
8888888888888888888888888888bbbaaa,,,______,ZZZZZZZZZZZZZZZ888888888888888888
88888888888888888888888888888888888888888ZZZZZZZZZZZZZZZ888888888888888888888
8888888888888888888888888888888888888888ZZZZZZZZZZZZZZ88888888888888888888888
888888888888888888888888888888888888888ZZZZZZZZZZZZZZ888888888888888888888888
8888888888888888888888888888888888888ZZZZZZZZZZZZZZ88888888888888888888888888
88888888888888888888888888888888888ZZZZZZZZZZZZZZ8888888888888888888888888888
8888888888888888888888888888888888ZZZZZZZZZZZZZZ88888888888888888 Normand  88
88888888888888888888888888888888ZZZZZZZZZZZZZZ8888888888888888888 Veilleux 88
8888888888888888888888888888888ZZZZZZZZZZZZZZ88888888888888888888888888888888
```

# Characters

```pycon
>>> artconsole.DRAWINGS.keys()

dict_keys(['captain_america', 'spiderman', 'mona_lisa', 'hexagonal', 'scorpion', 'snake', 
'brachiosaur', 'pterodactyl', 'turtle', 'wolf', 'canada', 'eiffel_tower', 'mount_rushmore', 
'statue_of_liberty', 'taj_mahal', 'pyramids', 'notre_dame', 'saint_basils_cathedral', 
'stonehenge', 'white_house', 'christmas_tree', 'snowman', 'santa_claus', 'joseph_mary_and_jesus', 
'candy_canes'])

>>> len(artconsole.DRAWINGS.keys())

25
```

# Contributors
<a href="https://github.com/dimamshirokov/artconsole/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=dimamshirokov/artconsole&columns=5" />
</a>

Guide: [CONTRIBUTING.md](https://github.com/dimamshirokov/artconsole/blob/main/CONTRIBUTING.md)

# Star History

[![Star History Chart](https://api.star-history.com/svg?repos=dimamshirokov/artconsole&type=date&legend=top-left)](https://www.star-history.com/#dimamshirokov/artconsole&type=date&legend=top-left)

# Gratitude

I would like to thank the [ASCII Art Archive](https://www.asciiart.eu) website separately since most of the drawings are taken from him!