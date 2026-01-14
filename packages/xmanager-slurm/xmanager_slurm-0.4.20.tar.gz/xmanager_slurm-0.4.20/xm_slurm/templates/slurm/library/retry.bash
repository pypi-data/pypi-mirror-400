# retry: rerun a command if it exits with certain codes
# Options:
#   -c CODE   Retry on this exit code (repeatable).
#   -n N      Max attempts (incl. first). Default: unlimited
#   -d SECS   Initial delay before first retry. Default: 1
#   -b FACTOR Integer backoff multiplier per retry. Default: 1 (no backoff)
#   -q        Quiet (no logs)
# Usage:
#   retry [-c CODE ...] [-n N] [-d SECS] [-b FACTOR] [-q] -- cmd arg1 arg2 ...
retry() {
  local -a codes=()
  local -i max=-1 delay=1 backoff=1 quiet=0 status
  local opt OPTIND=1

  while getopts ":c:n:d:b:q" opt; do
    case "$opt" in
      c) codes+=("$OPTARG") ;;
      n) max=$OPTARG ;;
      d) delay=$OPTARG ;;
      b) backoff=$OPTARG ;;
      q) quiet=1 ;;
      :) printf 'retry: option -%s requires an argument\n' "$OPTARG" >&2; return 2 ;;
      \?) printf 'retry: invalid option -- %s\n' "$OPTARG" >&2; return 2 ;;
    esac
  done
  shift $((OPTIND-1))
  (( $# )) || { printf 'retry: missing command\n' >&2; return 2; }

  ((${#codes[@]})) || { printf 'retry: no return codes specified\n' >&2; return 2; }

  for ((attempt=1; ; attempt++)); do
    if "$@"; then                    # safe with set -e (exception context)
      return 0
    else
      status=$?                       # capture failing status immediately
    fi

    # retryable?
    local retryable=0 c
    for c in "${codes[@]}"; do
      (( status == c )) && { retryable=1; break; }
    done

    # stop if not retryable OR we've just hit the max attempt
    if (( !retryable )) || (( max >= 0 && attempt >= max )); then
      (( quiet )) || {
        if (( attempt > 1 )); then
          printf 'retry: giving up after %d attempts; last exit=%d\n' "$attempt" "$status" >&2
        else
          printf 'retry: command failed; exit=%d\n' "$status" >&2
        fi
      }
      return "$status"               # propagate exact code; errexit will catch
    fi

    (( quiet )) || printf 'retry: attempt %d failed with %d; retrying in %ds...\n' \
                          "$attempt" "$status" "$delay" >&2
    sleep "$delay" || :              # never trip set -e if sleep errors
    (( delay *= backoff ))
  done
}
export -f retry