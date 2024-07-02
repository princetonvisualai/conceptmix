#!/bin/bash
#SBATCH -N 1                  ## Node count
#SBATCH --gres=gpu:0
#SBATCH --ntasks-per-node=1
#SBATCH -t 0-02:00:00           ## Walltime
#SBATCH --mem=10G 
#SBATCH -c 2
#SBATCH --account=
#SBATCH --array=1-56
#SBATCH --output=logs/%x-%j-%a.out
#SBATCH --job-name=grading

# i * 7 + (k-1) = $SLURM_ARRAY_TASK_ID - 1
i=$((($SLURM_ARRAY_TASK_ID - 1) / 7))
k=$((($SLURM_ARRAY_TASK_ID - 1) % 7 + 1))

#!/bin/sh
source ~/.bashrc
conda activate t2v

scores_base_dir="./all_ind_scores"
scores_dir="${scores_base_dir}/k_results_300"

models=(
  "gpt"
  "llava_score_13b"
  "instructblip_score"
  "clip_score"
  "blip_itm_score"
  "pick_score"
  "hpsv2_score"
  "image_reward_score"
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

model_name=${models[$i]}
  
image_question_path="${input_dir}/${model_name}/${k}/result.json"

echo "$(date): Calling run_demo with $image_question_path $model_name" | tee /dev/stderr

run_demo "$image_question_path" "$model_name"

echo "$(date): Script finished" | tee /dev/stderr
