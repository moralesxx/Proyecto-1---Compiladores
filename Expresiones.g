grammar Expresiones;


//NO DEJAR QUEMADO, VOLVERLO TOKEN, LO UNICO QUEMADO SON PALABRAS RESERVADAS.
root : 'program' '{' instrucciones+ '}' EOF # Prog ;

instrucciones
    : declaracion ';'                       #InstrDecl
    | asignacion ';'                        #InstrAsig
    | 'if' '(' exprRelacional ')' bloque ('else' bloque)? #InstrIf
    ;

bloque : '{' instrucciones* '}' ;

declaracion : 'int' ID ;

asignacion : ID '=' expr ;

expr: expr (MUL | DIV) expr    #Aritmetica
    | expr (SUM | RES) expr    #Aritmetica
    | NUM                      #Numero
    | ID                       #Variable
    | '(' expr ')'             #Parentesis
    ;

exprRelacional
    : expr op=( '>' | '<' | '==' | '>=' | '<=' | '!=' ) expr #Relacional
    ;

ID  : [a-zA-Z][a-zA-Z0-9]* ;
NUM : [0-9]+ ;
SUM : '+' ;
RES : '-' ;
MUL : '*' ;
DIV : '/' ;
COMENTARIO : '//' ~[\n\r]* -> skip ;