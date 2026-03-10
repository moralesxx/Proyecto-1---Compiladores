grammar Expresiones;

// --- REGLAS SINTÁCTICAS ---
root : PROGRAMA LLAVE_IZQ instrucciones+ LLAVE_DER EOF # Prog ;

instrucciones
    : declaracion PUNTO_COMA                 #InstrDecl
    | asignacion PUNTO_COMA                  #InstrAsig
    | SI PAR_IZQ condicion PAR_DER bloque (SINO bloque)? #InstrIf
    ;

bloque : LLAVE_IZQ instrucciones* LLAVE_DER ;

declaracion : TIPO ID (ASIGNACION expr)? ; 

asignacion : ID ASIGNACION expr ;

condicion
    : condicion O_LOGICO condicion          #Logica
    | condicion Y_LOGICO condicion          #Logica
    | NO_LOGICO condicion                   #NotLogica
    | expr op=(MAYOR | MENOR | IGUAL | MAYOR_IGUAL | MENOR_IGUAL | DIFERENTE) expr #Relacional
    | PAR_IZQ condicion PAR_DER             #ParentesisCond
    ;

expr: expr (MULT | DIV) expr                #Aritmetica
    | expr (SUMA | RESTA) expr              #Aritmetica
    | NUMERO                                #Numero
    | ID                                    #Variable
    | PAR_IZQ expr PAR_DER                  #ParentesisExpr
    ;

// --- REGLAS LÉXICAS ---
PROGRAMA : 'program' ;
SI       : 'if' ;
SINO     : 'else' ;
TIPO     : 'int' | 'float' | 'bool' ; 

LLAVE_IZQ : '{' ; 
LLAVE_DER : '}' ;
PAR_IZQ   : '(' ;
PAR_DER   : ')' ;
PUNTO_COMA: ';' ; 
ASIGNACION: '=' ; 

SUMA  : '+' ; 
RESTA : '-' ;
MULT  : '*' ;
DIV   : '/' ;

MAYOR       : '>' ;
MENOR       : '<' ;
IGUAL       : '==' ;
DIFERENTE   : '!=' | '<>' ;
MAYOR_IGUAL : '>=' ;
MENOR_IGUAL : '<=' ;

Y_LOGICO  : '&&' ;
O_LOGICO  : '||' ;
NO_LOGICO : '!' ;

ID     : [a-zA-Z][a-zA-Z0-9]* ;
NUMERO : [0-9]+ ('.' [0-9]+)? ;
WS     : [ \t\r\n]+ -> skip ;
COMENTARIO : '//' ~[\n\r]* -> skip ;