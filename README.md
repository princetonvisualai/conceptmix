# ConceptMix

We propose CONCEPTMIX, a scalable and customizable benchmark for evaluating the compositional capabilities of T2I models, including prompts from 8 visual concept categories.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Scripts](#scripts)
- [Contributing](#contributing)
- [License](#license)

## Installation

To set up the environment for ConceptMix, you can use the provided `environment.yml` file to create a Conda environment.

```sh
conda env create -f environment.yml
conda activate conceptmix
```

## Usage

### Step 1: Generating Prompts

To generate text, use the `generate_text.sh` script.

```sh
sh ./generate_text.sh
```

### Step 2: Generating Images

To generate images, use the `generate_image.sh` script. 

```sh
sh ./generate_image.sh
```


### Grading

To evaluate the generated images, use the `grading.sh` script.

```sh
sh ./grading.sh
```

You can also submit the grading job using the `grading.slurm` script if you are using a SLURM-based cluster.

```sh
sbatch grading.slurm
```

## Visual Concepts

The configuration files are located in the `config` directory. You can modify these files to adjust the settings for prompt generation.

<!-- ## Scripts

- `generate_image.sh`: Script to generate images.
- `generate_text.sh`: Script to generate text.
- `grading.sh`: Script to evaluate the generated images.
- `grading.slurm`: SLURM script to submit the grading job on a cluster. -->

## Contributing

We welcome contributions from the community. If you would like to contribute, please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
