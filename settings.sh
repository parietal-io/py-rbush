
export PYTHONPATH="$PWD:$PYTHONPATH"

# Filter line-profiler tables (python -m line_profiler benchmark.lprof
#
alias lprof_summary="awk '{if(/Function/){njit=\"no\";printf \"%s %20s \",\$1,\$2}if(/[0-9]\s+@njit/){njit=\"yes\"}if(/Total/){printf \"\t%10s %s\n\",\$3,njit}}'"


unjit_all () {
  code_py="$1"
  sed -E 's/#\s*(@n?jit.*)/\1/' $code_py > ${code_py}.unjit
}

jit_all () {
  code_py="$1"
  sed -E 's/(@n?jit.*)/#\1/' $code_py > ${code_py}.jit
}
