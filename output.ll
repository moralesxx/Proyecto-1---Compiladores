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
  %"msg" = alloca i8*
  %".41" = getelementptr inbounds [16 x i8], [16 x i8]* @".str.0", i32 0, i32 0
  store i8* %".41", i8** %"msg"
  %".43" = load i8*, i8** %"msg"
  %".44" = getelementptr inbounds [4 x i8], [4 x i8]* @".fmt.1", i32 0, i32 0
  %".45" = call i32 (i8*, ...) @"printf"(i8* %".44", i8* %".43")
  %".46" = call i32 @"fibonacci"(i32 7)
  %".47" = getelementptr inbounds [4 x i8], [4 x i8]* @".fmt.2", i32 0, i32 0
  %".48" = call i32 (i8*, ...) @"printf"(i8* %".47", i32 %".46")
  %".49" = getelementptr inbounds [14 x i8], [14 x i8]* @".str.3", i32 0, i32 0
  %".50" = getelementptr inbounds [4 x i8], [4 x i8]* @".fmt.4", i32 0, i32 0
  %".51" = call i32 (i8*, ...) @"printf"(i8* %".50", i8* %".49")
  %".52" = load i32, i32* %"total"
  %".53" = getelementptr inbounds [4 x i8], [4 x i8]* @".fmt.5", i32 0, i32 0
  %".54" = call i32 (i8*, ...) @"printf"(i8* %".53", i32 %".52")
  ret i32 0
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

@".str.0" = constant [16 x i8] c"Fibonacci(7) = \00"
@".fmt.1" = constant [4 x i8] c"%s\0a\00"
@".fmt.2" = constant [4 x i8] c"%d\0a\00"
@".str.3" = constant [14 x i8] c"Total pares: \00"
@".fmt.4" = constant [4 x i8] c"%s\0a\00"
@".fmt.5" = constant [4 x i8] c"%d\0a\00"