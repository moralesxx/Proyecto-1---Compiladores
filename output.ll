; ModuleID = "compilador_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

define i32 @"main"()
{
entry:
  %"nums" = alloca [5 x i32]
  %".2" = getelementptr inbounds [5 x i32], [5 x i32]* %"nums", i32 0, i32 0
  store i32 3, i32* %".2"
  %".4" = getelementptr inbounds [5 x i32], [5 x i32]* %"nums", i32 0, i32 1
  store i32 1, i32* %".4"
  %".6" = getelementptr inbounds [5 x i32], [5 x i32]* %"nums", i32 0, i32 2
  store i32 4, i32* %".6"
  %".8" = getelementptr inbounds [5 x i32], [5 x i32]* %"nums", i32 0, i32 3
  store i32 1, i32* %".8"
  %".10" = getelementptr inbounds [5 x i32], [5 x i32]* %"nums", i32 0, i32 4
  store i32 5, i32* %".10"
  %"total" = alloca i32
  store i32 0, i32* %"total"
  %"i" = alloca i32
  store i32 0, i32* %"i"
  br label %"while.check"
while.check:
  %".15" = load i32, i32* %"i"
  %".16" = icmp slt i32 %".15", 5
  br i1 %".16", label %"while.body", label %"while.end"
while.body:
  %"r" = alloca i32
  %".18" = load i32, i32* %"i"
  %".19" = getelementptr inbounds [5 x i32], [5 x i32]* %"nums", i32 0, i32 %".18"
  %".20" = load i32, i32* %".19"
  %".21" = srem i32 %".20", 2
  store i32 %".21", i32* %"r"
  %".23" = load i32, i32* %"r"
  %".24" = icmp eq i32 %".23", 0
  br i1 %".24", label %"if.then", label %"if.end"
while.end:
  %"suma" = alloca i32
  store i32 0, i32* %"suma"
  store i32 0, i32* %"i"
  br label %"for.check"
if.then:
  %".26" = load i32, i32* %"total"
  %".27" = load i32, i32* %"i"
  %".28" = getelementptr inbounds [5 x i32], [5 x i32]* %"nums", i32 0, i32 %".27"
  %".29" = load i32, i32* %".28"
  %".30" = add i32 %".26", %".29"
  store i32 %".30", i32* %"total"
  br label %"if.end"
if.end:
  %".33" = load i32, i32* %"i"
  %".34" = add i32 %".33", 1
  store i32 %".34", i32* %"i"
  %".36" = load i32, i32* %"total"
  %".37" = icmp sgt i32 %".36", 10
  br i1 %".37", label %"if.then.1", label %"if.end.1"
if.then.1:
  br label %"while.end"
if.end.1:
  br label %"while.check"
for.check:
  %".44" = load i32, i32* %"i"
  %".45" = icmp slt i32 %".44", 5
  br i1 %".45", label %"for.body", label %"for.end"
for.body:
  %".47" = load i32, i32* %"i"
  %".48" = getelementptr inbounds [5 x i32], [5 x i32]* %"nums", i32 0, i32 %".47"
  %".49" = load i32, i32* %".48"
  %".50" = icmp eq i32 %".49", 1
  br i1 %".50", label %"if.then.2", label %"if.end.2"
for.update:
  %".60" = load i32, i32* %"i"
  %".61" = add i32 %".60", 1
  store i32 %".61", i32* %"i"
  br label %"for.check"
for.end:
  %"msg" = alloca i8*
  %".64" = getelementptr inbounds [16 x i8], [16 x i8]* @".str.0", i32 0, i32 0
  store i8* %".64", i8** %"msg"
  %".66" = load i8*, i8** %"msg"
  %".67" = getelementptr inbounds [4 x i8], [4 x i8]* @".fmt.1", i32 0, i32 0
  %".68" = call i32 (i8*, ...) @"printf"(i8* %".67", i8* %".66")
  %".69" = call i32 @"fibonacci"(i32 7)
  %".70" = getelementptr inbounds [4 x i8], [4 x i8]* @".fmt.2", i32 0, i32 0
  %".71" = call i32 (i8*, ...) @"printf"(i8* %".70", i32 %".69")
  %".72" = getelementptr inbounds [26 x i8], [26 x i8]* @".str.3", i32 0, i32 0
  %".73" = getelementptr inbounds [4 x i8], [4 x i8]* @".fmt.4", i32 0, i32 0
  %".74" = call i32 (i8*, ...) @"printf"(i8* %".73", i8* %".72")
  %".75" = load i32, i32* %"total"
  %".76" = getelementptr inbounds [4 x i8], [4 x i8]* @".fmt.5", i32 0, i32 0
  %".77" = call i32 (i8*, ...) @"printf"(i8* %".76", i32 %".75")
  %".78" = getelementptr inbounds [16 x i8], [16 x i8]* @".str.6", i32 0, i32 0
  %".79" = getelementptr inbounds [4 x i8], [4 x i8]* @".fmt.7", i32 0, i32 0
  %".80" = call i32 (i8*, ...) @"printf"(i8* %".79", i8* %".78")
  %".81" = load i32, i32* %"suma"
  %".82" = getelementptr inbounds [4 x i8], [4 x i8]* @".fmt.8", i32 0, i32 0
  %".83" = call i32 (i8*, ...) @"printf"(i8* %".82", i32 %".81")
  %".84" = getelementptr inbounds [23 x i8], [23 x i8]* @".str.9", i32 0, i32 0
  %".85" = getelementptr inbounds [4 x i8], [4 x i8]* @".fmt.10", i32 0, i32 0
  %".86" = call i32 (i8*, ...) @"printf"(i8* %".85", i8* %".84")
  %".87" = call i32 @"maximo"(i32 42, i32 17)
  %".88" = getelementptr inbounds [4 x i8], [4 x i8]* @".fmt.11", i32 0, i32 0
  %".89" = call i32 (i8*, ...) @"printf"(i8* %".88", i32 %".87")
  ret i32 0
if.then.2:
  br label %"for.update"
if.end.2:
  %".53" = load i32, i32* %"suma"
  %".54" = load i32, i32* %"i"
  %".55" = getelementptr inbounds [5 x i32], [5 x i32]* %"nums", i32 0, i32 %".54"
  %".56" = load i32, i32* %".55"
  %".57" = add i32 %".53", %".56"
  store i32 %".57", i32* %"suma"
  br label %"for.update"
}

