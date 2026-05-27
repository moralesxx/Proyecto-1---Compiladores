; ModuleID = '<string>'
source_filename = "<string>"
target triple = "x86_64-unknown-linux-gnu"

@.str.0 = constant [16 x i8] c"Fibonacci(7) = \00"
@.fmt.1 = constant [4 x i8] c"%s\0A\00"
@.fmt.2 = constant [4 x i8] c"%d\0A\00"
@.str.3 = constant [14 x i8] c"Total pares: \00"
@.fmt.4 = constant [4 x i8] c"%s\0A\00"
@.fmt.5 = constant [4 x i8] c"%d\0A\00"

declare i32 @printf(ptr, ...)

define i32 @main() {
entry:
  %nums = alloca [5 x i32], align 4
  %.2 = getelementptr inbounds [5 x i32], ptr %nums, i32 0, i32 0
  store i32 3, ptr %.2, align 4
  %.4 = getelementptr inbounds [5 x i32], ptr %nums, i32 0, i32 1
  store i32 1, ptr %.4, align 4
  %.6 = getelementptr inbounds [5 x i32], ptr %nums, i32 0, i32 2
  store i32 4, ptr %.6, align 4
  %.8 = getelementptr inbounds [5 x i32], ptr %nums, i32 0, i32 3
  store i32 1, ptr %.8, align 4
  %.10 = getelementptr inbounds [5 x i32], ptr %nums, i32 0, i32 4
  store i32 5, ptr %.10, align 4
  br label %while.check

while.check:                                      ; preds = %if.end.1, %entry
  %total.0 = phi i32 [ 0, %entry ], [ %total.2, %if.end.1 ]
  %i.0 = phi i32 [ 0, %entry ], [ %.34, %if.end.1 ]
  %.16 = icmp slt i32 %i.0, 5
  br i1 %.16, label %while.body, label %while.end

while.body:                                       ; preds = %while.check
  %r = alloca i32, align 4
  %.19 = getelementptr inbounds [5 x i32], ptr %nums, i32 0, i32 %i.0
  %.20 = load i32, ptr %.19, align 4
  %.21 = srem i32 %.20, 2
  store i32 %.21, ptr %r, align 4
  %.23 = load i32, ptr %r, align 4
  %.24 = icmp eq i32 %.23, 0
  br i1 %.24, label %if.then, label %if.end

while.end:                                        ; preds = %if.then.1, %while.check
  %total.1 = phi i32 [ %total.2, %if.then.1 ], [ %total.0, %while.check ]
  %msg = alloca ptr, align 8
  %.41 = getelementptr inbounds [16 x i8], ptr @.str.0, i32 0, i32 0
  store ptr %.41, ptr %msg, align 8
  %.43 = load ptr, ptr %msg, align 8
  %.44 = getelementptr inbounds [4 x i8], ptr @.fmt.1, i32 0, i32 0
  %.45 = call i32 (ptr, ...) @printf(ptr %.44, ptr %.43)
  %.46 = call i32 @fibonacci(i32 7)
  %.47 = getelementptr inbounds [4 x i8], ptr @.fmt.2, i32 0, i32 0
  %.48 = call i32 (ptr, ...) @printf(ptr %.47, i32 %.46)
  %.49 = getelementptr inbounds [14 x i8], ptr @.str.3, i32 0, i32 0
  %.50 = getelementptr inbounds [4 x i8], ptr @.fmt.4, i32 0, i32 0
  %.51 = call i32 (ptr, ...) @printf(ptr %.50, ptr %.49)
  %.53 = getelementptr inbounds [4 x i8], ptr @.fmt.5, i32 0, i32 0
  %.54 = call i32 (ptr, ...) @printf(ptr %.53, i32 %total.1)
  ret i32 0

if.then:                                          ; preds = %while.body
  %.28 = getelementptr inbounds [5 x i32], ptr %nums, i32 0, i32 %i.0
  %.29 = load i32, ptr %.28, align 4
  %.30 = add i32 %total.0, %.29
  br label %if.end

if.end:                                           ; preds = %if.then, %while.body
  %total.2 = phi i32 [ %.30, %if.then ], [ %total.0, %while.body ]
  %.34 = add i32 %i.0, 1
  %.37 = icmp sgt i32 %total.2, 10
  br i1 %.37, label %if.then.1, label %if.end.1

if.then.1:                                        ; preds = %if.end
  br label %while.end

if.end.1:                                         ; preds = %if.end
  br label %while.check
}

define i32 @fibonacci(i32 %n) {
entry:
  %.5 = icmp sle i32 %n, 1
  br i1 %.5, label %if.then, label %if.end

if.then:                                          ; preds = %entry
  ret i32 %n

if.end:                                           ; preds = %entry
  %.10 = sub i32 %n, 1
  %.11 = call i32 @fibonacci(i32 %.10)
  %.13 = sub i32 %n, 2
  %.14 = call i32 @fibonacci(i32 %.13)
  %.15 = add i32 %.11, %.14
  ret i32 %.15
}
