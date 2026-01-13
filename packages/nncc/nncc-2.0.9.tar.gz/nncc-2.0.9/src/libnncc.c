/*
 * libnncc.c - Shared library interface for nncc
 */

#include "model.h"
#include "loader.h"
#include "codegen.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#if defined(_WIN32)
#define NNCC_API __declspec(dllexport)
#else
#define NNCC_API __attribute__((visibility("default")))
#endif

/*
 * Compile model from in-memory data to C code string.
 * 
 * Args:
 *   name: Model name prefix
 *   nnmodel_json: JSON content string
 *   safe_data: SafeTensors binary data
 *   safe_len: Length of safe_data
 *   out_len: Output pointer for code length (optional)
 * 
 * Returns:
 *   Allocated string containing C code. Caller must free with nncc_free().
 *   Returns NULL on error.
 */
NNCC_API char* nncc_compile(const char* name, const char* nnmodel_json, const void* safe_data, size_t safe_len, size_t* out_len) {
    if (!name || !nnmodel_json || !safe_data) return NULL;
    
    // Parse architecture
    Graph* graph = NULL;
    NnccError err = nnmodel_parse(nnmodel_json, strlen(nnmodel_json), &graph);
    if (err != NNCC_OK) return NULL;
    
    // Parse weights
    err = safetensors_parse(safe_data, safe_len, graph);
    if (err != NNCC_OK) {
        graph_free(graph);
        return NULL;
    }
    
    // Generate code
    CodegenConfig config;
    codegen_config_init(&config);
    config.model_name = name;
    
    char* code = NULL;
    size_t code_len = 0;
    
    err = codegen_generate_to_memory(graph, &config, &code, &code_len);
    
    graph_free(graph);
    
    if (err != NNCC_OK) {
        return NULL;
    }
    
    if (out_len) *out_len = code_len;
    return code;
}

/*
 * Free memory allocated by nncc_compile
 */
NNCC_API void nncc_free(void* ptr) {
    if (ptr) free(ptr);
}
