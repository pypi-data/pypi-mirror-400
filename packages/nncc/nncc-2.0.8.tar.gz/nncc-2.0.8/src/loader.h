/*
 * loader.h - Model and weights loader for nncc
 * 
 * Loads:
 *   - .safetensors files (weights only)
 *   - .nnmodel files (architecture definition in JSON)
 */

#ifndef NNCC_LOADER_H
#define NNCC_LOADER_H

#include "model.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ============================================================================
 * SafeTensors Loader
 * ========================================================================== */

/* Load weights from a SafeTensors file into an existing graph */
NnccError safetensors_load_weights(const char* path, Graph* graph);

/* Parse weights from memory buffer */
NnccError safetensors_parse(const void* data, size_t len, Graph* graph);

/* ============================================================================
 * Model Definition Loader (.nnmodel JSON format)
 * ========================================================================== */

/*
 * .nnmodel JSON format:
 * {
 *   "name": "model_name",
 *   "inputs": [{"name": "input", "dtype": "float32", "shape": [1, 784]}],
 *   "outputs": [{"name": "output", "dtype": "float32", "shape": [1, 10]}],
 *   "layers": [
 *     {
 *       "name": "fc1",
 *       "op": "gemm",
 *       "inputs": ["input"],
 *       "weights": {"weight": "fc1.weight", "bias": "fc1.bias"},
 *       "output_shape": [1, 128]
 *     },
 *     ...
 *   ]
 * }
 */

/* Load graph structure from .nnmodel file */
NnccError nnmodel_load(const char* path, Graph** out_graph);

/* Parse graph structure from JSON string */
NnccError nnmodel_parse(const char* json_data, size_t json_len, Graph** out_graph);

/* ============================================================================
 * Combined Loader
 * ========================================================================== */

/* Load complete model: architecture from .nnmodel, weights from .safetensors */
NnccError model_load(const char* nnmodel_path, const char* safetensors_path, Graph** out_graph);

#ifdef __cplusplus
}
#endif

#endif /* NNCC_LOADER_H */
