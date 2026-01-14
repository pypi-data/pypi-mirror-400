#include <float.h>
#include <math.h>
#include <stddef.h>

/*
References:

- All recurrences, asymptotic expansions can be found in Abramowitz & Stegun, "Handbook of Mathematical Functions", Section 6.4
- An overview of Euler-Maclaurin summation can be found in Chapter 4 of Sedgewick & Flajolet, "An Introduction to the Analysis of Algorithms"

-----------
The variance of a random variable log(X), where X ~ chi^2(d) is pos_trigamma(d/2).

To solve

    trigamma(d/2) = V

for d requires computing the inverse trigamma function:

    d = 2*trigamma^{-1}(V)

There's not a closed-form expression, and I haven't found a dedicated inverse
trigamma implementation in numpy, scipy, etc. to call in the munctrack EB update for Consenrich.

-----------

*Recurrences*

We use exact recurrences for small x before applying asymptotic expansions for large x:

    ---digamma (psi)---
        psi(x+1) = d/dx log(gamma(x+1)) = d/dx log(x * gamma(x)) = d/dx log(x) + d/dx log(gamma(x))
        --> psi(x+1) = (1/x) + psi(x)


    ---trigamma (psi')---
        psi'(x+1) = d/dx psi(x+1) = d/dx [ (1/x) + psi(x) ] = -1/x^2 + psi'(x)
            --> psi'(x+1) = (-1/x^2) + psi'(x)
            --> psi'(x) = ( 1/x^2) + psi'(x+1)


    ---tetragamma (psi'')---
        psi''(x+1) = d/dx psi'(x+1) = d/dx [ psi'(x) - 1/x^2 ] = psi''(x) + 2/x^3
            --> psi''(x) = psi''(x+1) - 2/(x^3)


*Asymptotic expansions*

We need trigamma and its derivative (tetragamma) for Newton-Raphson:

    psi'(z) ~ 1/z + 1/(2 z^2) + 1/(6 z^3) - 1/(30 z^5) + 1/(42 z^7) - 1/(30 z^9) + 5/(66 z^11) - 691/(2730 z^13) + 7/(6 z^15) ...
    psi''(z) ~ -1/z^2 - 1/z^3 - 1/(2 z^4) + 1/(6 z^6) - 1/(6 z^8) + 3/(10 z^10) - 5/(6 z^12) + 691/(210 z^14) - 35/(2 z^16) ...


------------
*/

static const double BEGIN_ASYMPTOTIC = 10.0; /*overkill but still fast for now */
static const double INVERSE_TRIGAMMA_Y_BIG = 1e7;
static const double INVERSE_TRIGAMMA_Y_SMALL = 1e-6;
static const double INVERSE_TRIGAMMA_REL_TOL = 1e-12;
static const double INVERSE_TRIGAMMA_FUNC_REL_TOL = 16.0 * DBL_EPSILON;
static const int INVERSE_TRIGAMMA_NEWTON_MAX_ITER = 50;
static const int INVERSE_TRIGAMMA_BISECT_MAX_ITER = 200;
static const double TRIGAMMA_AE_1 = 1.0;
static const double TRIGAMMA_AE_2 = 0.5;
static const double TRIGAMMA_AE_3 = 1.0 / 6.0;
static const double TRIGAMMA_AE_5 = -1.0 / 30.0;
static const double TRIGAMMA_AE_7 = 1.0 / 42.0;
static const double TRIGAMMA_AE_9 = -1.0 / 30.0;
static const double TRIGAMMA_AE_11 = 5.0 / 66.0;
static const double TRIGAMMA_AE_13 = -691.0 / 2730.0;
static const double TRIGAMMA_AE_15 = 7.0 / 6.0;
static const double TETRAGAMMA_AE_2 = -1.0;
static const double TETRAGAMMA_AE_3 = -1.0;
static const double TETRAGAMMA_AE_4 = -0.5;
static const double TETRAGAMMA_AE_6 = 1.0 / 6.0;
static const double TETRAGAMMA_AE_8 = -1.0 / 6.0;
static const double TETRAGAMMA_AE_10 = 3.0 / 10.0;
static const double TETRAGAMMA_AE_12 = -5.0 / 6.0;
static const double TETRAGAMMA_AE_14 = 691.0 / 210.0;
static const double TETRAGAMMA_AE_16 = -35.0 / 2.0;

static inline double eps_invSqrtX(void)
{
    /*smallest x such that 1/(x*x) will not overflow*/
    return 1.0 / sqrt(DBL_MAX);
}

