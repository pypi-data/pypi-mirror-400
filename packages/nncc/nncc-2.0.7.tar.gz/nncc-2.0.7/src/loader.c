// loader.c - Model and weights loader implementation
// 
// Parses .nnmodel JSON and .safetensors files

#include "loader.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

// Simple JSON Parser (minimal, for .nnmodel format only)

typedef struct {
    const char* src;
    size_t len;
    size_t pos;
    char error[256];
} JsonParser;

static void json_skip_ws(JsonParser* p) {
    while (p->pos < p->len && isspace((unsigned char)p->src[p->pos])) {
        p->pos++;
    }
}

static bool json_match(JsonParser* p, char c) {
    json_skip_ws(p);
    if (p->pos < p->len && p->src[p->pos] == c) {
        p->pos++;
        return true;
    }
    return false;
}

static char* json_parse_string(JsonParser* p) {
    json_skip_ws(p);
    if (p->pos >= p->len || p->src[p->pos] != '"') return NULL;
    p->pos++;
    
    size_t start = p->pos;
    while (p->pos < p->len && p->src[p->pos] != '"') {
        if (p->src[p->pos] == '\\') p->pos++; /* Skip escaped char */
        p->pos++;
    }
    
    size_t len = p->pos - start;
    if (p->pos >= p->len) return NULL;
    
    char* str = (char*)malloc(len + 1);
    if (!str) return NULL;
    memcpy(str, p->src + start, len);
    str[len] = '\0';
    
    p->pos++; /* Skip closing quote */
    return str;
}

static double json_parse_number(JsonParser* p) {
    json_skip_ws(p);
    char* end;
    double val = strtod(p->src + p->pos, &end);
    p->pos = end - p->src;
    return val;
}

static int json_parse_int(JsonParser* p) {
    return (int)json_parse_number(p);
}

// File Reading

static char* read_file(const char* path, size_t* out_size) {
    FILE* f = fopen(path, "rb");
    if (!f) return NULL;
    
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);
    
    if (size <= 0) { fclose(f); return NULL; }
    
    char* data = (char*)malloc(size + 1);
    if (!data) { fclose(f); return NULL; }
    
    size_t read = fread(data, 1, size, f);
    fclose(f);
    
    if ((long)read != size) { free(data); return NULL; }
    
    data[size] = '\0';
    *out_size = size;
    return data;
}

// SafeTensors Parser

static DataType parse_dtype(const char* s) {
    if (!s) return DTYPE_FLOAT32;
    if (strcmp(s, "F32") == 0 || strcmp(s, "float32") == 0) return DTYPE_FLOAT32;
    if (strcmp(s, "F16") == 0 || strcmp(s, "float16") == 0) return DTYPE_FLOAT16;
    if (strcmp(s, "I32") == 0 || strcmp(s, "int32") == 0) return DTYPE_INT32;
    if (strcmp(s, "I8") == 0 || strcmp(s, "int8") == 0) return DTYPE_INT8;
    if (strcmp(s, "U8") == 0 || strcmp(s, "uint8") == 0) return DTYPE_UINT8;
    return DTYPE_FLOAT32;
}



