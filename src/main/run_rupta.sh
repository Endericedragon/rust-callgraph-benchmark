cargo clean
export LD_LIBRARY_PATH=$(rustc --print sysroot)/lib:$LD_LIBRARY_PATH
RUST_BACKTRACE=1 cargo-pta pta --release -- --dump-overall-metadata om.json
# dot -v -Tsvg -o cg.svg cg.dot