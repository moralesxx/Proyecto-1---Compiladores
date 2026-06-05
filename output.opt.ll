; ModuleID = '/tmp/tmpdks_vpvt.ll'
source_filename = "/tmp/tmpdks_vpvt.ll"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@.str.0 = constant [16 x i8] c"Fibonacci(7) = \00"
@.fmt.1 = local_unnamed_addr constant [4 x i8] c"%s\0A\00"
@.fmt.2 = constant [4 x i8] c"%d\0A\00"
@.str.3 = constant [14 x i8] c"Total pares: \00"
@.fmt.4 = local_unnamed_addr constant [4 x i8] c"%s\0A\00"
@.fmt.5 = constant [4 x i8] c"%d\0A\00"

; Function Attrs: nofree nounwind
declare noundef i32 @printf(ptr nocapture noundef readonly, ...) local_unnamed_addr #0

; Function Attrs: nofree nounwind
define noundef i32 @main() local_unnamed_addr #0 {
entry:
  %puts = tail call i32 @puts(ptr nonnull dereferenceable(1) @.str.0)
  %.46 = tail call i32 @fibonacci(i32 7)
  %.48 = tail call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) @.fmt.2, i32 %.46)
  %puts7 = tail call i32 @puts(ptr nonnull dereferenceable(1) @.str.3)
  %.54 = tail call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) @.fmt.5, i32 4)
  ret i32 0
}

; Function Attrs: nofree nosync nounwind memory(none)
define i32 @fibonacci(i32 %n) local_unnamed_addr #1 {
entry:
  %.54 = icmp slt i32 %n, 2
  br i1 %.54, label %common.ret, label %if.end

common.ret:                                       ; preds = %if.end, %entry
  %accumulator.tr.lcssa = phi i32 [ 0, %entry ], [ %.15, %if.end ]
  %n.tr.lcssa = phi i32 [ %n, %entry ], [ %.13, %if.end ]
  %accumulator.ret.tr = add i32 %n.tr.lcssa, %accumulator.tr.lcssa
  ret i32 %accumulator.ret.tr

if.end:                                           ; preds = %entry, %if.end
  %n.tr6 = phi i32 [ %.13, %if.end ], [ %n, %entry ]
  %accumulator.tr5 = phi i32 [ %.15, %if.end ], [ 0, %entry ]
  %.10 = add nsw i32 %n.tr6, -1
  %.11 = tail call i32 @fibonacci(i32 %.10)
  %.13 = add nsw i32 %n.tr6, -2
  %.15 = add i32 %.11, %accumulator.tr5
  %.5 = icmp ult i32 %n.tr6, 4
  br i1 %.5, label %common.ret, label %if.end
}

; Function Attrs: nofree nounwind
declare noundef i32 @puts(ptr nocapture noundef readonly) local_unnamed_addr #0

attributes #0 = { nofree nounwind }
attributes #1 = { nofree nosync nounwind memory(none) }