NnccError safetensors_parse(const void* data_ptr, size_t data_len, Graph* graph) {
    if (!data_ptr || !graph) return NNCC_ERROR_INTERNAL;
    
    const char* file_data = (const char*)data_ptr;
    size_t file_size = data_len;
    
    // Read header size (first 8 bytes, little-endian)
    if (file_size < 8) { return NNCC_ERROR_INVALID_FORMAT; }
    
    uint64_t header_size = 0;
    for (int i = 0; i < 8; i++) {
        header_size |= ((uint64_t)(unsigned char)file_data[i]) << (i * 8);
    }
    
    if (8 + header_size > file_size) { return NNCC_ERROR_INVALID_FORMAT; }
    
    size_t data_start = 8 + (size_t)header_size;
    
    // Parse JSON header to find tensor offsets
    JsonParser parser = { .src = file_data + 8, .len = (size_t)header_size, .pos = 0 };
    
    if (!json_match(&parser, '{')) { return NNCC_ERROR_INVALID_FORMAT; }
    
    while (parser.pos < parser.len) {
        char* key = json_parse_string(&parser);
        if (!key) break;
        
        if (!json_match(&parser, ':')) { free(key); break; }
        
        // Skip __metadata__
        if (strcmp(key, "__metadata__") == 0) {
            free(key);
            // Skip the value (object or primitive)
            int depth = 0;
            do {
                if (parser.src[parser.pos] == '{' || parser.src[parser.pos] == '[') depth++;
                else if (parser.src[parser.pos] == '}' || parser.src[parser.pos] == ']') depth--;
                parser.pos++;
            } while (depth > 0 && parser.pos < parser.len);
            json_match(&parser, ',');
            continue;
        }
        
        // Parse tensor info object
        if (!json_match(&parser, '{')) { free(key); break; }
        
        DataType dtype = DTYPE_FLOAT32;
        int* shape = NULL;
        int shape_cap = 0;
        int ndim = 0;
        size_t offset_start = 0, offset_end = 0;
        
        json_skip_ws(&parser);
        while (parser.pos < parser.len && parser.src[parser.pos] != '}') {
            char* prop = json_parse_string(&parser);
            if (!prop) break;
            
            json_match(&parser, ':');
            
            if (strcmp(prop, "dtype") == 0) {
                char* dt = json_parse_string(&parser);
                dtype = parse_dtype(dt);
                free(dt);
            } else if (strcmp(prop, "shape") == 0) {
                json_match(&parser, '[');
                json_skip_ws(&parser);
                json_skip_ws(&parser);
                while (parser.pos < parser.len && parser.src[parser.pos] != ']') {
                    if (ndim >= shape_cap) {
                        int new_cap = (shape_cap == 0) ? 4 : shape_cap * 2;
                        int* new_arr = (int*)realloc(shape, new_cap * sizeof(int));
                        if (!new_arr) { free(shape); return NNCC_ERROR_OUT_OF_MEMORY; } // Leaking key/file_data on error, but simple exit
                        shape = new_arr;
                        shape_cap = new_cap;
                    }
                    shape[ndim++] = json_parse_int(&parser);
                    json_match(&parser, ',');
                }
                json_match(&parser, ']');
            } else if (strcmp(prop, "data_offsets") == 0) {
                json_match(&parser, '[');
                offset_start = (size_t)json_parse_number(&parser);
                json_match(&parser, ',');
                offset_end = (size_t)json_parse_number(&parser);
                json_match(&parser, ']');
            }
            
            free(prop);
            json_match(&parser, ',');
        }
        json_match(&parser, '}');
        
        // Find matching tensor in graph and copy data
        Tensor* tensor = graph_find_tensor(graph, key);
        if (tensor && tensor->is_weight && !tensor->data) {
            size_t size = offset_end - offset_start;
            if (size > 0 && data_start + offset_end <= file_size) {
                tensor->data = malloc(size);
                if (tensor->data) {
                    memcpy(tensor->data, file_data + data_start + offset_start, size);
                    tensor->data_size = size;
                    tensor->owns_data = true;
                    tensor->dtype = dtype;
                    tensor->owns_data = true;
                    tensor->dtype = dtype;
                    tensor->ndim = ndim;
                    
                    // Allocate tensor dims and copy
                    if (ndim > 0) {
                        tensor->dims = (int*)malloc(ndim * sizeof(int));
                        if (tensor->dims) {
                            memcpy(tensor->dims, shape, ndim * sizeof(int));
                        }
                    } else {
                        tensor->dims = NULL;
                    }
                }
            }
        }
        
        if (shape) free(shape);
        
        free(key);
        json_match(&parser, ',');
    }
    
    return NNCC_OK;
}

