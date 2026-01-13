#include "jonesum.h"
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>

struct jonesum_context {
    char** vocabulary;
    size_t* indices;
    size_t vocabulary_count;
    size_t current_index;
};

static int rand_int(int min, int max) {
    if (min >= max) {
        return min;
    }
    return min + (rand() % (max - min + 1));
}

static void shuffle_array(size_t* array, size_t length) {
    if (array == NULL || length < 2) {
        return;
    }
    for (size_t i = length - 1; i > 0; i--) {
        size_t j = rand() % (i + 1);
        size_t temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
}

jonesum_context_t* jonesum_init(const char** vocabulary, size_t vocabulary_count) {
    if (vocabulary == NULL || vocabulary_count == 0) {
        return NULL;
    }

    static int is_seeded = 0;
    if (!is_seeded) {
        srand((unsigned int)time(NULL));
        is_seeded = 1;
    }

    jonesum_context_t* ctx = (jonesum_context_t*)malloc(sizeof(jonesum_context_t));
    if (ctx == NULL) {
        return NULL;
    }

    ctx->vocabulary_count = vocabulary_count;
    ctx->current_index = 0;

    ctx->vocabulary = (char**)malloc(sizeof(char*) * vocabulary_count);
    if (ctx->vocabulary == NULL) {
        free(ctx);
        return NULL;
    }

    ctx->indices = (size_t*)malloc(sizeof(size_t) * vocabulary_count);
    if (ctx->indices == NULL) {
        free(ctx->vocabulary);
        free(ctx);
        return NULL;
    }

    for (size_t i = 0; i < vocabulary_count; i++) {
        size_t len = strlen(vocabulary[i]);
        ctx->vocabulary[i] = (char*)malloc(len + 1);
        if (ctx->vocabulary[i] == NULL) {
            for (size_t j = 0; j < i; j++) {
                free(ctx->vocabulary[j]);
            }
            free(ctx->vocabulary);
            free(ctx->indices);
            free(ctx);
            return NULL;
        }
        strcpy(ctx->vocabulary[i], vocabulary[i]);
        ctx->indices[i] = i;
    }

    shuffle_array(ctx->indices, vocabulary_count);

    return ctx;
}

void jonesum_free(jonesum_context_t* ctx) {
    if (ctx == NULL) {
        return;
    }

    if (ctx->vocabulary != NULL) {
        for (size_t i = 0; i < ctx->vocabulary_count; i++) {
            free(ctx->vocabulary[i]);
        }
        free(ctx->vocabulary);
    }

    if (ctx->indices != NULL) {
        free(ctx->indices);
    }

    free(ctx);
}

static char* capitalize_first(const char* str) {
    if (str == NULL || strlen(str) == 0) {
        return NULL;
    }

    size_t len = strlen(str);
    char* result = (char*)malloc(len + 1);
    if (result == NULL) {
        return NULL;
    }

    strcpy(result, str);
    result[0] = (char)toupper((unsigned char)result[0]);

    return result;
}

char* jonesum_pontificate(jonesum_context_t* ctx) {
    if (ctx == NULL || ctx->vocabulary == NULL || ctx->vocabulary_count == 0) {
        return NULL;
    }

    int count = rand_int(4, 8);
    if (count > (int)ctx->vocabulary_count) {
        count = (int)ctx->vocabulary_count;
    }
    // Be explicit for the compiler: we will always select at least one token.
    if (count <= 0) {
        return NULL;
    }

    if (ctx->current_index + count > ctx->vocabulary_count) {
        ctx->current_index = 0;
        shuffle_array(ctx->indices, ctx->vocabulary_count);
    }

    size_t total_length = 0;
    // calloc() ensures selected[i] starts NULL; this avoids "maybe-uninitialized"
    // warnings from GCC and makes cleanup paths safer.
    char** selected = (char**)calloc((size_t)count, sizeof(char*));
    int* allocated = (int*)calloc((size_t)count, sizeof(int));
    if (selected == NULL || allocated == NULL) {
        if (selected != NULL) {
            free(selected);
        }
        if (allocated != NULL) {
            free(allocated);
        }
        return NULL;
    }

    for (int i = 0; i < count; i++) {
        size_t idx = ctx->indices[ctx->current_index];
        ctx->current_index++;
        selected[i] = ctx->vocabulary[idx];
        total_length += strlen(selected[i]);
        allocated[i] = 0;
    }

    if (rand_int(1, 2) > 1 && count > 3) {
        int punctuation_index = rand_int(0, count - 3);
        size_t old_len = strlen(selected[punctuation_index]);
        char* new_str = (char*)malloc(old_len + 2);
        if (new_str != NULL) {
            strcpy(new_str, selected[punctuation_index]);
            strcat(new_str, ",");
            selected[punctuation_index] = new_str;
            allocated[punctuation_index] = 1;
            total_length += 1;
        }
    }

    // selected[0] is guaranteed non-NULL here because count > 0 and we filled it above.
    char* first_capitalized = capitalize_first(selected[0]);
    if (first_capitalized == NULL) {
        for (int i = 0; i < count; i++) {
            if (allocated[i]) {
                free(selected[i]);
            }
        }
        free(selected);
        free(allocated);
        return NULL;
    }
    if (allocated[0]) {
        free(selected[0]);
    }
    selected[0] = first_capitalized;
    allocated[0] = 1;

    const char* sep = " ";
    const char* end = ".";
    total_length += (strlen(sep) * (count - 1)) + strlen(end);

    char* result = (char*)malloc(total_length + 1);
    if (result == NULL) {
        for (int i = 0; i < count; i++) {
            if (allocated[i]) {
                free(selected[i]);
            }
        }
        free(selected);
        free(allocated);
        return NULL;
    }

    result[0] = '\0';
    strcpy(result, selected[0]);

    for (int i = 1; i < count; i++) {
        strcat(result, sep);
        strcat(result, selected[i]);
    }

    strcat(result, end);

    for (int i = 0; i < count; i++) {
        if (allocated[i]) {
            free(selected[i]);
        }
    }
    free(selected);
    free(allocated);
    return result;
}

char* jonesum_rant(jonesum_context_t* ctx, int count) {
    if (ctx == NULL) {
        return NULL;
    }

    if (count <= 0) {
        count = rand_int(4, 8);
    }
    // Be explicit for the compiler: we will always generate at least one sentence.
    if (count <= 0) {
        return NULL;
    }

    int angry_index = rand_int(0, count - 1);
    size_t total_length = 0;
    // calloc() avoids "maybe-uninitialized" warnings and makes cleanup paths safer.
    char** sentences = (char**)calloc((size_t)count, sizeof(char*));
    if (sentences == NULL) {
        return NULL;
    }

    for (int i = 0; i < count; i++) {
        char* sentence = jonesum_pontificate(ctx);
        if (sentence == NULL) {
            for (int j = 0; j < i; j++) {
                free(sentences[j]);
            }
            free(sentences);
            return NULL;
        }

        if (i == angry_index && rand_int(1, 4) > 3) {
            size_t len = strlen(sentence);
            for (size_t k = 0; k < len; k++) {
                sentence[k] = (char)toupper((unsigned char)sentence[k]);
            }

            size_t end_len = strlen(sentence);
            if (end_len > 0 && sentence[end_len - 1] == '.') {
                sentence[end_len - 1] = '!';
            }
        }

        sentences[i] = sentence;
        total_length += strlen(sentence) + 1;
    }

    char* result = (char*)malloc(total_length + 1);
    if (result == NULL) {
        for (int i = 0; i < count; i++) {
            free(sentences[i]);
        }
        free(sentences);
        return NULL;
    }

    result[0] = '\0';
    strcpy(result, sentences[0]);

    for (int i = 1; i < count; i++) {
        strcat(result, " ");
        strcat(result, sentences[i]);
    }

    for (int i = 0; i < count; i++) {
        free(sentences[i]);
    }
    free(sentences);

    return result;
}
