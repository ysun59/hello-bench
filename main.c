#include <stdio.h>
#include <sys/time.h>
//int main(int argc, char *argv[]) {
int main() {
    struct timeval tv;
    gettimeofday(&tv,NULL);
    printf("{\"entrypointTime\": %ld }\n", tv.tv_sec*1000 + tv.tv_usec/1000);
    printf("hello docker\n");
}
