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
    | SI PAR_IZQ expr PAR_DER bloque (SINO bloque)? #InstrIf
    | WHILE PAR_IZQ expr PAR_DER bloque  #InstrWhile
    | FOR PAR_IZQ asignacion PUNTO_COMA expr PUNTO_COMA asignacion PAR_DER bloque #InstrFor
    | BREAK PUNTO_COMA                        #InstrBreak
    | CONTINUE PUNTO_COMA                     #InstrContinue
    | PRINT PAR_IZQ expr PAR_DER PUNTO_COMA   #InstrPrint
    | funcion_decl                            #InstrFuncDecl
    | RETURN expr? PUNTO_COMA                 #InstrReturn
    | llamada_func PUNTO_COMA                 #InstrLlamada
    // ── v4: nuevas instrucciones ──────────────────────────────────────────
    | struct_decl                             #InstrStructDecl
    | struct_asig PUNTO_COMA                  #InstrStructAsig
    | switch_stmt                             #InstrSwitch
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

// --- EXPRESIONES UNIFICADAS (Resuelve la recursión mutua izquierda) ---
expr
    : expr O_LOGICO expr                               #Logica
    | expr Y_LOGICO expr                               #Logica
    | NO_LOGICO expr                                   #NotLogica
    | expr op=(MAYOR | MENOR | IGUAL | MAYOR_IGUAL | MENOR_IGUAL | DIFERENTE) expr #Relacional
    | expr (MULT | DIV | MOD) expr                     #Aritmetica
    | expr (SUMA | RESTA) expr                         #Aritmetica
    | ID COR_IZQ expr COR_DER                          #AccesoArray
    | NUMERO                                           #Numero
    | STRING                                           #Cadena
    | ID                                               #Variable
    | llamada_func                                     #LlamadaExpr
    | PAR_IZQ expr PAR_DER                             #ParentesisExpr
    | expr INTERROGACION expr COLON expr               #Ternario
    | PAR_IZQ TIPO PAR_DER expr                        #CastingExpr
    | ID PUNTO ID                                      #AccesoCampo
    ;

// ── v4: Structs ───────────────────────────────────────────────────────────
struct_decl : STRUCT ID LLAVE_IZQ campo_struct+ LLAVE_DER ;

campo_struct : TIPO ID PUNTO_COMA ;

// Asignación a campo:  p.x = 10
struct_asig : ID PUNTO ID ASIGNACION expr ;

// ── v4: Switch / Case ─────────────────────────────────────────────────────
switch_stmt : SWITCH PAR_IZQ expr PAR_DER LLAVE_IZQ case_clause+ default_clause? LLAVE_DER ;
case_clause   : CASE literal_valor COLON instrucciones* ;

default_clause : DEFAULT COLON instrucciones* ;

literal_valor : NUMERO | STRING ;

// --- REGLAS LÉXICAS --- (todas las originales sin cambios)
PROGRAMA : 'program' ;
SI       : 'if' ;
SINO     : 'else' ;
WHILE    : 'while' ;
FOR      : 'for' ;
PRINT    : 'print' ;
RETURN   : 'return' ;
IMPORT   : 'import' ;
BREAK    : 'break' ;
CONTINUE : 'continue' ;

TIPO     : 'int' | 'float' | 'bool' | 'string' ;

// ── v4: nuevas palabras reservadas ───────────────────────────────────────
STRUCT   : 'struct' ;
SWITCH   : 'switch' ;
CASE     : 'case' ;
DEFAULT  : 'default' ;
LLAVE_IZQ : '{' ;
LLAVE_DER : '}' ;
PAR_IZQ   : '(' ;
PAR_DER   : ')' ;
COR_IZQ   : '[' ;
COR_DER   : ']' ;
PUNTO_COMA: ';' ;
COMA      : ',' ;
ASIGNACION: '=' ;

// ── v4: nuevos tokens ────────────────────────────────────────────────────
INTERROGACION : '?' ;
COLON         : ':' ;
PUNTO         : '.' ;

SUMA  : '+' ;
RESTA : '-' ;
MULT  : '*' ;
DIV   : '/' ;
MOD   : '%' ;

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