#ifndef ITRIGAMMA_H
#define ITRIGAMMA_H

#include <stddef.h>

double pos_trigamma(double x);
double pos_tetragamma(double x);
double itrigamma(double y);

/* array-level versions for each */
void pos_trigamma_vec(const double *x, double *out, size_t n);
void pos_tetragamma_vec(const double *x, double *out, size_t n);
void itrigamma_vec(const double *y, double *out, size_t n);

#endif

