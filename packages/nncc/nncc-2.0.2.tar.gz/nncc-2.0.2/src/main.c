/*
 * main.c - nncc CLI entry point
 * 
 * Usage: nncc <model.safetensors> <model.nnmodel> -o <output.c>
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#include "model.h"
#include "loader.h"
#include "codegen.h"

#define NNCC_VERSION "2.0.0"

/* ============================================================================
 * CLI Parsing
 * ========================================================================== */

typedef struct {
    const char* safetensors_path;
    const char* nnmodel_path;
    const char* output_path;
    const char* model_name;
    bool verbose;
    bool help;
    bool version;
} CliArgs;

static void print_usage(const char* prog) {
    printf("nncc v%s - Neural Network to C Compiler\n\n", NNCC_VERSION);
    printf("Usage: %s <model.safetensors> <model.nnmodel> -o <output.c> [options]\n\n", prog);
    printf("Arguments:\n");
    printf("  <model.safetensors>  Path to SafeTensors weights file\n");
    printf("  <model.nnmodel>      Path to model architecture JSON file\n");
    printf("  -o <output.c>        Output C file path\n\n");
    printf("Options:\n");
    printf("  -n, --name <name>    Model name prefix (default: 'model')\n");
    printf("  -v, --verbose        Verbose output\n");
    printf("  -h, --help           Show this help\n");
    printf("  --version            Show version\n\n");
    printf("Example:\n");
    printf("  %s mnist.safetensors mnist.nnmodel -o mnist.c\n", prog);
}

static bool parse_args(int argc, char** argv, CliArgs* args) {
    memset(args, 0, sizeof(CliArgs));
    args->model_name = "model";
    
    if (argc < 2) return false;
    
    int positional = 0;
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            args->help = true;
            return true;
        } else if (strcmp(argv[i], "--version") == 0) {
            args->version = true;
            return true;
        } else if (strcmp(argv[i], "-v") == 0 || strcmp(argv[i], "--verbose") == 0) {
            args->verbose = true;
        } else if (strcmp(argv[i], "-o") == 0 && i + 1 < argc) {
            args->output_path = argv[++i];
        } else if ((strcmp(argv[i], "-n") == 0 || strcmp(argv[i], "--name") == 0) && i + 1 < argc) {
            args->model_name = argv[++i];
        } else if (argv[i][0] != '-') {
            if (positional == 0) {
                args->safetensors_path = argv[i];
            } else if (positional == 1) {
                args->nnmodel_path = argv[i];
            }
            positional++;
        }
    }
    
    return args->safetensors_path && args->nnmodel_path && args->output_path;
}

/* ============================================================================
 * Main
 * ========================================================================== */

int main(int argc, char** argv) {
    CliArgs args;
    
    if (!parse_args(argc, argv, &args)) {
        if (args.help) {
            print_usage(argv[0]);
            return 0;
        }
        if (args.version) {
            printf("nncc v%s\n", NNCC_VERSION);
            return 0;
        }
        fprintf(stderr, "Error: Missing required arguments\n\n");
        print_usage(argv[0]);
        return 1;
    }
    
    if (args.help) {
        print_usage(argv[0]);
        return 0;
    }
    
    if (args.version) {
        printf("nncc v%s\n", NNCC_VERSION);
        return 0;
    }
    
    if (args.verbose) {
        printf("Loading model architecture from: %s\n", args.nnmodel_path);
        printf("Loading weights from: %s\n", args.safetensors_path);
    }
    
    /* Load model */
    Graph* graph = NULL;
    NnccError err = model_load(args.nnmodel_path, args.safetensors_path, &graph);
    
    if (err != NNCC_OK) {
        const char* msg = "Unknown error";
        switch (err) {
            case NNCC_ERROR_FILE_NOT_FOUND: msg = "File not found"; break;
            case NNCC_ERROR_INVALID_FORMAT: msg = "Invalid file format"; break;
            case NNCC_ERROR_OUT_OF_MEMORY: msg = "Out of memory"; break;
            case NNCC_ERROR_IO: msg = "I/O error"; break;
            default: break;
        }
        fprintf(stderr, "Error loading model: %s\n", msg);
        return 1;
    }
    
    if (args.verbose) {
        printf("\nModel loaded:\n");
        graph_print(graph);
        printf("\n");
    }
    
    /* Generate C code */
    CodegenConfig config;
    codegen_config_init(&config);
    config.output_path = args.output_path;
    config.model_name = args.model_name;
    
    err = codegen_generate(graph, &config);
    
    if (err != NNCC_OK) {
        fprintf(stderr, "Error generating code\n");
        graph_free(graph);
        return 1;
    }
    
    if (args.verbose) {
        printf("Generated: %s\n", args.output_path);
    } else {
        printf("nncc: %s -> %s\n", args.nnmodel_path, args.output_path);
    }
    
    graph_free(graph);
    return 0;
}
