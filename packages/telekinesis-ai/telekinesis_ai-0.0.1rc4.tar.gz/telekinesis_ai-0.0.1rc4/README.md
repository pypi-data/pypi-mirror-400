<div align="center">
  <p>
    <a align="center" href="" target="_blank">
      <img
        width="100%"
        src="https://telekinesis-public-assets.s3.us-east-1.amazonaws.com/Telekinesis+Banner.png"
      >
    </a>
  </p>

  <br>

  [Telekinesis Examples](https://github.com/telekinesis-ai/telekinesis-examples) | [Telekinesis Data](https://gitlab.com/telekinesis/telekinesis-data)
  <br>

[![PyPI version](https://img.shields.io/pypi/v/telekinesis-ai)](https://pypi.org/project/telekinesis-ai/)
[![License](https://img.shields.io/pypi/l/telekinesis-ai)](https://pypi.org/project/telekinesis-ai/)
[![Python versions](https://img.shields.io/pypi/pyversions/telekinesis-ai)](https://pypi.org/project/telekinesis-ai/)

</div>

# Telekinesis SDK

Telekinesis SDK is a modular Python-based SDK for Physical AI, providing a unified set of algorithms for robotics, 3D perception, computer vision, motion planning, and vision-language models.

It is designed for roboticists and computer vision engineers who want to build end-to-end Physical AI systems without stitching together fragmented libraries.

## What You Can Build With Telekinesis SDK

**Telekinesis SDK includes:**
- 3D perception (filtering, registration, clustering)
- 2D perception (image processing, segmentation)
- Synthetic data generation
- Motion planning, kinematics, and control
- Vision-Language Models (VLMs)
- Physical AI agents

Learn more about the Telekinesis SDK in the
[About Telekinesis](https://docs.telekinesis.ai/#what-is-telekinesis).

## Installation

You will need to have `Python 3.11` or higher set up to use the Telekinesis SDK

Run the following command to install the Telekinesis SDK:

```bash
pip install telekinesis-ai
```

## Getting Started

**Telekinesis SDK requires a valid API key to authenticate requests.**

If you have not yet set up your API key, follow the official [Quickstart Guide](https://docs.telekinesis.ai/getting-started/quickstart) to set up your API key.

## Example

The following example assumes the API key has been generated and has been set as `TELEKINESIS_API_KEY` environment variable.

Run a python code to quickly test your installation:

> This example will fail if `TELEKINESIS_API_KEY` is not set correctly.

```python
import numpy as np
from telekinesis import vitreous

# Create a cylinder mesh
cylinder_mesh = vitreous.create_cylinder_mesh(
		radius=0.01,
		height=0.02,
		radial_resolution=20,
		height_resolution=4,
		retain_base=False,
		vertex_tolerance=1e-6,
		transformation_matrix=np.eye(4, dtype=np.float32),
		compute_vertex_normals=True,
	)

# Convert it to point cloud
point_cloud = vitreous.convert_mesh_to_point_cloud(
		mesh=cylinder_mesh,
		num_points=10000,
		sampling_method="poisson_disk",
		initial_sampling_factor=5,
		initial_point_cloud=None,
		use_triangle_normal=False,
	)
print(point_cloud.positions)
# Use point_cloud in downstream processing or visualize the point cloud with any tool        
```

Expected output:
Some logs and random valued point cloud positions in the below format is output
```bash
...
... 
[[-0.00835031 -0.00536731 -0.00429686]
 [ 0.00854885  0.00497764  0.00044501]
 [ 0.00838172  0.00530565  0.00249433]
 ...
 [-0.00280485  0.00955575  0.00949276]
 [-0.00743726 -0.00653076 -0.00238814]
 [ 0.00023231 -0.00996321  0.00887559]]
```

You are now set up to build with Telekinesis.

The recommended way to explore Telekinesis SDK today is via the [Telekinesis Examples](https://github.com/telekinesis-ai/telekinesis-examples.git) repository, which contains fully runnable workflows built on top of the SDK.

## Resources 

- Examples    
  Runnable examples demonstrating Telekinesis SDK capabilities: [Telekinesis Examples](https://github.com/telekinesis-ai/telekinesis-examples)

- Documentation   
  Full SDK documentation and usage details: [Telekinesis Docs](https://docs.telekinesis.ai)

- Sample Data   
  Datasets used across the examples: [Telekinesis Data](https://gitlab.com/telekinesis/telekinesis-data)

## Support

For issues and questions:
- Create an [issue](https://github.com/telekinesis-ai/telekinesis-examples/issues) in the GitHub repository.
- Contact the Telekinesis development team.

<p align="center">
  <a href="https://github.com/telekinesis-ai">GitHub</a>
  &nbsp;•&nbsp;
  <a href="https://www.linkedin.com/company/telekinesis-ai/">LinkedIn</a>
  &nbsp;•&nbsp;
  <a href="https://x.com/telekinesis_ai">X</a>
  &nbsp;•&nbsp;
  <a href="https://discord.gg/7NnQ3bQHqm">Discord</a>
</p>