/*
 * SudoDog Exec Blocker - LD_PRELOAD library for pre-execution command blocking
 *
 * This library intercepts exec* and system() calls to block dangerous commands
 * before they execute. It reads blocked patterns from SUDODOG_BLOCKED_PATTERNS
 * environment variable.
 *
 * Compile: gcc -shared -fPIC -o libexec_blocker.so exec_blocker.c -ldl
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dlfcn.h>
#include <unistd.h>
#include <errno.h>
#include <fnmatch.h>
#include <stdarg.h>

/* Maximum number of blocked patterns */
#define MAX_PATTERNS 100
#define MAX_PATTERN_LEN 256
#define MAX_CMD_LEN 4096

/* Blocked patterns loaded from environment */
static char blocked_patterns[MAX_PATTERNS][MAX_PATTERN_LEN];
static int num_patterns = 0;
static int initialized = 0;
static int debug_mode = 0;

/* Log file for blocked commands */
static const char* BLOCK_LOG_ENV = "SUDODOG_BLOCK_LOG";
static const char* PATTERNS_ENV = "SUDODOG_BLOCKED_PATTERNS";
static const char* DEBUG_ENV = "SUDODOG_EXEC_DEBUG";

/* Original function pointers */
static int (*real_execve)(const char*, char* const[], char* const[]) = NULL;
static int (*real_execvp)(const char*, char* const[]) = NULL;
static int (*real_execv)(const char*, char* const[]) = NULL;
static int (*real_system)(const char*) = NULL;
static FILE* (*real_popen)(const char*, const char*) = NULL;
static int (*real_execl)(const char*, const char*, ...) = NULL;
static int (*real_execlp)(const char*, const char*, ...) = NULL;

/* Dangerous command patterns - built-in defaults */
static const char* DEFAULT_PATTERNS[] = {
    /* Destructive file operations */
    "*rm -rf /*",
    "*rm -fr /*",
    "*rm --recursive --force /*",
    "*rm -rf ~*",
    "*rm -rf .*",
    "rm -rf *",

    /* Pipe to shell - code injection */
    "*curl*|*bash*",
    "*curl*|*sh*",
    "*wget*|*bash*",
    "*wget*|*sh*",
    "*curl*| bash*",
    "*curl*| sh*",
    "*wget*| bash*",
    "*wget*| sh*",

    /* Reverse shells */
    "*nc -e*",
    "*nc*-e */bin/*",
    "*ncat -e*",
    "*bash -i*>&*/dev/tcp/*",
    "*python*-c*import socket*",
    "*perl*-e*socket*",
    "*ruby*-rsocket*",
    "*php*-r*fsockopen*",

    /* Privilege escalation */
    "*chmod 777 /etc/*",
    "*chmod 666 /etc/*",
    "*chmod +s*",
    "*chown root*",

    /* Credential theft */
    "*cat /etc/shadow*",
    "*cat /etc/passwd*",
    "*cat*/.ssh/id_*",
    "*cat*/.aws/credentials*",
    "*cat*/.env*",

    /* Fork bombs */
    "*:(){ :|:& };:*",
    "*fork bomb*",

    /* Disk wiping */
    "*dd if=/dev/zero of=/dev/*",
    "*dd if=/dev/random of=/dev/*",
    "*mkfs*",

    /* Cron/persistence */
    "*crontab*curl*",
    "*crontab*wget*",

    NULL  /* Sentinel */
};

/* Initialize the blocker - load patterns from environment */
static void init_blocker(void) {
    if (initialized) return;
    initialized = 1;

    /* Check debug mode */
    const char* debug = getenv(DEBUG_ENV);
    debug_mode = (debug != NULL && strcmp(debug, "1") == 0);

    /* Load real functions */
    real_execve = dlsym(RTLD_NEXT, "execve");
    real_execvp = dlsym(RTLD_NEXT, "execvp");
    real_execv = dlsym(RTLD_NEXT, "execv");
    real_system = dlsym(RTLD_NEXT, "system");
    real_popen = dlsym(RTLD_NEXT, "popen");
    real_execl = dlsym(RTLD_NEXT, "execl");
    real_execlp = dlsym(RTLD_NEXT, "execlp");

    /* Load default patterns */
    for (int i = 0; DEFAULT_PATTERNS[i] != NULL && num_patterns < MAX_PATTERNS; i++) {
        strncpy(blocked_patterns[num_patterns], DEFAULT_PATTERNS[i], MAX_PATTERN_LEN - 1);
        blocked_patterns[num_patterns][MAX_PATTERN_LEN - 1] = '\0';
        num_patterns++;
    }

    /* Load additional patterns from environment */
    const char* env_patterns = getenv(PATTERNS_ENV);
    if (env_patterns != NULL) {
        char* patterns_copy = strdup(env_patterns);
        if (patterns_copy != NULL) {
            char* pattern = strtok(patterns_copy, ";");
            while (pattern != NULL && num_patterns < MAX_PATTERNS) {
                /* Skip empty patterns */
                while (*pattern == ' ') pattern++;
                if (*pattern != '\0') {
                    strncpy(blocked_patterns[num_patterns], pattern, MAX_PATTERN_LEN - 1);
                    blocked_patterns[num_patterns][MAX_PATTERN_LEN - 1] = '\0';
                    num_patterns++;
                }
                pattern = strtok(NULL, ";");
            }
            free(patterns_copy);
        }
    }

    if (debug_mode) {
        fprintf(stderr, "[SudoDog] Exec blocker initialized with %d patterns\n", num_patterns);
    }
}

