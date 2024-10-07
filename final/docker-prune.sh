#!/bin/bash
# Cleanup Docker orphan overlay2 directories which do pile up over time
# https://github.com/docker/buildx/issues/2061
set -eu

# Define the overlay2 directory
overlay_dir="/var/lib/docker/overlay2"

# Verify that the overlay2 directory exists
if [ ! -d "$overlay_dir" ]; then
  echo "The directory $overlay_dir does not exist. Please check the path."
  exit 1
fi

# Get all layer IDs associated with current containers (MergedDir, LowerDir, UpperDir, WorkDir)
container_layer_ids=$(docker ps -qa | xargs -r docker inspect --format '{{ .GraphDriver.Data.MergedDir }} {{ .GraphDriver.Data.LowerDir }} {{ .GraphDriver.Data.UpperDir }} {{ .GraphDriver.Data.WorkDir }}' | tr ' ' '\n' | tr ':' '\n' | awk -F'/' '{print $(NF-1)}' | sort | uniq)

# Get all layer IDs associated with images
image_layer_ids=$(docker images -qa | xargs -r docker inspect --format '{{ .GraphDriver.Data.MergedDir }} {{ .GraphDriver.Data.LowerDir }} {{ .GraphDriver.Data.UpperDir }} {{ .GraphDriver.Data.WorkDir }}' | tr ' ' '\n' | tr ':' '\n' | awk -F'/' '{print $(NF-1)}' | sort | uniq)

# Get all cache IDs of type source.local
source_local_cache_ids=$(docker system df -v | grep 'source.local' | awk '{print $1}' | sort | uniq)

# Combine the layer IDs of containers, images, and source.local caches
all_layer_ids=$(echo -e "$container_layer_ids\n$image_layer_ids" | sort | uniq)

echo "source_local_cache_ids:"
echo "$source_local_cache_ids"

echo "all_layer_ids:"
echo "$all_layer_ids"

# List all subdirectories in overlay2
overlay_subdirs=$(ls -1 $overlay_dir)

# Find and remove orphan directories that are not in the list of active layers or caches
echo "Searching for and removing orphan directories in $overlay_dir..."

for dir in $overlay_subdirs; do
  # Ignore directories ending in "-init" and the "l" directory
  if [[ "$dir" == *"-init" ]] || [[ "$dir" == "l" ]]; then
    echo "Ignoring special directory: $overlay_dir/$dir"
    continue
  fi

  # Check if the directory name starts with any of the source.local cache IDs
  preserve_dir=false
  for cache_id in $source_local_cache_ids; do
    if [[ "$dir" == "$cache_id"* ]]; then
      preserve_dir=true
      break
    fi
  done

  # If directory should be preserved, skip it
  if $preserve_dir; then
    echo "Preserving cache directory: $overlay_dir/$dir"
    continue
  fi

  # Check if the directory is associated with an active container or image
  if ! echo "$all_layer_ids" | grep -q "$dir"; then
    echo "Removing orphan directory: $overlay_dir/$dir"
    rm -rf "${overlay_dir:?}/$dir"
  fi
done

echo "Process completed."
