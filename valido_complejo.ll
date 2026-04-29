; ModuleID = "modulo_compilador"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"()
{
entry:
  %"datos" = alloca [5 x i32]
  %".2" = getelementptr [5 x i32], [5 x i32]* %"datos", i32 0, i32 0
  store i32 1, i32* %".2"
  %".4" = getelementptr [5 x i32], [5 x i32]* %"datos", i32 0, i32 1
  store i32 2, i32* %".4"
  %".6" = getelementptr [5 x i32], [5 x i32]* %"datos", i32 0, i32 2
  store i32 3, i32* %".6"
  %".8" = getelementptr [5 x i32], [5 x i32]* %"datos", i32 0, i32 3
  store i32 4, i32* %".8"
  %".10" = getelementptr [5 x i32], [5 x i32]* %"datos", i32 0, i32 4
  store i32 5, i32* %".10"
  %"i" = alloca i32
  store i32 0, i32* %"i"
  %"suma" = alloca i32
  store i32 0, i32* %"suma"
  %"msg" = alloca i8*
  %".14" = bitcast [38 x i8]* @"str_123718929295728" to i8*
  store i8* %".14", i8** %"msg"
  %"msg.1" = load i8*, i8** %"msg"
  br label %"w_cond"
w_cond:
  %"i.1" = load i32, i32* %"i"
  %".17" = icmp slt i32 %"i.1", 5
  br i1 %".17", label %"w_body", label %"w_end"
w_body:
  %"val" = alloca i32
  %"i.2" = load i32, i32* %"i"
  %".19" = getelementptr [5 x i32], [5 x i32]* %"datos", i32 0, i32 %"i.2"
  %".20" = load i32, i32* %".19"
  store i32 %".20", i32* %"val"
  %"fact" = alloca i32
  %"val.1" = load i32, i32* %"val"
  %".22" = call i32 @"calcularFactorial"(i32 %"val.1")
  store i32 %".22", i32* %"fact"
  %".24" = bitcast [14 x i8]* @"str_123718929297968" to i8*
  %"fact.1" = load i32, i32* %"fact"
  %"suma.1" = load i32, i32* %"suma"
  %"fact.2" = load i32, i32* %"fact"
  %".25" = add i32 %"suma.1", %"fact.2"
  store i32 %".25", i32* %"suma"
  %"i.3" = load i32, i32* %"i"
  %".27" = add i32 %"i.3", 1
  store i32 %".27", i32* %"i"
  br label %"w_cond"
w_end:
  %".30" = bitcast [37 x i8]* @"str_123718929299424" to i8*
  %"suma.2" = load i32, i32* %"suma"
  ret i32 0
}

define i32 @"calcularFactorial"(i32 %"n")
{
entry:
  %"n.1" = alloca i32
  store i32 %"n", i32* %"n.1"
  %"res" = alloca i32
  store i32 1, i32* %"res"
  %"j" = alloca i32
  store i32 1, i32* %"j"
  br label %"w_cond"
w_cond:
  %"j.1" = load i32, i32* %"j"
  %"n.2" = load i32, i32* %"n.1"
  %".7" = icmp sle i32 %"j.1", %"n.2"
  br i1 %".7", label %"w_body", label %"w_end"
w_body:
  %"res.1" = load i32, i32* %"res"
  %"j.2" = load i32, i32* %"j"
  %".9" = mul i32 %"res.1", %"j.2"
  store i32 %".9", i32* %"res"
  %"j.3" = load i32, i32* %"j"
  %".11" = add i32 %"j.3", 1
  store i32 %".11", i32* %"j"
  br label %"w_cond"
w_end:
  %"res.2" = load i32, i32* %"res"
  ret i32 %"res.2"
}

@"str_123718929295728" = global [38 x i8] c"Procesando factoriales del arreglo...\00"
@"str_123718929297968" = global [14 x i8] c"Calculando...\00"
@"str_123718929299424" = global [37 x i8] c"La suma total de los factoriales es:\00"