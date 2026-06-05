; ModuleID = 'output.ll'
source_filename = "output.ll"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
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
  %total = alloca i32, align 4
  store i32 0, ptr %total, align 4
  %i = alloca i32, align 4
  store i32 0, ptr %i, align 4
  br label %while.check

while.check:                                      ; preds = %if.end.1, %entry
  %.15 = load i32, ptr %i, align 4
  %.16 = icmp slt i32 %.15, 5
  br i1 %.16, label %while.body, label %while.end

while.body:                                       ; preds = %while.check
  %r = alloca i32, align 4
  %.18 = load i32, ptr %i, align 4
  %.19 = getelementptr inbounds [5 x i32], ptr %nums, i32 0, i32 %.18
  %.20 = load i32, ptr %.19, align 4
  %.21 = srem i32 %.20, 2
  store i32 %.21, ptr %r, align 4
  %.23 = load i32, ptr %r, align 4
  %.24 = icmp eq i32 %.23, 0
  br i1 %.24, label %if.then, label %if.end

while.end:                                        ; preds = %if.then.1, %while.check
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
  %.52 = load i32, ptr %total, align 4
  %.53 = getelementptr inbounds [4 x i8], ptr @.fmt.5, i32 0, i32 0
  %.54 = call i32 (ptr, ...) @printf(ptr %.53, i32 %.52)
  ret i32 0

if.then:                                          ; preds = %while.body
  %.26 = load i32, ptr %total, align 4
  %.27 = load i32, ptr %i, align 4
  %.28 = getelementptr inbounds [5 x i32], ptr %nums, i32 0, i32 %.27
  %.29 = load i32, ptr %.28, align 4
  %.30 = add i32 %.26, %.29
  store i32 %.30, ptr %total, align 4
  br label %if.end

if.end:                                           ; preds = %if.then, %while.body
  %.33 = load i32, ptr %i, align 4
  %.34 = add i32 %.33, 1
  store i32 %.34, ptr %i, align 4
  %.36 = load i32, ptr %total, align 4
  %.37 = icmp sgt i32 %.36, 10
  br i1 %.37, label %if.then.1, label %if.end.1

if.then.1:                                        ; preds = %if.end
  br label %while.end

if.end.1:                                         ; preds = %if.end
  br label %while.check
}

define i32 @fibonacci(i32 %n) {
entry:
  %n.1 = alloca i32, align 4
  store i32 %n, ptr %n.1, align 4
  %.4 = load i32, ptr %n.1, align 4
  %.5 = icmp sle i32 %.4, 1
  br i1 %.5, label %if.then, label %if.end

if.then:                                          ; preds = %entry
  %.7 = load i32, ptr %n.1, align 4
  ret i32 %.7

if.end:                                           ; preds = %entry
  %.9 = load i32, ptr %n.1, align 4
  %.10 = sub i32 %.9, 1
  %.11 = call i32 @fibonacci(i32 %.10)
  %.12 = load i32, ptr %n.1, align 4
  %.13 = sub i32 %.12, 2
  %.14 = call i32 @fibonacci(i32 %.13)
  %.15 = add i32 %.11, %.14
  ret i32 %.15
}
