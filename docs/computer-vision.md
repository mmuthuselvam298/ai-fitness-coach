# Computer Vision & Biomechanics Engineering

This document details the mathematical models, pose estimation mechanics, filtering algorithms, and state machines powering FormFit AI.

---

## 1. Landmark Extraction & Visibility Gating

FormFit AI employs Google MediaPipe's 33-point topological pose model. Each landmark provides:
- $x, y$: Normalized pixel coordinates $[0.0, 1.0]$.
- $z$: Relative depth coordinate scaled to hip reference plane.
- $v$: Visibility score $[0.0, 1.0]$ representing probability that the keypoint is present and unoccluded.

### Visibility Threshold Policy
Joint angle calculations strictly require all 3 vertex points to satisfy:
$$v_i \ge 0.55 \quad \forall i \in \{A, B, C\}$$
If visibility drops below $0.55$, calculations are suspended and a `Stand in full camera view` calibration event is dispatched, preventing erratic jitter angles caused by partial occlusion.

---

## 2. Joint Angle Calculation

For three anatomical points $A$ (proximal), $B$ (vertex joint), and $C$ (distal):

$$\vec{u} = A - B = (x_a - x_b, y_a - y_b)$$
$$\vec{v} = C - B = (x_c - x_b, y_c - y_b)$$

The interior angle $\theta$ in degrees is:

$$\cos \theta = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|}$$
$$\theta = \arccos\left(\max\left(-1.0, \min\left(1.0, \cos \theta\right)\right)\right) \times \frac{180^\circ}{\pi}$$

Degenerate vectors where $\|\vec{u}\| < 10^{-7}$ or $\|\vec{v}\| < 10^{-7}$ safely return $0.0^\circ$ to prevent division by zero.

---

## 3. Landmark Smoothing Algorithms

Webcam landmark predictions naturally exhibit high-frequency Gaussian noise due to CMOS sensor grain and lighting variations.

### Option A: Exponential Moving Average (EMA)
$$S_t = \alpha \cdot X_t + (1 - \alpha) \cdot S_{t-1}$$
Configured with $\alpha = 0.65$ by default, which filters coordinate noise while introducing only $\sim 15\text{ms}$ phase delay.

### Option B: One Euro Filter
An adaptive 1st-order low-pass filter (Casiez et al., CHI 2012). It modulates the cutoff frequency $f_c$ proportionally to the velocity of movement:
$$f_c = f_{c,\min} + \beta \cdot |\dot{x}|$$
- During static poses / holds: $f_c \to f_{c,\min} \implies$ heavy smoothing eliminates jitter.
- During explosive movements: $f_c$ expands $\implies$ lag is virtually eliminated.

---

## 4. Exercise State Machines

### Squat State Machine
1. **`READY`**: User stands upright with knee angle $> 160^\circ$.
2. **`DESCENDING`**: Knee angle flexes below $150^\circ$. Peak descent time starts tracking.
3. **`BOTTOM`**: Knee reaches inflection point (target $\le 95^\circ$). If user ascends before $110^\circ$, movement is classified as a shallow aborted dip and discarded.
4. **`ASCENDING`**: Knee angle expands upwards past $115^\circ$.
5. **`COMPLETED`**: Knee angle returns upright $\ge 160^\circ$. Rep counter increments by 1.

### Form Checks
- **Depth Quality**: Knee angle $\le 90^\circ \implies 100$, $91^\circ - 100^\circ \implies 88$, $> 110^\circ \implies 45$.
- **Torso Lean**: Angle of shoulder-hip segment relative to gravity vertical axis. Leans $> 45^\circ$ trigger warning prompt *"Keep your chest upright"*.
- **Tempo Control**: Rep cycle under $1.2\text{s}$ triggers *"Control your descent - avoid bouncing"*.
