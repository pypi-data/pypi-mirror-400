#ifndef JONESUM_H
#define JONESUM_H

#include <stddef.h>

typedef struct jonesum_context jonesum_context_t;

#ifdef __cplusplus
extern "C" {
#endif

jonesum_context_t* jonesum_init(const char** vocabulary, size_t vocabulary_count);
void jonesum_free(jonesum_context_t* ctx);

// Generates a single sentence (uses spaces between tokens and ends with a period).
// Intended to be used internally by jonesum_rant().
char* jonesum_pontificate(jonesum_context_t* ctx);

// Generates a rant by concatenating multiple sentences produced by jonesum_pontificate().
char* jonesum_rant(jonesum_context_t* ctx, int count);

#ifdef __cplusplus
}  // extern "C"
#endif

#endif