define i32 @"fibonacci"(i32 %"n")
{
entry:
  %"n.1" = alloca i32
  store i32 %"n", i32* %"n.1"
  %".4" = load i32, i32* %"n.1"
  %".5" = icmp sle i32 %".4", 1
  br i1 %".5", label %"if.then", label %"if.end"
if.then:
  %".7" = load i32, i32* %"n.1"
  ret i32 %".7"
if.end:
  %".9" = load i32, i32* %"n.1"
  %".10" = sub i32 %".9", 1
  %".11" = call i32 @"fibonacci"(i32 %".10")
  %".12" = load i32, i32* %"n.1"
  %".13" = sub i32 %".12", 2
  %".14" = call i32 @"fibonacci"(i32 %".13")
  %".15" = add i32 %".11", %".14"
  ret i32 %".15"
}

define i32 @"maximo"(i32 %"a", i32 %"b")
{
entry:
  %"a.1" = alloca i32
  store i32 %"a", i32* %"a.1"
  %"b.1" = alloca i32
  store i32 %"b", i32* %"b.1"
  %".6" = load i32, i32* %"a.1"
  %".7" = load i32, i32* %"b.1"
  %".8" = icmp sgt i32 %".6", %".7"
  br i1 %".8", label %"if.then", label %"if.end"
if.then:
  %".10" = load i32, i32* %"a.1"
  ret i32 %".10"
if.end:
  %".12" = load i32, i32* %"b.1"
  ret i32 %".12"
}

@".str.0" = constant [16 x i8] c"Fibonacci(7) = \00"
@".fmt.1" = constant [4 x i8] c"%s\0a\00"
@".fmt.2" = constant [4 x i8] c"%d\0a\00"
@".str.3" = constant [26 x i8] c"Total pares del arreglo: \00"
@".fmt.4" = constant [4 x i8] c"%s\0a\00"
@".fmt.5" = constant [4 x i8] c"%d\0a\00"
@".str.6" = constant [16 x i8] c"Suma sin unos: \00"
@".fmt.7" = constant [4 x i8] c"%s\0a\00"
@".fmt.8" = constant [4 x i8] c"%d\0a\00"
@".str.9" = constant [23 x i8] c"Maximo entre 42 y 17: \00"
@".fmt.10" = constant [4 x i8] c"%s\0a\00"
@".fmt.11" = constant [4 x i8] c"%d\0a\00"