NnccError safetensors_load_weights(const char* path, Graph* graph) {
    size_t size;
    char* data = read_file(path, &size);
    if (!data) return NNCC_ERROR_FILE_NOT_FOUND;
    
    NnccError err = safetensors_parse(data, size, graph);
    // Parse copies data to tensors, so we can free the file buffer
    free(data);
    return err;
}

// .nnmodel JSON Parser

static OpType parse_op_type(const char* s) {
    if (!s) return OP_UNKNOWN;
    if (strcmp(s, "gemm") == 0 || strcmp(s, "linear") == 0) return OP_GEMM;
    if (strcmp(s, "matmul") == 0) return OP_MATMUL;
    if (strcmp(s, "conv2d") == 0 || strcmp(s, "conv") == 0) return OP_CONV2D;
    if (strcmp(s, "maxpool2d") == 0 || strcmp(s, "maxpool") == 0) return OP_MAXPOOL2D;
    if (strcmp(s, "avgpool2d") == 0 || strcmp(s, "avgpool") == 0) return OP_AVGPOOL2D;
    if (strcmp(s, "global_avgpool") == 0 || strcmp(s, "adaptiveavgpool2d") == 0) return OP_GLOBAL_AVGPOOL;
    if (strcmp(s, "relu") == 0) return OP_RELU;
    if (strcmp(s, "relu6") == 0) return OP_RELU6;
    if (strcmp(s, "sigmoid") == 0) return OP_SIGMOID;
    if (strcmp(s, "tanh") == 0) return OP_TANH;
    if (strcmp(s, "softmax") == 0) return OP_SOFTMAX;
    if (strcmp(s, "leaky_relu") == 0) return OP_LEAKY_RELU;
    if (strcmp(s, "batchnorm") == 0 || strcmp(s, "batchnorm2d") == 0) return OP_BATCHNORM;
    if (strcmp(s, "add") == 0) return OP_ADD;
    if (strcmp(s, "mul") == 0) return OP_MUL;
    if (strcmp(s, "flatten") == 0) return OP_FLATTEN;
    if (strcmp(s, "reshape") == 0) return OP_RESHAPE;
    if (strcmp(s, "dropout") == 0) return OP_DROPOUT;
    return OP_UNKNOWN;
}

// Helper to skip a JSON value (string, number, object, or array)
static void json_skip_value(JsonParser* p) {
    json_skip_ws(p);
    char c = p->src[p->pos];
    
    if (c == '"') {
        // String
        char* s = json_parse_string(p);
        free(s);
    } else if (c == '{' || c == '[') {
        // Object or array - skip balanced brackets
        char open = c, close = (c == '{') ? '}' : ']';
        int depth = 1;
        p->pos++;
        while (p->pos < p->len && depth > 0) {
            c = p->src[p->pos];
            if (c == '"') {
                p->pos++;
                while (p->pos < p->len && p->src[p->pos] != '"') {
                    if (p->src[p->pos] == '\\') p->pos++;
                    p->pos++;
                }
            } else if (c == open) {
                depth++;
            } else if (c == close) {
                depth--;
            }
            p->pos++;
        }
    } else {
        // Number, true, false, null
        while (p->pos < p->len) {
            c = p->src[p->pos];
            if (c == ',' || c == '}' || c == ']' || isspace((unsigned char)c)) break;
            p->pos++;
        }
    }
}



