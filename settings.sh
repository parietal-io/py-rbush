
export PYTHONPATH="$PWD:$PYTHONPATH"

# Filter line-profiler tables (python -m line_profiler benchmark.lprof
#
alias lprof_summary="awk '{if(/Function/){njit=\"no\";printf \"%s %20s \",\$1,\$2}if(/njit/){njit=\"yes\"}if(/Total/){printf \"\t%10s %s\n\",\$3,njit}}'"
