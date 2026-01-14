# tlnr Zsh Real-Time Integration
# ZLE-based keystroke monitoring for instant command predictions
# Compatible with Oh-My-Zsh and other shell frameworks

# Global state variables
# Ensure UTF-8 handling for emojis and ANSI codes
export LC_ALL=${LC_ALL:-C.UTF-8}
export PYTHONIOENCODING=utf-8

typeset -g TT_CURRENT_PREDICTION=""
typeset -g TT_PREDICTION_DISPLAYED=""
typeset -g TT_LAST_BUFFER=""
typeset -g TT_REALTIME_ENABLED="1"
typeset -g TT_PREDICTION_LINES=""
typeset -g TT_OMZ_DETECTED="0"

# Detect Oh-My-Zsh for compatibility mode
if [[ -n "$ZSH" && -d "$ZSH" ]]; then
    TT_OMZ_DETECTED="1"
fi

# Performance cache
typeset -gA TT_PREDICTION_CACHE

# Terminal escape sequences (force update to ensure correct values)
typeset -g TT_SAVE_CURSOR=$'\033[s'
typeset -g TT_RESTORE_CURSOR=$'\033[u'
typeset -g TT_MOVE_DOWN=$'\033[B'
typeset -g TT_CLEAR_LINE=$'\033[2K'
typeset -g TT_GREY_TEXT=$'\033[90m'
typeset -g TT_RESET_COLOR=$'\033[0m'

# Core prediction widget - called on every keystroke
tt_predict_realtime() {
    # Skip if disabled (check for disable file)
    [[ -f "/tmp/tt_disabled" ]] && return

    local current_buffer="$BUFFER"

    # Skip if buffer unchanged
    [[ "$current_buffer" == "$TT_LAST_BUFFER" ]] && return
    TT_LAST_BUFFER="$current_buffer"

    # Skip empty or space-prefixed buffers
    [[ -z "$current_buffer" || "$current_buffer" =~ ^[[:space:]] ]] && {
        tt_clear_prediction
        return
    }

    # Check cache first
    if [[ -n "${TT_PREDICTION_CACHE[$current_buffer]}" ]]; then
        local cached_prediction="${TT_PREDICTION_CACHE[$current_buffer]}"
        if [[ "$cached_prediction" != "$TT_CURRENT_PREDICTION" ]]; then
            tt_display_prediction "$cached_prediction"
        fi
        return
    fi

    # Get prediction from Terminal Tutor
    # Priority: 1. Daemon (fastest), 2. Direct CLI (fallback)
    local prediction=""
    local sock_path="$HOME/.tlnr.sock"

    if [[ -S "$sock_path" ]]; then
        # Daemon mode: Use Unix socket for ~1000x faster response
        prediction=$(echo "$current_buffer" | nc -U "$sock_path" 2>/dev/null)
    elif command -v tlnr >/dev/null 2>&1; then
        # Fallback: Direct CLI call with 50ms timeout to prevent hanging
        if command -v timeout >/dev/null 2>&1; then
            prediction=$(timeout 0.05 tlnr predict "$current_buffer" 2>/dev/null)
        elif command -v gtimeout >/dev/null 2>&1; then
            # macOS with coreutils
            prediction=$(gtimeout 0.05 tlnr predict "$current_buffer" 2>/dev/null)
        else
            prediction=$(tlnr predict "$current_buffer" 2>/dev/null)
        fi
    fi

    # Check for rate limit message - clear cache so all queries go to daemon
    if [[ "$prediction" == *"Daily limit"* || "$prediction" == *"limit reached"* ]]; then
        TT_PREDICTION_CACHE=()
        tt_display_prediction "$prediction"
        return
    fi

    # Cache result (only if not rate limited)
    TT_PREDICTION_CACHE[$current_buffer]="$prediction"

    # Display if changed
    if [[ "$prediction" != "$TT_CURRENT_PREDICTION" ]]; then
        if [[ -n "$prediction" ]]; then
            tt_display_prediction "$prediction"
        else
            tt_clear_prediction
        fi
    fi
}

