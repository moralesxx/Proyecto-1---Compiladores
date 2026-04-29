grammar Expresiones;

// --- REGLAS SINTÁCTICAS ---
// Se añaden importaciones opcionales al inicio
root : (importStmt)* PROGRAMA LLAVE_IZQ instrucciones+ LLAVE_DER EOF # Prog ;

importStmt : IMPORT ID PUNTO_COMA # InstrImport ;

instrucciones
    : declaracion PUNTO_COMA                  #InstrDecl
    | declaracionArray PUNTO_COMA             #InstrDeclArray
    | asignacion PUNTO_COMA                   #InstrAsig
    | asignacionArray PUNTO_COMA              #InstrAsigArray
    | SI PAR_IZQ condicion PAR_DER bloque (SINO bloque)? #InstrIf
    | WHILE PAR_IZQ condicion PAR_DER bloque  #InstrWhile
    | FOR PAR_IZQ asignacion PUNTO_COMA condicion PUNTO_COMA asignacion PAR_DER bloque #InstrFor
    | BREAK PUNTO_COMA                        #InstrBreak
    | CONTINUE PUNTO_COMA                     #InstrContinue
    | PRINT PAR_IZQ expr PAR_DER PUNTO_COMA   #InstrPrint
    | funcion_decl                            #InstrFuncDecl
    | RETURN expr? PUNTO_COMA                 #InstrReturn
    | llamada_func PUNTO_COMA                 #InstrLlamada
    ;

bloque : LLAVE_IZQ instrucciones* LLAVE_DER ;

// Declaración normal y declaración de arreglos 
declaracion : TIPO ID (ASIGNACION expr)? ; 

declaracionArray : TIPO COR_IZQ COR_DER ID ASIGNACION COR_IZQ argumentos? COR_DER ;

// Asignación normal y a índices de arreglo 
asignacion : ID ASIGNACION expr ;

asignacionArray : ID COR_IZQ expr COR_DER ASIGNACION expr ;

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

expr: expr (MULT | DIV | MOD) expr          #Aritmetica
    | expr (SUMA | RESTA) expr              #Aritmetica
    | ID COR_IZQ expr COR_DER               #AccesoArray
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
IMPORT   : 'import' ;   // Requerido para módulos 
BREAK    : 'break' ;    // Requerido para ciclos 
CONTINUE : 'continue' ; // Requerido para ciclos 

TIPO     : 'int' | 'float' | 'bool' | 'string' ; 

LLAVE_IZQ : '{' ; 
LLAVE_DER : '}' ;
PAR_IZQ   : '(' ;
PAR_DER   : ')' ;
COR_IZQ   : '[' ;       // Requerido para arreglos 
COR_DER   : ']' ;       // Requerido para arreglos 
PUNTO_COMA: ';' ; 
COMA      : ',' ;
ASIGNACION: '=' ; 

SUMA  : '+' ; 
RESTA : '-' ;
MULT  : '*' ;
DIV   : '/' ;
MOD   : '%' ;           // Requerido 

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

WS         : [ \t\r\n]+ -> skip ;
COMENTARIO : '//' ~[\n\r]* -> skip ;
