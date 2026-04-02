grammar Expresiones;

// --- REGLAS SINTÁCTICAS ---
root : PROGRAMA LLAVE_IZQ instrucciones+ LLAVE_DER EOF # Prog ;

instrucciones
    : declaracion PUNTO_COMA                  #InstrDecl
    | asignacion PUNTO_COMA                   #InstrAsig
    | SI PAR_IZQ condicion PAR_DER bloque (SINO bloque)? #InstrIf
    | WHILE PAR_IZQ condicion PAR_DER bloque  #InstrWhile
    | FOR PAR_IZQ asignacion PUNTO_COMA condicion PUNTO_COMA asignacion PAR_DER bloque #InstrFor
    | PRINT PAR_IZQ expr PAR_DER PUNTO_COMA   #InstrPrint
    | funcion_decl                            #InstrFuncDecl
    | RETURN expr? PUNTO_COMA                 #InstrReturn
    | llamada_func PUNTO_COMA                 #InstrLlamada
    ;

bloque : LLAVE_IZQ instrucciones* LLAVE_DER ;

declaracion : TIPO ID (ASIGNACION expr)? ; 

asignacion : ID ASIGNACION expr ;

funcion_decl : (TIPO | 'void') ID PAR_IZQ (parametros)? PAR_DER bloque ;

parametros : TIPO ID (COMA TIPO ID)* ;

llamada_func : ID PAR_IZQ (argumentos)? PAR_DER ;

argumentos : expr (COMA expr)* ;

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
    | STRING                                #Cadena
    | ID                                    #Variable
    | llamada_func                          #LlamadaExpr
    | PAR_IZQ expr PAR_DER                  #ParentesisExpr
    ;

// --- REGLAS LÉXICAS ---
PROGRAMA : 'program' ;
SI       : 'if' ;
SINO     : 'else' ;
WHILE    : 'while' ;    
FOR      : 'for' ;      
PRINT    : 'print' ;     
RETURN   : 'return' ;   

TIPO     : 'int' | 'float' | 'bool' | 'string' ; 

LLAVE_IZQ : '{' ; 
LLAVE_DER : '}' ;
PAR_IZQ   : '(' ;
PAR_DER   : ')' ;
PUNTO_COMA: ';' ; 
COMA      : ',' ;
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
STRING : '"' (~["\r\n])* '"' ; 

WS     : [ \t\r\n]+ -> skip ;
COMENTARIO : '//' ~[\n\r]* -> skip ;