NnccError nnmodel_parse(const char* json_data, size_t json_len, Graph** out_graph) {
    if (!json_data || !out_graph) return NNCC_ERROR_INTERNAL;

    JsonParser parser = { .src = json_data, .len = json_len, .pos = 0 };
    
    Graph* graph = graph_create("model");
    if (!graph) { return NNCC_ERROR_OUT_OF_MEMORY; }
    
    if (!json_match(&parser, '{')) { 
        graph_free(graph); 
        return NNCC_ERROR_INVALID_FORMAT; 
    }
    
    char** deferred_outputs = NULL;
    int deferred_outputs_cap = 0;
    int num_deferred_outputs = 0;
    
    json_skip_ws(&parser);
    while (parser.pos < parser.len && parser.src[parser.pos] != '}') {
        char* key = json_parse_string(&parser);
        if (!key) break;
        
        if (!json_match(&parser, ':')) { free(key); break; }
        
        if (strcmp(key, "name") == 0) {
            char* name = json_parse_string(&parser);
            if (name) {
                strncpy(graph->name, name, TENSOR_NAME_MAX - 1);
                free(name);
            }
        } else if (strcmp(key, "inputs") == 0) {
            // Parse input tensors array
            if (!json_match(&parser, '[')) { free(key); break; }
            
            json_skip_ws(&parser);
            while (parser.pos < parser.len && parser.src[parser.pos] != ']') {
                if (!json_match(&parser, '{')) break;
                
                char* name = NULL;
                int* shape = NULL;
                int shape_cap = 0;
                int ndim = 0;
                
                json_skip_ws(&parser);
                while (parser.pos < parser.len && parser.src[parser.pos] != '}') {
                    char* prop = json_parse_string(&parser);
                    if (!prop) break;
                    json_match(&parser, ':');
                    
                    if (strcmp(prop, "name") == 0) {
                        name = json_parse_string(&parser);
                    } else if (strcmp(prop, "shape") == 0) {
                        json_match(&parser, '[');
                        json_skip_ws(&parser);
                        while (parser.pos < parser.len && parser.src[parser.pos] != ']') {
                            if (ndim >= shape_cap) {
                                int new_cap = (shape_cap == 0) ? 4 : shape_cap * 2;
                                int* new_arr = (int*)realloc(shape, new_cap * sizeof(int));
                                if (!new_arr) {
                                    if(shape) free(shape);
                                    if(name) free(name);
                                    if(deferred_outputs) free(deferred_outputs); // Cleanup partial
                                    graph_free(graph); return NNCC_ERROR_OUT_OF_MEMORY;
                                }
                                shape = new_arr;
                                shape_cap = new_cap;
                            }
                            shape[ndim++] = json_parse_int(&parser);
                            json_match(&parser, ',');
                            json_skip_ws(&parser);
                        }
                        json_match(&parser, ']');
                    } else {
                        json_skip_value(&parser);
                    }
                    free(prop);
                    json_match(&parser, ',');
                    json_skip_ws(&parser);
                }
                json_match(&parser, '}');
                
                if (name) {
                    Tensor* t = tensor_create(name, DTYPE_FLOAT32, ndim, shape);
                    if (t) {
                        int id = graph_add_tensor(graph, t);
                        graph_set_input(graph, id);
                    }
                    free(name);
                }
                if (shape) free(shape);
                json_match(&parser, ',');
                json_skip_ws(&parser);
            }
            json_match(&parser, ']');
        } else if (strcmp(key, "layers") == 0) {
            // Parse layers array
            if (!json_match(&parser, '[')) { free(key); break; }
            
            json_skip_ws(&parser);
            while (parser.pos < parser.len && parser.src[parser.pos] != ']') {
                if (!json_match(&parser, '{')) break;
                
                char* layer_name = NULL;
                char* op_str = NULL;
                
                char** inputs = NULL;
                int inputs_cap = 0;
                int num_inputs = 0;
                
                char* weight_name = NULL;
                char* bias_name = NULL;
                
                int* output_shape = NULL;
                int output_shape_cap = 0;
                int output_ndim = 0;
                int axis = -1;
                
                json_skip_ws(&parser);
                while (parser.pos < parser.len && parser.src[parser.pos] != '}') {
                    char* prop = json_parse_string(&parser);
                    if (!prop) break;
                    json_match(&parser, ':');
                    
                    if (strcmp(prop, "name") == 0) {
                        layer_name = json_parse_string(&parser);
                    } else if (strcmp(prop, "op") == 0) {
                        op_str = json_parse_string(&parser);
                    } else if (strcmp(prop, "inputs") == 0) {
                        json_match(&parser, '[');
                        json_skip_ws(&parser);
                        while (parser.pos < parser.len && parser.src[parser.pos] != ']') {
                            if (num_inputs >= inputs_cap) {
                                int new_cap = (inputs_cap == 0) ? 4 : inputs_cap * 2;
                                char** new_arr = (char**)realloc(inputs, new_cap * sizeof(char*));
                                if (!new_arr) break; // Error handling simplified
                                inputs = new_arr;
                                inputs_cap = new_cap;
                            }
                            inputs[num_inputs++] = json_parse_string(&parser);
                            json_match(&parser, ',');
                            json_skip_ws(&parser);
                        }
                        json_match(&parser, ']');
                    } else if (strcmp(prop, "weights") == 0) {
                        json_match(&parser, '{');
                        json_skip_ws(&parser);
                        while (parser.pos < parser.len && parser.src[parser.pos] != '}') {
                            char* wprop = json_parse_string(&parser);
                            if (!wprop) break;
                            json_match(&parser, ':');
                            if (strcmp(wprop, "weight") == 0) weight_name = json_parse_string(&parser);
                            else if (strcmp(wprop, "bias") == 0) bias_name = json_parse_string(&parser);
                            else json_skip_value(&parser);
                            free(wprop);
                            json_match(&parser, ',');
                            json_skip_ws(&parser);
                        }
                        json_match(&parser, '}');
                    } else if (strcmp(prop, "output_shape") == 0) {
                        json_match(&parser, '[');
                        json_skip_ws(&parser);
                        while (parser.pos < parser.len && parser.src[parser.pos] != ']') {
                            if (output_ndim >= output_shape_cap) {
                                int new_cap = (output_shape_cap == 0) ? 4 : output_shape_cap * 2;
                                int* new_arr = (int*)realloc(output_shape, new_cap * sizeof(int));
                                if (!new_arr) break;
                                output_shape = new_arr;
                                output_shape_cap = new_cap;
                            }
                            output_shape[output_ndim++] = json_parse_int(&parser);
                            json_match(&parser, ',');
                            json_skip_ws(&parser);
                        }
                        json_match(&parser, ']');
                    } else if (strcmp(prop, "axis") == 0) {
                        axis = json_parse_int(&parser);
                    } else {
                        json_skip_value(&parser);
                    }
                    free(prop);
                    json_match(&parser, ',');
                    json_skip_ws(&parser);
                }
                json_match(&parser, '}');
                
                // Create the operation
                if (layer_name && op_str) {
                    OpType op_type = parse_op_type(op_str);
                    Op* op = op_create(op_type, layer_name);
                    
                    if (op) {
                        // Resolve inputs
                        for (int i = 0; i < num_inputs; i++) {
                            char out_name[TENSOR_NAME_MAX + 8];
                            snprintf(out_name, sizeof(out_name), "%s.out", inputs[i]);
                            Tensor* t = graph_find_tensor(graph, out_name);
                            if (!t) t = graph_find_tensor(graph, inputs[i]);
                            if (t) op_add_input(op, t);
                        }
                        
                        // Add weight tensors
                        if (weight_name) {
                            Tensor* w = graph_find_tensor(graph, weight_name);
                            if (!w) {
                                w = tensor_create(weight_name, DTYPE_FLOAT32, 0, NULL);
                                if (w) { w->is_weight = true; graph_add_tensor(graph, w); }
                            }
                            if (w) op_add_input(op, w);
                        }
                        if (bias_name) {
                            Tensor* b = graph_find_tensor(graph, bias_name);
                            if (!b) {
                                b = tensor_create(bias_name, DTYPE_FLOAT32, 0, NULL);
                                if (b) { b->is_weight = true; graph_add_tensor(graph, b); }
                            }
                            if (b) op_add_input(op, b);
                        }
                        
                        // Create output tensor
                        char out_name[TENSOR_NAME_MAX + 8];
                        snprintf(out_name, sizeof(out_name), "%s.out", layer_name);
                        Tensor* out = tensor_create(out_name, DTYPE_FLOAT32, output_ndim, output_shape);
                        if (out) {
                            graph_add_tensor(graph, out);
                            op_add_output(op, out);
                        }
                        
                        if (op_type == OP_SOFTMAX) op_set_axis(op, axis);
                        graph_add_op(graph, op);
                    }
                }
                
                // Cleanup
                free(layer_name);
                free(op_str);
                free(weight_name);
                free(bias_name);
                if (output_shape) free(output_shape);
                for (int i = 0; i < num_inputs; i++) free(inputs[i]);
                if (inputs) free(inputs);
                
                json_match(&parser, ',');
                json_skip_ws(&parser);
            }
            json_match(&parser, ']');
        } else if (strcmp(key, "outputs") == 0) {
            // Parse outputs array
            if (!json_match(&parser, '[')) { free(key); break; }
            
            json_skip_ws(&parser);
            while (parser.pos < parser.len && parser.src[parser.pos] != ']') {
                if (!json_match(&parser, '{')) break;
                
                char* name = NULL;
                json_skip_ws(&parser);
                while (parser.pos < parser.len && parser.src[parser.pos] != '}') {
                    char* prop = json_parse_string(&parser);
                    if (!prop) break;
                    json_match(&parser, ':');
                    if (strcmp(prop, "name") == 0) name = json_parse_string(&parser);
                    else json_skip_value(&parser);
                    free(prop);
                    json_match(&parser, ',');
                    json_skip_ws(&parser);
                }
                json_match(&parser, '}');
                
                if (name) {
                    if (num_deferred_outputs >= deferred_outputs_cap) {
                        int new_cap = (deferred_outputs_cap == 0) ? 8 : deferred_outputs_cap * 2;
                        char** new_arr = (char**)realloc(deferred_outputs, new_cap * sizeof(char*));
                        if (new_arr) {
                            deferred_outputs = new_arr;
                            deferred_outputs_cap = new_cap;
                            deferred_outputs[num_deferred_outputs++] = name;
                        } else {
                            free(name); 
                        }
                    } else {
                        deferred_outputs[num_deferred_outputs++] = name;
                    }
                }
                json_match(&parser, ',');
                json_skip_ws(&parser);
            }
            json_match(&parser, ']');
        } else {
            json_skip_value(&parser);
        }
        
        free(key);
        json_match(&parser, ',');
        json_skip_ws(&parser);
    }
    
    // Resolve outputs at the end
    for (int i = 0; i < num_deferred_outputs; i++) {
        char out_name[TENSOR_NAME_MAX + 8];
        snprintf(out_name, sizeof(out_name), "%s.out", deferred_outputs[i]);
        Tensor* t = graph_find_tensor(graph, out_name);
        if (!t) t = graph_find_tensor(graph, deferred_outputs[i]);
        if (t) graph_set_output(graph, t->id);
        free(deferred_outputs[i]);
    }
    if (deferred_outputs) free(deferred_outputs);
    
    
    graph_topological_sort(graph);
    *out_graph = graph;
    return NNCC_OK;
}

NnccError nnmodel_load(const char* path, Graph** out_graph) {
    size_t size;
    char* data = read_file(path, &size);
    if (!data) return NNCC_ERROR_FILE_NOT_FOUND;
    
    NnccError err = nnmodel_parse(data, size, out_graph);
    free(data);
    return err;
}

// Combined Loader

NnccError model_load(const char* nnmodel_path, const char* safetensors_path, Graph** out_graph) {
    if (!nnmodel_path || !safetensors_path || !out_graph) {
        return NNCC_ERROR_INTERNAL;
    }
    
    // Load architecture
    NnccError err = nnmodel_load(nnmodel_path, out_graph);
    if (err != NNCC_OK) return err;
    
    // Load weights
    err = safetensors_load_weights(safetensors_path, *out_graph);
    if (err != NNCC_OK) {
        graph_free(*out_graph);
        *out_graph = NULL;
        return err;
    }
    
    return NNCC_OK;
}
