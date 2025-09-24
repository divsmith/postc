(module
  (import "wasi_snapshot_preview1" "fd_write" (func $fd_write (param i32 i32 i32 i32) (result i32)))
  (memory (export "memory") 1)
  (global $var_0 (mut f64) (f64.const 0.0))
  (global $var_1 (mut f64) (f64.const 0.0))
  (global $var_2 (mut i32) (i32.const 0))
  (func $main (export "main")
    (local $temp i32)
    i32.const 5
    i32.const 3
    ;; add (would need to determine if i32.add or f64.add)
    ;; print (would need to implement with WASI)
    ;; Loading string: Hello, PostC!
    ;; print (would need to implement with WASI)
  )
)