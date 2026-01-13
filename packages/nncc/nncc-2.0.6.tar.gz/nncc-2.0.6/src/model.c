// model.c - Consolidated IR implementation for nncc
// 
// Merged from: tensor.c, ops.c, graph.c

#include "model.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Data Type Utilities

size_t dtype_size(DataType dtype) {
    switch (dtype) {
        case DTYPE_FLOAT32: return 4;
        case DTYPE_FLOAT16: return 2;
        case DTYPE_INT32:   return 4;
        case DTYPE_INT8:    return 1;
        case DTYPE_UINT8:   return 1;
        default:            return 0;
    }
}

const char* dtype_name(DataType dtype) {
    switch (dtype) {
        case DTYPE_FLOAT32: return "float32";
        case DTYPE_FLOAT16: return "float16";
        case DTYPE_INT32:   return "int32";
        case DTYPE_INT8:    return "int8";
        case DTYPE_UINT8:   return "uint8";
        default:            return "unknown";
    }
}

// Operation Type Names

static const char* OP_TYPE_NAMES[] = {
    [OP_UNKNOWN] = "Unknown",
    [OP_MATMUL] = "MatMul",
    [OP_GEMM] = "Gemm",
    [OP_CONV2D] = "Conv2D",
    [OP_MAXPOOL2D] = "MaxPool2D",
    [OP_AVGPOOL2D] = "AvgPool2D",
    [OP_GLOBAL_AVGPOOL] = "GlobalAvgPool",
    [OP_RELU] = "ReLU",
    [OP_RELU6] = "ReLU6",
    [OP_SIGMOID] = "Sigmoid",
    [OP_TANH] = "Tanh",
    [OP_SOFTMAX] = "Softmax",
    [OP_LEAKY_RELU] = "LeakyReLU",
    [OP_BATCHNORM] = "BatchNorm",
    [OP_ADD] = "Add",
    [OP_MUL] = "Mul",
    [OP_FLATTEN] = "Flatten",
    [OP_RESHAPE] = "Reshape",
    [OP_DROPOUT] = "Dropout",
    [OP_IDENTITY] = "Identity",
};

const char* op_type_name(OpType type) {
    if (type >= 0 && type < OP_COUNT) {
        return OP_TYPE_NAMES[type];
    }
    return "Unknown";
}

// Tensor Implementation

Tensor* tensor_create(const char* name, DataType dtype, int ndim, const int* dims) {
    if (ndim < 0) return NULL;
    
    Tensor* t = (Tensor*)calloc(1, sizeof(Tensor));
    if (!t) return NULL;
    
    if (name) {
        strncpy(t->name, name, TENSOR_NAME_MAX - 1);
        t->name[TENSOR_NAME_MAX - 1] = '\0';
    }
    
    t->ndim = ndim;
    if (ndim > 0) {
        t->dims = (int*)malloc(ndim * sizeof(int));
        if (!t->dims) {
            free(t);
            return NULL;
        }
        for (int i = 0; i < ndim; i++) {
            t->dims[i] = dims[i];
        }
    } else {
        t->dims = NULL;
    }
    
    t->dtype = dtype;
    t->id = -1;
    t->scratch_offset = -1;
    
    return t;
}

Tensor* tensor_create_with_data(const char* name, DataType dtype, int ndim, const int* dims, const void* data) {
    Tensor* t = tensor_create(name, dtype, ndim, dims);
    if (!t) return NULL;
    
    size_t size = tensor_size_bytes(t);
    if (size > 0 && data) {
        t->data = malloc(size);
        if (!t->data) {
            tensor_free(t);
            return NULL;
        }
        memcpy(t->data, data, size);
        t->data_size = size;
        t->owns_data = true;
    }
    return t;
}

void tensor_free(Tensor* t) {
    if (!t) return;
    if (t->owns_data && t->data) free(t->data);
    if (t->dims) free(t->dims);
    free(t);
}

size_t tensor_numel(const Tensor* t) {
    if (!t || t->ndim == 0) return 0;
    size_t n = 1;
    for (int i = 0; i < t->ndim; i++) {
        n *= (size_t)t->dims[i];
    }
    return n;
}