double pos_trigamma(double x)
{
    double result;
    double reciprocalX;
    double reciprocalX2;
    double reciprocalPower;

    if (isnan(x))
        return NAN;
    if (x == INFINITY)
        return 0.0;
    if (!(x > 0.0))
        return NAN;

    if (x <= eps_invSqrtX())
        return INFINITY; // trigamma --> infty for positive x --> 0

    result = 0.0;

    /*
     * (I) We use the trigamma recurrence up to BEGIN_ASYMPTOTIC,
     * at which point the asymptotic expansion is nearly exact.
     */
    while (x < BEGIN_ASYMPTOTIC) {
        double x2_ = x * x;
        result += 1.0 / x2_;
        x += 1.0;
    }

    /* (II) Apply the truncated trigamma asymptotic expansion */

    reciprocalX = 1.0 / x;

    // beginning with x^-5, expansion is only --odd-- powers
    // so we can save some operations by storing x2
    reciprocalX2 = reciprocalX * reciprocalX;

    reciprocalPower = reciprocalX; // 1 / x
    result += TRIGAMMA_AE_1 * reciprocalPower;

    reciprocalPower *= reciprocalX; // 1 / x^2
    result += TRIGAMMA_AE_2 * reciprocalPower;

    reciprocalPower *= reciprocalX; // 1 / x^3
    result += TRIGAMMA_AE_3 * reciprocalPower;

    reciprocalPower *= reciprocalX2; // 1 / x^5
    result += TRIGAMMA_AE_5 * reciprocalPower;

    reciprocalPower *= reciprocalX2; // 1 / x^7
    result += TRIGAMMA_AE_7 * reciprocalPower;

    reciprocalPower *= reciprocalX2; // 1 / x^9
    result += TRIGAMMA_AE_9 * reciprocalPower;

    reciprocalPower *= reciprocalX2; // 1 / x^11
    result += TRIGAMMA_AE_11 * reciprocalPower;

    reciprocalPower *= reciprocalX2; // 1 / x^13
    result += TRIGAMMA_AE_13 * reciprocalPower;

    reciprocalPower *= reciprocalX2; // 1 / x^15
    result += TRIGAMMA_AE_15 * reciprocalPower;

    return result;
}

double pos_tetragamma(double x)
{
    double result;
    double reciprocalX;
    double reciprocalX2;
    double reciprocalPower;

    if (isnan(x))
        return NAN;
    if (x == INFINITY)
        return 0.0;
    if (!(x > 0.0))
        return NAN;

    if (x <= eps_invSqrtX())
        return -INFINITY;

    result = 0.0;

    while (x < BEGIN_ASYMPTOTIC) {
        double x3_ = x * x * x;

        if (!(x3_ > 0.0))
            return -INFINITY;

        result -= 2.0 / x3_;
        x += 1.0;
    }

    /* tetragamma asymptotic expansion */
    reciprocalX = 1.0 / x;
    // same trick as in trigamma -- save operations by storing x2
    reciprocalX2 = reciprocalX * reciprocalX;

    reciprocalPower = reciprocalX2; // 1/x^2
    result += TETRAGAMMA_AE_2 * reciprocalPower;

    reciprocalPower *= reciprocalX; // 1/x^3
    result += TETRAGAMMA_AE_3 * reciprocalPower;

    reciprocalPower *= reciprocalX; // 1/x^4
    result += TETRAGAMMA_AE_4 * reciprocalPower;

    reciprocalPower *= reciprocalX2; // 1/x^6
    result += TETRAGAMMA_AE_6 * reciprocalPower;

    reciprocalPower *= reciprocalX2; // 1/x^8
    result += TETRAGAMMA_AE_8 * reciprocalPower;

    reciprocalPower *= reciprocalX2; // 1/x^10
    result += TETRAGAMMA_AE_10 * reciprocalPower;

    reciprocalPower *= reciprocalX2; // 1/x^12
    result += TETRAGAMMA_AE_12 * reciprocalPower;

    reciprocalPower *= reciprocalX2; // 1/x^14
    result += TETRAGAMMA_AE_14 * reciprocalPower;

    reciprocalPower *= reciprocalX2; // 1/x^16
    result += TETRAGAMMA_AE_16 * reciprocalPower;
    return result;
}

