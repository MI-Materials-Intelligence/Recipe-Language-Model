## Concentration PVK
### From concentration to coverage & gray level
1. **Too low concentration (e.g. ~0.1 M)**
- **Fluid mechanics**: low viscosity and low solute load mean that during spin-coating, most of the liquid is flung off; the residual wet film is extremely thin. Classical spin-coating theory predicts thickness roughly scales with viscosity and solute content, so lowering concentration pushes the thickness down strongly.
- **Crystallization**: the total amount of perovskite that can nucleate and grow is limited. Nucleation often happens at discrete centers, giving sparse islands rather than a continuous layer.
- **Morphology**:
- Coverage often falls below **60%**, with clear coffee-ring patterns and uncoated patches.
- Average gray level moves into the **90–120** range (light/whitish), reflecting exposed substrate and ultra-thin domains.
2. **Optimal concentration (e.g. ~1.73 mol/L)**
- **Flow and film thickness**: viscosity is high enough to keep a substantial wet film on the substrate after the spin, but not so high that the film cannot level.
- **Crystallization**: the supersaturation reached during antisolvent treatment and solvent evaporation leads to a dense, interconnected network of crystals. Grain boundaries per unit area decrease as grains grow laterally and vertically.
- **Morphology**:
- Coverage can reach **99.9–100%**, i.e., essentially pinhole-free.
- Mean gray level drops into the **0–40** window, corresponding to a dark, compact film.
3. **Too high concentration (≥1.8–1.9 mol/L)**
- **Fluid mechanics**: viscosity becomes large; the solution resists radial flow, so most of the material remains near the center.
- **Crystallization stress**: local supersaturation can be excessive; nucleation is hyperspatial and the film locks in before it has time to level, giving “mountains and valleys”.
- **Morphology**:
- Center regions become thick “domes” with dark gray level (0–40 or 40–65), while outer regions are under-coated, giving coverage that can fall to ~**9–13%** effective area.
- Cracks form from drying and crystallization stress, adding extra pinholes and shunt paths.
### Impact on PCE, Voc, Jsc, FF
- **Jsc**
- At very low concentration, the optical path length is short and large portions of the area are inactive; Jsc falls sharply.
- At optimal concentration (~1.7 M), you get high optical density with minimal parasitic transmission, so Jsc is maximized.
- At too high concentration, the average thickness in active regions may be high, but the *effective* active area is small and scattering at rough interfaces increases recombination, so Jsc again decreases.
- **Voc**
- Strongly tied to defect density and nonradiative recombination. Low concentration → sparse islands with many exposed interfaces and grain boundaries → high trap density → Voc loss.
- Optimal concentration → better crystalline coherence, fewer voids → reduced Shockley–Read–Hall (SRH) recombination and higher Voc.
- Excessive concentration → cracks and local decomposition products (e.g. PbI₂ clusters) introduce recombination centers; Voc suffers.
- **FF**
- Poor coverage (0–60%) and discrete islands give low Rsh (many leakage paths between ETL and HTL) and high Rs (current forced through narrow percolation paths), which strongly depresses FF.
- Optimal coverage (~90–100%) aligns with high Rsh and moderate Rs → FF peaks.
- Very high concentration with macro-cracks again lowers Rsh and increases Rs, cutting FF.
- **PCE**
- Follows the combined trend: extremely low at low and very high concentrations, with a broad maximum near the “optimum” viscosity/coverage/gray-level window where both Jsc and Voc are reasonably high and FF is not compromised.