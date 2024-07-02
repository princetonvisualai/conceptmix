#!/bin/bash

output_dir=""
num_iterations=300

for num_skills in {1..7}; do
    for i in $(seq 1 $num_iterations); do
        CUDA_VISIBLE_DEVICES=0 python ./dynamix/main_sentence_generation.py --num_skills $num_skills --output_dir $output_dir --index $i --num_iterations $num_iterations
    done
done

echo "Image generation completed."
