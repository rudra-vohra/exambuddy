# Section 1: Twiddle Factor Properties and DFT Equations

Twiddle factor definition: $W_N = e^{-j 2\pi / N}$.

Fundamental Properties:
1. Periodicity: $W_N^{k + N} = W_N^k$.
2. Symmetry: $W_N^{k + N/2} = -W_N^k$.
3. Reduction Property: $W_N^{2k} = W_{N/2}^k$.

Butterfly Operation in Radix-2 DIT FFT:
$$X[k] = G[k] + W_N^k H[k]$$
$$X[k + N/2] = G[k] - W_N^k H[k]$$
Only a single complex multiplication is required for each butterfly pair.
---
# Section 2: Circular Shift and Circulant Matrix Formulation

A circular shift of sequence $x[n]$ by $m$ positions modulo $N$ is defined as $x[((n - m))_N]$.

Circulant Matrix Form of Circular Convolution:
The circular convolution $y[n] = x[n] \circledast h[n]$ can be written as matrix-vector product $y = H_c x$:
$$H_c = \begin{bmatrix} h[0] & h[N-1] & \dots & h[1] \\ h[1] & h[0] & \dots & h[2] \\ \vdots & \vdots & \ddots & \vdots \\ h[N-1] & h[N-2] & \dots & h[0] \end{bmatrix}$$
Every row is a circular right-shift of the previous row. Circular convolution is diagonalized by the DFT matrix $F_N$.
---
# Section 3: Block Convolution: Overlap-Add and Overlap-Save

When filtering very long or streaming sequences $x[n]$ with an FIR filter of length $M$:

1. Overlap-Add (OLA) Method:
- Segment input into non-overlapping blocks of length $L$.
- Convolve each block with filter (length $N = L + M - 1$).
- Adjacent output blocks overlap by $M - 1$ samples and are added together.

2. Overlap-Save (OLS) Method:
- Segment input into overlapping blocks of length $N = L + M - 1$, overlapping by $M - 1$ samples.
- Perform $N$-point circular convolution.
- Discard the first $M - 1$ points contaminated by circular wrap-around and retain the remaining $L$ valid samples.
---
# Section 4: Goertzel Algorithm for Single-Bin DFT

The Goertzel algorithm calculates a single frequency bin $X[k]$ without computing the full FFT:

Difference Equation (Second-Order IIR Filter):
$$s[n] = x[n] + 2 \cos(2\pi k / N) s[n-1] - s[n-2]$$
with initial conditions $s[-1] = s[-2] = 0$.

Output calculation at $n = N$:
$$X[k] = s[N] - W_N^k s[N-1]$$

Complexity: $N + 2$ real multiplications and $2N + 1$ real additions. Highly efficient for DTMF tone detection.
---
# Section 5: Chirp Z-Transform (CZT)

The Chirp Z-Transform evaluates the Z-transform along arbitrary spiral contours in the z-plane:
$$z_k = A \cdot W^{-k}, \quad k = 0, 1, \dots, M-1$$
where $A = A_0 e^{j \theta_0}$ and $W = W_0 e^{-j \phi_0}$.

Bluestein's Substitution:
Using the identity $2nk = n^2 + k^2 - (k - n)^2$, CZT is reformulated as a linear high-speed FFT convolution.
---
# Section 6: Parks-McClellan (Remez Exchange) Algorithm

The Parks-McClellan algorithm designs optimal linear-phase FIR filters in the Chebyshev (minimax error) sense.

Alternation Theorem:
The error function $E(\omega) = W(\omega)[H_d(\omega) - H(\omega)]$ alternates between local extrema with alternating signs:
$$E(\omega_i) = -E(\omega_{i-1}) = \pm \max |E(\omega)|$$
Number of extremal frequencies is at least $r + 1$, where $r$ is the number of independent cosine basis functions.
Yields strictly equiripple passband and stopband behavior with minimum possible filter order.
---
# Section 7: Bilinear Prewarping Quick Lookup Table

Prewarping relationship: $\Omega_c = 2 F_s \tan(\omega_c / 2) = 2 F_s \tan(\pi f_c / F_s)$.

Prewarped Analog Cutoff $\Omega_c$ for $f_c = 1000 \text{ Hz}$ across Standard Sampling Rates:
- $F_s = 8000 \text{ Hz} \implies \omega_c = 0.25\pi \implies \Omega_c = 16000 \cdot \tan(0.125\pi) = 6627.42 \text{ rad/s}$.
- $F_s = 10000 \text{ Hz} \implies \omega_c = 0.2\pi \implies \Omega_c = 20000 \cdot \tan(0.1\pi) = 6498.39 \text{ rad/s}$.
- $F_s = 16000 \text{ Hz} \implies \omega_c = 0.125\pi \implies \Omega_c = 32000 \cdot \tan(0.0625\pi) = 6384.78 \text{ rad/s}$.
- $F_s = 44100 \text{ Hz} \implies \omega_c = 0.04535\pi \implies \Omega_c = 88200 \cdot \tan(0.02268\pi) = 6303.88 \text{ rad/s}$.
---
# Section 8: Direct Form to Lattice Realization

FIR Lattice Structure:
Recursive reflection coefficients $k_m$ for $m = M-1, \dots, 0$:
$$A_{m-1}(z) = \frac{A_m(z) - k_m B_m(z)}{1 - k_m^2}$$
Stability check for IIR filters: An all-pole IIR filter is stable if and only if all reflection coefficients satisfy $|k_m| < 1$.
---
# Section 9: Fixed-Point Arithmetic and Quantization Mechanics

Two's Complement Format $Q_{m.f}$:
Total bits $B = 1 + m + f$ (1 sign bit, $m$ integer bits, $f$ fractional bits).

Quantization Error Characteristics:
- Truncation: Error $e = Q(x) - x$ is always non-positive for two's complement $(-2^{-f} < e \le 0)$, causing DC bias.
- Rounding: Error is symmetric $(-2^{-f}/2 \le e < 2^{-f}/2)$ with zero mean and variance $\sigma^2 = 2^{-2f} / 12$.
- Overflow Protection: Wrap-around overflow causes large destructive limit cycles; saturation arithmetic clamps output to full-scale limits.
---
# Section 10: DSP Hardware Architecture Features

Key Hardware Blocks for High-Throughput DSP:
1. Dedicated Multiply-Accumulate (MAC) Unit: Computes $y \leftarrow y + a \cdot b$ in a single clock cycle.
2. Harvard Architecture: Separate program memory and data memory buses, enabling simultaneous instruction fetch and dual operand access.
3. Circular Addressing: Hardware pointer wrap-around for implementing delay lines and circular buffers without software bounds checking.