# Display prediction below current line
tt_display_prediction() {
    local prediction="$1"

    # Use plain text for POSTDISPLAY (no ANSI codes)
    POSTDISPLAY=$'\n'"${prediction}"

    # Apply styling using Zsh's region_highlight mechanism
    # This avoids "raw" escape codes appearing in the terminal
    # format: "start end highlighting_spec"
    # attributes: fg=8 (grey)
    local start_pos=$#BUFFER
    local end_pos=$(($#BUFFER + $#POSTDISPLAY))
    
    # FIX: Reset highlight array to prevent accumulation (Issue #1)
    # Using = instead of += ensures only one highlight entry exists
    region_highlight=("$start_pos $end_pos fg=8")

    TT_CURRENT_PREDICTION="$prediction"
    TT_PREDICTION_DISPLAYED="1"
}

# Clear prediction display
tt_clear_prediction() {
    POSTDISPLAY=""
    TT_CURRENT_PREDICTION=""
    TT_PREDICTION_DISPLAYED=""
    TT_PREDICTION_LINES=""
    # FIX: Clear region_highlight to prevent visual artifacts
    region_highlight=()
}

# Clean up on command execution
tt_cleanup_on_accept() {
    tt_clear_prediction

    # Log command to local history file for stats (simple append, near-zero latency)
    # Format: TIMESTAMP|COMMAND
    if [[ -n "$BUFFER" ]]; then
        echo "$(date +%s)|$BUFFER" >> ~/.tlnr_local_history
    fi

    # Periodic cache cleanup - increased from 100 to 500 entries
    # Use LRU-style eviction: clear oldest half when limit reached
    if (( ${#TT_PREDICTION_CACHE} > 500 )); then
        # Clear cache (simple approach - full clear at 500)
        TT_PREDICTION_CACHE=()
    fi

    zle accept-line
}

# Handle backspace with prediction update
tt_handle_backward_delete() {
    zle backward-delete-char
    tt_predict_realtime
}

# Handle Ctrl+C
tt_handle_cancel() {
    tt_clear_prediction
    TT_PREDICTION_CACHE=()
    zle send-break
}

# Self-insert with prediction
tt_self_insert_and_predict() {
    zle self-insert
    tt_predict_realtime
}

# Handle paste (bracketed-paste)


# Handle history navigation (up)
tt_handle_up_history() {
    zle up-line-or-history
    tt_predict_realtime
}

# Handle history navigation (down)
tt_handle_down_history() {
    zle down-line-or-history
    tt_predict_realtime
}

# Register ZLE widgets
zle -N tt_predict_realtime
zle -N tt_cleanup_on_accept
zle -N tt_handle_backward_delete
zle -N tt_handle_cancel
zle -N tt_self_insert_and_predict

zle -N tt_handle_up_history
zle -N tt_handle_down_history

# Bind to key events
bindkey '^M' tt_cleanup_on_accept      # Enter
bindkey '^?' tt_handle_backward_delete  # Backspace
bindkey '^C' tt_handle_cancel          # Ctrl+C

# Bind history navigation
bindkey '^[[A' tt_handle_up_history    # Up Arrow
bindkey '^[[B' tt_handle_down_history  # Down Arrow
bindkey '^[OA' tt_handle_up_history    # Up Arrow (Application mode)
bindkey '^[OB' tt_handle_down_history  # Down Arrow (Application mode)

# Handle Paste (Robust Widget Wrapping)
# We wrap the existing bracketed-paste widget (or bracketed-paste-magic)
# This ensures we don't break existing paste functionality while adding our hook.

# Ensure some form of bracketed paste exists
autoload -Uz bracketed-paste-magic
zle -N bracketed-paste bracketed-paste-magic

# Wrap it if we haven't already (check for our wrapper name)
if [[ "${widgets[bracketed-paste]}" != "user:tt_handle_paste" ]]; then
    # Save original widget
    if zle -l bracketed-paste; then
        zle -A bracketed-paste _tt_orig_bracketed_paste
    else
        # Fallback if no bracketed-paste exists (unlikely in modern zsh)
        zle -N _tt_orig_bracketed_paste .bracketed-paste
    fi

    # Define our wrapper that calls original + predict
    tt_handle_paste() {
        zle _tt_orig_bracketed_paste
        tt_predict_realtime
        zle redisplay
    }
    
    # Register our wrapper as "bracketed-paste"
    zle -N bracketed-paste tt_handle_paste
fi
# Note: We do NOT manually bind ^[[200~. We assume Zsh or user has bound 
# bracketed-paste to the paste sequence (standard behavior).

# Bind printable characters to prediction function (completely silent)
if zle -l tt_self_insert_and_predict >/dev/null 2>&1; then
    for char in {a..z} {A..Z} {0..9} ' ' '-' '_' '.' '/' '=' ':' '@' '+' ',' '!' '?' '*' '%' '$' '#' '&' '(' ')' '[' ']' '{' '}' '<' '>' '|' ';' '"' "'" '`' '~'; do
        bindkey "$char" tt_self_insert_and_predict >/dev/null 2>&1 || :
    done
fi

# Utility functions (terminal-tutor CLI only interface)
tt_clear_cache() {
    TT_PREDICTION_CACHE=()
    echo "${TT_GREY_TEXT}🧹 Prediction cache cleared${TT_RESET_COLOR}"
}

# Hook cleanup on prompt display
precmd() {
    tt_clear_prediction
    TT_LAST_BUFFER=""
}

# Cleanup on exit
zshexit() {
    tt_clear_prediction
}

# Initialize (silent load)