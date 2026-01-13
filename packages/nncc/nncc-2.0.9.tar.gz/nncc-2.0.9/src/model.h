/*
 * model.h - Consolidated IR for nncc
 * 
 * Merged from: tensor.h, ops.h, graph.h
 * This file contains all data structures for representing neural networks.
 */

#ifndef NNCC_MODEL_H
#define NNCC_MODEL_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ============================================================================
 * Constants
 * ========================================================================== */

#define TENSOR_NAME_MAX     128
#define GRAPH_INITIAL_CAP   64

// Note: Limits removed. Arrays are dynamically allocated.

/* ============================================================================
 * Error Codes
 * ========================================================================== */

typedef enum {
    NNCC_OK = 0,
    NNCC_ERROR_FILE_NOT_FOUND,
    NNCC_ERROR_INVALID_FORMAT,
    NNCC_ERROR_UNSUPPORTED_OP,
    NNCC_ERROR_SHAPE_MISMATCH,
    NNCC_ERROR_OUT_OF_MEMORY,
    NNCC_ERROR_IO,
    NNCC_ERROR_INTERNAL,
} NnccError;

/* ============================================================================
 * Data Types
 * ========================================================================== */

typedef enum {
    DTYPE_FLOAT32 = 0,
    DTYPE_FLOAT16,
    DTYPE_INT32,
    DTYPE_INT8,
    DTYPE_UINT8,
} DataType;

size_t dtype_size(DataType dtype);
const char* dtype_name(DataType dtype);

/* ============================================================================
 * Operation Types - All essential ops for SOTA networks
 * ========================================================================== */

typedef enum {
    OP_UNKNOWN = 0,
    
    /* Matrix operations */
    OP_MATMUL,
    OP_GEMM,
    
    /* Convolution */
    OP_CONV2D,
    
    /* Pooling */
    OP_MAXPOOL2D,
    OP_AVGPOOL2D,
    OP_GLOBAL_AVGPOOL,
    
    /* Activations */
    OP_RELU,
    OP_RELU6,
    OP_SIGMOID,
    OP_TANH,
    OP_SOFTMAX,
    OP_LEAKY_RELU,
    
    /* Normalization */
    OP_BATCHNORM,
    
    /* Element-wise */
    OP_ADD,
    OP_MUL,
    
    /* Shape operations */
    OP_FLATTEN,
    OP_RESHAPE,
    
    /* Other */
    OP_DROPOUT,
    OP_IDENTITY,
    
    OP_COUNT
} OpType;

const char* op_type_name(OpType type);

/* ============================================================================
 * Operation Attributes
 * ========================================================================== */

typedef struct {
    int kernel_h, kernel_w;
    int stride_h, stride_w;
    int pad_h, pad_w;
    int groups;
} ConvAttrs;

typedef struct {
    int kernel_h, kernel_w;
    int stride_h, stride_w;
    int pad_h, pad_w;
} PoolAttrs;

typedef struct {
    int axis;
} AxisAttrs;

typedef struct {
    float epsilon;
} BatchNormAttrs;

typedef struct {
    int* new_dims;      // Dynamic array
    int new_ndim;
} ReshapeAttrs;

typedef struct {
    float alpha;
} LeakyReluAttrs;

typedef union {
    ConvAttrs conv;
    PoolAttrs pool;
    AxisAttrs axis;
    BatchNormAttrs batchnorm;
    ReshapeAttrs reshape;
    LeakyReluAttrs leaky_relu;
} OpAttrs;

/* ============================================================================
 * Tensor Structure
 * ========================================================================== */

typedef struct Tensor {
    char name[TENSOR_NAME_MAX];
    int id;
    
    int* dims;          // Dynamic array
    int ndim;
    DataType dtype;
    
    void* data;
    size_t data_size;
    bool owns_data;
    
    bool is_weight;
    bool is_input;
    bool is_output;
    
    int scratch_offset;  /* Memory planning */
} Tensor;

/* Tensor functions */
Tensor* tensor_create(const char* name, DataType dtype, int ndim, const int* dims);
Tensor* tensor_create_with_data(const char* name, DataType dtype, int ndim, const int* dims, const void* data);
void tensor_free(Tensor* tensor);
size_t tensor_numel(const Tensor* tensor);
size_t tensor_size_bytes(const Tensor* tensor);

/* ============================================================================
 * Operation Structure
 * ========================================================================== */

typedef struct Op {
    int id;
    char name[TENSOR_NAME_MAX];
    OpType type;
    
    Tensor** inputs;    // Dynamic array
    int num_inputs;
    int inputs_capacity;

    Tensor** outputs;   // Dynamic array
    int num_outputs;
    int outputs_capacity;
    
    OpAttrs attrs;
    
    /* Fused activation */
    bool fused_activation;
    OpType activation_type;
} Op;

/* Op functions */
Op* op_create(OpType type, const char* name);
void op_free(Op* op);
bool op_add_input(Op* op, Tensor* tensor);
bool op_add_output(Op* op, Tensor* tensor);
void op_set_conv_attrs(Op* op, int kh, int kw, int sh, int sw, int ph, int pw, int groups);
void op_set_pool_attrs(Op* op, int kh, int kw, int sh, int sw, int ph, int pw);
void op_set_axis(Op* op, int axis);
void op_set_batchnorm_attrs(Op* op, float epsilon);

/* ============================================================================
 * Graph Structure
 * ========================================================================== */

typedef struct Graph {
    char name[TENSOR_NAME_MAX];
    
    Op** ops;
    int num_ops;
    int ops_capacity;
    
    Tensor** tensors;
    int num_tensors;
    int tensors_capacity;
    
    Tensor** inputs;    // Dynamic array
    int num_inputs;
    int inputs_capacity;

    Tensor** outputs;   // Dynamic array
    int num_outputs;
    int outputs_capacity;
    
    int scratch_size;
    bool is_sorted;
} Graph;

/* Graph functions */
Graph* graph_create(const char* name);
void graph_free(Graph* graph);
int graph_add_tensor(Graph* graph, Tensor* tensor);
int graph_add_op(Graph* graph, Op* op);
bool graph_set_input(Graph* graph, int tensor_id);
bool graph_set_output(Graph* graph, int tensor_id);
Tensor* graph_find_tensor(Graph* graph, const char* name);
Tensor* graph_get_tensor(Graph* graph, int id);
Op* graph_get_op(Graph* graph, int id);
NnccError graph_topological_sort(Graph* graph);
Op* graph_get_producer(Graph* graph, Tensor* tensor);
void graph_print(const Graph* graph);

#ifdef __cplusplus
}
#endif

#endif /* NNCC_MODEL_H */
