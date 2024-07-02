#!/bin/bash

output_dir=""
config_path="./config"
models=("$1")

# models=(
#     "playground-v2.5-1024px-aesthetic"
#     "DeepFloyd_I_XL_v1"
#     "SDXL_Turbo"
#     "SDXL_2_1"
#     "SDXL_Base"
#     "stable-diffusion"
#     "dall-e-3"
#     "PixArt-XL-2-1024-MS"
# )


models_arg=$(printf ",%s" "${models[@]}")
models_arg=${models_arg:1}

for num_skills in {1..7}; do
    intermediate_file_path="all/0_sentence_collection/300_sentences_k=${num_skills}.json"
    
    CUDA_VISIBLE_DEVICES=0 python ./dynamix/main_image_generation.py --num_skills $num_skills --output_dir $output_dir --config_path $config_path --intermediate_file_path $intermediate_file_path --model $models_arg
done

echo "Image generation completed."