size_t tensor_size_bytes(const Tensor* t) {
    return tensor_numel(t) * dtype_size(t->dtype);
}

// Op Implementation

Op* op_create(OpType type, const char* name) {
    Op* op = (Op*)calloc(1, sizeof(Op));
    if (!op) return NULL;
    
    op->type = type;
    // Initial capacity for inputs/outputs
    op->inputs_capacity = 4;
    op->inputs = (Tensor**)calloc(op->inputs_capacity, sizeof(Tensor*));
    
    op->outputs_capacity = 4;
    op->outputs = (Tensor**)calloc(op->outputs_capacity, sizeof(Tensor*));
    
    if (!op->inputs || !op->outputs) {
        if (op->inputs) free(op->inputs);
        if (op->outputs) free(op->outputs);
        free(op);
        return NULL;
    }

    if (name) {
        strncpy(op->name, name, TENSOR_NAME_MAX - 1);
    }
    
    // Default attributes
    switch (type) {
        case OP_CONV2D:
            op->attrs.conv.kernel_h = 3;
            op->attrs.conv.kernel_w = 3;
            op->attrs.conv.stride_h = 1;
            op->attrs.conv.stride_w = 1;
            op->attrs.conv.groups = 1;
            break;
        case OP_MAXPOOL2D:
        case OP_AVGPOOL2D:
            op->attrs.pool.kernel_h = 2;
            op->attrs.pool.kernel_w = 2;
            op->attrs.pool.stride_h = 2;
            op->attrs.pool.stride_w = 2;
            break;
        case OP_SOFTMAX:
            op->attrs.axis.axis = -1;
            break;
        case OP_BATCHNORM:
            op->attrs.batchnorm.epsilon = 1e-5f;
            break;
        case OP_LEAKY_RELU:
            op->attrs.leaky_relu.alpha = 0.01f;
            break;
        default:
            break;
    }
    return op;
}

void op_free(Op* op) {
    if (op->type == OP_RESHAPE && op->attrs.reshape.new_dims) {
        free(op->attrs.reshape.new_dims);
    }
    if (op->inputs) free(op->inputs);
    if (op->outputs) free(op->outputs);
    free(op);
}

bool op_add_input(Op* op, Tensor* t) {
    if (!op || !t) return false;
    
    if (op->num_inputs >= op->inputs_capacity) {
        int new_cap = op->inputs_capacity * 2;
        Tensor** new_arr = (Tensor**)realloc(op->inputs, new_cap * sizeof(Tensor*));
        if (!new_arr) return false;
        op->inputs = new_arr;
        op->inputs_capacity = new_cap;
    }
    
    op->inputs[op->num_inputs++] = t;
    return true;
}

bool op_add_output(Op* op, Tensor* t) {
    if (!op || !t) return false;

    if (op->num_outputs >= op->outputs_capacity) {
        int new_cap = op->outputs_capacity * 2;
        Tensor** new_arr = (Tensor**)realloc(op->outputs, new_cap * sizeof(Tensor*));
        if (!new_arr) return false;
        op->outputs = new_arr;
        op->outputs_capacity = new_cap;
    }

    op->outputs[op->num_outputs++] = t;
    return true;
}

void op_set_conv_attrs(Op* op, int kh, int kw, int sh, int sw, int ph, int pw, int groups) {
    if (!op) return;
    op->attrs.conv.kernel_h = kh;
    op->attrs.conv.kernel_w = kw;
    op->attrs.conv.stride_h = sh;
    op->attrs.conv.stride_w = sw;
    op->attrs.conv.pad_h = ph;
    op->attrs.conv.pad_w = pw;
    op->attrs.conv.groups = groups;
}

void op_set_pool_attrs(Op* op, int kh, int kw, int sh, int sw, int ph, int pw) {
    if (!op) return;
    op->attrs.pool.kernel_h = kh;
    op->attrs.pool.kernel_w = kw;
    op->attrs.pool.stride_h = sh;
    op->attrs.pool.stride_w = sw;
    op->attrs.pool.pad_h = ph;
    op->attrs.pool.pad_w = pw;
}