/* Log a blocked command */
static void log_blocked(const char* command, const char* matched_pattern) {
    const char* log_path = getenv(BLOCK_LOG_ENV);

    /* Always print to stderr */
    fprintf(stderr, "\n\033[1;31m🛑 BLOCKED BY SUDODOG GUARDRAILS\033[0m\n");
    fprintf(stderr, "   Command: %s\n", command);
    fprintf(stderr, "   Pattern: %s\n", matched_pattern);
    fprintf(stderr, "   Action:  Execution prevented\n\n");

    /* Also log to file if specified */
    if (log_path != NULL) {
        FILE* f = fopen(log_path, "a");
        if (f != NULL) {
            fprintf(f, "BLOCKED|%s|%s\n", command, matched_pattern);
            fclose(f);
        }
    }
}

/* Check if a command matches any blocked pattern */
static int is_blocked(const char* command, const char** matched_pattern) {
    if (command == NULL || *command == '\0') {
        return 0;
    }

    init_blocker();

    for (int i = 0; i < num_patterns; i++) {
        if (fnmatch(blocked_patterns[i], command, FNM_CASEFOLD) == 0) {
            *matched_pattern = blocked_patterns[i];
            return 1;
        }
    }

    /* Also check for specific dangerous substrings */
    const char* dangerous_substrings[] = {
        "| bash", "|bash", "| sh", "|sh",
        "; rm -rf", ";rm -rf",
        "&& rm -rf", "&&rm -rf",
        "/dev/tcp/", "/dev/udp/",
        ">(", ")<", /* Process substitution for data exfil */
        NULL
    };

    for (int i = 0; dangerous_substrings[i] != NULL; i++) {
        if (strstr(command, dangerous_substrings[i]) != NULL) {
            *matched_pattern = dangerous_substrings[i];
            return 1;
        }
    }

    return 0;
}

/* Build command string from argv */
static void build_command_str(char* buffer, size_t bufsize, const char* file, char* const argv[]) {
    size_t pos = 0;

    if (file != NULL) {
        size_t len = strlen(file);
        if (pos + len + 1 < bufsize) {
            strcpy(buffer + pos, file);
            pos += len;
            buffer[pos++] = ' ';
        }
    }

    if (argv != NULL) {
        for (int i = 0; argv[i] != NULL && pos < bufsize - 1; i++) {
            size_t len = strlen(argv[i]);
            if (pos + len + 1 < bufsize) {
                strcpy(buffer + pos, argv[i]);
                pos += len;
                buffer[pos++] = ' ';
            }
        }
    }

    if (pos > 0) pos--;  /* Remove trailing space */
    buffer[pos] = '\0';
}

/* Intercepted execve */
int execve(const char* pathname, char* const argv[], char* const envp[]) {
    init_blocker();

    char cmd[MAX_CMD_LEN];
    build_command_str(cmd, sizeof(cmd), pathname, argv);

    const char* matched = NULL;
    if (is_blocked(cmd, &matched)) {
        log_blocked(cmd, matched);
        errno = EPERM;
        return -1;
    }

    if (debug_mode) {
        fprintf(stderr, "[SudoDog] execve allowed: %s\n", cmd);
    }

    return real_execve(pathname, argv, envp);
}

/* Intercepted execvp */
int execvp(const char* file, char* const argv[]) {
    init_blocker();

    char cmd[MAX_CMD_LEN];
    build_command_str(cmd, sizeof(cmd), file, argv);

    const char* matched = NULL;
    if (is_blocked(cmd, &matched)) {
        log_blocked(cmd, matched);
        errno = EPERM;
        return -1;
    }

    if (debug_mode) {
        fprintf(stderr, "[SudoDog] execvp allowed: %s\n", cmd);
    }

    return real_execvp(file, argv);
}

/* Intercepted execv */
int execv(const char* pathname, char* const argv[]) {
    init_blocker();

    char cmd[MAX_CMD_LEN];
    build_command_str(cmd, sizeof(cmd), pathname, argv);

    const char* matched = NULL;
    if (is_blocked(cmd, &matched)) {
        log_blocked(cmd, matched);
        errno = EPERM;
        return -1;
    }

    if (debug_mode) {
        fprintf(stderr, "[SudoDog] execv allowed: %s\n", cmd);
    }

    return real_execv(pathname, argv);
}

/* Intercepted system() - most commonly used for shell commands */
int system(const char* command) {
    init_blocker();

    if (command == NULL) {
        return real_system(command);
    }

    const char* matched = NULL;
    if (is_blocked(command, &matched)) {
        log_blocked(command, matched);
        errno = EPERM;
        return -1;
    }

    if (debug_mode) {
        fprintf(stderr, "[SudoDog] system() allowed: %s\n", command);
    }

    return real_system(command);
}

/* Intercepted popen() */
FILE* popen(const char* command, const char* type) {
    init_blocker();

    if (command == NULL) {
        return real_popen(command, type);
    }

    const char* matched = NULL;
    if (is_blocked(command, &matched)) {
        log_blocked(command, matched);
        errno = EPERM;
        return NULL;
    }

    if (debug_mode) {
        fprintf(stderr, "[SudoDog] popen() allowed: %s\n", command);
    }

    return real_popen(command, type);
}

/* Constructor - runs when library is loaded */
__attribute__((constructor))
static void blocker_init(void) {
    init_blocker();
    if (debug_mode) {
        fprintf(stderr, "[SudoDog] Exec blocker library loaded\n");
    }
}
