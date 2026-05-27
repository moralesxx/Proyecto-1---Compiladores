; ModuleID = '<string>'
source_filename = "<string>"
target triple = "x86_64-unknown-linux-gnu"

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
  %nums = alloca [5 x i32], align 4
  store i32 3, ptr %nums, align 4
  %.4 = getelementptr inbounds nuw i8, ptr %nums, i64 4
  store i32 1, ptr %.4, align 4
  %.6 = getelementptr inbounds nuw i8, ptr %nums, i64 8
  store i32 4, ptr %.6, align 4
  %.8 = getelementptr inbounds nuw i8, ptr %nums, i64 12
  store i32 1, ptr %.8, align 4
  %.10 = getelementptr inbounds nuw i8, ptr %nums, i64 16
  store i32 5, ptr %.10, align 4
  br label %while.body

while.body:                                       ; preds = %entry, %while.body
  %total.0 = phi i32 [ 0, %entry ], [ %spec.select, %while.body ]
  %i.0 = phi i32 [ 0, %entry ], [ %.34, %while.body ]
  %0 = zext nneg i32 %i.0 to i64
  %.19 = getelementptr inbounds nuw [5 x i32], ptr %nums, i64 0, i64 %0
  %.20 = load i32, ptr %.19, align 4
  %1 = and i32 %.20, 1
  %.24 = icmp eq i32 %1, 0
  %.30 = select i1 %.24, i32 %.20, i32 0
  %spec.select = add i32 %.30, %total.0
  %.34 = add nuw nsw i32 %i.0, 1
  %.37 = icmp slt i32 %spec.select, 11
  %.16 = icmp samesign ult i32 %i.0, 4
  %or.cond = and i1 %.16, %.37
  br i1 %or.cond, label %while.body, label %while.end

while.end:                                        ; preds = %while.body
  %puts = tail call i32 @puts(ptr nonnull dereferenceable(1) @.str.0)
  %.46 = tail call i32 @fibonacci(i32 7)
  %.48 = tail call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) @.fmt.2, i32 %.46)
  %puts7 = tail call i32 @puts(ptr nonnull dereferenceable(1) @.str.3)
  %.54 = tail call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) @.fmt.5, i32 %spec.select)
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
  %.5 = icmp samesign ult i32 %n.tr6, 4
  br i1 %.5, label %common.ret, label %if.end
}

; Function Attrs: nofree nounwind
declare noundef i32 @puts(ptr nocapture noundef readonly) local_unnamed_addr #0

attributes #0 = { nofree nounwind }
attributes #1 = { nofree nosync nounwind memory(none) }
