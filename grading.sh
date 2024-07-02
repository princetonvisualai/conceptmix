#!/bin/sh
source ~/.bashrc
conda activate t2v

scores_base_dir="./all_ind_scores"
scores_dir="${scores_base_dir}/k_results_300"

models=(
  "gpt"
  # "llava_score_13b"
  # "instructblip_score"
  # "clip_score"
  # "blip_itm_score"
  # "pick_score"
  # "hpsv2_score"
  # "image_reward_score"
)

run_demo() {
  image_question_path=$1
  model_name=$2
  
  if [ ! -d "$scores_dir" ]; then
    echo "$(date): Creating directory $scores_dir" | tee /dev/stderr
    mkdir -p "$scores_dir"
  fi

  model_name_short=$(basename "$(dirname "$(dirname "$image_question_path")")")
  k_value=$(basename "$(dirname "$image_question_path")")
  score_path="${scores_dir}/${model_name_short}_k=${k_value}_score.json"

  echo "$(date): Running $model_name on $image_question_path" | tee /dev/stderr
  echo "$(date): Score path should be: $score_path" | tee /dev/stderr
  
  score=$(python ./dynamix/grading/multi_grading.py --image_question_path "$image_question_path" --model_name "$model_name" --score_path $score_path)

  echo "{\"image_question_path\": \"$image_question_path\", \"score\": $score},"
}

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <directory>"
  exit 1
fi

input_dir=$1

echo "$(date): Script started" | tee /dev/stderr

for model_name in "${models[@]}"; do
  directories=$(find "$input_dir" -type f -name "*result.json" ! -name "*.png" -exec dirname {} \; | sort -u)

  for dir in $directories; do
    echo "$(date): Processing directory: $dir" | tee /dev/stderr
    find "$dir" -type f -name "*result.json" ! -name "*.png" -print0 | while IFS= read -r -d '' image_question_path; do
      echo "$(date): Calling run_demo with $image_question_path $model_name" | tee /dev/stderr
      run_demo "$image_question_path" "$model_name"
    done
  done
done

echo "$(date): Script finished" | tee /dev/stderr