double itrigamma(double y)
{
    double minX;
    double currentX;
    double lowerBound;
    double upperBound;
    double lowerResidual;
    double upperResidual;
    double funcTol = INVERSE_TRIGAMMA_FUNC_REL_TOL * fmax(y, 1.0);

    if (isnan(y))
        return NAN;
    if (y == 0.0)
        return INFINITY;
    if (y == INFINITY)
        return 0.0;
    if (!(y > 0.0))
        return NAN;
    if (y < INVERSE_TRIGAMMA_Y_SMALL)
        return 1.0 / y + 0.5;
    /*
     * early-exits -- use expansions for large and small
     */
    if (y > INVERSE_TRIGAMMA_Y_BIG)
        return 1.0 / sqrt(y);

    minX = eps_invSqrtX();
    if (y < 1.0)
        currentX = 1.0 / y + 0.5;
    else
        currentX = 1.0 / sqrt(y);

    if (!(currentX > minX))
        currentX = 1.0;
    if (!isfinite(currentX))
        currentX = 1.0;

    lowerBound = fmax(minX, 0.5 * currentX); /* avoid zero or negative */
    upperBound =
        fmax(lowerBound * 2.0, currentX); /* ensure upper >= curr, lower */
    lowerResidual = pos_trigamma(lowerBound) - y;

    if (!isfinite(lowerResidual))
        lowerResidual = INFINITY;

    upperResidual = pos_trigamma(upperBound) - y;

    if (!isfinite(upperResidual))
        upperResidual = -y;

    for (int k = 0; k < 256 && upperResidual > 0.0; k++) {
        upperBound *= 2.0;

        if (!isfinite(upperBound))
            return NAN;
        if (upperBound > 1e100)
            return NAN;

        upperResidual = pos_trigamma(upperBound) - y;

        if (!isfinite(upperResidual))
            upperResidual = -y;
    }

    for (int k = 0; k < 256 && lowerResidual < 0.0 && lowerBound > minX; k++) {
        lowerBound *= 0.5;

        if (lowerBound < minX)
            lowerBound = minX;

        lowerResidual = pos_trigamma(lowerBound) - y;

        if (!isfinite(lowerResidual))
            lowerResidual = INFINITY;
    }

    if (!(lowerResidual > 0.0 && upperResidual < 0.0))
        return NAN;

    /*
     * Newton-raphson iteration to find the root: pos_trigamma(x) - y == 0
     */
    for (int iter = 0; iter < INVERSE_TRIGAMMA_NEWTON_MAX_ITER; iter++) {
        double functionValue;
        double grad_;
        double nextX;
        double boundedInterval;
        double xTolerance;

        functionValue = pos_trigamma(currentX) - y;

        /* we're optimizing over [minX, +infinity)*/
        if (!isfinite(functionValue)) {
            if (currentX <= minX)
                functionValue = INFINITY;
            else
                functionValue = -y;
        }

        if (fabs(functionValue) <= funcTol)
            return currentX;
        if (functionValue > 0.0) {
            lowerBound = currentX;
            lowerResidual = functionValue;
        } else if (functionValue < 0.0) {
            upperBound = currentX;
            upperResidual = functionValue;
        } else {
            return currentX;
        }

        boundedInterval = upperBound - lowerBound;

        xTolerance = INVERSE_TRIGAMMA_REL_TOL * fmax(1.0, fabs(currentX));

        if (boundedInterval <= xTolerance)
            return 0.5 * (lowerBound + upperBound);

        grad_ = pos_tetragamma(currentX);
        if (!isfinite(grad_))
            grad_ = 0.0;

        if (grad_ == 0.0) {
            nextX = 0.5 * (lowerBound + upperBound);
        } else {
            nextX = currentX - functionValue / grad_;

            if (!(nextX > lowerBound && nextX < upperBound))
                nextX = 0.5 * (lowerBound + upperBound);

            if (!isfinite(nextX))
                nextX = 0.5 * (lowerBound + upperBound);

            if (!(nextX > 0.0))
                nextX = 0.5 * (lowerBound + upperBound);
        }

        currentX = nextX;
    }

    /* bisect */
    for (int iter = 0; iter < INVERSE_TRIGAMMA_BISECT_MAX_ITER; iter++) {
        double midpoint;
        double midpointResidual;
        double boundedInterval;
        double midpointTolerance;
        double funcTol = INVERSE_TRIGAMMA_FUNC_REL_TOL * fmax(y, 1.0);
        midpoint = 0.5 * (lowerBound + upperBound);
        midpointResidual = pos_trigamma(midpoint) - y;

        if (fabs(midpointResidual) <= funcTol)
            return midpoint;
        if (!isfinite(midpointResidual))
            return NAN;

        boundedInterval = upperBound - lowerBound;
        midpointTolerance =
            INVERSE_TRIGAMMA_REL_TOL * fmax(1.0, fabs(midpoint));

        if (boundedInterval <= midpointTolerance)
            return midpoint;

        if (midpointResidual > 0.0)
            lowerBound = midpoint;
        else
            upperBound = midpoint;
    }

    return 0.5 * (lowerBound + upperBound);
}

/*vectorization: trigamma, tetragamma, inverse*/
void pos_trigamma_vec(const double *x, double *out, size_t n)
{
for (size_t i = 0; i < n; i++)
out[i] = pos_trigamma(x[i]);
}

void pos_tetragamma_vec(const double *x, double *out, size_t n)
{
for (size_t i = 0; i < n; i++)
out[i] = pos_tetragamma(x[i]);
}

void itrigamma_vec(const double *y, double *out, size_t n)
{
for (size_t i = 0; i < n; i++)
out[i] = itrigamma(y[i]);
}