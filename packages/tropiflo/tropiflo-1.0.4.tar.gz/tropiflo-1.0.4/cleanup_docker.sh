#!/bin/bash
# Cleanup script for Co-DataScientist Docker artifacts
# Run this if you want to manually clean up all Co-DataScientist Docker images

echo "Co-DataScientist Docker Cleanup Script"
echo "======================================="
echo ""

# Count Co-DataScientist images
IMAGE_COUNT=$(docker images | grep -c "co-datascientist-" || true)

if [ "$IMAGE_COUNT" -eq 0 ]; then
    echo "No Co-DataScientist Docker images found. Already clean!"
    exit 0
fi

echo "Found $IMAGE_COUNT Co-DataScientist Docker images"
echo ""
echo "Images to be removed:"
docker images | grep "co-datascientist-"
echo ""

read -p "Remove all these images? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing Co-DataScientist Docker images..."
    docker images | grep "co-datascientist-" | awk '{print $3}' | xargs docker rmi -f 2>/dev/null || true
    echo "Cleanup complete!"
    
    # Also clean up any stopped containers (just in case)
    CONTAINER_COUNT=$(docker ps -a | grep -c "co-datascientist-" || true)
    if [ "$CONTAINER_COUNT" -gt 0 ]; then
        echo "Found $CONTAINER_COUNT stopped containers, removing..."
        docker ps -a | grep "co-datascientist-" | awk '{print $1}' | xargs docker rm -f 2>/dev/null || true
    fi
    
    echo "All Co-DataScientist Docker artifacts removed!"
else
    echo "Cleanup cancelled."
fi