void op_set_axis(Op* op, int axis) {
    if (op) op->attrs.axis.axis = axis;
}

void op_set_batchnorm_attrs(Op* op, float epsilon) {
    if (op) op->attrs.batchnorm.epsilon = epsilon;
}

// Graph Implementation

Graph* graph_create(const char* name) {
    Graph* g = (Graph*)calloc(1, sizeof(Graph));
    if (!g) return NULL;
    
    if (name) {
        strncpy(g->name, name, TENSOR_NAME_MAX - 1);
    }
    
    g->ops_capacity = GRAPH_INITIAL_CAP;
    g->ops = (Op**)calloc(g->ops_capacity, sizeof(Op*));
    
    g->tensors_capacity = GRAPH_INITIAL_CAP;
    g->tensors = (Tensor**)calloc(g->tensors_capacity, sizeof(Tensor*));
    
    g->inputs_capacity = 8;
    g->inputs = (Tensor**)calloc(g->inputs_capacity, sizeof(Tensor*));
    
    g->outputs_capacity = 8;
    g->outputs = (Tensor**)calloc(g->outputs_capacity, sizeof(Tensor*));
    
    if (!g->ops || !g->tensors || !g->inputs || !g->outputs) {
        if (g->ops) free(g->ops);
        if (g->tensors) free(g->tensors);
        if (g->inputs) free(g->inputs);
        if (g->outputs) free(g->outputs);
        free(g);
        return NULL;
    }
    return g;
}

void graph_free(Graph* g) {
    if (!g) return;
    
    for (int i = 0; i < g->num_tensors; i++) {
        tensor_free(g->tensors[i]);
    }
    for (int i = 0; i < g->num_ops; i++) {
        op_free(g->ops[i]);
    }
    
    if (g->inputs) free(g->inputs);
    if (g->outputs) free(g->outputs);
    free(g->tensors);
    free(g->ops);
    free(g);
}

static bool ensure_tensor_capacity(Graph* g) {
    if (g->num_tensors < g->tensors_capacity) return true;
    int new_cap = g->tensors_capacity * 2;
    Tensor** new_arr = (Tensor**)realloc(g->tensors, new_cap * sizeof(Tensor*));
    if (!new_arr) return false;
    g->tensors = new_arr;
    g->tensors_capacity = new_cap;
    return true;
}

static bool ensure_op_capacity(Graph* g) {
    if (g->num_ops < g->ops_capacity) return true;
    int new_cap = g->ops_capacity * 2;
    Op** new_arr = (Op**)realloc(g->ops, new_cap * sizeof(Op*));
    if (!new_arr) return false;
    g->ops = new_arr;
    g->ops_capacity = new_cap;
    return true;
}

int graph_add_tensor(Graph* g, Tensor* t) {
    if (!g || !t || !ensure_tensor_capacity(g)) return -1;
    t->id = g->num_tensors;
    g->tensors[g->num_tensors++] = t;
    return t->id;
}

int graph_add_op(Graph* g, Op* op) {
    if (!g || !op || !ensure_op_capacity(g)) return -1;
    op->id = g->num_ops;
    g->ops[g->num_ops++] = op;
    g->is_sorted = false;
    return op->id;
}

bool graph_set_input(Graph* g, int tensor_id) {
    if (!g || tensor_id < 0 || tensor_id >= g->num_tensors) return false;
    
    if (g->num_inputs >= g->inputs_capacity) {
        int new_cap = g->inputs_capacity * 2;
        Tensor** new_arr = (Tensor**)realloc(g->inputs, new_cap * sizeof(Tensor*));
        if (!new_arr) return false;
        g->inputs = new_arr;
        g->inputs_capacity = new_cap;
    }
    
    g->inputs[g->num_inputs++] = g->tensors[tensor_id];
    g->tensors[tensor_id]->is_input = true;
    return true;
}

