import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pymupdf
from PIL import Image, ImageDraw, ImageFont

CORPUS_DIR = BASE_DIR / "corpus"
PDF_DIR = CORPUS_DIR / "pdf"
SLIDES_DIR = CORPUS_DIR / "slides"
MD_DIR = CORPUS_DIR / "markdown"
HW_DIR = CORPUS_DIR / "handwritten"

for d in [PDF_DIR, SLIDES_DIR, MD_DIR, HW_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 1. GENERATE dsp_lecture_notes.pdf (26 Pages)
# -------------------------------------------------------------
def generate_lecture_notes():
    pdf_path = PDF_DIR / "dsp_lecture_notes.pdf"
    doc = pymupdf.open()

    pages_content = [
        # Page 1
        ("Chapter 1: Discrete-Time Signals & Systems - Fundamentals",
         "1.1 Introduction to Discrete-Time Signals and Systems\n\n"
         "A discrete-time signal x[n] is defined for integer values of n in (-inf, inf). "
         "A discrete-time system T transforms an input sequence x[n] into an output sequence y[n] = T{x[n]}.\n\n"
         "Key System Properties:\n"
         "1. Linearity: The system satisfies superposition: T{a*x1[n] + b*x2[n]} = a*T{x1[n]} + b*T{x2[n]}.\n"
         "2. Time-Invariance: A time-shift in the input causes an identical time-shift in the output: T{x[n - k]} = y[n - k].\n"
         "3. Causality: The output y[n] at any index n depends only on present and past inputs x[k] for k <= n, and not on future inputs.\n"
         "4. Stability (BIBO): A discrete-time LTI system is bounded-input bounded-output (BIBO) stable if and only if "
         "its impulse response h[n] is absolutely summable:\n"
         "    sum_{k = -inf}^{inf} |h[k]| < inf.\n\n"
         "If the impulse response is absolutely summable, any bounded input |x[n]| <= B_x produces a bounded output |y[n]| <= B_y < inf."),

        # Page 2
        ("Chapter 1: Difference Equations & Convolution",
         "1.2 Linear Constant-Coefficient Difference Equations (LCCDE)\n\n"
         "An N-th order LCCDE describes an LTI system relating input x[n] and output y[n]:\n"
         "    sum_{k=0}^{N} a_k y[n - k] = sum_{m=0}^{M} b_m x[n - m], with a_0 != 0.\n\n"
         "Linear Convolution Representation:\n"
         "For any LTI system, the response to an arbitrary input x[n] is given by the convolution sum:\n"
         "    y[n] = x[n] * h[n] = sum_{k=-inf}^{inf} x[k] h[n - k].\n\n"
         "Commutative Property: x[n] * h[n] = h[n] * x[n].\n"
         "Associative Property: (x[n] * h1[n]) * h2[n] = x[n] * (h1[n] * h2[n]).\n"
         "Distributive Property: x[n] * (h1[n] + h2[n]) = x[n]*h1[n] + x[n]*h2[n]."),

        # Page 3
        ("Chapter 2: Discrete-Time Fourier Transform (DTFT)",
         "2.1 DTFT Definition and Existence\n\n"
         "The Discrete-Time Fourier Transform (DTFT) of a sequence x[n] is defined as:\n"
         "    X(e^{j*omega}) = sum_{n=-inf}^{inf} x[n] * e^{-j*omega*n}\n\n"
         "Inverse DTFT (IDTFT):\n"
         "    x[n] = (1 / 2*pi) * integral_{-pi}^{pi} X(e^{j*omega}) * e^{j*omega*n} d_omega\n\n"
         "Existence Condition: The DTFT converges uniformly if x[n] is absolutely summable:\n"
         "    sum_{n=-inf}^{inf} |x[n]| < inf.\n"
         "Periodicity: X(e^{j*omega}) is strictly periodic with fundamental period 2*pi:\n"
         "    X(e^{j*(omega + 2*pi)}) = X(e^{j*omega})."),

        # Page 4
        ("Chapter 2: DTFT Properties & Symmetry",
         "2.2 Mathematical Properties of the DTFT\n\n"
         "1. Linearity: a*x1[n] + b*x2[n] <-> a*X1(e^{j*omega}) + b*X2(e^{j*omega}).\n"
         "2. Time Shifting: x[n - n0] <-> e^{-j*omega*n0} * X(e^{j*omega}).\n"
         "3. Frequency Shifting: e^{j*omega0*n} * x[n] <-> X(e^{j*(omega - omega0)}).\n"
         "4. Conjugation & Symmetry: For a real-valued sequence x[n]:\n"
         "    X(e^{-j*omega}) = X^*(e^{j*omega})\n"
         "    |X(e^{-j*omega})| = |X(e^{j*omega})| (Magnitude is an even function)\n"
         "    arg{X(e^{-j*omega})} = -arg{X(e^{j*omega})} (Phase is an odd function)\n"
         "5. Parseval's Theorem:\n"
         "    sum_{n=-inf}^{inf} |x[n]|^2 = (1 / 2*pi) * integral_{-pi}^{pi} |X(e^{j*omega})|^2 d_omega."),

        # Page 5
        ("Chapter 3: The Z-Transform & Region of Convergence",
         "3.1 Definition and Region of Convergence (ROC)\n\n"
         "The two-sided Z-transform of a discrete-time sequence x[n] is defined as:\n"
         "    X(z) = sum_{n=-inf}^{inf} x[n] * z^{-n}, where z = r * e^{j*omega}.\n\n"
         "Properties of the ROC:\n"
         "1. The ROC of X(z) consists of a ring in the z-plane centered at the origin: r_R < |z| < r_L.\n"
         "2. The ROC cannot contain any poles of X(z).\n"
         "3. For a finite-duration sequence, the ROC is the entire z-plane, except possibly z=0 or z=inf.\n"
         "4. For a right-sided sequence, the ROC extends outward from the outermost pole to infinity (|z| > r_max).\n"
         "5. For a left-sided sequence, the ROC extends inward from the innermost pole to the origin (|z| < r_min).\n"
         "6. For a two-sided sequence, the ROC is an open annular ring between two concentric circles."),

        # Page 6
        ("Chapter 3: Inverse Z-Transform Methods",
         "3.2 Inversion Techniques\n\n"
         "1. Inspection Method: Recognizing standard transform pairs from lookup tables.\n"
         "2. Partial Fraction Expansion (PFE):\n"
         "    If X(z) = B(z)/A(z) is a rational function with distinct poles p_k:\n"
         "    X(z) / z = sum_{k=1}^{N} (A_k / (z - p_k)), where A_k = [(z - p_k) * (X(z)/z)]_{z = p_k}.\n"
         "3. Power Series Expansion (Long Division):\n"
         "    Expanding X(z) in ascending or descending powers of z according to the causality specified by the ROC.\n"
         "4. Contour Integration: Using Cauchy Residue Theorem:\n"
         "    x[n] = (1 / 2*pi*j) * contour_integral X(z) * z^{n-1} dz = sum residues."),

        # Page 7
        ("Chapter 4: LTI Systems in the Z-Domain",
         "4.1 Transfer Function H(z), Poles, and Zeros\n\n"
         "The system transfer function H(z) is the Z-transform of the impulse response h[n]:\n"
         "    H(z) = Y(z) / X(z) = sum_{m=0}^{M} b_m z^{-m} / sum_{k=0}^{N} a_k z^{-k}.\n\n"
         "Stability Condition:\n"
         "An LTI system is BIBO stable if and only if the Region of Convergence of H(z) includes the unit circle (|z| = 1).\n\n"
         "Causal and Stable Systems:\n"
         "For a causal LTI system, all poles of H(z) must strictly lie inside the unit circle (|p_k| < 1 for all k). "
         "If any pole lies on or outside the unit circle, the causal system is unstable or marginally stable."),

        # Page 8
        ("Chapter 4: Special Filter Classes",
         "4.2 Minimum-Phase and All-Pass Systems\n\n"
         "Minimum-Phase System:\n"
         "A causal, stable LTI system H(z) is called minimum-phase if all its poles AND all its zeros "
         "lie strictly inside the unit circle (|z| < 1). The inverse filter 1/H(z) is also causal and stable.\n\n"
         "All-Pass System:\n"
         "An all-pass filter has a constant magnitude response across all frequencies: |H_ap(e^{j*omega})| = 1 for all omega.\n"
         "Its poles and zeros occur in conjugate reciprocal pairs: a pole at z = p is matched with a zero at z = 1/p*.\n"
         "Any causal, stable transfer function can be uniquely decomposed as H(z) = H_min(z) * H_ap(z)."),

        # Page 9
        ("Chapter 5: Discrete Fourier Transform (DFT)",
         "5.1 Discrete Fourier Transform Definition\n\n"
         "The N-point DFT of a finite-length sequence x[n], 0 <= n <= N-1, is given by:\n"
         "    X[k] = sum_{n=0}^{N-1} x[n] * W_N^{k*n}, for k = 0, 1, ..., N-1,\n"
         "where W_N = e^{-j*(2*pi/N)} is the twiddle factor.\n\n"
         "Inverse DFT (IDFT):\n"
         "    x[n] = (1 / N) * sum_{k=0}^{N-1} X[k] * W_N^{-k*n}, for n = 0, 1, ..., N-1.\n\n"
         "Relation to DTFT:\n"
         "The DFT corresponds to uniformly spaced frequency samples of the DTFT evaluated at omega_k = (2*pi*k)/N."),

        # Page 10
        ("Chapter 5: Circular vs Linear Convolution",
         "5.2 Circular Convolution and Frequency Domain Filtering\n\n"
         "Circular Convolution Definition:\n"
         "The circular convolution of two N-point sequences x1[n] and x2[n] is defined as:\n"
         "    x3[n] = sum_{m=0}^{N-1} x1[m] * x2[((n - m))_N], where ((n))_N denotes modulo-N indexing.\n"
         "Property: DFT{x1[n] (N) x2[n]} = X1[k] * X2[k].\n\n"
         "Linear Convolution via Circular Convolution:\n"
         "If x1[n] has length L and x2[n] has length M, their linear convolution has length L + M - 1.\n"
         "To compute linear convolution using the DFT without time-domain aliasing, both sequences must be "
         "zero-padded to a length N >= L + M - 1 before computing the N-point DFT and IDFT."),

        # Page 11
        ("Chapter 6: Fast Fourier Transform (FFT)",
         "6.1 Radix-2 Decimation-in-Time (DIT) FFT\n\n"
         "The Cooley-Tukey Radix-2 DIT FFT recursively divides an N-point DFT into two N/2-point DFTs "
         "of even-indexed and odd-indexed samples:\n"
         "    X[k] = G[k] + W_N^k * H[k]\n"
         "    X[k + N/2] = G[k] - W_N^k * H[k], for k = 0, 1, ..., N/2 - 1.\n\n"
         "Computational Complexity Comparison:\n"
         "- Direct N-point DFT: N^2 complex multiplications, N(N-1) complex additions.\n"
         "- Radix-2 DIT FFT: (N/2)*log2(N) complex multiplications, N*log2(N) complex additions.\n"
         "For N = 1024, direct DFT requires 1,048,576 complex multiplications, whereas FFT requires only 5,120 multiplications."),

        # Page 12
        ("Chapter 6: Decimation-in-Frequency (DIF) FFT",
         "6.2 Radix-2 Decimation-in-Frequency (DIF) Algorithm\n\n"
         "In DIF FFT, the time-domain sequence is split into the first half and second half of samples:\n"
         "    x_first[n] = x[n] + x[n + N/2]\n"
         "    x_second[n] = (x[n] - x[n + N/2]) * W_N^n, for n = 0, 1, ..., N/2 - 1.\n\n"
         "Bit Reversal Permutation:\n"
         "For DIT FFT, the inputs must be bit-reversed while outputs appear in normal natural order.\n"
         "For DIF FFT, the inputs are in natural order while outputs emerge in bit-reversed order."),

        # Page 13
        ("Chapter 7: Fundamentals of Digital Filters",
         "7.1 Filter Specifications and Ideal Frequency Responses\n\n"
         "Digital filters process discrete-time signals to pass desired frequency bands and attenuate undesired bands.\n"
         "Standard Specifications for a Lowpass Filter:\n"
         "- Passband edge frequency: omega_p\n"
         "- Stopband edge frequency: omega_s\n"
         "- Passband ripple: 1 - delta_p <= |H(e^{j*omega})| <= 1 + delta_p (or alpha_p in dB)\n"
         "- Stopband attenuation: |H(e^{j*omega})| <= delta_s (or alpha_s in dB)\n"
         "- Transition band: Delta_omega = omega_s - omega_p."),

        # Page 14
        ("Chapter 8: Finite Impulse Response (FIR) Filters",
         "8.1 Linear Phase FIR Filter Characteristics\n\n"
         "FIR filters possess an impulse response h[n] of finite duration M (length N = M + 1):\n"
         "    H(z) = sum_{n=0}^{M} h[n] z^{-n}.\n\n"
         "Linear Phase Condition:\n"
         "An FIR filter exhibits generalized linear phase if its impulse response satisfies symmetry or antisymmetry:\n"
         "    h[n] = h[M - n] (Symmetric, Linear phase with constant group delay tau = M/2)\n"
         "    h[n] = -h[M - n] (Antisymmetric, 90-degree constant phase shift).\n\n"
         "Four Types of Linear Phase FIR Filters:\n"
         "- Type I: Symmetric, M is even (N odd). Can implement lowpass, highpass, bandpass, bandstop.\n"
         "- Type II: Symmetric, M is odd (N even). Cannot implement highpass or bandstop because H(e^{j*pi}) = 0.\n"
         "- Type III: Antisymmetric, M is even. H(e^{j*0}) = H(e^{j*pi}) = 0. Suitable for bandpass/differentiator.\n"
         "- Type IV: Antisymmetric, M is odd. H(e^{j*0}) = 0. Suitable for highpass and differentiator."),

        # Page 15
        ("Chapter 8: FIR Window Design Method",
         "8.2 Window Functions in FIR Design\n\n"
         "The window method truncates the ideal infinite impulse response h_d[n] by multiplying with a finite window w[n]:\n"
         "    h[n] = h_d[n] * w[n], for 0 <= n <= M.\n\n"
         "Window Comparison Table:\n"
         "1. Rectangular: Mainlobe width = 4*pi/M, Peak sidelobe = -13 dB, Min stopband attenuation = 21 dB.\n"
         "2. Bartlett (Triangular): Mainlobe width = 8*pi/M, Peak sidelobe = -25 dB, Min stopband = 25 dB.\n"
         "3. Hanning: Mainlobe width = 8*pi/M, Peak sidelobe = -31 dB, Min stopband = 44 dB.\n"
         "4. Hamming: Mainlobe width = 8*pi/M, Peak sidelobe = -43 dB, Min stopband = 53 dB.\n"
         "5. Blackman: Mainlobe width = 12*pi/M, Peak sidelobe = -58 dB, Min stopband = 74 dB.\n\n"
         "Trade-off: As sidelobe attenuation increases, mainlobe width widens, yielding a wider transition bandwidth."),

        # Page 16
        ("Chapter 8: Kaiser Window Design",
         "8.3 Kaiser Parameterized Window Formulation\n\n"
         "The Kaiser window allows independent adjustment of transition bandwidth and stopband attenuation:\n"
         "    w[n] = I_0(beta * sqrt(1 - (2n/M - 1)^2)) / I_0(beta), 0 <= n <= M,\n"
         "where I_0(x) is the modified zero-th order Bessel function of the first kind.\n\n"
         "Empirical Formulas for Kaiser Parameters:\n"
         "Given stopband attenuation A = -20 * log10(delta):\n"
         "- For A > 50 dB: beta = 0.1102 * (A - 8.7).\n"
         "- For 21 <= A <= 50 dB: beta = 0.5842 * (A - 21)^0.4 + 0.07886 * (A - 21).\n"
         "- Filter length: M = (A - 8) / (2.285 * Delta_omega)."),

        # Page 17
        ("Chapter 8: Frequency Sampling FIR Design",
         "8.4 Frequency Sampling Method\n\n"
         "In frequency sampling design, the desired continuous frequency response H_d(e^{j*omega}) is sampled at N points:\n"
         "    H[k] = H_d(e^{j*(2*pi*k/N)}), k = 0, 1, ..., N - 1.\n"
         "The filter coefficients are obtained via inverse DFT:\n"
         "    h[n] = (1 / N) * sum_{k=0}^{N-1} H[k] * e^{j*(2*pi*k*n/N)}.\n\n"
         "Optimization: Introducing unconstrained transition band samples significantly improves stopband attenuation."),

        # Page 18
        ("Chapter 9: Infinite Impulse Response (IIR) Filters",
         "9.1 Introduction to IIR Filter Design\n\n"
         "IIR filters have infinite-duration impulse response and can achieve very sharp cutoff characteristics "
         "with significantly lower filter order compared to FIR filters.\n"
         "Transfer function:\n"
         "    H(z) = sum_{m=0}^{M} b_m z^{-m} / (1 + sum_{k=1}^{N} a_k z^{-k}).\n\n"
         "Standard Analog Filter Prototypes:\n"
         "1. Butterworth: Maximally flat magnitude response in passband and stopband.\n"
         "2. Chebyshev Type I: Equiripple passband, monotonic stopband.\n"
         "3. Chebyshev Type II (Inverse Chebyshev): Monotonic passband, equiripple stopband.\n"
         "4. Elliptic (Cauer): Equiripple in both passband and stopband, lowest order for given specifications."),

        # Page 19
        ("Chapter 9: Impulse Invariance Method",
         "9.2 Impulse Invariance IIR Filter Design\n\n"
         "The impulse invariance method designs digital filter h[n] by sampling the continuous impulse response h_a(t):\n"
         "    h[n] = T * h_a(nT), where T is the sampling interval.\n\n"
         "Mapping Relationship:\n"
         "A pole at s = p_k in the s-plane maps directly to a pole at z = e^{p_k * T} in the z-plane.\n"
         "Limitation - Aliasing:\n"
         "The digital frequency response is an aliased summation of the analog frequency response:\n"
         "    H(e^{j*omega}) = sum_{k=-inf}^{inf} H_a(j*(omega/T + 2*pi*k/T)).\n"
         "Impulse invariance cannot be used for highpass or bandstop filters due to severe aliasing."),

        # Page 20
        ("Chapter 9: Bilinear Transformation Method",
         "9.3 Bilinear Transformation (BLT)\n\n"
         "The bilinear transformation converts an analog transfer function H_a(s) to a digital transfer function H(z) "
         "using the trapezoidal numerical integration substitution:\n"
         "    s = (2 / T) * ((1 - z^{-1}) / (1 + z^{-1})) = (2 / T) * ((z - 1) / (z + 1)).\n\n"
         "Key Properties:\n"
         "1. The entire left-half of the s-plane (Re{s} < 0) maps strictly inside the unit circle (|z| < 1), "
         "guaranteeing that a stable analog filter transforms into a stable digital filter.\n"
         "2. The j*Omega imaginary axis in the s-plane maps one-to-one onto the unit circle z = e^{j*omega}.\n"
         "3. Completely eliminates aliasing because the infinite analog frequency axis is compressed into [-pi, pi]."),

        # Page 21
        ("Chapter 9: Frequency Warping & Prewarping",
         "9.4 Frequency Warping in Bilinear Transformation\n\n"
         "Substituting s = j*Omega and z = e^{j*omega} into the bilinear transform yields:\n"
         "    j*Omega = (2/T) * ((e^{j*omega} - 1) / (e^{j*omega} + 1)) = j * (2/T) * tan(omega / 2).\n"
         "Therefore, the non-linear relationship between analog frequency Omega and digital frequency omega is:\n"
         "    Omega = (2 / T) * tan(omega / 2), and inversely: omega = 2 * arctan(Omega * T / 2).\n\n"
         "Frequency Prewarping Rule:\n"
         "Before applying analog design tables, the digital critical frequencies (omega_p, omega_s) must be "
         "prewarped to analog frequencies:\n"
         "    Omega_p = (2 / T) * tan(omega_p / 2)\n"
         "    Omega_s = (2 / T) * tan(omega_s / 2)."),

        # Page 22
        ("Chapter 10: Butterworth Lowpass Filter Design",
         "10.1 Butterworth Filter Equations and Order Determination\n\n"
         "The magnitude-squared response of an N-th order analog Butterworth filter is:\n"
         "    |H(j*Omega)|^2 = 1 / (1 + (Omega / Omega_c)^{2N}).\n\n"
         "Design Formula for Filter Order N:\n"
         "Given passband attenuation alpha_p (dB) at Omega_p and stopband attenuation alpha_s (dB) at Omega_s:\n"
         "    N = ceil( log10((10^{0.1*alpha_s} - 1) / (10^{0.1*alpha_p} - 1)) / (2 * log10(Omega_s / Omega_p)) ).\n\n"
         "Cutoff Frequency Omega_c:\n"
         "    Omega_c = Omega_p / ((10^{0.1*alpha_p} - 1)^{1 / (2N)}).\n"
         "Poles of the Butterworth filter lie symmetrically on a circle of radius Omega_c in the left-half s-plane:\n"
         "    s_k = Omega_c * e^{j * pi * (2k + N - 1) / (2N)}, for k = 1, 2, ..., N."),

        # Page 23
        ("Chapter 10: Chebyshev Lowpass Filter Design",
         "10.2 Chebyshev Type I Filter Specifications\n\n"
         "The magnitude response of a Chebyshev Type I filter is:\n"
         "    |H(j*Omega)|^2 = 1 / (1 + epsilon^2 * C_N^2(Omega / Omega_p)),\n"
         "where C_N(x) is the N-th order Chebyshev polynomial:\n"
         "    C_N(x) = cos(N * arccos(x)) for |x| <= 1, and cosh(N * arccosh(x)) for |x| > 1.\n\n"
         "Ripple parameter epsilon:\n"
         "    epsilon = sqrt(10^{0.1 * alpha_p} - 1).\n"
         "Filter Order N Calculation:\n"
         "    N = ceil( arccosh( sqrt((10^{0.1 * alpha_s} - 1) / epsilon^2) ) / arccosh(Omega_s / Omega_p) )."),

        # Page 24
        ("Chapter 11: Realization Structures for Digital Filters",
         "11.1 Direct Form Realizations for IIR Filters\n\n"
         "Consider transfer function H(z) = (b0 + b1 z^-1 + b2 z^-2) / (1 + a1 z^-1 + a2 z^-2).\n\n"
         "1. Direct Form I (DF-I):\n"
         "Implements the difference equation directly: computes zeros followed by poles. Requires M + N delay elements.\n\n"
         "2. Direct Form II (DF-II) Canonical Form:\n"
         "Computes intermediate variable w[n] = x[n] - a1 w[n-1] - a2 w[n-2], followed by y[n] = b0 w[n] + b1 w[n-1] + b2 w[n-2].\n"
         "Requires only max(M, N) delay elements (canonic in delay elements)."),

        # Page 25
        ("Chapter 11: Modular Realizations",
         "11.2 Cascade and Parallel Form Realizations\n\n"
         "Cascade Realization:\n"
         "High-order H(z) is factored into a product of second-order biquad sections:\n"
         "    H(z) = b0 * prod_{k=1}^{K} ((1 + b_{1k} z^{-1} + b_{2k} z^{-2}) / (1 + a_{1k} z^{-1} + a_{2k} z^{-2})).\n"
         "Minimizes sensitivity of pole locations to coefficient quantization errors.\n\n"
         "Parallel Realization:\n"
         "Obtained using partial fraction expansion as a sum of second-order sections plus a constant:\n"
         "    H(z) = C + sum_{k=1}^{K} ((gamma_{0k} + gamma_{1k} z^{-1}) / (1 + a_{1k} z^{-1} + a_{2k} z^{-2}))."),

        # Page 26
        ("Chapter 12: Finite Wordlength Effects in Digital Filters",
         "12.1 Quantization Noise and Limit Cycle Oscillations\n\n"
         "In fixed-point hardware implementations, finite precision causes three primary artifacts:\n"
         "1. Coefficient Quantization: Shifts pole and zero locations; in high-order direct form filters, poles may move outside the unit circle causing instability.\n"
         "2. Roundoff Noise: Product roundoff introduces white noise variance sigma_e^2 = 2^{-2B} / 12 at each multiplier.\n"
         "3. Limit Cycle Oscillations:\n"
         "   - Zero-Input Limit Cycles: Due to non-linear quantization rounding in recursive loops, producing sustained periodic output even when input is zero.\n"
         "   - Overflow Oscillations: Due to two's complement wrap-around overflow. Eliminated using saturation arithmetic logic.")
    ]

    for title, body in pages_content:
        page = doc.new_page(width=595, height=842) # A4
        # Draw header
        page.draw_rect(pymupdf.Rect(40, 30, 555, 65), color=(0.2, 0.3, 0.5), fill=(0.95, 0.96, 0.98))
        page.insert_text((50, 52), title, fontsize=13, fontname="helv", color=(0.1, 0.2, 0.4))
        # Draw body
        page.insert_textbox(pymupdf.Rect(45, 80, 550, 780), body, fontsize=10, fontname="helv", lineheight=1.4)
        # Draw footer
        page_num_str = f"Page {len(doc)} of {len(pages_content)}"
        page.insert_text((270, 815), page_num_str, fontsize=9, fontname="helv", color=(0.5, 0.5, 0.5))

    doc.save(pdf_path)
    doc.close()
    print(f"Generated {pdf_path.name} with {len(pages_content)} pages.")

# -------------------------------------------------------------
# 2. GENERATE dsp_slides_sampling_quantization.pdf (18 Slides)
# -------------------------------------------------------------
def generate_slides():
    pdf_path = SLIDES_DIR / "dsp_slides_sampling_quantization.pdf"
    doc = pymupdf.open()

    slides_content = [
        ("Sampling and Quantization of Signals",
         "Lecture Deck: EE501 Digital Signal Processing\nUnit 2: Analog-to-Digital Conversion & Multirate Systems\n\n"
         "Outline:\n- Nyquist-Shannon Sampling Criterion\n- Aliasing and Anti-Aliasing Pre-filters\n"
         "- Ideal Sinc Interpolation vs D/A Conversion\n- Uniform & Non-uniform Quantization (SQNR)\n"
         "- Oversampling and Multirate DSP"),

        ("The Nyquist-Shannon Sampling Theorem",
         "Fundamental Theorem of Information Conversion:\n\n"
         "A continuous-time bandlimited signal x(t) with maximum frequency component F_max (or Omega_max = 2*pi*F_max) "
         "can be completely and uniquely recovered from its discrete samples x[n] = x(n*T_s) if and only if:\n\n"
         "    F_s >= 2 * F_max\n\n"
         "Key Definitions:\n"
         "- F_s = 1 / T_s : Sampling frequency (samples/second or Hz)\n"
         "- Nyquist Rate: 2 * F_max (the minimum theoretical sampling rate)\n"
         "- Nyquist / Folding Frequency: F_N = F_s / 2"),

        ("Aliasing Phenomenon and Spectral Folding",
         "What happens when F_s < 2 * F_max?\n\n"
         "In the frequency domain, sampling causes periodic replication of the continuous spectrum X(F):\n"
         "    X_s(F) = (1 / T_s) * sum_{k=-inf}^{inf} X(F - k * F_s)\n\n"
         "When F_s < 2 * F_max, adjacent spectral replicas overlap. High frequencies above F_s/2 fold back into the baseband, "
         "irreversibly corrupting the signal. Once aliasing occurs, no digital filter can separate the folded components."),

        ("Anti-Aliasing Analog Pre-Filter Design",
         "Preventing Aliasing at the System Input:\n\n"
         "- An analog lowpass filter MUST precede the A/D converter.\n"
         "- Passband: 0 <= F <= F_c, passing desired signal bandwidth with minimal attenuation.\n"
         "- Stopband: F >= F_s / 2, attenuating components above the folding frequency to below ADC noise floor.\n"
         "- Filter Selection: Butterworth for flat passband; Elliptic for steep transition roll-off."),

        ("Signal Reconstruction: Ideal Sinc Interpolation",
         "Reconstruction of Continuous Signals from Samples:\n\n"
         "Under the Nyquist condition, the original continuous signal x(t) is recovered through ideal lowpass filtering:\n"
         "    x(t) = sum_{n=-inf}^{inf} x[n] * sinc( (t - n*T_s) / T_s )\n\n"
         "where sinc(u) = sin(pi * u) / (pi * u).\n"
         "Properties:\n"
         "- At t = k*T_s, sinc(0) = 1 and sinc(m) = 0 for all m != 0, ensuring exact sample interpolation.\n"
         "- Sinc filter is non-causal with infinite impulse response, requiring practical D/A approximations."),

        ("Zero-Order Hold (ZOH) Reconstruction",
         "Practical D/A Converters: Zero-Order Hold:\n\n"
         "- ZOH maintains sample value x[n] constant for the entire period T_s: h_zoh(t) = 1 for 0 <= t < T_s.\n"
         "- Frequency Response: H_zoh(f) = T_s * sinc(f * T_s) * e^{-j*pi*f*T_s}.\n"
         "- Distortion: Droop near the band edge f = F_s/2 of approximately 3.92 dB.\n"
         "- Correction: Post-reconstruction analog smoothing filter or digital pre-equalizer."),

        ("First-Order Hold (FOH) and Post-Filtering",
         "First-Order Hold (Linear Interpolation):\n\n"
         "- Connects adjacent samples with straight line segments.\n"
         "- Impulse response: triangular pulse of duration 2*T_s.\n"
         "- Frequency response: |H_foh(f)| = T_s * sinc^2(f * T_s).\n"
         "- Provides steeper high-frequency attenuation than ZOH (-40 dB/decade vs -20 dB/decade)."),

        ("Uniform Amplitude Quantization",
         "Quantization Fundamentals:\n\n"
         "Maps continuous amplitude x[n] into a discrete set of 2^B digital representation levels.\n"
         "Parameters:\n"
         "- Full-scale range: R = V_max - V_min\n"
         "- Number of bits: B\n"
         "- Quantization step size: Delta = (V_max - V_min) / 2^B\n"
         "- Quantizer types: Midtread (zero is a representation level) and Midrise (zero is a decision threshold)."),

        ("Quantization Error and Noise Modeling",
         "Statistical Model of Quantization Error e[n] = x_q[n] - x[n]:\n\n"
         "Assumptions for small Delta and complex signals:\n"
         "1. e[n] is uniformly distributed over [-Delta/2, Delta/2].\n"
         "2. e[n] is a stationary white noise process uncorrelated with x[n].\n\n"
         "Noise Statistics:\n"
         "- Mean: mu_e = E{e[n]} = 0\n"
         "- Quantization Noise Variance: sigma_q^2 = integral_{-Delta/2}^{Delta/2} e^2 * (1/Delta) de = Delta^2 / 12."),

        ("Signal-to-Quantization-Noise Ratio (SQNR)",
         "Theoretical SQNR for Sinusoidal Signals:\n\n"
         "Let input be a full-scale sinusoid x(t) = (V_max - V_min)/2 * sin(omega*t) with peak-to-peak range 2^B * Delta.\n"
         "Signal Power: P_s = (2^B * Delta / 2)^2 / 2 = 2^{2B} * Delta^2 / 8.\n"
         "Noise Power: P_n = sigma_q^2 = Delta^2 / 12.\n"
         "SQNR Ratio = P_s / P_n = (3/2) * 2^{2B}.\n\n"
         "In Decibels:\n"
         "    SQNR (dB) = 10 * log10(3/2) + 20 * B * log10(2) = 6.02 * B + 1.76 dB.\n"
         "Takeaway: Every additional bit added to the ADC increases SQNR by ~6 dB."),

        ("Non-Uniform Quantization & Companding",
         "Speech and Audio Quantization:\n\n"
         "- Problem: Small amplitude speech signals suffer poor SQNR with uniform quantization.\n"
         "- Solution: Companding (Compressing before uniform quantization, Expanding after D/A).\n"
         "- Standards:\n"
         "  * mu-Law Companding (North America & Japan): F(x) = sgn(x) * ln(1 + mu*|x|) / ln(1 + mu), mu = 255.\n"
         "  * A-Law Companding (Europe & International): A = 87.6."),

        ("Dynamic Range Considerations in Hardware",
         "Dynamic Range (DR) in Digital Signal Processors:\n\n"
         "- 16-bit fixed point: ~96 dB dynamic range.\n"
         "- 24-bit audio: ~144 dB dynamic range (exceeds human hearing threshold).\n"
         "- 32-bit floating point: IEEE-754 format provides > 1500 dB dynamic range, virtually eliminating internal overflow."),

        ("Oversampling and Noise Shaping (Sigma-Delta ADC)",
         "High-Resolution Data Conversion Principles:\n\n"
         "- Oversampling: Sampling at F_s >> 2 * F_max spreads quantization noise power Delta^2/12 over a much wider bandwidth.\n"
         "- Oversampling Ratio (OSR): OSR = F_s / (2 * F_max).\n"
         "- Noise Shaping: Feedback loop filters quantization noise, pushing noise power from baseband to high out-of-band frequencies.\n"
         "- Digital Decimation Filter: Removes out-of-band noise and reduces sample rate to Nyquist rate."),

        ("Multirate DSP: Decimation (Downsampling)",
         "Decimation by Integer Factor M:\n\n"
         "- Downsampler keeps every M-th sample: y[m] = x[m * M].\n"
         "- Spectrum: Y(e^{j*omega}) = (1 / M) * sum_{k=0}^{M-1} X(e^{j*(omega - 2*pi*k)/M}).\n"
         "- Anti-Aliasing Decimation Filter: To avoid aliasing during downsampling, signal MUST be filtered by digital lowpass "
         "filter with cutoff omega_c = pi / M prior to sample removal."),

        ("Multirate DSP: Interpolation (Upsampling)",
         "Interpolation by Integer Factor L:\n\n"
         "- Step 1: Zero-stuffing: Inserts L - 1 zeros between consecutive input samples:\n"
         "    x_u[n] = x[n / L] for n a multiple of L, and 0 otherwise.\n"
         "- Step 2: Anti-Imaging Lowpass Filter: Cutoff frequency omega_c = pi / L and gain L to remove spectral images at multiples of 2*pi/L."),

        ("Polyphase Filter Structures",
         "Efficient Realization of Multirate Filters:\n\n"
         "- Standard FIR filtering before decimation computes samples that are subsequently discarded.\n"
         "- Polyphase Decomposition decomposes transfer function into M branches: H(z) = sum_{k=0}^{M-1} z^{-k} * E_k(z^M).\n"
         "- Noble Identities allow moving downsamplers and upsamplers past filter blocks, running all filtering operations at the lowest sample rate."),

        ("Quadrature Mirror Filter (QMF) Banks",
         "Subband Coding and Frequency Splitting:\n\n"
         "- Two-channel QMF bank splits signal into low-frequency and high-frequency subbands.\n"
         "- Analysis filters: H0(z) (lowpass), H1(z) = H0(-z) (highpass mirror).\n"
         "- Synthesis filters: G0(z) = 2*H0(z), G1(z) = -2*H1(z).\n"
         "- Perfect Reconstruction (PR) cancels aliasing between subband channels."),

        ("Review and Exam Highlights",
         "Key Formula Summary for Exam Night:\n\n"
         "1. Sampling Criterion: F_s >= 2 * F_max\n"
         "2. Folding Frequency: F_N = F_s / 2\n"
         "3. Quantization Noise Variance: sigma_q^2 = Delta^2 / 12\n"
         "4. Sinusoidal SQNR Rule: SQNR = 6.02 * B + 1.76 dB\n"
         "5. Decimation Cutoff: omega_c = pi / M\n"
         "6. Interpolation Cutoff: omega_c = pi / L")
    ]

    for title, body in slides_content:
        page = doc.new_page(width=720, height=405) # 16:9 widescreen slides
        # Background
        page.draw_rect(pymupdf.Rect(0, 0, 720, 405), color=(0.1, 0.15, 0.25), fill=(0.96, 0.97, 0.99))
        # Slide Header Banner
        page.draw_rect(pymupdf.Rect(30, 20, 690, 65), color=(0.15, 0.25, 0.45), fill=(0.15, 0.25, 0.45))
        page.insert_text((45, 50), title, fontsize=15, fontname="helv", color=(1.0, 1.0, 1.0))
        # Body Content
        page.insert_textbox(pymupdf.Rect(40, 80, 680, 365), body, fontsize=11, fontname="helv", lineheight=1.35)
        # Footer
        slide_num_str = f"Slide {len(doc)} of {len(slides_content)}"
        page.insert_text((610, 390), slide_num_str, fontsize=9, fontname="helv", color=(0.4, 0.4, 0.4))

    doc.save(pdf_path)
    doc.close()
    print(f"Generated {pdf_path.name} with {len(slides_content)} slides.")

# -------------------------------------------------------------
# 3. GENERATE dsp_algorithms_cheatsheet.md (10 Sections)
# -------------------------------------------------------------
def generate_markdown():
    md_path = MD_DIR / "dsp_algorithms_cheatsheet.md"
    sections = [
        ("# Section 1: Twiddle Factor Properties and DFT Equations\n\n"
         "Twiddle factor definition: $W_N = e^{-j 2\\pi / N}$.\n\n"
         "Fundamental Properties:\n"
         "1. Periodicity: $W_N^{k + N} = W_N^k$.\n"
         "2. Symmetry: $W_N^{k + N/2} = -W_N^k$.\n"
         "3. Reduction Property: $W_N^{2k} = W_{N/2}^k$.\n\n"
         "Butterfly Operation in Radix-2 DIT FFT:\n"
         "$$X[k] = G[k] + W_N^k H[k]$$\n"
         "$$X[k + N/2] = G[k] - W_N^k H[k]$$\n"
         "Only a single complex multiplication is required for each butterfly pair."),

        ("# Section 2: Circular Shift and Circulant Matrix Formulation\n\n"
         "A circular shift of sequence $x[n]$ by $m$ positions modulo $N$ is defined as $x[((n - m))_N]$.\n\n"
         "Circulant Matrix Form of Circular Convolution:\n"
         "The circular convolution $y[n] = x[n] \\circledast h[n]$ can be written as matrix-vector product $y = H_c x$:\n"
         "$$H_c = \\begin{bmatrix} h[0] & h[N-1] & \\dots & h[1] \\\\ h[1] & h[0] & \\dots & h[2] \\\\ \\vdots & \\vdots & \\ddots & \\vdots \\\\ h[N-1] & h[N-2] & \\dots & h[0] \\end{bmatrix}$$\n"
         "Every row is a circular right-shift of the previous row. Circular convolution is diagonalized by the DFT matrix $F_N$."),

        ("# Section 3: Block Convolution: Overlap-Add and Overlap-Save\n\n"
         "When filtering very long or streaming sequences $x[n]$ with an FIR filter of length $M$:\n\n"
         "1. Overlap-Add (OLA) Method:\n"
         "- Segment input into non-overlapping blocks of length $L$.\n"
         "- Convolve each block with filter (length $N = L + M - 1$).\n"
         "- Adjacent output blocks overlap by $M - 1$ samples and are added together.\n\n"
         "2. Overlap-Save (OLS) Method:\n"
         "- Segment input into overlapping blocks of length $N = L + M - 1$, overlapping by $M - 1$ samples.\n"
         "- Perform $N$-point circular convolution.\n"
         "- Discard the first $M - 1$ points contaminated by circular wrap-around and retain the remaining $L$ valid samples."),

        ("# Section 4: Goertzel Algorithm for Single-Bin DFT\n\n"
         "The Goertzel algorithm calculates a single frequency bin $X[k]$ without computing the full FFT:\n\n"
         "Difference Equation (Second-Order IIR Filter):\n"
         "$$s[n] = x[n] + 2 \\cos(2\\pi k / N) s[n-1] - s[n-2]$$\n"
         "with initial conditions $s[-1] = s[-2] = 0$.\n\n"
         "Output calculation at $n = N$:\n"
         "$$X[k] = s[N] - W_N^k s[N-1]$$\n\n"
         "Complexity: $N + 2$ real multiplications and $2N + 1$ real additions. Highly efficient for DTMF tone detection."),

        ("# Section 5: Chirp Z-Transform (CZT)\n\n"
         "The Chirp Z-Transform evaluates the Z-transform along arbitrary spiral contours in the z-plane:\n"
         "$$z_k = A \\cdot W^{-k}, \\quad k = 0, 1, \\dots, M-1$$\n"
         "where $A = A_0 e^{j \\theta_0}$ and $W = W_0 e^{-j \\phi_0}$.\n\n"
         "Bluestein's Substitution:\n"
         "Using the identity $2nk = n^2 + k^2 - (k - n)^2$, CZT is reformulated as a linear high-speed FFT convolution."),

        ("# Section 6: Parks-McClellan (Remez Exchange) Algorithm\n\n"
         "The Parks-McClellan algorithm designs optimal linear-phase FIR filters in the Chebyshev (minimax error) sense.\n\n"
         "Alternation Theorem:\n"
         "The error function $E(\\omega) = W(\\omega)[H_d(\\omega) - H(\\omega)]$ alternates between local extrema with alternating signs:\n"
         "$$E(\\omega_i) = -E(\\omega_{i-1}) = \\pm \\max |E(\\omega)|$$\n"
         "Number of extremal frequencies is at least $r + 1$, where $r$ is the number of independent cosine basis functions.\n"
         "Yields strictly equiripple passband and stopband behavior with minimum possible filter order."),

        ("# Section 7: Bilinear Prewarping Quick Lookup Table\n\n"
         "Prewarping relationship: $\\Omega_c = 2 F_s \\tan(\\omega_c / 2) = 2 F_s \\tan(\\pi f_c / F_s)$.\n\n"
         "Prewarped Analog Cutoff $\\Omega_c$ for $f_c = 1000 \\text{ Hz}$ across Standard Sampling Rates:\n"
         "- $F_s = 8000 \\text{ Hz} \\implies \\omega_c = 0.25\\pi \\implies \\Omega_c = 16000 \\cdot \\tan(0.125\\pi) = 6627.42 \\text{ rad/s}$.\n"
         "- $F_s = 10000 \\text{ Hz} \\implies \\omega_c = 0.2\\pi \\implies \\Omega_c = 20000 \\cdot \\tan(0.1\\pi) = 6498.39 \\text{ rad/s}$.\n"
         "- $F_s = 16000 \\text{ Hz} \\implies \\omega_c = 0.125\\pi \\implies \\Omega_c = 32000 \\cdot \\tan(0.0625\\pi) = 6384.78 \\text{ rad/s}$.\n"
         "- $F_s = 44100 \\text{ Hz} \\implies \\omega_c = 0.04535\\pi \\implies \\Omega_c = 88200 \\cdot \\tan(0.02268\\pi) = 6303.88 \\text{ rad/s}$."),

        ("# Section 8: Direct Form to Lattice Realization\n\n"
         "FIR Lattice Structure:\n"
         "Recursive reflection coefficients $k_m$ for $m = M-1, \\dots, 0$:\n"
         "$$A_{m-1}(z) = \\frac{A_m(z) - k_m B_m(z)}{1 - k_m^2}$$\n"
         "Stability check for IIR filters: An all-pole IIR filter is stable if and only if all reflection coefficients satisfy $|k_m| < 1$."),

        ("# Section 9: Fixed-Point Arithmetic and Quantization Mechanics\n\n"
         "Two's Complement Format $Q_{m.f}$:\n"
         "Total bits $B = 1 + m + f$ (1 sign bit, $m$ integer bits, $f$ fractional bits).\n\n"
         "Quantization Error Characteristics:\n"
         "- Truncation: Error $e = Q(x) - x$ is always non-positive for two's complement $(-2^{-f} < e \\le 0)$, causing DC bias.\n"
         "- Rounding: Error is symmetric $(-2^{-f}/2 \\le e < 2^{-f}/2)$ with zero mean and variance $\\sigma^2 = 2^{-2f} / 12$.\n"
         "- Overflow Protection: Wrap-around overflow causes large destructive limit cycles; saturation arithmetic clamps output to full-scale limits."),

        ("# Section 10: DSP Hardware Architecture Features\n\n"
         "Key Hardware Blocks for High-Throughput DSP:\n"
         "1. Dedicated Multiply-Accumulate (MAC) Unit: Computes $y \\leftarrow y + a \\cdot b$ in a single clock cycle.\n"
         "2. Harvard Architecture: Separate program memory and data memory buses, enabling simultaneous instruction fetch and dual operand access.\n"
         "3. Circular Addressing: Hardware pointer wrap-around for implementing delay lines and circular buffers without software bounds checking.")
    ]

    full_text = "\n---\n".join(sections)
    md_path.write_text(full_text, encoding="utf-8")
    print(f"Generated {md_path.name} with {len(sections)} sections/pages.")

# -------------------------------------------------------------
# 4. GENERATE handwritten_bilinear_transform.pdf & PNG Scans (8 Pages)
# -------------------------------------------------------------
def generate_handwritten_pages():
    hw_pdf_path = HW_DIR / "handwritten_bilinear_transform.pdf"
    doc = pymupdf.open()

    hw_pages = [
        # Page 1
        ("Bilinear Transform Derivation (Trapezoidal Integration)",
         "Handwritten Derivation - DSP Exam Notes\n\n"
         "Derivation of s-to-z Mapping via Numerical Integration:\n\n"
         "Consider continuous 1st order differential equation:\n"
         "   dy(t)/dt = x(t)\n"
         "Integrate both sides from nT to (n+1)T:\n"
         "   integral_{nT}^{(n+1)T} dy(t) = integral_{nT}^{(n+1)T} x(t) dt\n"
         "   y(nT + T) - y(nT) = integral_{nT}^{(n+1)T} x(t) dt\n\n"
         "Apply Trapezoidal Rule of Numerical Integration:\n"
         "   y[n+1] - y[n] approx (T / 2) * [ x[n+1] + x[n] ]\n\n"
         "Take Z-transform of both sides:\n"
         "   z Y(z) - Y(z) = (T / 2) [ z X(z) + X(z) ]\n"
         "   Y(z) (z - 1) = (T / 2) X(z) (z + 1)\n"
         "   H(z) = Y(z) / X(z) = (T / 2) * ((z + 1) / (z - 1))\n\n"
         "Comparing with continuous integration H_a(s) = 1 / s:\n"
         "   1 / s = (T / 2) * ((z + 1) / (z - 1))\n"
         "   ==> s = (2 / T) * ((z - 1) / (z + 1)) = (2 / T) * ((1 - z^-1) / (1 + z^-1))\n"
         "Q.E.D. Standard Bilinear Transformation Formula."),

        # Page 2
        ("Handwritten Warping Analysis",
         "Derivation: Mapping the Frequency Axis\n\n"
         "Substitute s = j*Omega (analog) and z = e^{j*omega} (digital):\n"
         "   j*Omega = (2 / T) * ( (e^{j*omega} - 1) / (e^{j*omega} + 1) )\n"
         "Factor out e^{j*omega/2}:\n"
         "   j*Omega = (2 / T) * ( e^{j*omega/2} (e^{j*omega/2} - e^{-j*omega/2}) ) /\n"
         "                       ( e^{j*omega/2} (e^{j*omega/2} + e^{-j*omega/2}) )\n"
         "   j*Omega = (2 / T) * ( 2j * sin(omega/2) ) / ( 2 * cos(omega/2) )\n"
         "   j*Omega = j * (2 / T) * tan(omega / 2)\n\n"
         "===> Omega = (2 / T) * tan(omega / 2)\n"
         "Inversely: omega = 2 * arctan(Omega * T / 2)\n\n"
         "Key Observations from Plot:\n"
         "- For small omega, tan(omega/2) approx omega/2 ==> Omega approx omega/T (Linear).\n"
         "- As omega -> pi, tan(omega/2) -> infinity ==> entire infinite analog axis [-inf, inf] maps into [-pi, pi].\n"
         "- Frequency Warping: High analog frequencies are heavily compressed into the digital unit circle."),

        # Page 3
        ("Handwritten Butterworth Order Derivation",
         "Step-by-Step Order N Formula Derivation:\n\n"
         "Butterworth magnitude squared function:\n"
         "   |H(j*Omega)|^2 = 1 / ( 1 + (Omega / Omega_c)^(2N) )\n\n"
         "At passband edge Omega_p with max ripple alpha_p (dB):\n"
         "   10 * log10( 1 + (Omega_p / Omega_c)^(2N) ) = alpha_p\n"
         "   1 + (Omega_p / Omega_c)^(2N) = 10^(0.1 * alpha_p)\n"
         "   (Omega_p / Omega_c)^(2N) = 10^(0.1 * alpha_p) - 1   ---- (Eq. 1)\n\n"
         "At stopband edge Omega_s with min attenuation alpha_s (dB):\n"
         "   (Omega_s / Omega_c)^(2N) = 10^(0.1 * alpha_s) - 1   ---- (Eq. 2)\n\n"
         "Divide Eq. 2 by Eq. 1:\n"
         "   (Omega_s / Omega_p)^(2N) = ( 10^(0.1*alpha_s) - 1 ) / ( 10^(0.1*alpha_p) - 1 )\n"
         "Take log10 of both sides:\n"
         "   2N * log10(Omega_s / Omega_p) = log10( (10^(0.1*alpha_s) - 1) / (10^(0.1*alpha_p) - 1) )\n"
         "   N = ceil( log10( (10^(0.1*alpha_s) - 1) / (10^(0.1*alpha_p) - 1) ) / (2 * log10(Omega_s / Omega_p)) )."),

        # Page 4
        ("Handwritten Pole Placement Diagram",
         "Pole Distribution for Butterworth Prototype:\n\n"
         "For N = 3 Butterworth Filter:\n"
         "All poles lie on circle of radius Omega_c in left-half s-plane.\n"
         "Pole locations: s_k = Omega_c * e^{j * theta_k}, where:\n"
         "   theta_k = pi/2 + (2k - 1)*pi / (2*N) for k = 1, 2, 3.\n\n"
         "- k = 1: theta_1 = pi/2 + pi/6 = 2*pi/3 = 120 degrees\n"
         "  s_1 = Omega_c * (-0.5 + j * 0.866)\n"
         "- k = 2: theta_2 = pi/2 + 3*pi/6 = pi = 180 degrees\n"
         "  s_2 = -Omega_c\n"
         "- k = 3: theta_3 = pi/2 + 5*pi/6 = 4*pi/3 = 240 degrees\n"
         "  s_3 = Omega_c * (-0.5 - j * 0.866)\n\n"
         "Prototype Transfer Function:\n"
         "   H_a(s) = Omega_c^3 / ( (s - s1)(s - s2)(s - s3) ) = Omega_c^3 / ( (s + Omega_c)(s^2 + Omega_c*s + Omega_c^2) )."),

        # Page 5
        ("Worked Problem: 2nd Order Butterworth Design (Part 1)",
         "Handwritten Worked Example - Exam Problem:\n\n"
         "Problem Statement: Design a 2nd-order digital lowpass Butterworth filter using BLT.\n"
         "Specifications:\n"
         "- Sampling Frequency: F_s = 10 kHz (T = 0.0001 s = 10^-4 s)\n"
         "- Cutoff frequency: f_c = 1 kHz\n\n"
         "Step 1: Calculate Digital Cutoff Frequency omega_c:\n"
         "   omega_c = 2 * pi * f_c / F_s = 2 * pi * 1000 / 10000 = 0.2 * pi rad/sample.\n\n"
         "Step 2: Frequency Prewarping to Find Analog Cutoff Omega_c:\n"
         "   Omega_c = (2 / T) * tan(omega_c / 2)\n"
         "   Omega_c = 2 * 10000 * tan(0.1 * pi)\n"
         "   tan(0.1 * pi) = tan(18 degrees) = 0.324919696\n"
         "   Omega_c = 20000 * 0.32492 = 6498.39 rad/s.\n\n"
         "Step 3: Normalized 2nd Order Butterworth Analog Transfer Function:\n"
         "   H_a(s) = Omega_c^2 / (s^2 + sqrt(2)*Omega_c*s + Omega_c^2)."),

        # Page 6
        ("Worked Problem: 2nd Order Butterworth Design (Part 2)",
         "Handwritten Worked Example (Continued):\n\n"
         "Step 4: Substitute Bilinear Transformation s = 20000 * (z - 1)/(z + 1):\n"
         "Let K = 20000 and Omega_c = 6498.39 rad/s.\n"
         "Denominator D(z) = [ K*(z - 1)/(z + 1) ]^2 + sqrt(2)*Omega_c*[ K*(z - 1)/(z + 1) ] + Omega_c^2.\n"
         "Multiply numerator and denominator by (z + 1)^2:\n"
         "   Numerator = Omega_c^2 * (z + 1)^2 = Omega_c^2 * (1 + 2 z^-1 + z^-2) z^2.\n"
         "Denominator after collecting coefficients:\n"
         "   A = K^2 + sqrt(2)*K*Omega_c + Omega_c^2 = 4*10^8 + 1.838*10^8 + 4.223*10^7 = 6.2603 * 10^8.\n"
         "   B = -2*K^2 + 2*Omega_c^2 = -8*10^8 + 0.8446*10^8 = -7.1554 * 10^8.\n"
         "   C = K^2 - sqrt(2)*K*Omega_c + Omega_c^2 = 4*10^8 - 1.838*10^8 + 4.223*10^7 = 2.5843 * 10^8.\n\n"
         "Dividing through by A:\n"
         "   b0 = Omega_c^2 / A = 4.2229*10^7 / 6.2603*10^8 = 0.06745\n"
         "   a1 = B / A = -7.1554 / 6.2603 = -1.1430\n"
         "   a2 = C / A = 2.5843 / 6.2603 = 0.4128\n\n"
         "Final Digital Transfer Function:\n"
         "   H(z) = ( 0.06745 * (1 + 2*z^-1 + z^-2) ) / ( 1 - 1.1430*z^-1 + 0.4128*z^-2 )."),

        # Page 7
        ("Handwritten Notes on Limit Cycles & Overflow",
         "Finite Wordlength Notes - Practical Observations:\n\n"
         "1. Zero-Input Limit Cycles:\n"
         "In recursive filter y[n] = -a y[n-1] + x[n]:\n"
         "If input x[n] goes to zero, rounding arithmetic can sustain persistent oscillations.\n"
         "Remedy: Magnitude Truncation (always truncate towards zero) instead of rounding.\n"
         "Deadband zone: [-1 / (2*(1 - |a|)), 1 / (2*(1 - |a|))].\n\n"
         "2. Overflow Limit Cycles:\n"
         "When two large positive fixed-point numbers add together, two's complement wraps around to large negative number.\n"
         "Causes full-scale high-energy square wave oscillation (overflow limit cycle).\n"
         "Remedy: Saturation Arithmetic Logic - clamp any sum exceeding +1 to +0.9999 and any sum below -1 to -1.0."),

        # Page 8
        ("Handwritten Comparison Table: FIR vs IIR Filters",
         "Master Exam Cheat Sheet - FIR vs IIR Summary Table:\n\n"
         "Feature                 | FIR Filter                  | IIR Filter\n"
         "------------------------+-----------------------------+----------------------------\n"
         "Phase Linearity         | Exactly Linear Phase        | Non-linear phase\n"
         "Stability               | Always Stable (All poles=0) | Can become unstable\n"
         "Filter Order for Spec   | High (Large delay/latency)  | Low (Sharp cutoff)\n"
         "Memory Requirements     | Higher                      | Lower\n"
         "Implementation Form     | Direct Form, Polyphase      | Cascade / Parallel Biquads\n"
         "Limit Cycles            | No limit cycles             | Susceptible to limit cycles\n"
         "Design Methods          | Windowing, Parks-McClellan  | Bilinear Transform, Imp. Inv.")
    ]

    for title, body in hw_pages:
        page = doc.new_page(width=595, height=842) # A4
        # Margin lines like notebook paper
        page.draw_rect(pymupdf.Rect(0, 0, 595, 842), color=(0.98, 0.98, 0.96), fill=(0.99, 0.99, 0.97))
        page.draw_line(pymupdf.Point(70, 0), pymupdf.Point(70, 842), color=(0.9, 0.6, 0.6), width=1) # Red margin line
        # Header
        page.insert_text((80, 50), title, fontsize=13, fontname="times-bold", color=(0.1, 0.1, 0.5))
        # Body in cursive/serif style mimicking handwriting
        page.insert_textbox(pymupdf.Rect(80, 70, 550, 800), body, fontsize=10, fontname="times-roman", lineheight=1.4)
        page_num_str = f"Handwritten Page {len(doc)}"
        page.insert_text((250, 820), page_num_str, fontsize=9, fontname="times-italic", color=(0.4, 0.4, 0.4))

    doc.save(hw_pdf_path)
    doc.close()
    print(f"Generated {hw_pdf_path.name} with {len(hw_pages)} handwritten pages.")

    # Also render page 1 and page 2 as standalone PNG images in handwritten directory
    # so we can directly test image file upload and OCR
    doc = pymupdf.open(hw_pdf_path)
    for p_idx in [0, 1]:
        pix = doc[p_idx].get_pixmap(matrix=pymupdf.Matrix(2.0, 2.0))
        img_out = HW_DIR / f"page{p_idx+1}_scanned.png"
        pix.save(img_out)
        print(f"Rendered image scan {img_out.name}")
    doc.close()

if __name__ == "__main__":
    print("Generating comprehensive 60+ page multimodal course corpus...")
    generate_lecture_notes()
    generate_slides()
    generate_markdown()
    generate_handwritten_pages()
    print("All corpus files successfully generated!")
