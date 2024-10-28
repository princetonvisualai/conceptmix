# ConceptMix


**ConceptMix: A Compositional Image Generation Benchmark with Controllable Difficulty** 

NeurIPS 2024, Dataset and Benchmark Track [[paper](https://arxiv.org/abs/2408.14339)][[website](https://princetonvisualai.github.io/conceptmix/)]


[Xindi Wu\*](https://xindiwu.github.io/), [Dingli Yu\*](https://dingliyu.net/), [Yangsibo Huang\*](https://hazelsuko07.github.io/yangsibo/), [Olga Russakovsky](https://www.cs.princeton.edu/~olgarus/), [Sanjeev Arora](https://www.cs.princeton.edu/~arora/)


We propose ConceptMix, a scalable and customizable benchmark for evaluating the compositional capabilities of T2I models, including prompts from 8 visual concept categories.

## News 🔥
- [10/24] We have released the 300 x 7 prompts used for evaluation in the [`sentence_collection`](https://github.com/princetonvisualai/conceptmix/tree/main/sentence_collection) folder for public use.
- [09/24] Our paper [ConceptMix](https://arxiv.org/abs/2408.14339) has been accepted to NeurIPS 2024, Dataset and Benchmark Track.


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
This project is licensed under the MIT License.


## Citation

If you find this repository useful for your research, please cite with the following BibTeX entry:

```
@article{wu2024conceptmix,
  title={ConceptMix: A Compositional Image Generation Benchmark with Controllable Difficulty},
  author={Wu, Xindi and Yu, Dingli and Huang, Yangsibo and Russakovsky, Olga and Arora, Sanjeev},
  journal={arXiv preprint arXiv:2408.14339},
  year={2024}
}
```

## Acknowledgements
```
This material is based upon work supported by the National Science Foundation under Grant No.2107048. 
Any opinions, findings, and conclusions, or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the National Science Foundation. 
DY and SA are supported by NSF and ONR. YH is supported by the Wallace Memorial Fellowship. 
We thank many people for their helpful discussion, feedback, and human studies listed in alphabetical order by last name: 
Allison Chen, Jihoon Chung, Victor Chu, Derek Geng, Luxi He, Erich Liang, Kaiqu Liang, Michel Liao, Yuhan Liu, Abhishek Panigrahi, Simon Park, Ofir Press, Zeyu Wang, Boyi Wei, David Yan, William Yang, Zoe Zager, Cindy Zhang, and Tyler Zhu from Princeton University, 
Zhiqiu Lin, Tiffany Ling from Carnegie Mellon University, 
Chiyuan Zhang from Google Research.
```