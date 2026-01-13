/*
 * codegen.h - C code generator for nncc
 */

#ifndef NNCC_CODEGEN_H
#define NNCC_CODEGEN_H

#include "model.h"
#include <stdio.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ============================================================================
 * Configuration
 * ========================================================================== */

typedef enum {
    SIMD_NONE = 0,
    SIMD_SSE4,
    SIMD_AVX2,
    SIMD_NEON,
} SimdLevel;

typedef struct {
    const char* output_path;
    const char* model_name;
    SimdLevel simd_level;
    bool use_libc_math;
    bool inline_weights;
    bool emit_comments;
    int indent_spaces;
} CodegenConfig;

void codegen_config_init(CodegenConfig* config);

/* ============================================================================
 * Code Generation Context
 * ========================================================================== */

typedef struct {
    FILE* out;
    char* buffer;       // Output buffer (if out is NULL)
    size_t buffer_cap;  // Capacity
    size_t buffer_len;  // Current length

    const Graph* graph;
    const CodegenConfig* config;
    int indent;
} CodegenContext;

/* ============================================================================
 * Main API
 * ========================================================================== */

/* Generate C code from graph to file */
NnccError codegen_generate(const Graph* graph, const CodegenConfig* config);

/* Generate C code from graph to memory buffer (allocated by caller or internal) */
/* If buffer is NULL, returns required size in *out_len */
NnccError codegen_generate_to_memory(const Graph* graph, const CodegenConfig* config, char** out_buffer, size_t* out_len);

#ifdef __cplusplus
}
#endif

#endif /* NNCC_CODEGEN_H */
