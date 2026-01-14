#!/usr/bin/env uv run python3


from agentica import spawn
from agentica.common import MaxTokens


async def main():
    agent = await spawn(
        "You are a physicist who is an expert in the field of solid state physics."
        + "All your answers are off the top of your head.",
        model='openrouter:google/gemini-2.5-flash',
        max_tokens=MaxTokens(per_invocation=None, per_round=None, rounds=5),
    )

    c = await agent.call(float, "What is the lattice constant of silicon in Ångströms")
    print("Lattice constant of silicon:", c)
    print("Usage:", agent.last_usage())

    derivation = await agent.call("And how is this constant derived?")
    print("Derivation of lattice constant:", derivation)
    print("Usage:", agent.last_usage())

    x = await agent.call(str, "Short greeting please")
    print("Short greeting:", x)
    print("Usage:", agent.last_usage())

    print("\nTotal usage:", agent.total_usage())


# Output:
# Lattice constant of silicon: 5.431
# Derivation of lattice constant: The lattice constant of silicon is historically derived from experimental measurements using X-ray diffraction techniques. This method involves analyzing the patterns created when X-rays are scattered by the silicon crystal lattice.

# Here is a brief explanation of the process:
# 1. **X-ray Diffraction (XRD):** When a beam of X-rays hits a crystal, it is diffracted in many specific directions. By measuring the angles and intensities of these diffracted beams, one can infer the crystal structure.
# 2. **Bragg's Law:** The relationship between the wavelength of the X-rays, the angle of diffraction, and the lattice spacing (lattice parameters) is given by Bragg's Law: \( n\lambda = 2d\sin(\theta) \), where \( \lambda \) is the X-ray wavelength, \( d \) is the lattice plane spacing, \( \theta \) is the diffraction angle, and \( n \) is an integer.
# 3. **Analysis:** By applying Bragg's Law to experimental data, the lattice constant can be accurately calculated. For silicon, which has a diamond cubic structure, the relationship between the lattice constant and the plane spacing for a specific family of planes in the crystal lattice is used to deduce the lattice constant.

# Thus, the lattice constant is not theoretically derived but rather measured through precise physical experiments.

if __name__ == "__main__":
    from demos.runner import run

    run(main())