bool graph_set_output(Graph* g, int tensor_id) {
    if (!g || tensor_id < 0 || tensor_id >= g->num_tensors) return false;
    
    if (g->num_outputs >= g->outputs_capacity) {
        int new_cap = g->outputs_capacity * 2;
        Tensor** new_arr = (Tensor**)realloc(g->outputs, new_cap * sizeof(Tensor*));
        if (!new_arr) return false;
        g->outputs = new_arr;
        g->outputs_capacity = new_cap;
    }
    
    g->outputs[g->num_outputs++] = g->tensors[tensor_id];
    g->tensors[tensor_id]->is_output = true;
    return true;
}

Tensor* graph_find_tensor(Graph* g, const char* name) {
    if (!g || !name) return NULL;
    for (int i = 0; i < g->num_tensors; i++) {
        if (strcmp(g->tensors[i]->name, name) == 0) {
            return g->tensors[i];
        }
    }
    return NULL;
}

Tensor* graph_get_tensor(Graph* g, int id) {
    if (!g || id < 0 || id >= g->num_tensors) return NULL;
    return g->tensors[id];
}

Op* graph_get_op(Graph* g, int id) {
    if (!g || id < 0 || id >= g->num_ops) return NULL;
    return g->ops[id];
}

Op* graph_get_producer(Graph* g, Tensor* t) {
    if (!g || !t) return NULL;
    for (int i = 0; i < g->num_ops; i++) {
        Op* op = g->ops[i];
        for (int j = 0; j < op->num_outputs; j++) {
            if (op->outputs[j] == t) return op;
        }
    }
    return NULL;
}

// Topological sort using DFS
typedef enum { WHITE, GRAY, BLACK } VisitState;

static bool topo_visit(Graph* g, int op_idx, VisitState* state, Op** sorted, int* count) {
    if (state[op_idx] == BLACK) return true;
    if (state[op_idx] == GRAY) return false; // Cycle detected
    
    state[op_idx] = GRAY;
    Op* op = g->ops[op_idx];
    
    // Visit producers of inputs
    for (int i = 0; i < op->num_inputs; i++) {
        Op* producer = graph_get_producer(g, op->inputs[i]);
        if (producer) {
            if (!topo_visit(g, producer->id, state, sorted, count)) {
                return false;
            }
        }
    }
    
    state[op_idx] = BLACK;
    sorted[(*count)++] = op;
    return true;
}

NnccError graph_topological_sort(Graph* g) {
    if (!g || g->num_ops == 0) return NNCC_OK;
    if (g->is_sorted) return NNCC_OK;
    
    VisitState* state = (VisitState*)calloc(g->num_ops, sizeof(VisitState));
    Op** sorted = (Op**)calloc(g->num_ops, sizeof(Op*));
    int count = 0;
    
    if (!state || !sorted) {
        free(state);
        free(sorted);
        return NNCC_ERROR_OUT_OF_MEMORY;
    }
    
    for (int i = 0; i < g->num_ops; i++) {
        if (state[i] == WHITE) {
            if (!topo_visit(g, i, state, sorted, &count)) {
                free(state);
                free(sorted);
                return NNCC_ERROR_INTERNAL; // Cycle
            }
        }
    }
    
    // Replace ops array with sorted order
    for (int i = 0; i < g->num_ops; i++) {
        g->ops[i] = sorted[i];
        g->ops[i]->id = i;
    }
    
    free(state);
    free(sorted);
    g->is_sorted = true;
    return NNCC_OK;
}

void graph_print(const Graph* g) {
    if (!g) {
        printf("Graph: (null)\n");
        return;
    }
    
    printf("Graph '%s':\n", g->name);
    printf("  Tensors: %d\n", g->num_tensors);
    printf("  Ops: %d\n", g->num_ops);
    printf("  Inputs: %d, Outputs: %d\n", g->num_inputs, g->num_outputs);
    
    printf("\nOperations:\n");
    for (int i = 0; i < g->num_ops; i++) {
        Op* op = g->ops[i];
        printf("  [%d] %s (%s)\n", i, op->name, op_type_name(op->type));
    }
}
