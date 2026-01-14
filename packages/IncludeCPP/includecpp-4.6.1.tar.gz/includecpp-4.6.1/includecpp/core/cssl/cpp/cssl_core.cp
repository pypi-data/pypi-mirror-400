SOURCE(include/cssl_core.cpp) cssl_core

PUBLIC(
    // Full Interpreter - Main Entry Point
    cssl_core FUNC(run_cssl)
    cssl_core FUNC(version)
    cssl_core FUNC(is_keyword)

    // Lexer & Token Classes
    cssl_core CLASS(Lexer) {
        CONSTRUCTOR(const std::string&)
        METHOD(tokenize)
    }
    cssl_core CLASS(Token) {
        CONSTRUCTOR()
        CONSTRUCTOR(int, int, int)
        CONSTRUCTOR(int, const std::string&, int, int)
        CONSTRUCTOR(int, double, int, int)
        CONSTRUCTOR(int, bool, int, int)
        FIELD(type)
        FIELD(str_value)
        FIELD(num_value)
        FIELD(bool_value)
        FIELD(value_type)
        FIELD(line)
        FIELD(column)
    }

    // Full Interpreter Class
    cssl_core CLASS(Interpreter) {
        CONSTRUCTOR()
        METHOD(run)
        METHOD(run_string)
    }

    // Value Class (for advanced usage)
    cssl_core CLASS(Value) {
        CONSTRUCTOR()
        CONSTRUCTOR(bool)
        CONSTRUCTOR(int64_t)
        CONSTRUCTOR(double)
        CONSTRUCTOR(const std::string&)
        METHOD_CONST(as_bool)
        METHOD_CONST(as_float)
        METHOD_CONST(as_int)
        METHOD_CONST(as_string)
        METHOD_CONST(get_type)
        METHOD_CONST(is_bool)
        METHOD_CONST(is_dict)
        METHOD_CONST(is_float)
        METHOD_CONST(is_int)
        METHOD_CONST(is_list)
        METHOD_CONST(is_null)
        METHOD_CONST(is_number)
        METHOD_CONST(is_string)
        METHOD_CONST(to_bool)
        METHOD_CONST(to_string)
    }

    // String Operations
    cssl_core FUNC(str_concat)
    cssl_core FUNC(str_contains)
    cssl_core FUNC(str_join)
    cssl_core FUNC(str_lower)
    cssl_core FUNC(str_replace)
    cssl_core FUNC(str_split)
    cssl_core FUNC(str_trim)
    cssl_core FUNC(str_upper)
    cssl_core FUNC(str_reverse)
    cssl_core FUNC(str_len)
    cssl_core FUNC(str_repeat)
    cssl_core FUNC(str_startswith)
    cssl_core FUNC(str_endswith)
    cssl_core FUNC(str_indexof)
    cssl_core FUNC(str_substr)
    cssl_core FUNC(str_cmp)

    // Math Operations
    cssl_core FUNC(math_clamp)
    cssl_core FUNC(math_ipow)
    cssl_core FUNC(math_pow)
    cssl_core FUNC(math_mod)
    cssl_core FUNC(math_abs)
    cssl_core FUNC(math_min)
    cssl_core FUNC(math_max)
    cssl_core FUNC(math_floor)
    cssl_core FUNC(math_ceil)

    // Array Operations
    cssl_core FUNC(array_sum)
    cssl_core FUNC(array_isum)
    cssl_core FUNC(array_avg)
    cssl_core FUNC(array_min)
    cssl_core FUNC(array_max)
    cssl_core FUNC(range)

    // Loop Helpers
    cssl_core FUNC(loop_check_lt)
    cssl_core FUNC(loop_check_le)
    cssl_core FUNC(loop_check_gt)
    cssl_core FUNC(loop_check_ge)

    // Comparison Helpers
    cssl_core FUNC(num_cmp)
    cssl_core FUNC(eq_int)
    cssl_core FUNC(eq_float)
    cssl_core FUNC(eq_str)
)
